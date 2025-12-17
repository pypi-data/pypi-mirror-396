"""
Data Loading Utilities for Long-Term Precipitation Forecasts

This module provides functions for loading and preparing precipitation
and satellite observation datasets.
"""

from typing import List, Optional, Union, Dict
from pathlib import Path
import numpy as np
import xarray as xr
import pandas as pd

from wxcbench.long_term_precipitation_forecast.config import INPUT_OBSERVATION_DAYS


def load_precipitation_data(
    file_path: Union[str, Path],
    variable_name: Optional[str] = None,
    return_coords: bool = False,
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Load precipitation data from NetCDF file.

    Supports both PERSIANN CDR and IMERG Final precipitation datasets.

    Parameters:
        file_path (str or Path): Path to the NetCDF file.
        variable_name (str, optional): Name of the precipitation variable.
            If None, will attempt to auto-detect (default: None).
        return_coords (bool): If True, returns Dataset with coordinates;
            if False, returns DataArray (default: False).

    Returns:
        xr.Dataset or xr.DataArray: Precipitation data with coordinates.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Precipitation file not found: {file_path}")

    # Load dataset
    ds = xr.open_dataset(file_path)

    # Auto-detect variable name if not specified
    if variable_name is None:
        # Common variable names for precipitation
        possible_names = ["precipitation", "precip", "prcp", "rain", "prec"]
        for name in possible_names:
            if name in ds.data_vars:
                variable_name = name
                break

        if variable_name is None:
            # Take the first data variable
            variable_name = list(ds.data_vars)[0] if ds.data_vars else None
            if variable_name is None:
                raise ValueError("No precipitation variable found in dataset")

    if return_coords:
        return ds
    else:
        return ds[variable_name]


def load_satellite_observations(
    file_path: Union[str, Path],
    return_coords: bool = False,
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Load satellite observation data from NetCDF file.

    Supports GridSat, PATMOS-x, and SSMI observation datasets.

    Parameters:
        file_path (str or Path): Path to the NetCDF file.
        return_coords (bool): If True, returns Dataset with coordinates;
            if False, returns DataArray (default: False).

    Returns:
        xr.Dataset or xr.DataArray: Satellite observation data with coordinates.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Satellite observation file not found: {file_path}")

    # Load dataset
    ds = xr.open_dataset(file_path)

    if return_coords:
        return ds
    else:
        # Return all data variables if multiple, or single DataArray if one
        if len(ds.data_vars) == 1:
            return ds[list(ds.data_vars)[0]]
        else:
            return ds


def combine_observations(
    obs_files: List[Union[str, Path]],
    n_days: int = INPUT_OBSERVATION_DAYS,
    sort_by_date: bool = True,
) -> xr.Dataset:
    """
    Combine multiple daily observation files into a single dataset.

    Creates a sequence of observations from consecutive days (typically 8 days).

    Parameters:
        obs_files (list): List of paths to observation NetCDF files.
            Should contain observations for consecutive days.
        n_days (int): Number of days to combine (default: 8).
        sort_by_date (bool): If True, sort files by date before combining
            (default: True).

    Returns:
        xr.Dataset: Combined observations with time dimension.
    """
    if len(obs_files) < n_days:
        raise ValueError(
            f"Not enough observation files: {len(obs_files)} provided, "
            f"{n_days} required"
        )

    if sort_by_date:
        # Sort files by filename (assuming date in filename)
        obs_files = sorted(obs_files)

    # Take only the required number of days
    obs_files = obs_files[:n_days]

    # Load all observation files
    datasets = []
    for file_path in obs_files:
        ds = load_satellite_observations(file_path, return_coords=True)
        datasets.append(ds)

    # Combine along time dimension
    combined = xr.concat(datasets, dim="time", combine_attrs="override")

    # Add day index (0 to n_days-1)
    combined = combined.assign_coords(day=("time", list(range(n_days))))

    return combined


def prepare_training_data(
    input_dir: Union[str, Path],
    target_dir: Union[str, Path],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, List[Path]]:
    """
    Prepare training datasets by pairing input observations with target precipitation.

    Matches observation sequences (8 consecutive days) with corresponding
    precipitation targets (28 days following the observations).

    Parameters:
        input_dir (str or Path): Directory containing satellite observation files.
        target_dir (str or Path): Directory containing precipitation target files.
        start_date (str, optional): Start date in YYYYMMDD format (default: None).
        end_date (str, optional): End date in YYYYMMDD format (default: None).
        output_dir (str or Path, optional): Directory to save prepared dataset list.
            If None, only returns the mapping (default: None).

    Returns:
        dict: Dictionary with 'input_files' and 'target_files' keys, each containing
            a list of file paths.
    """
    input_dir = Path(input_dir)
    target_dir = Path(target_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if not target_dir.exists():
        raise FileNotFoundError(f"Target directory not found: {target_dir}")

    # Find all observation files
    obs_files = sorted(list(input_dir.glob("*.nc")))
    precip_files = sorted(list(target_dir.glob("*.nc")))

    if len(obs_files) == 0:
        raise ValueError(f"No observation files found in {input_dir}")
    if len(precip_files) == 0:
        raise ValueError(f"No precipitation files found in {target_dir}")

    # Extract dates from filenames (assuming YYYYMMDD format)
    def extract_date(filename: Path) -> str:
        name = filename.stem
        # Try to find 8-digit date pattern
        import re
        match = re.search(r"\d{8}", name)
        if match:
            return match.group()
        return ""

    obs_dates = [extract_date(f) for f in obs_files]
    precip_dates = [extract_date(f) for f in precip_files]

    # Filter by date range if provided
    if start_date:
        obs_files = [f for f, d in zip(obs_files, obs_dates) if d >= start_date]
        obs_dates = [d for d in obs_dates if d >= start_date]
    if end_date:
        obs_files = [f for f, d in zip(obs_files, obs_dates) if d <= end_date]
        obs_dates = [d for d in obs_dates if d <= end_date]

    # Match observations with precipitation targets
    # Each observation sequence (8 days) should have 28 days of precipitation targets
    input_sequences = []
    target_sequences = []

    for i in range(len(obs_files) - INPUT_OBSERVATION_DAYS + 1):
        # Get 8 consecutive observation files
        obs_sequence = obs_files[i : i + INPUT_OBSERVATION_DAYS]
        obs_start_date = obs_dates[i]
        obs_end_date = obs_dates[i + INPUT_OBSERVATION_DAYS - 1]

        # Find corresponding precipitation files (28 days after observation period)
        # This is simplified - actual implementation would need proper date arithmetic
        input_sequences.append(obs_sequence)

        # Find precipitation files for 28 days starting after observation period
        # Note: This is a simplified version - full implementation would need
        # proper date parsing and arithmetic
        target_sequences.append([])  # Placeholder

    result = {
        "input_files": input_sequences,
        "target_files": target_sequences,
    }

    # Save to file if output directory specified
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        # Save as JSON or CSV listing file paths
        # This is a placeholder - full implementation would serialize the paths

    return result


def load_evaluation_data(
    forecast_dir: Union[str, Path],
    observation_dir: Union[str, Path],
    lead_times: Optional[List[int]] = None,
) -> Dict[str, xr.DataArray]:
    """
    Load forecast and observation data for evaluation.

    Parameters:
        forecast_dir (str or Path): Directory containing forecast files.
        observation_dir (str or Path): Directory containing observation files.
        lead_times (list, optional): List of lead times to load (default: None).

    Returns:
        dict: Dictionary with 'forecasts' and 'observations' keys.
    """
    forecast_dir = Path(forecast_dir)
    observation_dir = Path(observation_dir)

    if not forecast_dir.exists():
        raise FileNotFoundError(f"Forecast directory not found: {forecast_dir}")
    if not observation_dir.exists():
        raise FileNotFoundError(f"Observation directory not found: {observation_dir}")

    # Load forecast files
    forecast_files = sorted(list(forecast_dir.glob("*.nc")))
    observation_files = sorted(list(observation_dir.glob("*.nc")))

    if len(forecast_files) == 0:
        raise ValueError(f"No forecast files found in {forecast_dir}")
    if len(observation_files) == 0:
        raise ValueError(f"No observation files found in {observation_dir}")

    # Load all forecast files
    forecast_datasets = [xr.open_dataset(f) for f in forecast_files]
    observation_datasets = [xr.open_dataset(f) for f in observation_files]

    # Combine along time dimension if multiple files
    if len(forecast_datasets) > 1:
        forecasts = xr.concat(forecast_datasets, dim="time")
    else:
        forecasts = forecast_datasets[0]

    if len(observation_datasets) > 1:
        observations = xr.concat(observation_datasets, dim="time")
    else:
        observations = observation_datasets[0]

    return {
        "forecasts": forecasts,
        "observations": observations,
    }

