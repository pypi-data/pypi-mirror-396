"""
PIREP Data Download Module

Downloads historical pilot report (PIREP) data from Iowa State University archive.
"""

import os
from pathlib import Path
from typing import List, Optional
import pandas as pd

from wxcbench.aviation_turbulence.config import PIREP_DOWNLOAD_BASE_URL, DEFAULT_PIREP_OUTPUT_DIR


def get_pirep_data(
    start_year: int = 2003,
    end_year: Optional[int] = None,
    output_dir: Optional[str] = None,
    combine_files: bool = True
) -> pd.DataFrame:
    """
    Download PIREP data from Iowa State University archive.
    
    This function downloads historical PIREP data (2003-present) and optionally
    combines all monthly files into a single CSV file.
    
    Parameters
    ----------
    start_year : int, optional
        Starting year for data download (default: 2003)
    end_year : int, optional
        Ending year for data download. If None, downloads up to current year (default: None)
    output_dir : str, optional
        Directory to save downloaded files. If None, uses default directory (default: None)
    combine_files : bool, optional
        If True, combines all monthly files into a single 'all_pireps.csv' file (default: True)
    
    Returns
    -------
    pd.DataFrame
        Combined DataFrame containing all PIREP data if combine_files=True,
        otherwise returns empty DataFrame
        
    Examples
    --------
    >>> import wxcbench.aviation_turbulence as wab
    >>> df = wab.get_pirep_data(start_year=2020, end_year=2023)
    >>> print(df.head())
    """
    import datetime
    
    # Set default output directory
    if output_dir is None:
        output_dir = DEFAULT_PIREP_OUTPUT_DIR
    
    # Set end_year to current year if not provided
    if end_year is None:
        end_year = datetime.datetime.now().year
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Create dictionary with months and corresponding days
    month_days = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    # Generate list of URLs for monthly downloads
    file_list = []
    for year in range(start_year, end_year + 1):
        for month in month_days.keys():
            start_month = month
            end_month = month
            day_1 = 1
            day_2 = month_days[month]
            
            # Handle leap years
            if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                day_2 = 29
            
            url = (
                f"{PIREP_DOWNLOAD_BASE_URL}?"
                f"year1={year}&month1={start_month}&day1={day_1}&hour1=0&minute1=0&"
                f"year2={year}&month2={end_month}&day2={day_2}&hour2=23&minute2=59&fmt=csv"
            )
            file_list.append(url)
    
    # Download and process each file
    for url in file_list:
        try:
            # Read CSV with specific columns
            df = pd.read_csv(
                url,
                usecols=['VALID', 'REPORT', 'TURBULENCE', 'LAT', 'LON'],
                dtype=str
            )
            
            # Remove duplicate reports
            df = df.drop_duplicates()
            
            # Drop NA values
            df = df.dropna()
            
            # Drop rows with 'None' values for latitude and longitude
            df = df.mask(df.eq('None')).dropna(subset=['LAT', 'LON'])
            
            # Save individual monthly file
            filename = url.split("?")[-1] + ".csv"
            output_file = output_path / filename
            df.to_csv(output_file, index=False)
            print(f"Downloaded {filename}")
            
        except Exception as e:
            print(f"Warning: {url} could not be read - {str(e)}")
            continue
    
    print("Finished downloading PIREP data.")
    
    # Combine all files if requested
    if combine_files:
        import glob
        pirep_files = glob.glob(str(output_path / "*.csv"))
        
        # Filter out the combined file if it exists
        combined_file = output_path / "all_pireps.csv"
        pirep_files = [f for f in pirep_files if f != str(combined_file)]
        
        if pirep_files:
            df_all = pd.concat(map(pd.read_csv, pirep_files), ignore_index=True)
            combined_file_path = output_path / "all_pireps.csv"
            df_all.to_csv(combined_file_path, index=False)
            print(f"Combined all files into {combined_file_path}")
            return df_all
    
    return pd.DataFrame()

