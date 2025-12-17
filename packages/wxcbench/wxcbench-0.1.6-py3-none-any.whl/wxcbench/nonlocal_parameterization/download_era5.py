"""
Download ERA5 Model Level Data

This module provides functionality to download ERA5 model level analysis fields
including temperature (T), zonal wind (U), meridional wind (V), and vertical velocity (W).
"""

import calendar
from pathlib import Path
from typing import Optional
import cdsapi

from wxcbench.nonlocal_parameterization.config import (
    ERA5_GRID_RESOLUTION,
    ERA5_LEVELS,
    ERA5_TIME_STEPS,
    ERA5_STREAM,
    ERA5_TYPE,
    ERA5_FORMAT,
    ERA5_PARAM_CODES,
    DEFAULT_ERA5_DATA_DIR,
)


def get_days_in_month(year: int, month: int) -> int:
    """
    Calculate the number of days in a given month and year, accounting for leap years.

    Parameters:
        year (int): The year.
        month (int): The month (1-12).

    Returns:
        int: The number of days in the month.
    """
    return calendar.monthrange(year, month)[1]


def download_era5_field(
    year: int,
    month: int,
    day: int,
    param: str,
    output_dir: Optional[str] = None,
    cds_client: Optional[cdsapi.Client] = None
) -> str:
    """
    Download ERA5 model level data for a specific field (T, U, V, or W).

    Parameters:
        year (int): The year.
        month (int): The month (1-12).
        day (int): The day of the month (1-31).
        param (str): The parameter code for the field to download.
                    Options: '130' (T), '131' (U), '132' (V), '135' (W)
        output_dir (str, optional): Directory to save the output file.
                                   Defaults to DEFAULT_ERA5_DATA_DIR.
        cds_client (cdsapi.Client, optional): CDS API client. If None, creates a new one.

    Returns:
        str: Path to the downloaded file.
    """
    if output_dir is None:
        output_dir = DEFAULT_ERA5_DATA_DIR

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Format date strings
    date_str = f"{year}-{month:02d}-{day:02d}"
    date_code = f"{year}{month:02d}{day:02d}"

    # Determine field prefix based on parameter code
    field_map = {
        "130": "T",
        "131": "U",
        "132": "V",
        "135": "W",
    }
    field_prefix = field_map.get(param, "FIELD")

    # Output filename
    outfile = output_path / f"{field_prefix}{date_code}_ml.nc"

    # Initialize CDS API client if not provided
    if cds_client is None:
        cds_client = cdsapi.Client()

    # Download data
    print(f"Downloading {field_prefix} field for {date_str}...")
    cds_client.retrieve(
        "reanalysis-era5-complete",
        {
            "date": date_str,
            "levelist": ERA5_LEVELS,
            "levtype": "ml",
            "param": param,
            "stream": ERA5_STREAM,
            "time": ERA5_TIME_STEPS,
            "type": ERA5_TYPE,
            "grid": ERA5_GRID_RESOLUTION,
            "format": ERA5_FORMAT,
        },
        str(outfile),
    )

    return str(outfile)


def download_era5_modellevel_data(
    year: int,
    month: int,
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
    output_dir: Optional[str] = None,
    fields: Optional[list] = None,
) -> list:
    """
    Download ERA5 model level analysis fields for specified time period.

    Downloads temperature (T), zonal wind (U), meridional wind (V), and vertical velocity (W)
    for specified days. Defaults to all days in the month if start_day and end_day are not specified.

    Parameters:
        year (int): The year.
        month (int): The month (1-12).
        start_day (int, optional): The start day of the month (1-31). If None, uses 1.
        end_day (int, optional): The end day of the month (1-31). If None, uses last day of month.
        output_dir (str, optional): Directory to save the output files.
                                   Defaults to DEFAULT_ERA5_DATA_DIR.
        fields (list, optional): List of field names to download.
                                Options: ['T', 'U', 'V', 'W'] or parameter codes.
                                If None, downloads all fields (T, U, V, W).

    Returns:
        list: List of paths to downloaded files.
    """
    # Calculate number of days in the month
    ndays = get_days_in_month(year, month)

    # Set default day range if not specified
    if start_day is None:
        start_day = 1
    if end_day is None:
        end_day = ndays

    # Set default fields if not specified
    if fields is None:
        fields = ["T", "U", "V", "W"]

    # Map field names to parameter codes
    field_to_param = {
        "T": ERA5_PARAM_CODES["temperature"],
        "U": ERA5_PARAM_CODES["zonal_wind"],
        "V": ERA5_PARAM_CODES["meridional_wind"],
        "W": ERA5_PARAM_CODES["vertical_wind"],
    }

    downloaded_files = []
    cds_client = cdsapi.Client()

    # Loop over each day
    for day in range(start_day, end_day + 1):
        # Download each field
        for field in fields:
            # Get parameter code (accept both field names and codes)
            if field in field_to_param:
                param_code = field_to_param[field]
            elif field in ERA5_PARAM_CODES.values():
                param_code = field
            else:
                raise ValueError(f"Unknown field: {field}. Must be one of {list(field_to_param.keys())} or parameter codes.")

            try:
                file_path = download_era5_field(
                    year=year,
                    month=month,
                    day=day,
                    param=param_code,
                    output_dir=output_dir,
                    cds_client=cds_client,
                )
                downloaded_files.append(file_path)
            except Exception as e:
                print(f"Error downloading {field} field for {year}-{month:02d}-{day:02d}: {e}")
                continue

    return downloaded_files

