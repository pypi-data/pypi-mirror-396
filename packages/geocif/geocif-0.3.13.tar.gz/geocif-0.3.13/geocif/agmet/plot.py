import os
import math
import datetime
import matplotlib
import numpy as np
import pandas as pd
import bottleneck as bn
import arrow as ar
import matplotlib.pyplot as plt
import palettable as pal
from cycler import cycler
from matplotlib import rcParams

from geocif.backup import constants
from geocif.agmet import utils


def set_matplotlib_params():
    """
    Set matplotlib defaults to nicer values
    Returns:

    """
    # rcParams dict
    rcParams["mathtext.default"] = "regular"
    rcParams["axes.labelsize"] = 12
    rcParams["xtick.labelsize"] = 12
    rcParams["ytick.labelsize"] = 12
    rcParams["legend.fontsize"] = 12
    rcParams["font.family"] = "sans-serif"
    rcParams["font.serif"] = ["Helvetica"]
    rcParams["legend.numpoints"] = 1
    # rcParams['figure.figsize'] = 7.3, 4.2


def get_colors(palette="colorbrewer", cmap=False, only_colors=False):
    """
    Get palettable colors, which are nicer
    Args:
        palette:
        cmap:

    Returns:

    """
    if palette == "colorbrewer":
        bmap = pal.colorbrewer.diverging.PRGn_11.mpl_colors
        if cmap:
            bmap = pal.colorbrewer.diverging.PRGn_11.mpl_colormap
    elif palette == "tableau":
        bmap = pal.tableau.Tableau_20.mpl_colors
        if cmap:
            bmap = pal.tableau.Tableau_20.mpl_colormap
    elif palette == "cubehelix":
        bmap = pal.cubehelix.cubehelix2_16.mpl_colors
        if cmap:
            bmap = pal.cubehelix.cubehelix2_16.mpl_colormap
    elif palette == "qualitative":
        bmap = pal.tableau.GreenOrange_12.mpl_colors
        if cmap:
            bmap = pal.tableau.GreenOrange_12.mpl_colormap

    if cmap:
        return bmap

    if only_colors:
        color_cycle = cycler("color", bmap)  # color cycle
    else:
        color_cycle = (cycler(marker=["*", "o"]) * cycler("ls", ["-", "--"])) * cycler(
            "color", bmap
        )  # color cycle
    plt.rc("axes", prop_cycle=color_cycle)

    return bmap


def compute_stats(df_current, df_last, df_previous, var, window):
    """

    Args:
        df_current:
        df_last:
        df_previous:
        var:
        window:

    Returns:

    """
    df_mean_vals = df_previous.groupby(df_previous["doy"])[var].mean()
    df_mean_vals = df_mean_vals.reindex(
        index=df_current["doy"]
    )  # reorder to match current season dates

    df_min_vals = df_previous.groupby(df_previous["doy"])[var].min()
    df_min_vals = df_min_vals.reindex(
        index=df_current["doy"]
    )  # reorder to match current season dates

    df_max_vals = df_previous.groupby(df_previous["doy"])[var].max()
    df_max_vals = df_max_vals.reindex(
        index=df_current["doy"]
    )  # reorder to match current season dates

    curr_vals = bn.move_mean(df_current[var].values, window=window, min_count=1)
    last_vals = bn.move_mean(df_last[var].values, window=window, min_count=1)
    past_vals = bn.move_mean(df_mean_vals.values, window=window, min_count=1)

    min_vals = bn.move_mean(
        np.minimum(df_min_vals.values, df_mean_vals.values), window=window, min_count=1
    )
    max_vals = bn.move_mean(
        np.maximum(df_max_vals.values, df_mean_vals.values), window=window, min_count=1
    )

    return df_mean_vals, curr_vals, last_vals, past_vals, min_vals, max_vals


def plots_ts_cur_yr(
    df,
    names_cols,
    closest=None,
    dates_cal=None,
    frcast_yr=None,
    logos=None,
    window=5,
    dir_out="",
    sup_title="",
    fname="",
):
    """
    Expectes dataframe to have a time-series index
    Args:
        df:
        names_cols:
        closest:
        dates_cal:
        frcast_yr:
        logos:
        window:
        dir_out:
        sup_title:
        fname:

    Returns:

    """
    use_forecast = False
    os.makedirs(dir_out, exist_ok=True)

    color_list = get_colors("tableau", only_colors=True)

    # Figure out source of precip (chirps or cpc_precip)
    precip_var = "chirps" if "chirps" in df.columns.values else "cpc_precip"

    # # If all values of column to be plotted are NaN, then return
    available_cols = []
    for col in names_cols + [precip_var]:
        if col in df.columns.values:
            available_cols.append(col)
    # if df[available_cols].isnull().values.all():
    #     return pd.DataFrame()

    # Specify number of columns, should not exceed 3
    ncols = (
        3 if int(len(names_cols) / 2.0) >= 2 else int(math.floor(len(names_cols) / 2.0))
    )
    nrows = int(math.ceil(len(names_cols) / 3.0))

    # Get data frame of current year
    df_current = df[df["harvest_season"] == frcast_yr]
    df_last = df[df["harvest_season"] == frcast_yr - 1]

    # If df_current has no non NaN data for current season then do not plot
    _num_nans = 0
    for idx in range(len(available_cols)):
        # TODO: replace sliding_mean with numpy convolve function
        if np.all(
            np.isnan(
                utils.sliding_mean(
                    df_current[available_cols[idx]].values, window=window
                )
            )
        ):
            _num_nans += 1

    if _num_nans == len(available_cols):
        return pd.DataFrame()

    # Get data frame of previous years for the same month and days as df_current
    df_previous = df[
        np.in1d(df["month"], df_current.index.month)
        & np.in1d(df["day"], df_current.index.day)
        & (df["harvest_season"].isin(closest))
    ]

    # Drop rows where harvest_season is missing i.e. NaN
    df_previous = df_previous[np.isfinite(df_previous["harvest_season"])]

    # Drop rows for year greater than current year
    df_previous = df_previous[
        df_previous["harvest_season"] < datetime.datetime.now().year
    ]

    if (
        df_current.empty
        or df_previous.empty
        or df_current["cpc_tmax"].isnull().values.all()
    ):
        return pd.DataFrame()

    # Plot current year
    fig, ax = plt.subplots(nrows, ncols, squeeze=False, figsize=(20, 10))
    # delete empty axes
    for i in range(len(names_cols), nrows * ncols):
        fig.delaxes(ax.flatten()[i])

    # ax[0, 0].grid(True)
    fig.suptitle(sup_title, fontsize=16, fontweight="bold")
    rcParams["xtick.labelsize"] = 12
    rcParams["ytick.labelsize"] = 12
    rcParams["axes.labelsize"] = 12

    # Create individual plots
    for idx in range(len(names_cols)):
        # 'ndvi', 'cumulative_precip', 'cpc_tmax', 'yearly_ndvi', 'daily_precip', 'cpc_tmax', 'esi_4wk', 'cpc_tmin', 'soil_moisture_as1'
        if names_cols[idx] in ["cumulative_precip", "daily_precip"]:
            cur_var = precip_var
        elif names_cols[idx] in ["ndvi", "yearly_ndvi"]:
            cur_var = "ndvi"
        elif names_cols[idx] in ["gcvi", "yearly_gcvi"]:
            cur_var = "gcvi"
        else:
            cur_var = names_cols[idx]

        _window = window

        ax[idx // 3, idx % 3] = plt.subplot(nrows, ncols, idx + 1)

        # Setup major and minor locations for time on x axis
        ax[idx // 3, idx % 3].xaxis.set_major_locator(matplotlib.dates.YearLocator())
        ax[idx // 3, idx % 3].xaxis.set_minor_locator(
            matplotlib.dates.MonthLocator(range(1, 13))
        )

        ax[idx // 3, idx % 3].xaxis.set_major_formatter(
            matplotlib.dates.DateFormatter("\n%Y")
        )
        ax[idx // 3, idx % 3].xaxis.set_minor_formatter(
            matplotlib.dates.DateFormatter("%b")
        )

        # Plot title for each subplot except cpc_tmax; y label for all though
        # if names_cols[idx] != 'cpc_tmax':
        #     plt.title(cc.dict_vars.get(cur_var)[0], fontsize=14)
        plt.title(utils.dict_vars.get(cur_var)[0], fontsize=14)
        plt.ylabel(utils.dict_vars.get(cur_var)[1], fontsize=10)
        try:
            if np.all(np.isnan(df_current[cur_var].values)):
                ax[idx // 3, idx % 3].text(
                    0.3, 0.5, "No within season data available yet"
                )
                continue
        except:
            breakpoint()

        (
            df_mean_vals,
            curr_vals,
            last_vals,
            past_vals,
            min_vals,
            max_vals,
        ) = compute_stats(df_current, df_last, df_previous, cur_var, _window)

        if cur_var in ["ndvi", "gcvi"]:
            import statsmodels.api as sm

            lowess_sm = sm.nonparametric.lowess
            curr_vals = lowess_sm(
                curr_vals,
                range(len(curr_vals)),
                frac=1.0 / 5.0,
                it=3,
                return_sorted=False,
            )
            last_vals = lowess_sm(
                last_vals,
                range(len(last_vals)),
                frac=1.0 / 5.0,
                it=3,
                return_sorted=False,
            )
            min_vals = lowess_sm(
                min_vals,
                range(len(min_vals)),
                frac=1.0 / 5.0,
                it=3,
                return_sorted=False,
            )
            max_vals = lowess_sm(
                max_vals,
                range(len(max_vals)),
                frac=1.0 / 5.0,
                it=3,
                return_sorted=False,
            )

        if np.isnan(curr_vals).all():
            ax[idx // 3, idx % 3].text(0.3, 0.5, "No within season data available yet")
            continue

        # Create nice-looking grid for ease of visualization
        ax[idx // 3, idx % 3].grid(which="major", alpha=0.5, linestyle="--")
        ax[idx // 3, idx % 3].grid(which="minor", alpha=0.5, linestyle="--")

        if names_cols[idx] in ["daily_precip"]:
            plt.title("Precipitation (Daily)", fontsize=14)

            df_c = df_current[precip_var].resample("D").sum()
            ax[idx // 3, idx % 3].bar(
                df_c.index,
                df_c.values,
                color="b",
                label=frcast_yr if idx == 0 else "",
                width=1.0,
            )
        elif names_cols[idx] in ["cumulative_precip"]:
            plt.title("Cumulative Precipitation (vs 5 year mean)", fontsize=14)

            df_c = df_current[cur_var].cumsum()
            df_m = df_mean_vals.cumsum()
            y1 = df_c.values
            y2 = df_m.values
            (a1,) = ax[idx // 3, idx % 3].plot(df_c.index, y1, color="b")
            (a9,) = ax[idx // 3, idx % 3].plot(df_c.index, y2, color="k")

            # Plot CHIRPS_GEFS if last date in dataframe exceeds current date for CHIRPS
            if (
                df_c.index[-1].date() > ar.utcnow().date()
                and precip_var == "chirps"
                and "chirps_gefs" in df_current.columns
                and not df_current["chirps_gefs"].isnull().values.all()
            ):
                use_forecast = True
                val_gefs = (
                    np.nanmax(df_c.values)
                    + df_current.loc[df_current["chirps_gefs"].idxmax()]["chirps_gefs"]
                )

                df_tmp = pd.DataFrame(
                    {"date": [ar.utcnow().shift(days=+15).date()], "val": [val_gefs]}
                )
                df_tmp = df_tmp.set_index("date")
                df_tmp.index = pd.to_datetime(df_tmp.index)

                try:
                    mean_precip = df_m[ar.utcnow().shift(days=+15).timetuple().tm_yday]
                except:
                    mean_precip = df_m[
                        ar.utcnow().shift(days=+15).timetuple().tm_yday - 1
                    ]
                which_col = "red" if val_gefs < mean_precip else "green"
                ax[idx // 3, idx % 3].plot_date(
                    df_tmp.index, np.asarray([val_gefs]), "o", color=which_col
                )
                p4 = ax[idx // 3, idx % 3].plot(
                    np.NaN,
                    np.NaN,
                    "o",
                    color=which_col,
                    alpha=0.2,
                    label="Forecast (15 day)",
                )

            ax[idx // 3, idx % 3].fill_between(
                df_c.index, y1, y2, where=y2 >= y1, lw=1.0, facecolor="red", alpha=0.2
            )
            ax[idx // 3, idx % 3].fill_between(
                df_c.index, y1, y2, where=y2 <= y1, lw=1.0, facecolor="green", alpha=0.2
            )

            p2 = ax[idx // 3, idx % 3].fill(
                np.NaN, np.NaN, "red", alpha=0.2, label="< 5 year mean"
            )
            p3 = ax[idx // 3, idx % 3].fill(
                np.NaN, np.NaN, "green", alpha=0.2, label="> 5 year mean"
            )
            ax[idx // 3, idx % 3].legend(loc="upper left", fontsize="small")
        elif names_cols[idx] in ["yearly_ndvi"]:
            from heapq import nsmallest
            import statsmodels.api as sm

            lowess_sm = sm.nonparametric.lowess

            closest = nsmallest(
                6,
                range(2001, max(ar.utcnow().year, frcast_yr)),
                key=lambda x: abs(x - frcast_yr),
            )
            closest.extend([frcast_yr])
            closest = list(set(closest))
            closest.sort()
            if len(closest) > 6:
                closest = closest[(len(closest) - 6) :]

            for y in closest:
                _cur = df[df["harvest_season"] == y]
                _tmp = _cur["yield"]
                if not _tmp.isnull().all():
                    _yld = np.unique(_tmp[~np.isnan(_tmp)])[0]
                else:
                    _yld = np.NaN
                vals = _cur["ndvi"].values
                vals = bn.move_mean(vals, window=_window, min_count=1)
                vals = lowess_sm(
                    vals, range(len(vals)), frac=1.0 / 5.0, it=3, return_sorted=False
                )

                if y == frcast_yr:
                    if np.isnan(_yld):
                        ax[idx // 3, idx % 3].plot(
                            df_current.index, vals, lw=1.5, color="b", label=str(y)
                        )
                    else:
                        ax[idx // 3, idx % 3].plot(
                            df_current.index,
                            vals,
                            lw=1.5,
                            color="b",
                            label=str(y) + ", " + "{0:.2f}".format(_yld) + " MT/ha",
                        )
                else:
                    if np.isnan(_yld):
                        if y == frcast_yr - 1:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index,
                                vals,
                                lw=1.0,
                                alpha=0.75,
                                color=color_list[8],
                                label=str(y),
                            )
                        else:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index, vals, lw=1.0, alpha=0.75, label=str(y)
                            )
                    else:
                        if y == frcast_yr - 1:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index,
                                vals,
                                lw=1.0,
                                alpha=0.75,
                                color=color_list[8],
                                label=str(y) + ", " + "{0:.2f}".format(_yld) + " MT/ha",
                            )
                        else:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index,
                                vals,
                                lw=1.0,
                                alpha=0.75,
                                label=str(y) + ", " + "{0:.2f}".format(_yld) + " MT/ha",
                            )
            plt.title("Recent 5 Years NDVI Comparison", fontsize=14)
            ax[idx // 3, idx % 3].legend(loc="upper left", fontsize="small")
        elif names_cols[idx] in ["yearly_gcvi"]:
            from heapq import nsmallest
            import statsmodels.api as sm

            lowess_sm = sm.nonparametric.lowess

            closest = nsmallest(
                6,
                range(2001, max(ar.utcnow().year, frcast_yr)),
                key=lambda x: abs(x - frcast_yr),
            )
            closest.extend([frcast_yr])
            closest = list(set(closest))
            closest.sort()
            if len(closest) > 6:
                closest = closest[(len(closest) - 6) :]

            for y in closest:
                _cur = df[df["harvest_season"] == y]
                _tmp = _cur["yield"]
                if not _tmp.isnull().all():
                    _yld = np.unique(_tmp[~np.isnan(_tmp)])[0]
                else:
                    _yld = np.NaN
                vals = _cur["gcvi"].values
                vals = bn.move_mean(vals, window=_window, min_count=1)
                vals = lowess_sm(
                    vals, range(len(vals)), frac=1.0 / 5.0, it=3, return_sorted=False
                )

                if y == frcast_yr:
                    if np.isnan(_yld):
                        ax[idx // 3, idx % 3].plot(
                            df_current.index, vals, lw=1.5, color="b", label=str(y)
                        )
                    else:
                        ax[idx // 3, idx % 3].plot(
                            df_current.index,
                            vals,
                            lw=1.5,
                            color="b",
                            label=str(y) + ", " + "{0:.2f}".format(_yld) + " MT/ha",
                        )
                else:
                    if np.isnan(_yld):
                        if y == frcast_yr - 1:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index,
                                vals,
                                lw=1.0,
                                alpha=0.75,
                                color=color_list[8],
                                label=str(y),
                            )
                        else:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index, vals, lw=1.0, alpha=0.75, label=str(y)
                            )
                    else:
                        if y == frcast_yr - 1:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index,
                                vals,
                                lw=1.0,
                                alpha=0.75,
                                color=color_list[8],
                                label=str(y) + ", " + "{0:.2f}".format(_yld) + " MT/ha",
                            )
                        else:
                            ax[idx // 3, idx % 3].plot(
                                df_current.index,
                                vals,
                                lw=1.0,
                                alpha=0.75,
                                label=str(y) + ", " + "{0:.2f}".format(_yld) + " MT/ha",
                            )
            plt.title("Recent 5 Years GCVI Comparison", fontsize=14)
            ax[idx // 3, idx % 3].legend(loc="upper left", fontsize="small")
        elif names_cols[idx] in ["cpc_tmax"]:
            plt.title("Temperature (daily mean)", fontsize=14)

            # Plot average_temperature
            (
                df_mean_vals,
                curr_vals,
                last_vals,
                past_vals,
                min_vals,
                max_vals,
            ) = compute_stats(
                df_current, df_last, df_previous, "average_temperature", _window
            )

            (a1,) = ax[idx // 3, idx % 3].plot(
                df_current.index,
                curr_vals,
                color="b",
                lw=1.5,
                label=frcast_yr if idx == 0 else "",
            )
            (a2,) = ax[idx // 3, idx % 3].plot(
                df_current.index,
                last_vals,
                color=color_list[8],
                lw=1.25,
                label=frcast_yr - 1 if idx == 0 else "",
            )
            (a3,) = ax[idx // 3, idx % 3].plot(
                df_current.index,
                past_vals,
                color="k",
                lw=1.25,
                label="Mean" if idx == 0 else "",
            )

            a4 = ax[idx // 3, idx % 3].fill_between(
                df_current.index,
                min_vals,
                max_vals,
                color="lightgray",
                label="Min/Max" if idx == 0 else "",
                alpha=0.7,
                lw=0,
            )

            mask_max = df_current["cpc_tmax"] > 30
            mask_min = df_current["cpc_tmin"] < 5

            # Plot temperatures that fall above or below the GDD threshold
            p2 = ax[idx // 3, idx % 3].plot(
                df_current.index[mask_max],
                df_current[mask_max]["cpc_tmax"],
                "ro",
                markersize=2,
                label="Max temp > 30°C",
            )
            p3 = ax[idx // 3, idx % 3].plot(
                df_current.index[mask_min],
                df_current[mask_min]["cpc_tmin"],
                "co",
                markersize=2,
                label="Min temp < 5°C",
            )

            ax[idx // 3, idx % 3].legend(loc="upper left", fontsize="small")
        else:
            # Plot mean value
            (a1,) = ax[idx // 3, idx % 3].plot(
                df_current.index,
                curr_vals,
                color="b",
                lw=1.5,
                label=frcast_yr if idx == 0 else "",
            )
            (a2,) = ax[idx // 3, idx % 3].plot(
                df_current.index,
                last_vals,
                color=color_list[8],
                lw=1.25,
                label=frcast_yr - 1 if idx == 0 else "",
            )
            (a3,) = ax[idx // 3, idx % 3].plot(
                df_current.index,
                past_vals,
                color="k",
                lw=1.25,
                label="Mean" if idx == 0 else "",
            )
            # a9, = ax[idx // 3, idx % 3].plot(df_current.index, new_past_vals, color='b', linestyle='-.', lw=1.25, label='Mean' if idx == 0 else '')

            a4 = ax[idx // 3, idx % 3].fill_between(
                df_current.index,
                min_vals,
                max_vals,
                color="lightgray",
                label="Min/Max" if idx == 0 else "",
                alpha=0.7,
                lw=0,
            )

        if dates_cal:
            if dates_cal[0]:
                a5 = ax[idx // 3, idx % 3].axvline(
                    dates_cal[0],
                    color=color_list[10],
                    label="Planting",
                    lw=1.5,
                    linestyle="--",
                )

            if dates_cal[1]:
                a6 = ax[idx // 3, idx % 3].axvline(
                    dates_cal[1], color=color_list[4], label="Greenup", lw=1.5
                )

            if dates_cal[2]:
                a7 = ax[idx // 3, idx % 3].axvline(
                    dates_cal[2], color="darkgoldenrod", label="Senescence", lw=1.5
                )

            if dates_cal[3]:
                a8 = ax[idx // 3, idx % 3].axvline(
                    dates_cal[3],
                    color=color_list[6],
                    label="Harvest",
                    lw=1.5,
                    linestyle="--",
                )

        # Create a legend with transparent box around it (inside first subplot)
        # leg = ax[idx // 3, idx % 3].legend(loc='upper left', fancybox=None, prop={'size': 'large'}, ncol=2)
        # leg.get_frame().set_linewidth(0.0)  # remove only the border of the box of the legend

    # Plot legend outside of subplots
    if dates_cal:
        # all_labels = [str(frcast_yr), 'Median Analog years (OND 2021)', str(frcast_yr - 1), '5 year Mean', '10 year Min/Max', 'Planting', 'Greenup', 'Senescence', 'Harvest']
        # leg = plt.figlegend([a1, a9, a2, a3, a4, a5, a6, a7, a8], all_labels, loc='lower center', bbox_to_anchor=[0.76, 0.06])
        all_labels = [
            str(frcast_yr),
            str(frcast_yr - 1),
            "5 year Mean",
            "10 year Min/Max",
            "Planting",
            "Greenup",
            "Senescence",
            "Harvest",
        ]
        leg = plt.figlegend(
            [a1, a2, a3, a4, a5, a6, a7, a8],
            all_labels,
            loc="lower center",
            bbox_to_anchor=[0.76, 0.06],
        )
    else:
        all_labels = [str(frcast_yr), "5 year Mean", "5 year Min/Max"]
        leg = plt.figlegend(
            [a1, a2, a3], all_labels, loc="lower center", bbox_to_anchor=[0.76, 0.06]
        )

    # Add Harvest and GEOGLAM logos
    import matplotlib.image as image

    im = image.imread(str(logos[0]))
    fig.figimage(im, 3800, 2270, zorder=3)
    im = image.imread(str(logos[1]))
    fig.figimage(im, 4100, 2300, zorder=3)

    # TODO: Should be updated every time a new data source is added or previous one deleted or modified
    fig.text(0.83, 0.25, "Data Sources\n", fontsize=14, fontweight="bold")
    precip_var = "chirps" if "chirps" in df.columns.values else "cpc_precip"
    precip_str = (
        "Precipitation: CHIRPS\n"
        if precip_var == "chirps"
        else "Precipitation: NOAA CPC\n"
    )
    if use_forecast:
        precip_str += "Precipitation Forecast: CHIRPS-GEFS\n"
    if precip_var == "chirps":
        fig.text(
            0.83,
            0.14,
            "NDVI: UMD GLAM system\n"
            + "Temperature: NOAA CPC\n"
            + precip_str
            + "Evaporative Stress Index: NASA ESI\n"
            + "Soil Moisture: NASA-USDA Global Soil Moisture\n",
            # 'Growing degree days: NOAA CPC temperature',
            linespacing=1.5,
        )
    else:
        fig.text(
            0.83,
            0.15,
            "NDVI: UMD GLAM system\n"
            + "Temperature: NOAA CPC\n"
            + precip_str
            + "Evaporative Stress Index: NASA ESI\n"
            + "Soil Moisture: NASA-USDA Global Soil Moisture\n",
            # 'Growing degree days: NOAA CPC temperature',
            linespacing=1.5,
        )

    fig.text(
        0.67,
        0.04,
        r"$\blacktriangleright$ Crop growth stage dates are based on the 5 year average GEOGLAM best available crop calendars",
        fontsize=9,
    )
    fig.text(
        0.91, 0.02, f"Produced on: {ar.utcnow().format('MMM DD YYYY')}", fontsize=9
    )

    leg.get_frame().set_facecolor("none")
    leg.set_title("Legend", prop={"size": 14, "weight": "heavy"})
    leg.get_frame().set_linewidth(0.0)
    leg._legend_box.align = "left"

    # Final layout adjustment and output
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)

    plt.savefig(dir_out / fname, dpi=constants.DPI)
    plt.close()

    # Revert to default matplotlib parameters
    set_matplotlib_params()
