"""
Preprocess Weather Analog Data

This module processes MERRA2 data by extracting specific variables (SLP and T2M)
for defined geographic regions and time periods, saving processed data into daily NetCDF files.
"""

import glob
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List
import xarray as xr

from wxcbench.weather_analog.config import (
    DEFAULT_LON_BOUNDS,
    DEFAULT_LAT_BOUNDS,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    MERRA2_VARIABLES,
    MERRA2_FILE_PATTERN,
    MERRA2_OUTPUT_PATTERN,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TIME_INDEX,
)


def process_single_file(
    input_file: str,
    output_file: str,
    variables: Optional[List[str]] = None,
    lon_bounds: Optional[Tuple[float, float]] = None,
    lat_bounds: Optional[Tuple[float, float]] = None,
    time_index: Optional[List[int]] = None,
) -> bool:
    """
    Process a single MERRA2 file and save the extracted data.

    Extracts specified variables (default: SLP and T2M) for a geographic region
    and saves to a new NetCDF file.

    Parameters:
        input_file (str): Path to input MERRA2 NetCDF file.
        output_file (str): Path to output NetCDF file.
        variables (list, optional): List of variable names to extract.
                                  Defaults to ['SLP', 'T2M'].
        lon_bounds (tuple, optional): Longitude bounds as (min, max) in degrees.
                                     Defaults to (-15, 0).
        lat_bounds (tuple, optional): Latitude bounds as (min, max) in degrees.
                                     Defaults to (42, 58).
        time_index (list, optional): List of time indices to extract.
                                    Defaults to [0] (first time step).

    Returns:
        bool: True if processing succeeded, False otherwise.

    Example:
        >>> success = process_single_file(
        ...     input_file='MERRA2.20190101.SUB.nc',
        ...     output_file='MERRA2_SLP_T2M_20190101.nc',
        ...     lon_bounds=(-15, 0),
        ...     lat_bounds=(42, 58)
        ... )
    """
    if variables is None:
        variables = MERRA2_VARIABLES

    if lon_bounds is None:
        lon_bounds = DEFAULT_LON_BOUNDS

    if lat_bounds is None:
        lat_bounds = DEFAULT_LAT_BOUNDS

    if time_index is None:
        time_index = DEFAULT_TIME_INDEX

    try:
        # Open dataset
        with xr.open_dataset(input_file) as ds:
            # Check if variables exist
            missing_vars = [var for var in variables if var not in ds.data_vars]
            if missing_vars:
                print(f"Warning: Variables not found in dataset: {missing_vars}")

            # Select required variables and region
            ds_selected = (
                ds[variables]
                .sel(lon=slice(*lon_bounds), lat=slice(*lat_bounds))
                .isel(time=time_index)
            )

            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save processed data
            ds_selected.to_netcdf(output_file)
            print(f"Processed {input_file} -> {output_file}")

        return True

    except Exception as e:
        print(f"Failed to process {input_file}: {e}")
        return False


def preprocess_weather_analog(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    input_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    lon_bounds: Optional[Tuple[float, float]] = None,
    lat_bounds: Optional[Tuple[float, float]] = None,
    variables: Optional[List[str]] = None,
    skip_existing: bool = True,
) -> List[str]:
    """
    Main processing function for weather analog data preprocessing.

    Processes MERRA2 data files for a specified time period, extracting
    selected variables for a geographic region and saving daily NetCDF files.

    Parameters:
        start_date (datetime, optional): Start date for processing.
                                        Defaults to 2019-01-01.
        end_date (datetime, optional): End date for processing.
                                      Defaults to 2021-12-31.
        input_dir (str, optional): Directory containing MERRA2 input files.
                                  Defaults to DEFAULT_INPUT_DIR.
        output_dir (str, optional): Directory to save processed output files.
                                   Defaults to DEFAULT_OUTPUT_DIR.
        lon_bounds (tuple, optional): Longitude bounds as (min, max) in degrees.
                                     Defaults to (-15, 0).
        lat_bounds (tuple, optional): Latitude bounds as (min, max) in degrees.
                                     Defaults to (42, 58).
        variables (list, optional): List of variable names to extract.
                                  Defaults to ['SLP', 'T2M'].
        skip_existing (bool, optional): Skip processing if output file exists.
                                       Defaults to True.

    Returns:
        list: List of paths to successfully processed output files.

    Example:
        >>> from datetime import datetime
        >>> processed_files = preprocess_weather_analog(
        ...     start_date=datetime(2019, 1, 1),
        ...     end_date=datetime(2019, 12, 31),
        ...     input_dir='./MERRA2_data',
        ...     output_dir='./MERRA2_processed'
        ... )
    """
    # Set defaults
    if start_date is None:
        start_date = DEFAULT_START_DATE

    if end_date is None:
        end_date = DEFAULT_END_DATE

    if input_dir is None:
        input_dir = DEFAULT_INPUT_DIR

    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    if lon_bounds is None:
        lon_bounds = DEFAULT_LON_BOUNDS

    if lat_bounds is None:
        lat_bounds = DEFAULT_LAT_BOUNDS

    if variables is None:
        variables = MERRA2_VARIABLES

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    processed_files = []
    current_date = start_date

    # Process each day in the date range
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")

        # Construct file paths
        try:
            # Search for input file using pattern
            input_pattern = os.path.join(input_dir, MERRA2_FILE_PATTERN.format(date=date_str))
            input_files = glob.glob(input_pattern)

            if not input_files:
                print(f"No input file found for date: {date_str}")
                current_date += timedelta(days=1)
                continue

            input_file = input_files[0]  # Use first matching file

        except Exception as e:
            print(f"Error finding input file for date {date_str}: {e}")
            current_date += timedelta(days=1)
            continue

        # Construct output file path
        output_file = os.path.join(output_dir, MERRA2_OUTPUT_PATTERN.format(date=date_str))

        # Skip if output exists and skip_existing is True
        if skip_existing and os.path.isfile(output_file):
            print(f"Output file already exists: {output_file}")
            processed_files.append(output_file)
            current_date += timedelta(days=1)
            continue

        # Check if input file exists
        if os.path.isfile(input_file):
            # Process the file
            success = process_single_file(
                input_file=input_file,
                output_file=output_file,
                variables=variables,
                lon_bounds=lon_bounds,
                lat_bounds=lat_bounds,
            )

            if success:
                processed_files.append(output_file)
        else:
            print(f"File not found: {input_file}")

        current_date += timedelta(days=1)

    print(f"\nProcessing complete. {len(processed_files)} files processed.")
    return processed_files

