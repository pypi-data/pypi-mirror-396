from collections import Counter

import numpy as np
import pandas as pd
from scipy.stats import pearsonr as pearsonr
from tqdm import tqdm


def extract_regions(X, y, regions=[]):
    """
    Extract data of specific regions
    :param X: pd.DataFrame, input data
    :param y: pd.Series, target data
    :param regions: list, list of regions to extract
    """
    X, y = X.copy(), y.copy()

    indexes = X[X["Region"].isin(regions)].index
    X = X.loc[indexes, :].reset_index(drop=True)
    y = y.loc[indexes].reset_index(drop=True)

    return X, y


def _compute_correlations(X, y):
    feature_correlations = {}

    for feature in X.columns:
        # Ignore object or categorical type columns
        if X[feature].dtypes.name in ["object", "category"]:
            continue

        f_series = X[feature]

        # Ignore NaN values in either y or f_series
        mask = ~(np.isnan(y) | np.isnan(f_series))
        y_filtered = y[mask]
        f_series_filtered = f_series[mask]

        # Handle cases where std is zero
        if np.std(f_series_filtered) == 0 or np.std(y_filtered) == 0:
            feature_correlations[feature] = np.nan
        else:
            try:
                r = pearsonr(y_filtered, f_series_filtered)[0]
                feature_correlations[feature] = round(r, 3)
            except Exception as e:
                # print(f"Error computing correlation for {feature}: {e}")
                feature_correlations[feature] = np.nan

    return feature_correlations



def find_most_common_top_feature(top_feature_by_region):
    """
    Find the most common top feature and number of occurences
    :param top_feature_by_region: dict, top feature by region
    """
    # Extract the first position values from the tuples
    values_first_position = [value[0][0] for value in top_feature_by_region.values()]

    # Count occurrences of each value and average value of the top feature
    counter = Counter(values_first_position)

    # Return the counter which contains the most
    # common top feature(s) and number of occurences
    return counter


def get_top_correlated_features(inputs, targets):
    """
    Get most correlated features for each region
    :param inputs: pd.DataFrame, input data
    :param targets: pd.Series, target data
    :param type: str, Find top feature by correlation (top), or compute all feature correlations (all)
    """
    feature_by_region = {}

    for region_id in inputs["Region"].unique():
        X, y = extract_regions(inputs, targets, regions=[region_id])

        feature_correlations = _compute_correlations(X, y)

        # Exclude any nan values
        feature_correlations = {
            k: v for k, v in feature_correlations.items() if not np.isnan(v)
        }

        if not feature_correlations:
            continue

        # Sorts the items of feature_correlations, a dictionary mapping features to their
        # correlation values, by the absolute value of the correlation in descending order,
        # resulting in a list of tuples with the feature and its corresponding correlation value
        sorted_corr_features = sorted(
            feature_correlations.items(), key=lambda x: abs(x[1]), reverse=True
        )

        top_feature, top_corr = sorted_corr_features[0]
        feature_by_region[region_id] = ([top_feature], [top_corr])

    counter = find_most_common_top_feature(feature_by_region)

    return feature_by_region, counter


def get_all_features_correlation(inputs: pd.DataFrame,
                                 targets: pd.Series,
                                 method: str) -> pd.DataFrame:
    """
    Fast version – identical output, no length-mismatch on regions whose
    feature names contain no spaces.
    """
    numeric_cols = inputs.select_dtypes(include=[np.number]).columns.tolist()

    df_all = inputs[numeric_cols + ["Region"]].copy()
    df_all["__target__"] = targets.values

    frames: list[pd.DataFrame] = []

    for region_id, g in tqdm(df_all.groupby("Region", sort=False), leave=False):
        corr = g[numeric_cols].corrwith(g["__target__"]).round(3).dropna()
        if corr.empty:
            continue

        # ---- safe split: always two columns --------------------------------
        split = (
            pd.Series(corr.index)            # guarantees a Series
              .str.split(" ", n=1, expand=True)
        )
        if split.shape[1] == 1:              # no spaces in any feature name
            split[1] = ""                    # match legacy behaviour
        split.columns = [0, 1]               # make column labels predictable

        df_region = (
            pd.DataFrame({
                "Metric": split[0].values,
                method:  split[1].values,
                "Value": corr.values         # same length as above
            })
            .pivot_table(index=method, columns="Metric",
                         values="Value", aggfunc="first")
            .reset_index()
        )
        df_region.insert(0, "Region", region_id)
        frames.append(df_region)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


