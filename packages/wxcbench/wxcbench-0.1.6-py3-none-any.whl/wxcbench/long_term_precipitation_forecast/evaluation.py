"""
Evaluation Metrics for Long-Term Precipitation Forecasts

This module provides functions for evaluating precipitation forecast accuracy
using bias, mean-squared error, correlation, and other metrics.
"""

from typing import Union, List, Dict, Tuple, Optional
import numpy as np
import xarray as xr

from wxcbench.long_term_precipitation_forecast.config import (
    DEFAULT_LAT_RANGE,
    MAX_LEAD_TIME_DAYS,
    EVALUATION_METRICS,
)


def area_weighted_mean(
    data: Union[np.ndarray, xr.DataArray],
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat_range: Tuple[float, float] = DEFAULT_LAT_RANGE,
) -> Union[float, np.ndarray]:
    """
    Compute area-weighted mean over specified latitude range.

    Parameters:
        data (np.ndarray or xr.DataArray): Data to average. If 2D, assumes (lat, lon).
            If 3D, assumes (time, lat, lon) or (lead_time, lat, lon).
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates.
            If None and data is xr.DataArray, will use coordinates.
        lat_range (tuple): Latitude range (min, max) in degrees (default: (-60, 60)).

    Returns:
        float or np.ndarray: Area-weighted mean value(s).
    """
    if isinstance(data, xr.DataArray):
        if lat is None:
            lat = data.coords.get("lat", data.coords.get("latitude"))
        data = data.values

    if lat is None:
        raise ValueError("Latitude coordinates must be provided if data is not xr.DataArray")

    # Convert to numpy if needed
    lat = np.asarray(lat)
    data = np.asarray(data)

    # Mask data outside latitude range
    lat_mask = (lat >= lat_range[0]) & (lat <= lat_range[1])

    if lat_mask.sum() == 0:
        raise ValueError(f"No data points found in latitude range {lat_range}")

    # Compute weights based on cosine of latitude
    weights = np.cos(np.deg2rad(lat[lat_mask]))
    weights = weights / weights.sum()  # Normalize

    # Apply mask and compute weighted mean
    if data.ndim == 2:
        # (lat, lon)
        masked_data = data[lat_mask, :]
        weighted_mean = np.nansum(masked_data * weights[:, np.newaxis]) / np.nansum(weights)
    elif data.ndim == 3:
        # (time/lead_time, lat, lon)
        masked_data = data[:, lat_mask, :]
        weighted_mean = np.nansum(
            masked_data * weights[np.newaxis, :, np.newaxis], axis=(1, 2)
        ) / np.nansum(weights)
    else:
        raise ValueError(f"Unsupported data dimensionality: {data.ndim}D")

    return weighted_mean


def compute_bias(
    predictions: Union[np.ndarray, xr.DataArray],
    observations: Union[np.ndarray, xr.DataArray],
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat_range: Tuple[float, float] = DEFAULT_LAT_RANGE,
) -> Union[float, np.ndarray]:
    """
    Compute bias between predictions and observations.

    Bias = mean(predictions - observations)

    Parameters:
        predictions (np.ndarray or xr.DataArray): Predicted precipitation values.
        observations (np.ndarray or xr.DataArray): Observed precipitation values.
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates for area weighting.
        lat_range (tuple): Latitude range for evaluation (default: (-60, 60)).

    Returns:
        float or np.ndarray: Bias value(s). Positive values indicate over-prediction.
    """
    if isinstance(predictions, xr.DataArray) and isinstance(observations, xr.DataArray):
        diff = predictions - observations
        if lat is None:
            lat = diff.coords.get("lat", diff.coords.get("latitude"))
        if lat is not None:
            return area_weighted_mean(diff, lat=lat, lat_range=lat_range)
        else:
            return float(diff.mean().values)

    predictions = np.asarray(predictions)
    observations = np.asarray(observations)

    if predictions.shape != observations.shape:
        raise ValueError(
            f"Shape mismatch: predictions {predictions.shape} vs "
            f"observations {observations.shape}"
        )

    diff = predictions - observations

    if lat is not None:
        return area_weighted_mean(diff, lat=lat, lat_range=lat_range)
    else:
        return np.nanmean(diff)


def compute_mse(
    predictions: Union[np.ndarray, xr.DataArray],
    observations: Union[np.ndarray, xr.DataArray],
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat_range: Tuple[float, float] = DEFAULT_LAT_RANGE,
) -> Union[float, np.ndarray]:
    """
    Compute mean-squared error between predictions and observations.

    MSE = mean((predictions - observations)^2)

    Parameters:
        predictions (np.ndarray or xr.DataArray): Predicted precipitation values.
        observations (np.ndarray or xr.DataArray): Observed precipitation values.
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates for area weighting.
        lat_range (tuple): Latitude range for evaluation (default: (-60, 60)).

    Returns:
        float or np.ndarray: MSE value(s).
    """
    if isinstance(predictions, xr.DataArray) and isinstance(observations, xr.DataArray):
        squared_diff = (predictions - observations) ** 2
        if lat is None:
            lat = squared_diff.coords.get("lat", squared_diff.coords.get("latitude"))
        if lat is not None:
            return area_weighted_mean(squared_diff, lat=lat, lat_range=lat_range)
        else:
            return float(squared_diff.mean().values)

    predictions = np.asarray(predictions)
    observations = np.asarray(observations)

    if predictions.shape != observations.shape:
        raise ValueError(
            f"Shape mismatch: predictions {predictions.shape} vs "
            f"observations {observations.shape}"
        )

    squared_diff = (predictions - observations) ** 2

    if lat is not None:
        return area_weighted_mean(squared_diff, lat=lat, lat_range=lat_range)
    else:
        return np.nanmean(squared_diff)


def compute_correlation(
    predictions: Union[np.ndarray, xr.DataArray],
    observations: Union[np.ndarray, xr.DataArray],
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat_range: Tuple[float, float] = DEFAULT_LAT_RANGE,
) -> Union[float, np.ndarray]:
    """
    Compute correlation coefficient between predictions and observations.

    Parameters:
        predictions (np.ndarray or xr.DataArray): Predicted precipitation values.
        observations (np.ndarray or xr.DataArray): Observed precipitation values.
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates for area weighting.
        lat_range (tuple): Latitude range for evaluation (default: (-60, 60)).

    Returns:
        float or np.ndarray: Correlation coefficient(s) between -1 and 1.
    """
    predictions = np.asarray(predictions)
    observations = np.asarray(observations)

    if predictions.shape != observations.shape:
        raise ValueError(
            f"Shape mismatch: predictions {predictions.shape} vs "
            f"observations {observations.shape}"
        )

    # Flatten spatial dimensions for correlation calculation
    if predictions.ndim > 1:
        # Handle latitude masking if provided
        if lat is not None:
            lat = np.asarray(lat)
            lat_mask = (lat >= lat_range[0]) & (lat <= lat_range[1])
            if predictions.ndim == 2:
                predictions = predictions[lat_mask, :].flatten()
                observations = observations[lat_mask, :].flatten()
            elif predictions.ndim == 3:
                # Compute correlation for each time/lead_time
                correlations = []
                for i in range(predictions.shape[0]):
                    pred_flat = predictions[i, lat_mask, :].flatten()
                    obs_flat = observations[i, lat_mask, :].flatten()
                    # Remove NaN values
                    valid_mask = ~(np.isnan(pred_flat) | np.isnan(obs_flat))
                    if valid_mask.sum() > 1:
                        corr = np.corrcoef(pred_flat[valid_mask], obs_flat[valid_mask])[0, 1]
                        correlations.append(corr if not np.isnan(corr) else 0.0)
                    else:
                        correlations.append(0.0)
                return np.array(correlations)
        else:
            predictions = predictions.flatten()
            observations = observations.flatten()

    # Remove NaN values
    valid_mask = ~(np.isnan(predictions) | np.isnan(observations))
    if valid_mask.sum() < 2:
        return 0.0

    corr = np.corrcoef(predictions[valid_mask], observations[valid_mask])[0, 1]
    return corr if not np.isnan(corr) else 0.0


def compute_rmse(
    predictions: Union[np.ndarray, xr.DataArray],
    observations: Union[np.ndarray, xr.DataArray],
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat_range: Tuple[float, float] = DEFAULT_LAT_RANGE,
) -> Union[float, np.ndarray]:
    """
    Compute root mean-squared error between predictions and observations.

    RMSE = sqrt(mean((predictions - observations)^2))

    Parameters:
        predictions (np.ndarray or xr.DataArray): Predicted precipitation values.
        observations (np.ndarray or xr.DataArray): Observed precipitation values.
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates for area weighting.
        lat_range (tuple): Latitude range for evaluation (default: (-60, 60)).

    Returns:
        float or np.ndarray: RMSE value(s).
    """
    mse_val = compute_mse(predictions, observations, lat=lat, lat_range=lat_range)
    if isinstance(mse_val, (int, float, np.number)):
        return np.sqrt(mse_val)
    else:
        return np.sqrt(mse_val)


def compute_mae(
    predictions: Union[np.ndarray, xr.DataArray],
    observations: Union[np.ndarray, xr.DataArray],
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat_range: Tuple[float, float] = DEFAULT_LAT_RANGE,
) -> Union[float, np.ndarray]:
    """
    Compute mean absolute error between predictions and observations.

    MAE = mean(|predictions - observations|)

    Parameters:
        predictions (np.ndarray or xr.DataArray): Predicted precipitation values.
        observations (np.ndarray or xr.DataArray): Observed precipitation values.
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates for area weighting.
        lat_range (tuple): Latitude range for evaluation (default: (-60, 60)).

    Returns:
        float or np.ndarray: MAE value(s).
    """
    if isinstance(predictions, xr.DataArray) and isinstance(observations, xr.DataArray):
        abs_diff = np.abs(predictions - observations)
        if lat is None:
            lat = abs_diff.coords.get("lat", abs_diff.coords.get("latitude"))
        if lat is not None:
            return area_weighted_mean(abs_diff, lat=lat, lat_range=lat_range)
        else:
            return float(abs_diff.mean().values)

    predictions = np.asarray(predictions)
    observations = np.asarray(observations)

    if predictions.shape != observations.shape:
        raise ValueError(
            f"Shape mismatch: predictions {predictions.shape} vs "
            f"observations {observations.shape}"
        )

    abs_diff = np.abs(predictions - observations)

    if lat is not None:
        return area_weighted_mean(abs_diff, lat=lat, lat_range=lat_range)
    else:
        return np.nanmean(abs_diff)


def evaluate_forecasts(
    forecasts: Union[np.ndarray, xr.DataArray],
    observations: Union[np.ndarray, xr.DataArray],
    lead_times: Optional[List[int]] = None,
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat_range: Tuple[float, float] = DEFAULT_LAT_RANGE,
    metrics: Optional[List[str]] = None,
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Comprehensive evaluation of precipitation forecasts.

    Computes multiple metrics for each lead time and returns a dictionary
    with all computed metrics.

    Parameters:
        forecasts (np.ndarray or xr.DataArray): Forecast precipitation values.
            Shape should be (lead_time, lat, lon) or (time, lead_time, lat, lon).
        observations (np.ndarray or xr.DataArray): Observed precipitation values.
            Shape should match forecasts.
        lead_times (list, optional): List of lead times in days. If None, uses
            indices 0, 1, 2, ... (default: None).
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates.
        lat_range (tuple): Latitude range for evaluation (default: (-60, 60)).
        metrics (list, optional): List of metrics to compute.
            Options: 'bias', 'mse', 'rmse', 'correlation', 'mae'.
            If None, computes all available metrics (default: None).

    Returns:
        dict: Dictionary with metric names as keys and arrays of values
            (one per lead time) as values.
    """
    if metrics is None:
        metrics = EVALUATION_METRICS

    forecasts = np.asarray(forecasts)
    observations = np.asarray(observations)

    if forecasts.shape != observations.shape:
        raise ValueError(
            f"Shape mismatch: forecasts {forecasts.shape} vs "
            f"observations {observations.shape}"
        )

    # Determine lead time dimension
    if forecasts.ndim == 3:
        # (lead_time, lat, lon)
        n_lead_times = forecasts.shape[0]
        lead_time_dim = 0
    elif forecasts.ndim == 4:
        # (time, lead_time, lat, lon)
        n_lead_times = forecasts.shape[1]
        lead_time_dim = 1
    else:
        raise ValueError(
            f"Unsupported forecast dimensionality: {forecasts.ndim}D. "
            "Expected 3D (lead_time, lat, lon) or 4D (time, lead_time, lat, lon)."
        )

    if lead_times is None:
        lead_times = list(range(n_lead_times))

    if len(lead_times) != n_lead_times:
        raise ValueError(
            f"Length of lead_times ({len(lead_times)}) does not match "
            f"number of lead times in forecasts ({n_lead_times})."
        )

    results = {}

    # Compute metrics for each lead time
    for metric in metrics:
        metric_values = []
        for i in range(n_lead_times):
            if forecasts.ndim == 3:
                pred = forecasts[i, :, :]
                obs = observations[i, :, :]
            else:
                # Average over time dimension
                pred = forecasts[:, i, :, :].mean(axis=0)
                obs = observations[:, i, :, :].mean(axis=0)

            if metric == "bias":
                val = compute_bias(pred, obs, lat=lat, lat_range=lat_range)
            elif metric == "mse":
                val = compute_mse(pred, obs, lat=lat, lat_range=lat_range)
            elif metric == "rmse":
                mse_val = compute_mse(pred, obs, lat=lat, lat_range=lat_range)
                val = np.sqrt(mse_val) if isinstance(mse_val, (int, float, np.number)) else np.sqrt(mse_val)
            elif metric == "correlation":
                val = compute_correlation(pred, obs, lat=lat, lat_range=lat_range)
            elif metric == "mae":
                val = compute_mae(pred, obs, lat=lat, lat_range=lat_range)
            else:
                raise ValueError(f"Unknown metric: {metric}")

            metric_values.append(val)

        results[metric] = np.array(metric_values)

    results["lead_times"] = np.array(lead_times)
    return results

