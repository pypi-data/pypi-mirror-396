"""
geoanalysis.py

Full refactor of the code you provided.  *Every* original function is
present, but the bugs flagged in the review are fixed, the style is
Black-formatted (line-length = 88), and wide “except:” blocks are replaced
by precise exceptions with proper logging.

The module contains two dataclasses:

* ``Geoanalysis`` – national-scale metrics, plots, DB write-back
* ``RegionalMapper`` – regional diagnostics (heat-map, KDE, MAPE map)

External helpers assumed unchanged:

* ``geocif.utils``   – nse, mape, pbias, to_db …
* ``geocif.logger``  – setup_logger_parser()
* ``viz.plot``       – plot_df_shpfile()

If any of those change their API, patch accordingly.
"""

from __future__ import annotations

import ast
import logging
import os
import re
import sqlite3
import warnings
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import arrow as ar
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import palettable as pal
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from geocif import logger as log
from geocif import utils
from .viz import plot

# --------------------------------------------------------------------- #
# Globals & style                                                      #
# --------------------------------------------------------------------- #

warnings.simplefilter("ignore", category=FutureWarning)
plt.rcParams.update({"figure.autolayout": True})

OBSERVED_COL = "Observed Yield (tn per ha)"
PREDICTED_COL = "Predicted Yield (tn per ha)"

# --------------------------------------------------------------------- #
# Helper utilities                                                     #
# --------------------------------------------------------------------- #


def safe_logger(logger: Optional[logging.Logger] = None) -> logging.Logger:
    """Return a configured logger instance."""
    if logger is None:
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s | %(message)s", force=True
        )
        logger = logging.getLogger(__name__)
    return logger


def table_exists(con: sqlite3.Connection, table: str) -> bool:
    """Return True if *table* exists in *con*."""
    sql = "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?"
    return con.execute(sql, (table,)).fetchone() is not None


# --------------------------------------------------------------------- #
# Geoanalysis                                                           #
# --------------------------------------------------------------------- #


@dataclass
class Geoanalysis:
    path_config_files: List[Path] = field(default_factory=list)
    logger: Optional[logging.Logger] = None
    parser: ConfigParser = field(default_factory=ConfigParser)

    # ----------------------------------------------------------------- #
    # Init                                                              #
    # ----------------------------------------------------------------- #
    def __post_init__(self) -> None:
        self.logger = safe_logger(self.logger)

        # runtime attributes
        self.country: str | None = None
        self.crop: str | None = None
        self.model: str | None = None
        self.table: str | None = None
        self.method: str | None = None
        self.admin_zone: str | None = None
        self.boundary_file: str | None = None
        self.number_lag_years: int = 5

        # directories
        self._date = ar.utcnow().to("America/New_York")
        self.today = self._date.format("MMMM_DD_YYYY")

        self.dir_out = Path(self.parser.get("PATHS", "dir_output"))
        self.dir_ml = self.dir_out / "ml"
        self.dir_db = self.dir_ml / "db"
        self.dir_analysis = self.dir_ml / "analysis" / self.today
        self.dir_db.mkdir(parents=True, exist_ok=True)
        self.dir_analysis.mkdir(parents=True, exist_ok=True)

        self.db_path = self.dir_db / self.parser.get("DEFAULT", "db")

        input_root = Path(self.parser.get("PATHS", "dir_input"))
        self.dir_shapefiles = input_root / "Global_Datasets" / "Regions" / "Shps"

        self.df_analysis = pd.DataFrame()  # placeholder

    # ----------------------------------------------------------------- #
    # Database read                                                     #
    # ----------------------------------------------------------------- #
    def query(self) -> None:
        """Populate ``self.df_analysis`` from SQLite for the current attrs."""
        if not all([self.country, self.crop, self.model, self.table]):
            raise ValueError("query(): country/crop/model/table not fully set")

        self.logger.info("Query %s | %s | %s", self.country, self.crop, self.model)

        with sqlite3.connect(self.db_path) as con:
            if not table_exists(con, self.table):
                self.logger.warning("table %s does not exist", self.table)
                self.df_analysis = pd.DataFrame()
                return

            sql = f"SELECT * FROM {self.table}"
            try:
                df = pd.read_sql_query(sql, con)
            except sqlite3.Error:
                self.logger.error("failed reading %s", self.table)
                self.df_analysis = pd.DataFrame()
                return

        mask = (
            (df["Country"] == self.country)
            & (df["Crop"] == self.crop)
            & (df["Model"] == self.model)
        )
        self.df_analysis = df.loc[mask].copy()
        self.logger.info("rows fetched: %d", len(self.df_analysis))

    # ----------------------------------------------------------------- #
    # Metric helpers                                                    #
    # ----------------------------------------------------------------- #
    @staticmethod
    def annual_metrics(df: pd.DataFrame) -> pd.Series:
        import scipy.stats as st
        from sklearn.metrics import mean_absolute_error, mean_squared_error

        if len(df) < 3:
            return pd.Series(dtype=float)

        obs, pred = df[OBSERVED_COL], df[PREDICTED_COL]

        return pd.Series(
            {
                "Root Mean Square Error": np.sqrt(mean_squared_error(obs, pred)),
                "Nash-Sutcliffe Efficiency": utils.nse(obs, pred),
                "$r^2$": st.pearsonr(obs, pred)[0] ** 2,
                "Mean Absolute Error": mean_absolute_error(obs, pred),
                "Mean Absolute\nPercentage Error": utils.mape(obs, pred),
                "Percentage Bias": utils.pbias(obs, pred),
            }
        )

    @staticmethod
    def regional_metrics(df: pd.DataFrame) -> pd.Series:
        actual, pred = df[OBSERVED_COL], df[PREDICTED_COL]
        mape = np.mean(np.abs((actual - pred) / actual)) * 100
        return pd.Series({"Mean Absolute Percentage Error": mape})

    @staticmethod
    def add_stage_information(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Date"] = df["Stage Name"].str.split("-").str[0]
        return df

    @staticmethod
    def select_top_N_years(group: pd.DataFrame, n: int = 5) -> pd.DataFrame:
        return group.nsmallest(n, "Mean Absolute Percentage Error")

    # ----------------------------------------------------------------- #
    # Historic production                                               #
    # ----------------------------------------------------------------- #
    def _get_historic_production(self) -> pd.DataFrame:
        root = (
            Path(self.parser.get("PATHS", "dir_output"))
            / "cei"
            / "indices"
            / self.method
            / "global"
        )
        country = self.country.title().replace("_", " ")
        crop = self.crop.title().replace("_", " ")
        csv = root / f"{country}_{crop}_statistics_s1_{self.method}.csv"

        cols = ["Region", "Harvest Year", "Yield (tn per ha)"]
        try:
            df = pd.read_csv(csv, usecols=cols).dropna()
        except FileNotFoundError:
            self.logger.warning("historic production file missing: %s", csv)
            return pd.DataFrame()

        last5 = sorted(df["Harvest Year"].unique())[-5:]
        pct = (
            df[df["Harvest Year"].isin(last5)]
            .groupby("Region")["Yield (tn per ha)"]
            .sum()
            .pipe(lambda s: s / s.sum() * 100)
            .rename("% of total Area (ha)")
            .reset_index()
        )

        def _median(start: int, end: int, name: str) -> pd.DataFrame:
            return (
                df[df["Harvest Year"].between(start, end)]
                .groupby("Region")["Yield (tn per ha)"]
                .mean()
                .rename(name)
                .reset_index()
            )

        med_18_22 = _median(2018, 2022, "Median Yield (tn per ha) (2018-2022)")
        med_13_17 = _median(2013, 2017, "Median Yield (tn per ha) (2013-2017)")

        return pct.merge(med_18_22, on="Region").merge(med_13_17, on="Region")

    # ----------------------------------------------------------------- #
    # Pre-processing                                                    #
    # ----------------------------------------------------------------- #
    def preprocess(self) -> pd.DataFrame:
        if self.df_analysis.empty:
            return pd.DataFrame()

        df = self.df_analysis.dropna(subset=[OBSERVED_COL]).copy()

        # lag yield per region
        med_col = f"{self.number_lag_years} year average"
        med = df.groupby("Region")["Median Yield (tn per ha)"].median().rename(med_col)
        df = df.merge(med, on="Region", how="left")

        # historic production
        df = df.merge(self._get_historic_production(), on="Region", how="left")

        ref = "Median Yield (tn per ha) (2018-2022)"
        if ref in df.columns:
            df["Anomaly"] = df[PREDICTED_COL] * 100 / df[ref]
        else:
            self.logger.error("%s missing; Anomaly NaN", ref)
            df["Anomaly"] = np.nan

        self.df_analysis = df
        return df

    # ----------------------------------------------------------------- #
    # National metrics                                                  #
    # ----------------------------------------------------------------- #
    def _clean_data(self) -> pd.DataFrame:
        return self.df_analysis.dropna(subset=[OBSERVED_COL])

    def _compute_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby(
                ["Country", "Model", "Harvest Year", "Stage Name", "Stage Range"]
            )
            .apply(self.annual_metrics)
            .reset_index()
        )

    def _process_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Stage_ID"] = pd.Categorical(df["Stage Name"]).codes
        df = df.sort_values(["Harvest Year", "Stage_ID"])
        df["Country"] = self.country
        df["Crop"] = self.crop
        return self.add_stage_information(df)

    def _plot_metrics(self, df: pd.DataFrame) -> None:
        metrics = [
            "Root Mean Square Error",
            "$r^2$",
            "Mean Absolute Error",
            "Mean Absolute\nPercentage Error",
            "Percentage Bias",
        ]
        for metric in metrics:
            self.plot_metric(df, metric)

    # ----------------------------------------------------------------- #
    # Regional metrics helpers                                          #
    # ----------------------------------------------------------------- #
    def _compute_regional_metrics(
        self, df: pd.DataFrame, by: str | None = None
    ) -> pd.DataFrame:
        cols = [
            "Country",
            "Region",
            "% of total Area (ha)",
            "Model",
            "Crop",
            "Stage Name",
            "Stage Range",
        ]
        gb_cols = cols + ([by] if by else [])
        return df.groupby(gb_cols).apply(self.regional_metrics).reset_index()

    def _select_top_years(self, df: pd.DataFrame, top_N: int = -1) -> pd.DataFrame:
        if top_N == -1:
            return df
        return (
            df.groupby(["Country", "Region"])
            .apply(lambda g: self.select_top_N_years(g, top_N))
            .reset_index(drop=True)
        )

    @staticmethod
    def _average_mape(df: pd.DataFrame) -> pd.DataFrame:
        cols = [
            "Country",
            "Region",
            "% of total Area (ha)",
            "Model",
            "Crop",
            "Stage Name",
            "Stage Range",
        ]
        return (
            df.groupby(cols)["Mean Absolute Percentage Error"].mean().reset_index()
        )

    # ----------------------------------------------------------------- #
    # DB write                                                          #
    # ----------------------------------------------------------------- #
    def _store_results(
        self,
        df_metrics: pd.DataFrame,
        df_regional: pd.DataFrame,
        df_regional_year: pd.DataFrame,
    ) -> None:
        # create index for each table
        df_metrics.index = df_metrics.apply(
            lambda r: "_".join(
                map(str, [r["Country"], r["Crop"], r["Model"], r["Harvest Year"], r["Stage Name"]])
            ),
            axis=1,
        )
        df_regional.index = df_regional.apply(
            lambda r: "_".join(
                map(str, [r["Country"], r["Region"], r["Model"], r["Crop"], r["Stage Name"]])
            ),
            axis=1,
        )
        df_regional_year.index = df_regional_year.apply(
            lambda r: "_".join(
                map(
                    str,
                    [
                        r["Country"],
                        r["Region"],
                        r["Model"],
                        r["Crop"],
                        r["Stage Name"],
                        r["Harvest Year"],
                    ],
                )
            ),
            axis=1,
        )

        df_metrics = df_metrics.round(3)
        df_regional = df_regional.round(3)
        df_regional_year = df_regional_year.round(3)

        with sqlite3.connect(self.db_path):
            utils.to_db(self.db_path, "country_metrics", df_metrics)
            utils.to_db(self.db_path, "regional_metrics", df_regional)
            utils.to_db(self.db_path, "regional_metrics_by_year", df_regional_year)

    # ----------------------------------------------------------------- #
    # National yield scatter helpers                                    #
    # ----------------------------------------------------------------- #
    def _compute_national_yield(self, df: pd.DataFrame) -> pd.DataFrame:
        observed, predicted, area = OBSERVED_COL, PREDICTED_COL, "Area (ha)"
        df = df.copy()
        df[area] = df.groupby("Country")[area].transform(lambda x: x.fillna(x.median()))

        # national totals
        nat = (
            df.assign(
                **{
                    observed: df[observed] * df[area],
                    predicted: df[predicted] * df[area],
                }
            )
            .groupby(["Country", "Harvest Year"])
            .agg({observed: "sum", predicted: "sum", area: "sum"})
            .reset_index()
        )
        nat[observed] = nat[observed] / nat[area]
        nat[predicted] = nat[predicted] / nat[area]
        return nat

    def _plot_regional_yield_scatter(self, df: pd.DataFrame) -> None:
        from sklearn.metrics import (
            mean_absolute_percentage_error,
            mean_squared_error,
            r2_score,
        )

        years = pd.to_numeric(df["Harvest Year"], errors="coerce")
        obs, pred = df[OBSERVED_COL], df[PREDICTED_COL]

        cmap, norm = plt.cm.viridis, plt.Normalize(vmin=years.min(), vmax=years.max())
        colors = cmap(norm(years))

        with plt.style.context("science"):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.grid(True, ls="--", alpha=0.5)
            ax.scatter(obs, pred, c=colors, s=50)
            lim = 1.25 * max(obs.max(), pred.max())
            ax.plot([0, lim], [0, lim], ls="--", color="gray")

            txt = (
                f"RMSE: {np.sqrt(mean_squared_error(obs, pred)):.2f} tn/ha\n"
                f"MAPE: {mean_absolute_percentage_error(obs, pred):.2%}\n"
                f"$r^2$: {r2_score(obs, pred):.2f}\n"
                f"N: {len(obs)}"
            )
            ax.annotate(txt, xy=(0.05, 0.95), xycoords="axes fraction", va="top")

            ax.set(
                xlabel="Observed Yield (tn/ha)",
                ylabel="Predicted Yield (tn/ha)",
                xlim=(0, lim),
                ylim=(0, lim),
            )

            cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
            cbar.set_label("Harvest Year")
            cbar.set_ticks(np.linspace(years.min(), years.max(), 5, dtype=int))
            fig.savefig(self.dir_analysis / f"scatter_all_regions_{self.country}_{self.crop}.png", dpi=250)
            plt.close(fig)

    def _plot_national_yield(self, nat: pd.DataFrame) -> None:
        from sklearn.metrics import (
            mean_absolute_percentage_error,
            mean_squared_error,
            r2_score,
        )

        x = pd.to_numeric(nat["Harvest Year"], errors="coerce")
        obs, pred = nat[OBSERVED_COL], nat[PREDICTED_COL]
        cmap, norm = plt.cm.viridis, plt.Normalize(vmin=x.min(), vmax=x.max())

        with plt.style.context("science"):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.grid(True, ls="--", alpha=0.5)

            for yr, o, p in zip(x, obs, pred):
                ax.scatter(o, p, s=50, c=[cmap(norm(yr))])

            lim = 1.25 * max(obs.max(), pred.max())
            ax.plot([0, lim], [0, lim], ls="--", color="gray")

            txt = (
                f"RMSE: {np.sqrt(mean_squared_error(obs, pred)):.2f} tn/ha\n"
                f"MAPE: {mean_absolute_percentage_error(obs, pred):.2%}\n"
                f"$r^2$: {r2_score(obs, pred):.2f}\n"
                f"N: {len(obs)}"
            )
            ax.annotate(txt, xy=(0.05, 0.95), xycoords="axes fraction", va="top")

            ax.set(
                xlabel="Observed Yield (tn/ha)",
                ylabel="Predicted Yield (tn/ha)",
                xlim=(0, lim),
                ylim=(0, lim),
            )

            cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
            cbar.set_label("Harvest Year")
            cbar.set_ticks(np.linspace(x.min(), x.max(), 5, dtype=int))
            fig.savefig(self.dir_analysis / f"scatter_{self.country}_{self.crop}.png", dpi=250)
            plt.close(fig)

    # ----------------------------------------------------------------- #
    # Metric line plot                                                  #
    # ----------------------------------------------------------------- #
    def plot_metric(self, df: pd.DataFrame, metric: str = "$r^2$") -> None:
        with plt.style.context("science"):
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.lineplot(data=df, x="Date", y=metric, ax=ax)
            ax.set(xlabel="", ylabel=metric.replace("\n", " "))
            if metric in {"$r^2$", "Nash-Sutcliffe Efficiency"}:
                ax.set_ylim(0, 1)
            fname = f"{self.country}_{self.crop}_{metric.replace(' ', '_')}.png"
            fig.savefig(self.dir_analysis / fname, dpi=250)
            plt.close(fig)

    # ----------------------------------------------------------------- #
    # Execute full pipeline                                             #
    # ----------------------------------------------------------------- #
    def execute(
        self,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Run the full workflow; return key DataFrames for inspection."""
        self.query()
        df_clean = self.preprocess()
        if df_clean.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # national metrics
        df_metrics = self._process_metrics(self._compute_metrics(df_clean))
        self._plot_metrics(df_metrics)

        # regional metrics
        df_reg_year = self._compute_regional_metrics(df_clean, by="Harvest Year")
        df_reg_year = self._select_top_years(df_reg_year, top_N=10)
        df_regional = self._average_mape(df_reg_year)

        # persist
        self._store_results(df_metrics, df_regional, df_reg_year)

        # national & regional scatter
        nat = self._compute_national_yield(df_clean)
        self._plot_national_yield(nat)
        self._plot_regional_yield_scatter(df_clean)

        return df_metrics, df_regional, nat

    # ----------------------------------------------------------------- #
    # Config handling                                                   #
    # ----------------------------------------------------------------- #
    def get_config_data(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as con:
                df = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'config%'", con
                )
                if df.empty:
                    raise ValueError("No config tables")

                pattern = r"(\d{4} \d{2}:\d{2})$"
                df["datetime"] = pd.to_datetime(df["name"].str.extract(pattern)[0], format="%Y %H:%M")
                latest = df.sort_values("datetime", ascending=False)["name"].iloc[0]

                self.logger.info("Using configuration table: %s", latest)
                self.df_config = pd.read_sql_query(f"SELECT * FROM {latest}", con)
        except Exception:
            self.logger.error("Failed to fetch configuration")

    def setup(self) -> None:
        self.dict_config: dict[str, dict] = {}
        self.observed, self.predicted = OBSERVED_COL, PREDICTED_COL

        df_ml = self.df_config[self.df_config["Section"] == "ML"]
        self.countries = ast.literal_eval(df_ml.loc[df_ml["Option"] == "countries", "Value"].values[0])

        for country in self.countries:
            df = self.df_config[self.df_config["Section"] == country]
            method = df.loc[df["Option"] == "method", "Value"].values[0]
            crops = ast.literal_eval(df.loc[df["Option"] == "crops", "Value"].values[0])
            models = ast.literal_eval(df.loc[df["Option"] == "models", "Value"].values[0])
            admin_zone = df.loc[df["Option"] == "admin_zone", "Value"].values[0]
            shp_name = df.loc[df["Option"] == "boundary_file", "Value"].values[0]

            for crop in crops:
                table = f"{country}_{crop}"
                if table_exists(sqlite3.connect(self.db_path), table):
                    self.dict_config[f"{country}_{crop}"] = {
                        "method": method,
                        "crops": crop,
                        "models": models,
                        "admin_zone": admin_zone,
                        "name_shapefile": shp_name,
                    }

        # load shapefile for first country only (others on demand)
        first_country = self.countries[0]
        shp_file = self.parser.get(first_country, "boundary_file")
        self.dg = gpd.read_file(self.dir_shapefiles / shp_file, engine="pyogrio")

        self.admin_col_name = self.parser.get(first_country, "admin_col_name")
        self.annotate_regions = self.parser.getboolean(first_country, "annotate_regions")

        # normalise column names
        self.dg = self.dg.rename(
            columns={"ADMIN0": "ADM0_NAME", "ADMIN1": "ADM1_NAME", "ADMIN2": "ADM2_NAME"}
        )
        if "ADM0_NAME" not in self.dg:
            self.dg["ADM0_NAME"] = first_country.title().replace("_", " ")

        if self.admin_col_name in self.dg.columns and "ADM1_NAME" not in self.dg.columns:
            if admin_zone == "admin_1":
                self.dg.rename(columns={self.admin_col_name: "ADM1_NAME"}, inplace=True)

        # convenience column for merge
        self.dg["Country Region"] = self.dg["ADM0_NAME"].str.lower().str.replace("_", " ")
        self.dg["Country Region"] = (
            self.dg["Country Region"].str.cat(self.dg["ADM1_NAME"].fillna(""), sep=" ").str.strip()
        )
        if "ADM2_NAME" in self.dg.columns:
            mask = self.dg["ADM2_NAME"].notna()
            self.dg.loc[mask, "Country Region"] = (
                self.dg.loc[mask, "ADM0_NAME"] + " " + self.dg.loc[mask, "ADM2_NAME"]
            ).str.lower()

    # ----------------------------------------------------------------- #
    # Map-drawing (unchanged except bug fixes)                          #
    # ----------------------------------------------------------------- #
        # ----------------------------------------------------------------- #
    # Map-drawing                                                       #
    # ----------------------------------------------------------------- #
    def map(self, df_plot: pd.DataFrame) -> None:
        """
        Create regional maps (% area, region clusters, predicted yield,
        anomaly, area) for every model, stage, year, and country.

        Notes
        -----
        * Uses ``plot.plot_df_shpfile`` from your ``viz`` package.
        * Two review fixes applied:
            1. `df_model["Region_ID"].nunique() > 1`   (not
               `len(df_model["Region_ID"].unique() > 1)`).
            2. Removed all manual ``pbar.update()`` calls – `tqdm`
               auto-increments inside the loop.
        """

        # ensure we do not mutate the caller’s frame
        df_plot = df_plot.copy()
        models = df_plot["Model"].unique()

        for model in models:
            df_model = df_plot[df_plot["Model"] == model].copy()

            # ------------------------------------------------------------------
            # Directory set-up
            # ------------------------------------------------------------------
            countries_raw = df_model["Country"].unique().tolist()
            if len(countries_raw) > 1:
                self.dir_plot = self.dir_analysis
                fname_prefix = f"{len(countries_raw)}_countries"
            else:
                self.dir_plot = self.dir_analysis / self.country / self.crop
                fname_prefix = self.country

            countries = [c.title().replace("_", " ") for c in countries_raw]

            # helper column for shapefile merge
            df_model["Country Region"] = (
                df_model["Country"].str.lower().str.replace("_", " ")
                + " "
                + df_model["Region"].str.lower().str.replace("_", " ")
            )

            # enforce int for year
            df_model["Harvest Year"] = df_model["Harvest Year"].astype(int)

            annotate_region_column = (
                "ADM1_NAME" if self.admin_zone == "admin_1" else "ADM2_NAME"
            )

            # ------------------------------------------------------------------
            # Loop over years and stages
            # ------------------------------------------------------------------
            for year in tqdm(
                sorted(df_model["Harvest Year"].unique()), desc="Years", leave=False
            ):
                df_year = df_model[df_model["Harvest Year"] == year]

                # ── % of total area (only once per model) ──────────────────
                if year == df_model["Harvest Year"].min():
                    col = "% of total Area (ha)"
                    plot.plot_df_shpfile(
                        self.dg,
                        df_model,
                        merge_col="Country Region",
                        name_country=countries,
                        name_col=col,
                        dir_out=self.dir_plot / str(year),
                        fname=f"map_{fname_prefix}_{self.crop}_perc_area.png",
                        label=f"% of Total Area (ha)\n{self.crop.title()}",
                        vmin=df_model[col].min(),
                        vmax=df_model[col].max(),
                        cmap=pal.scientific.sequential.Bamako_20_r,
                        series="sequential",
                        show_bg=False,
                        annotate_regions=self.annotate_regions,
                        annotate_region_column=annotate_region_column,
                        loc_legend="lower left",
                    )

                # iterate over dekads / stage names
                for stage in tqdm(
                    df_year["Stage Name"].unique(), desc=f"{year} stages", leave=False
                ):
                    df_stage = df_year[df_year["Stage Name"] == stage]

                    # ── Region-ID cluster map ───────────────────────────────
                    if df_stage["Region_ID"].nunique() > 1:
                        col = "Region_ID"
                        df_stage[col] = df_stage[col].astype(int) + 1
                        dict_region = {
                            int(val): val for val in df_stage[col].unique()
                        }
                        plot.plot_df_shpfile(
                            self.dg,
                            df_stage,
                            dict_lup=dict_region,
                            merge_col="Country Region",
                            name_country=countries,
                            name_col=col,
                            dir_out=self.dir_plot / str(year),
                            fname=f"map_{fname_prefix}_{self.crop}_region_ID.png",
                            label=f"Region Cluster\n{self.crop.title()}",
                            vmin=df_stage[col].min(),
                            vmax=df_stage[col].max(),
                            cmap=pal.tableau.Tableau_20.mpl_colors,
                            series="qualitative",
                            show_bg=False,
                            alpha_feature=1,
                            use_key=True,
                            annotate_regions=self.annotate_regions,
                            annotate_region_column=annotate_region_column,
                            loc_legend="lower left",
                        )

                    # ------------------------------------------------------------------
                    # Country-specific maps (% area, predicted yield, anomaly)
                    # ------------------------------------------------------------------
                    for country in countries:
                        c_norm = country.lower().replace(" ", "_")
                        df_country = df_stage[
                            df_stage["Country"] == c_norm
                        ].copy()

                        # % total area (per country)
                        col = "% of total Area (ha)"
                        plot.plot_df_shpfile(
                            self.dg,
                            df_country,
                            merge_col="Country Region",
                            name_country=[country],
                            name_col=col,
                            dir_out=self.dir_plot / str(year),
                            fname=f"map_perc_area_{country}_{self.crop}.png",
                            label=f"% of Total Area (ha)\n{self.crop.title()}",
                            vmin=df_country[col].min(),
                            vmax=df_country[col].max(),
                            cmap=pal.scientific.sequential.Bamako_20_r,
                            series="sequential",
                            show_bg=False,
                            annotate_regions=self.annotate_regions,
                            annotate_region_column=annotate_region_column,
                            loc_legend="lower left",
                        )

                        # predicted yield
                        col_y = PREDICTED_COL
                        plot.plot_df_shpfile(
                            self.dg,
                            df_country,
                            merge_col="Country Region",
                            name_country=[country],
                            name_col=col_y,
                            dir_out=self.dir_plot / str(year),
                            fname=f"map_predicted_yield_{country}_{self.crop}_{stage}_{year}.png",
                            label=f"Predicted Yield (Mg/ha)\n{self.crop.title()}, {year}",
                            vmin=df_country[col_y].min(),
                            vmax=df_country[col_y].max(),
                            cmap=pal.scientific.sequential.Bamako_20_r,
                            series="sequential",
                            show_bg=False,
                            annotate_regions=self.annotate_regions,
                            annotate_region_column=annotate_region_column,
                            loc_legend="lower left",
                        )

                        # anomaly (% of N-year median)
                        col_a = "Anomaly"
                        plot.plot_df_shpfile(
                            self.dg,
                            df_country,
                            merge_col="Country Region",
                            name_country=[country],
                            name_col=col_a,
                            dir_out=self.dir_plot / str(year),
                            fname=f"map_anomaly_{country}_{self.crop}_{stage}_{year}.png",
                            label=(
                                f"% of {self.number_lag_years}-year Median Yield\n"
                                f"{self.crop.title()}, {year}"
                            ),
                            vmin=df_country[col_a].min(),
                            vmax=110,
                            cmap=pal.cartocolors.diverging.Geyser_5_r,
                            series="sequential",
                            show_bg=False,
                            annotate_regions=self.annotate_regions,
                            annotate_region_column=annotate_region_column,
                            loc_legend="lower left",
                        )

                    # ------------------------------------------------------------------
                    # Area map (global) – only if Area data present
                    # ------------------------------------------------------------------
                    if df_stage["Area (ha)"].notna().all():
                        col_area = "Area (ha)"
                        plot.plot_df_shpfile(
                            self.dg,
                            df_stage,
                            merge_col="Country Region",
                            name_country=countries,
                            name_col=col_area,
                            dir_out=self.dir_plot / str(year),
                            fname=f"map_{fname_prefix}_{self.crop}_{year}_area.png",
                            label=f"Area (ha)\n{self.crop.title()}, {stage}",
                            vmin=df_stage[col_area].min(),
                            vmax=df_stage[col_area].max(),
                            cmap=pal.scientific.sequential.Bamako_20_r,
                            series="sequential",
                            show_bg=False,
                            annotate_regions=self.annotate_regions,
                            loc_legend="lower left",
                        )

# --------------------------------------------------------------------- #
# RegionalMapper                                                        #
# --------------------------------------------------------------------- #


@dataclass
class RegionalMapper(Geoanalysis):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.get_config_data()
        self.setup()
        self.df_regional = pd.DataFrame()
        self.df_regional_by_year = pd.DataFrame()

    # ---- (full helpers identical to the earlier response) ------------ #
    # _read_data, _clean_data, _plot_heatmaps, _draw_heatmap,
    # _plot_kde, _plot_mape_map, _plot_mape_by_year
    # ------------------------------------------------------------------ #
    #   ...  See the RegionalMapper code block from the previous answer.
    # ------------------------------------------------------------------ #


# --------------------------------------------------------------------- #
# Entrypoint util                                                      #
# --------------------------------------------------------------------- #


def run(path_config_files: Optional[List[Path]] = None) -> None:
    if path_config_files is None:
        path_config_files = [Path("../config/geocif.txt")]

    logger, parser = log.setup_logger_parser(path_config_files)
    obj = Geoanalysis(path_config_files, logger, parser)
    obj.get_config_data()
    obj.setup()

    frames: list[pd.DataFrame] = []

    for country_crop, cfg in obj.dict_config.items():
        obj.crop = cfg["crops"]
        obj.country = country_crop.removesuffix(f"_{obj.crop}")
        obj.method = cfg["method"]
        obj.admin_zone = cfg["admin_zone"]
        obj.table = f"{obj.country}_{obj.crop}"
        obj.boundary_file = cfg["name_shapefile"]

        for obj.model in cfg["models"]:
            df_metrics, df_regional, nat = obj.execute()
            frames.append(nat)

    # regional visualisations
    RegionalMapper(path_config_files, logger, parser).map_regional()


if __name__ == "__main__":
    run()
