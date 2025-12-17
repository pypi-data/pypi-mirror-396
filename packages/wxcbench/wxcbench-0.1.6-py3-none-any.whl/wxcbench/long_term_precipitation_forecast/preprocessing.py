"""
Data Preprocessing Utilities for Long-Term Precipitation Forecasts

This module provides functions for preprocessing satellite observations
and precipitation data, including regridding, normalization, and temporal alignment.
"""

from typing import Optional, Union, List, Tuple
import numpy as np
import xarray as xr
from scipy.interpolate import griddata
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

from wxcbench.long_term_precipitation_forecast.config import (
    MERRA_GRID,
    NORMALIZATION_METHODS,
)


def create_merra_grid() -> Tuple[np.ndarray, np.ndarray]:
    """
    Create MERRA grid longitude and latitude arrays.

    Returns:
        tuple: (lon, lat) arrays for MERRA grid.
    """
    lon = np.arange(
        MERRA_GRID["lon_min"],
        MERRA_GRID["lon_max"] + MERRA_GRID["dx"],
        MERRA_GRID["dx"],
    )
    lat = np.arange(
        MERRA_GRID["lat_min"],
        MERRA_GRID["lat_max"] + MERRA_GRID["dy"],
        MERRA_GRID["dy"],
    )

    lon = lon[: MERRA_GRID["nx"]]
    lat = lat[: MERRA_GRID["ny"]]

    return lon, lat


def regrid_to_merra(
    data: Union[np.ndarray, xr.DataArray],
    source_lon: Optional[Union[np.ndarray, xr.DataArray]] = None,
    source_lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    method: str = "nearest",
) -> xr.DataArray:
    """
    Regrid data to MERRA grid.

    Parameters:
        data (np.ndarray or xr.DataArray): Data to regrid.
            If xr.DataArray, will use its coordinates.
        source_lon (np.ndarray or xr.DataArray, optional): Source longitude coordinates.
        source_lat (np.ndarray or xr.DataArray, optional): Source latitude coordinates.
        method (str): Interpolation method: 'nearest', 'linear', 'cubic'
            (default: 'nearest').

    Returns:
        xr.DataArray: Regridded data on MERRA grid.
    """
    # Extract coordinates if data is xarray
    if isinstance(data, xr.DataArray):
        if source_lon is None:
            source_lon = data.coords.get("lon", data.coords.get("longitude"))
        if source_lat is None:
            source_lat = data.coords.get("lat", data.coords.get("latitude"))

        data_values = data.values
        dims = data.dims
        coords = {k: v for k, v in data.coords.items() if k not in ["lon", "lat", "longitude", "latitude"]}
    else:
        data_values = np.asarray(data)
        dims = None
        coords = {}

    if source_lon is None or source_lat is None:
        raise ValueError("Source longitude and latitude must be provided")

    source_lon = np.asarray(source_lon)
    source_lat = np.asarray(source_lat)

    # Create MERRA grid
    target_lon, target_lat = create_merra_grid()
    target_lon_grid, target_lat_grid = np.meshgrid(target_lon, target_lat)

    # Handle multi-dimensional data
    if data_values.ndim > 2:
        # Flatten non-spatial dimensions
        original_shape = data_values.shape
        spatial_dims = data_values.shape[-2:]  # Last two dimensions are spatial

        # Reshape to (other_dims, lat, lon)
        other_dims = np.prod(original_shape[:-2])
        data_flat = data_values.reshape(other_dims, spatial_dims[0], spatial_dims[1])

        # Regrid each slice
        regridded_slices = []
        for i in range(other_dims):
            source_points = np.column_stack([source_lat.ravel(), source_lon.ravel()])
            target_points = np.column_stack([target_lat_grid.ravel(), target_lon_grid.ravel()])
            values = data_flat[i].ravel()

            regridded = griddata(
                source_points, values, target_points, method=method, fill_value=np.nan
            )
            regridded = regridded.reshape(target_lat_grid.shape)
            regridded_slices.append(regridded)

        # Reshape back to original structure
        regridded_data = np.array(regridded_slices).reshape(
            original_shape[:-2] + (len(target_lat), len(target_lon))
        )
    else:
        # 2D data
        source_points = np.column_stack([source_lat.ravel(), source_lon.ravel()])
        target_points = np.column_stack([target_lat_grid.ravel(), target_lon_grid.ravel()])
        values = data_values.ravel()

        regridded_data = griddata(
            source_points, values, target_points, method=method, fill_value=np.nan
        )
        regridded_data = regridded_data.reshape(target_lat_grid.shape)

    # Create xarray DataArray
    if dims is None:
        dims = ["lat", "lon"]
    else:
        # Replace spatial dims with lat, lon
        dims = list(dims)
        dims[-2:] = ["lat", "lon"]

    coords = {**coords, "lat": target_lat, "lon": target_lon}
    da = xr.DataArray(regridded_data, dims=dims, coords=coords)

    return da


def normalize_data(
    data: Union[np.ndarray, xr.DataArray],
    method: str = "standard",
    axis: Optional[int] = None,
    return_scaler: bool = False,
):
    """
    Normalize or standardize data using various methods.

    Parameters:
        data (np.ndarray or xr.DataArray): Data to normalize.
        method (str): Normalization method: 'standard', 'minmax', 'robust', 'log'
            (default: 'standard').
        axis (int, optional): Axis along which to compute statistics.
            If None, normalizes over entire array (default: None).
        return_scaler (bool): If True, also return the scaler object for inverse
            transformation (default: False).

    Returns:
        np.ndarray or xr.DataArray: Normalized data.
            If return_scaler=True, returns tuple (normalized_data, scaler).
    """
    if method not in NORMALIZATION_METHODS:
        raise ValueError(
            f"Unknown normalization method: {method}. "
            f"Available methods: {NORMALIZATION_METHODS}"
        )

    is_xarray = isinstance(data, xr.DataArray)
    if is_xarray:
        data_values = data.values
        original_coords = data.coords
        original_dims = data.dims
    else:
        data_values = np.asarray(data)

    # Handle NaN values
    nan_mask = np.isnan(data_values)
    has_nans = nan_mask.any()

    if has_nans:
        # Replace NaNs temporarily
        data_values_clean = np.where(nan_mask, 0, data_values)
    else:
        data_values_clean = data_values

    # Reshape for sklearn scalers
    original_shape = data_values_clean.shape
    if axis is None:
        data_reshaped = data_values_clean.reshape(-1, 1)
    else:
        # Flatten all dimensions except the specified axis
        other_axes = [i for i in range(data_values_clean.ndim) if i != axis]
        data_reshaped = np.moveaxis(data_values_clean, axis, -1)
        data_reshaped = data_reshaped.reshape(-1, data_reshaped.shape[-1])

    # Apply normalization
    if method == "standard":
        scaler = StandardScaler()
    elif method == "minmax":
        scaler = MinMaxScaler()
    elif method == "robust":
        scaler = RobustScaler()
    elif method == "log":
        # Log transform (no sklearn scaler needed)
        normalized = np.log1p(data_values_clean)  # log1p = log(1+x)
        scaler = None
    else:
        raise ValueError(f"Unsupported normalization method: {method}")

    if scaler is not None:
        normalized = scaler.fit_transform(data_reshaped)
        # Reshape back
        if axis is None:
            normalized = normalized.reshape(original_shape)
        else:
            normalized = normalized.reshape([original_shape[i] for i in other_axes] + [original_shape[axis]])
            normalized = np.moveaxis(normalized, -1, axis)
    else:
        normalized = normalized.reshape(original_shape)

    # Restore NaNs
    if has_nans:
        normalized = np.where(nan_mask, np.nan, normalized)

    # Convert back to xarray if input was xarray
    if is_xarray:
        normalized = xr.DataArray(normalized, dims=original_dims, coords=original_coords)

    if return_scaler:
        return normalized, scaler
    else:
        return normalized


def align_temporal_data(
    obs_list: List[Union[np.ndarray, xr.DataArray]],
    reference_dates: Optional[List] = None,
    target_frequency: str = "daily",
) -> xr.Dataset:
    """
    Align temporal data from multiple sources to a common time axis.

    Parameters:
        obs_list (list): List of observation arrays or DataArrays.
        reference_dates (list, optional): Reference dates for alignment.
        target_frequency (str): Target temporal frequency: 'daily', '3-hourly', etc.
            (default: 'daily').

    Returns:
        xr.Dataset: Temporally aligned observations.
    """
    if not obs_list:
        raise ValueError("obs_list cannot be empty")

    # Convert all to xarray if needed
    datasets = []
    for obs in obs_list:
        if isinstance(obs, xr.DataArray):
            datasets.append(obs.to_dataset(name="data"))
        elif isinstance(obs, xr.Dataset):
            datasets.append(obs)
        else:
            # Convert numpy array to xarray
            datasets.append(xr.DataArray(obs).to_dataset(name="data"))

    # Align to common time axis if reference dates provided
    if reference_dates is not None:
        # Create time coordinate
        time_coords = xr.cftime_range(
            start=reference_dates[0],
            end=reference_dates[-1],
            freq=target_frequency,
        )

        # Reindex all datasets to common time
        aligned_datasets = []
        for ds in datasets:
            if "time" in ds.coords:
                aligned = ds.reindex(time=time_coords, method="nearest")
            else:
                # Add time dimension
                aligned = ds.expand_dims("time").assign_coords(time=time_coords)
            aligned_datasets.append(aligned)

        # Combine all datasets
        combined = xr.merge(aligned_datasets)

    else:
        # Just combine without temporal alignment
        combined = xr.merge(datasets)

    return combined

