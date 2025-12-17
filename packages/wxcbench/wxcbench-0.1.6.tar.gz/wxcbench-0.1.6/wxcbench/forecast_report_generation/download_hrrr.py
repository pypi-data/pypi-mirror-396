"""
Download HRRR Module

Downloads HRRR (High-Resolution Rapid Refresh) weather data files
from NOAA's public S3 bucket.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import urllib.request as ureq

from wxcbench.forecast_report_generation.config import (
    HRRR_ARCHIVE_URL,
    HRRR_DATASET_TYPES,
    DEFAULT_HRRR_OUTPUT_DIR
)


def download_hrrr(
    start_date: str,
    end_date: str,
    forecast_hours: Optional[List[int]] = None,
    time_interval: int = 24,
    dataset_type: str = "nat",
    output_dir: Optional[str] = None
) -> None:
    """
    Download HRRR weather data files from NOAA's public dataset.
    
    Downloads HRRR grib2 files from NOAA's S3 bucket for a specified date range,
    forecast hours, and dataset type. Supports different forecast hours and dataset
    types (pressure, natural, surface).
    
    Parameters
    ----------
    start_date : str
        Start date for downloading HRRR data (format: "YYYYMMDD-HH")
        Example: "20180101-01"
    end_date : str
        End date for downloading HRRR data (format: "YYYYMMDD-HH")
        Example: "20180102-01"
    forecast_hours : List[int], optional
        Forecast hours to download (0 represents analysis files).
        If None, uses [0] (default: None)
    time_interval : int, optional
        Interval between downloads in hours (default: 24)
    dataset_type : str, optional
        HRRR dataset type. Options: "prs" (pressure), "nat" (natural), "sfc" (surface).
        Default: "nat"
    output_dir : str, optional
        Local directory to save downloaded HRRR files.
        If None, uses default from config (default: None)
        
    Examples
    --------
    >>> import wxcbench.forecast_report_generation as frg
    >>> frg.download_hrrr(
    ...     start_date="20180101-01",
    ...     end_date="20180102-01",
    ...     forecast_hours=[0],
    ...     dataset_type="nat"
    ... )
    """
    # Validate dataset type
    if dataset_type not in HRRR_DATASET_TYPES:
        raise ValueError(
            f"Invalid dataset_type '{dataset_type}'. "
            f"Must be one of: {HRRR_DATASET_TYPES}"
        )
    
    # Use defaults if not provided
    if forecast_hours is None:
        forecast_hours = [0]
    if output_dir is None:
        output_dir = DEFAULT_HRRR_OUTPUT_DIR
    
    # Create output directory if it doesn't exist
    save_path = Path(output_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Generate a list of dates within the specified range
    start_date_obj = datetime.strptime(start_date, "%Y%m%d-%H")
    end_date_obj = datetime.strptime(end_date, "%Y%m%d-%H")
    
    date_range = [
        start_date_obj + timedelta(hours=time_interval * i)
        for i in range(
            int(((end_date_obj - start_date_obj).total_seconds() / 3600) // time_interval)
        )
    ]
    
    # Download files for each date and forecast hour
    for current_date in date_range:
        for forecast_hour in forecast_hours:
            try:
                # Construct the file name and URL
                file_name = (
                    f"hrrr.t{current_date.strftime('%H')}z."
                    f"wrf{dataset_type}f{forecast_hour:02d}.grib2"
                )
                save_name = (
                    f"hrrr.{current_date.strftime('%Y%m%d')}."
                    f"t{current_date.strftime('%H')}z."
                    f"wrf{dataset_type}f{forecast_hour:02d}.grib2"
                )
                file_url = (
                    f"{HRRR_ARCHIVE_URL}/hrrr.{current_date.strftime('%Y%m%d')}/"
                    f"conus/{file_name}"
                )
                
                print(f"Downloading: {file_url}")
                ureq.urlretrieve(file_url, str(save_path / save_name))
                print(f"Saved: {save_name}")
                
            except Exception as e:
                print(f"Error: {save_name} file not found. Reason: {e}")
                continue
    
    print(f"HRRR download complete. Files saved to: {save_path}")

