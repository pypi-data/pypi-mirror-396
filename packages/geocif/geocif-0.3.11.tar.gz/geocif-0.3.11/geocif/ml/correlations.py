import os

import matplotlib.pyplot as plt
import palettable as pal
import pandas as pd
from tqdm import tqdm

from geocif import utils
from geocif.ml import embedding
from geocif.ml import stages


def most_correlated_feature_by_time(df_train, simulation_stages, target_col):
    """

    Args:
        df_train:
        simulation_stages:
        target_col:

    Returns:

    """
    frames = []

    stages = [simulation_stages[: idx + 1] for idx in range(len(simulation_stages))]

    # Only select columns that have been observed till the current stage
    for stage in tqdm(stages, leave=False, desc="Compute most correlated feature"):
        current_feature_set = [
            col for col in df_train.columns if col.endswith(f"_{stage[-1]}")
        ]

        # Get the most correlated feature for each region
        top_feature_by_region, counter = embedding.get_top_correlated_features(
            df_train[current_feature_set + ["Region"]],
            df_train[target_col],
        )

        # Create a dataframe with the most common top feature and number of occurrences over timestep
        _feature = counter.most_common(1)[0][0]
        # Loop through top_feature_by_region and find the average score for _feature
        # Calculate the average score for 'DTR_36'
        _feature_scores = [
            value[1][0]
            for key, value in top_feature_by_region.items()
            if _feature in value[0]
        ]
        average_score = sum(_feature_scores) / len(_feature_scores)
        _feature = utils.remove_last_part(_feature)

        df = pd.DataFrame(
            {
                "Stage": [stage[-1]],
                "Date": [utils.dict_growth_stages[stage[-1]]],
                "Feature with Highest Correlation": [counter.most_common(1)[0][0]],
                "Feature Category": [_feature],
                "Score": [average_score],
                # "Type": [ci.dict_indices[_feature][0]],
                "Number of Occurrences": [counter.most_common(1)[0][1]],
                # "Current Feature Set": [current_feature_set],
            }
        )
        frames.append(df)

    df_most_corr_feature_by_time = pd.concat(frames)


def plot_feature_corr_by_time(df, **kwargs):
    import seaborn as sns

    country = kwargs.get("country")
    crop = kwargs.get("crop")
    dir_output = kwargs.get("dir_output")
    forecast_season = kwargs.get("forecast_season")
    national_correlation = kwargs.get("national_correlation")
    group_by = kwargs.get("groupby")
    plot_map = kwargs.get("plot_map")
    region_name = kwargs.get("region_name")

    # Setup the figure and gridspec
    fig = plt.figure(figsize=(10, 5))
    if plot_map:
        gs = fig.add_gridspec(
            3, 2, height_ratios=[6, 5, 1], width_ratios=[5, 1.5], hspace=0.6, wspace=0.0
        )
    else:
        gs = fig.add_gridspec(3, 1, height_ratios=[6, 5, 1], hspace=0.6, wspace=0.0)

    # Assign subplots
    ax_heatmap = fig.add_subplot(gs[0:2, 0])
    cbar_ax = fig.add_subplot(gs[2, 0])
    if plot_map:
        ax_map = fig.add_subplot(gs[0, 1])
        ax4 = fig.add_subplot(gs[2, 1])

    # Transpose and reverse the columns of the dataframe
    df_transpose = df.T
    df = df_transpose[df_transpose.columns[::-1]]
    ax_heatmap = sns.heatmap(
        df,
        ax=ax_heatmap,
        annot=True,
        cmap=pal.cartocolors.diverging.Earth_5.get_mpl_colormap(),
        fmt=".2f",
        square=False,
        linewidths=0.5,
        linecolor="white",
        cbar_ax=cbar_ax,
        cbar_kws={"orientation": "horizontal"},  # , "shrink": 0.5},
        annot_kws={"size": 4},
        xticklabels=True,
        yticklabels=True,
    )
    ax_heatmap.tick_params(left=False, bottom=False)

    if plot_map:
        # Plot the map using GeoPandas
        dg_country = kwargs.get("dg_country")

        ax_map = dg_country.plot(
            ax=ax_map,
            color="white",
            edgecolor="black",
            linewidth=1.0,
            facecolor=None,
            legend=False,
        )

    id = kwargs["region_id"]
    if plot_map:
        if not national_correlation:
            dg_region = dg_country[dg_country[group_by] == id]
            ax_map = dg_region.plot(
                ax=ax_map, color="blue", edgecolor="blue", linewidth=1.0, legend=False
            )
            # Set title with color blue
            ax_map.set_title(f"Region: {id}", color="blue")

        # No colorbar for the map
        ax_map.axis("off")
        # Remove borders
        ax_map.spines["top"].set_visible(False)
        ax_map.spines["right"].set_visible(False)
        ax_map.spines["bottom"].set_visible(False)
        ax_map.spines["left"].set_visible(False)
        # ax4 should not be visible
        ax4.axis("off")

    # Add colorbar label
    # cbar_ax.set_xlabel("Correlation Coefficient", labelpad=3, size="small")
    cbar_ax.set_title("Correlation Coefficient", loc="left", size="small")
    ax_heatmap.set_xticklabels(ax_heatmap.get_xticklabels(), size="x-small", rotation=0, fontsize=5)
    ax_heatmap.set_yticklabels(ax_heatmap.get_yticklabels(), size="x-small", fontsize=5)
    ax_heatmap.set_xlabel("")
    ax_heatmap.set_ylabel(" ")
    # Reduce font size of ticks of colorbar
    cbar_ax.tick_params(axis="both", which="major", labelsize=5)

    _country = country.title().replace("_", " ")
    _region_name = region_name if not national_correlation else ""
    _crop = crop.title().replace("_", " ")
    if not national_correlation:
        fname = f"{country}_{crop}_{id}_corr_feature_by_time.png"
    else:
        fname = f"{country}_{crop}_corr_feature_by_time.png"
    # first line – big
    ax_heatmap.set_title(f"{_country}, {_crop}",
                        fontsize=12,              # larger size
                        pad=18)                   # push it up a bit

    # second line – smaller, positioned just under the first
    ax_heatmap.text(0.5, 1.02,                    # x=50 % of axes, y just above top
                    _region_name,
                    transform=ax_heatmap.transAxes,
                    ha='center', va='bottom',
                    fontsize=8)                  # smaller size


    # plt.tight_layout()
    os.makedirs(dir_output, exist_ok=True)
    plt.savefig(dir_output / fname, dpi=250)
    plt.close()


def _all_correlated_feature_by_time(df, **kwargs):
    """

    Args:
        df:
        **kwargs:

    Returns:

    """
    frames = []
    all_stages = kwargs.get("all_stages")
    target_col = kwargs.get("target_col")
    method = kwargs.get("method")

    longest_stage = max(all_stages, key=len)

    # Split the original string into a list of its parts
    longest_stage = longest_stage.split("_")

    # Generate the list of strings as described by the user, removing one element from the start each time
    stages_features = ["_".join(longest_stage[i:]) for i in range(len(longest_stage))]

    # Drop columns with no yield information
    df = df.dropna(subset=[target_col])

    # Only select columns that have been observed till the current stage
    pbar = tqdm(stages_features, total=len(stages_features), leave=False)
    for stage in pbar:
        pbar.set_description(f"Calculating correlations")
        pbar.update()

        stage_name = stages.get_stage_information_dict(f"GD4_{stage}", method)[
            "Stage Name"
        ]
        # starting_stage = stage_name.split("-")[0]
        current_feature_set = [col for col in df.columns if stage_name in col]

        # Get the most correlated feature for each region
        df_tmp = embedding.get_all_features_correlation(
            df[current_feature_set + ["Region"]], df[target_col], method
        )

        frames.append(df_tmp)

    df_results = pd.concat(frames)
    if not df_results.empty:
        # Exclude Region column
        df_results = df_results.drop(columns="Region")
        # Groupby Dekad and compute mean of all columns apart from Region
        df_results = df_results.groupby(method).mean()

        all_stage_names = []
        for stage in stages_features:
            _tmp = stages.get_stage_information_dict(f"GD4_{stage}", method)[
                "Stage Name"
            ]
            all_stage_names.append(_tmp)

        df_results = df_results.reindex(all_stage_names)

        # Drop rows with all NaN values
        df_results = df_results.dropna(how="all")

        # Split the index based on - and only keep the first element
        df_results.index = df_results.index.str.split("-").str[0]

        return df_results
    else:
        return pd.DataFrame()


def all_correlated_feature_by_time(df, **kwargs):
    """

    Args:
        df:
        **kwargs:

    Returns:

    """
    national_correlation = kwargs.get("national_correlation")
    group_by = kwargs.get("groupby")
    combined_dict = kwargs.get("combined_dict")
    THRESHOLD = kwargs.get("correlation_threshold")

    dict_selected_features = {}
    dict_best_cei = {}

    if not national_correlation:
        groups = df.groupby(group_by)
        for region_id, group in tqdm(
            groups, desc=f"Compute all correlated feature by {group_by}", leave=False
        ):
            df_corr = _all_correlated_feature_by_time(group, **kwargs)

            # Remove columns with more than 50% NaN values
            df_corr = df_corr.dropna(thresh=len(df_corr) / 2, axis=1)

            if not df_corr.empty:
                df_tmp = df_corr[df_corr.columns[(abs(df_corr.mean()) > THRESHOLD)]]
                # Add the columns to dict_selected_features along with the absolute mean value
                absolute_medians = df_tmp.abs().median()

                # Create a DataFrame to display the column names and their absolute median values
                absolute_median_df = absolute_medians.reset_index()
                absolute_median_df.columns = ['CEI', 'Median']

                # Add the CEI and Median value to dict_selected_features
                dict_selected_features[region_id] = absolute_median_df

                df_tmp2 = (
                    df_tmp.median(axis=0)
                    .abs()
                    .sort_values(ascending=False)
                    .reset_index()
                )
                df_tmp2.columns = ["Metric", "Value"]
                # Add another column based on Type of Metric
                for idx, row in df_tmp2.iterrows():
                    df_tmp2.loc[idx, "Type"] = combined_dict[row[0]][0]

                # Compute median of each CEI and sort the dataframe based on the absolute value of the median
                dict_best_cei[region_id] = (
                    df_tmp2.groupby("Type")
                    .max()
                    .reset_index()
                    .sort_values("Value", ascending=False)["Metric"]
                    .values
                )

                kwargs["region_id"] = region_id
                _region_names = ", ".join([str(x) for x in group['Region'].unique()])
                kwargs["region_name"] = _region_names
                plot_feature_corr_by_time(df_tmp, **kwargs)
                # For each element in dict_best_cei, add the type of the cei
            else:
                # HACK
                df_corr = _all_correlated_feature_by_time(df, **kwargs)

                df_tmp = df_corr[df_corr.columns[(abs(df_corr.mean()) > THRESHOLD)]]
                # Add the columns to dict_selected_features along with the absolute mean value
                absolute_medians = df_tmp.abs().median()

                # Create a DataFrame to display the column names and their absolute median values
                absolute_median_df = absolute_medians.reset_index()
                absolute_median_df.columns = ['CEI', 'Median']

                # Add the CEI and Median value to dict_selected_features
                dict_selected_features[region_id] = absolute_median_df
                dict_best_cei[region_id] = {}
    else:
        df_corr = _all_correlated_feature_by_time(df, **kwargs)
        df_tmp = df_corr[df_corr.columns[(abs(df_corr.mean()) > THRESHOLD)]]
        # Add the columns to dict_selected_features along with the absolute mean value
        absolute_medians = df_tmp.abs().median()

        # Create a DataFrame to display the column names and their absolute median values
        absolute_median_df = absolute_medians.reset_index()
        absolute_median_df.columns = ['CEI', 'Median']

        # Add the CEI and Median value to dict_selected_features
        dict_selected_features[0] = absolute_median_df

        plot_feature_corr_by_time(df_corr, **kwargs)

    return dict_selected_features, dict_best_cei


def feature_correlation_by_time(**kwargs):
    raise NotImplementedError()

    frames = []
    simulation_stages = kwargs.get("simulation_stages")
    df_train = kwargs.get("df_train")
    target_col = kwargs.get("target_col")

    stages = [simulation_stages[: idx + 1] for idx in range(len(simulation_stages))]

    # Only select columns that have been observed till the current stage
    for stage in tqdm(stages, leave=False, desc="Compute feature correlation by time"):
        current_feature_set = [
            col for col in df_train.columns if col.endswith(f"_{stage[-1]}")
        ]

        # Get the most correlated feature for each region
        top_feature_by_region, counter = embedding.compute_feature_correlations(
            df_train[current_feature_set + ["Region"]],
            df_train[target_col],
            "all",
        )

        # Create a dataframe with the most common top feature and number of occurrences over timestep
        _feature = counter.most_common(1)[0][0]
        # Loop through top_feature_by_region and find the average score for _feature
        # Calculate the average score for 'DTR_36'
        _feature_scores = [
            value[1][0]
            for key, value in top_feature_by_region.items()
            if _feature in value[0]
        ]
        average_score = sum(_feature_scores) / len(_feature_scores)
        _feature = utils.remove_last_part(_feature)

        df = pd.DataFrame(
            {
                "Stage": [stage[-1]],
                "Date": [utils.dict_growth_stages[stage[-1]]],
                "Feature with Highest Correlation": [counter.most_common(1)[0][0]],
                "Feature Category": [_feature],
                "Score": [average_score],
                # "Type": [ci.dict_indices[_feature][0]],
                "Number of Occurrences": [counter.most_common(1)[0][1]],
                # "Current Feature Set": [current_feature_set],
            }
        )
        frames.append(df)

    df_corr_feature_by_time = pd.concat(frames)
