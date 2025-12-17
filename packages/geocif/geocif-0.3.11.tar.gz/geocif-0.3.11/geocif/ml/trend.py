import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant


class DetrendedData:
    """
    A class to store the detrended series, the model used for detrending,
    and the type of model ('mean', 'linear', 'quadratic', 'difference').
    """

    def __init__(self, detrended_series, trend_model, model_type):
        self.detrended_series = detrended_series
        self.trend_model = trend_model
        self.model_type = model_type


def detrend_dataframe(df, column_name="y", model_type="best"):
    """
    Removes the trend from the specified column of a DataFrame using the specified method
    (mean, linear, quadratic, difference) or the method that results in the lowest AIC value.

    Parameters:
    - df: pandas DataFrame containing the time series data.
    - column_name: string name of the column to detrend.
    - model_type: string specifying which model to use for detrending ('mean', 'linear',
                  'quadratic', 'difference', or 'best' for automatic selection based on AIC).

    Returns:
    - DetrendedData object containing the detrended series, the statistical model,
      and the model type.
    """
    df["t"] = np.array(df["Harvest Year"])

    # Mean method
    mean_model = OLS(df[column_name], np.ones(len(df))).fit()

    # Linear trend model
    X_linear = add_constant(df["t"])
    linear_model = OLS(df[column_name], X_linear).fit()

    # Quadratic trend model
    X_quad = add_constant(np.column_stack((df["t"], df["t"] ** 2)))
    quad_model = OLS(df[column_name], X_quad).fit()

    # Differencing method
    diff_series = df[column_name].diff().dropna()
    diff_model = OLS(diff_series, np.ones(len(diff_series))).fit()

    models = {
        "mean": mean_model,
        "linear": linear_model,
        "quadratic": quad_model,
        "difference": diff_model
    }

    if model_type == "best":
        best_model_type = min(models, key=lambda x: models[x].aic)
    else:
        best_model_type = model_type

    best_model = models[best_model_type]

    if best_model_type == "mean":
        detrended = df[column_name] - mean_model.predict(np.ones(len(df)))
    elif best_model_type == "linear":
        detrended = df[column_name] - linear_model.predict(X_linear)
    elif best_model_type == "quadratic":
        detrended = df[column_name] - quad_model.predict(X_quad)
    else:  # difference
        detrended = df[column_name].diff().dropna()

    return DetrendedData(detrended, best_model, best_model_type)


def compute_trend(detrended_data, future_time_points=None):
    """
    Adds the trend back to a detrended series, useful for forecasting or visualization.

    Parameters:
    - detrended_data: DetrendedData object containing the detrended series and the model.
    - time_points: Optional numpy array of time points for which to retrend the data.
                   If None, uses the original time points from detrending.

    Returns:
    - The retrended series as a pandas Series.
    """
    future_time_points = np.array(future_time_points)

    model_type = detrended_data.model_type.unique()[0]
    model = detrended_data.trend_model.unique()[0]

    if model_type == "mean":
        trend_component = model.predict(
            np.ones(len(future_time_points)), has_constant="add"
        )
    elif model_type == "linear":
        X_linear = add_constant(future_time_points, has_constant="add")
        trend_component = model.predict(X_linear)
    elif model_type == "quadratic":
        X_quad = add_constant(
            np.column_stack((future_time_points, future_time_points**2)),
            has_constant="add",
        )
        trend_component = model.predict(X_quad)
    else:  # difference
        trend_component = pd.Series(np.nan, index=future_time_points)
        trend_component.iloc[0] = model.params[0]  # Add mean of differenced series

    return trend_component
