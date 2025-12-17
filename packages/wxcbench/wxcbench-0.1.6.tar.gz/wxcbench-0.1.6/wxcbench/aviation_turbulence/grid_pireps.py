"""
Grid PIREPs Module

Takes downloaded PIREPs, filters them, and bins them by day onto the MERRA-2 grid.
Converts data to binary classification indicating whether moderate or greater (MOG)
turbulence is present.
"""

import numpy as np
import pandas as pd
import netCDF4 as nc
from pathlib import Path
from typing import List, Optional

from wxcbench.aviation_turbulence.config import (
    MERRA2_GRID,
    TURBULENCE_THRESHOLD,
    NO_DATA_VALUE,
    DEFAULT_GRIDDED_DATA_DIR
)


def find_min_idx(x: np.ndarray) -> tuple:
    """
    Helper function for finding minimum of 2D array.
    
    Returns the row and column indices of the minimum value.
    
    Parameters
    ----------
    x : np.ndarray
        2D array
        
    Returns
    -------
    tuple
        (row_index, column_index) of minimum value
    """
    k = x.argmin()
    ncol = x.shape[1]
    return int(k // ncol), int(k % ncol)


def grid_pireps(
    pirep_files: List[str],
    output_dir: Optional[str] = None,
    threshold: float = None,
    nodata: int = None
) -> None:
    """
    Grid PIREP data onto MERRA-2 grid and create binary turbulence classification.
    
    This function takes downloaded PIREP files, filters them, and bins them by day
    onto the MERRA-2 grid. The data is converted to a binary classification indicating
    whether moderate or greater (MOG) turbulence is present.
    
    Parameters
    ----------
    pirep_files : List[str]
        List of paths to PIREP CSV files (e.g., ['updated_CSVs/low_fl.csv', ...])
    output_dir : str, optional
        Directory to save gridded data. If None, uses default directory (default: None)
    threshold : float, optional
        Fraction of reports that must be MOG before cell is classified as turbulence.
        If None, uses default from config (default: None)
    nodata : int, optional
        No data value. If None, uses default from config (default: None)
        
    Examples
    --------
    >>> import wxcbench.aviation_turbulence as wab
    >>> wab.grid_pireps(['updated_CSVs/low_fl.csv', 'updated_CSVs/med_fl.csv'])
    """
    # Use defaults if not provided
    if output_dir is None:
        output_dir = DEFAULT_GRIDDED_DATA_DIR
    if threshold is None:
        threshold = TURBULENCE_THRESHOLD
    if nodata is None:
        nodata = NO_DATA_VALUE
    
    # Create output directory
    sdir = Path(output_dir)
    sdir.mkdir(parents=True, exist_ok=True)
    
    # Build the MERRA-2 grid
    dx = MERRA2_GRID["dx"]
    dy = MERRA2_GRID["dy"]
    nx = MERRA2_GRID["nx"]
    ny = MERRA2_GRID["ny"]
    
    x = np.arange(MERRA2_GRID["x_start"], MERRA2_GRID["x_start"] + dx * nx, dx)
    y = np.arange(MERRA2_GRID["y_start"], MERRA2_GRID["y_start"] + dy * ny, dy)
    xg, yg = np.meshgrid(x, y)
    
    # Loop over the input files
    for fpath in pirep_files:
        # Open the PIREPS file and sort by date
        pdf = pd.read_csv(fpath)
        pdf = pdf.sort_values(by='VALID')
        
        # Initialize arrays for counting reports and storing turbulence value
        turbulence = np.zeros((y.size, x.size))  # MOG turbulence
        counts = np.zeros((y.size, x.size))  # Report count
        binaries = []  # List to hold turbulence occurrence arrays
        dates = []  # List to hold the dates
        
        # Loop over each row
        date = str(pdf.VALID.iloc[0])[:8]
        year = date[:4]
        
        for index, row in pdf.iterrows():
            # Grab the new date
            new_date = str(row.VALID)[:8]
            new_year = new_date[:4]
            
            # Skip if not 2023 (adjust as needed)
            if new_year != '2023':
                date = new_date
                year = new_year
                continue
            
            if new_date != date:
                # Append old date to date list
                dates.append(date)
                
                # Compute turbulence occurrence
                dummy = turbulence / counts
                dummy[dummy >= threshold] = 1  # yes turbulence
                dummy[dummy < 1] = 0  # no turbulence
                dummy[counts == 0] = nodata  # no data
                binaries.append(dummy)
                
                # Reset values
                turbulence = np.zeros((y.size, x.size))
                counts = np.zeros((y.size, x.size))
                date = new_date
            
            if new_year != year:
                # Write out the data
                out = nc.Dataset(
                    f"{sdir}/{year}_{Path(fpath).stem.replace('csv', 'nc')}",
                    "w"
                )
                out.description = (
                    'Daily moderate or greater turbulence presence from PIREPS '
                    'reports gridded onto the MERRA 2 grid.'
                )
                
                # Data dimensions
                out.createDimension('Time', len(binaries))
                out.createDimension('Y', xg.shape[0])
                out.createDimension('X', xg.shape[1])
                out.createDimension('StringLength', 8)
                
                # Variables
                turb_var = out.createVariable('Turbulence', 'uint8', ('Time', 'Y', 'X'))
                turb_var.long_name = 'Turbulence Presence (1=Yes, 0=No)'
                turb_var.missing_data_value = str(nodata)
                
                date_var = out.createVariable('Dates', 'S8', ('Time',))
                date_var.long_name = 'Date of turbulence report (UTC)'
                
                lon_var = out.createVariable('Lons', 'f8', ('Y', 'X'))
                lon_var.long_name = 'Longitude (deg)'
                
                lat_var = out.createVariable('Lats', 'f8', ('Y', 'X'))
                lat_var.long_name = 'Latitude (deg)'
                
                # Save the data
                turb_var[:] = np.array(binaries)
                date_var[:] = np.array(dates)
                lon_var[:] = xg
                lat_var[:] = yg
                
                # Close the file
                out.close()
                
                # Reset variables
                print(year, new_year)
                year = new_year
                binaries = []
                dates = []
            
            # Assign grid point
            dist = (row.LON - xg) ** 2 + (row.LAT - yg) ** 2
            yind, xind = find_min_idx(dist)
            
            # Determine if report is moderate or greater
            if hasattr(row, 'Intensity') and row.Intensity >= 2:
                turbulence[yind, xind] += 1
            counts[yind, xind] += 1
        
        print(f"Processed {len(dates)} dates")
        print(f"First 10 dates: {dates[:10]}")
        
        # Write out the last year
        if binaries:
            out = nc.Dataset(
                f"{sdir}/{year}_{Path(fpath).stem.replace('csv', 'nc')}",
                "w"
            )
            out.description = (
                'Daily moderate or greater turbulence presence from PIREPS '
                'reports gridded onto the MERRA 2 grid.'
            )
            
            # Data dimensions
            out.createDimension('Time', len(binaries))
            out.createDimension('Y', xg.shape[0])
            out.createDimension('X', xg.shape[1])
            out.createDimension('StringLength', 8)
            
            # Variables
            turb_var = out.createVariable('Turbulence', 'uint8', ('Time', 'Y', 'X'))
            turb_var.long_name = 'Turbulence Presence (1=Yes, 0=No)'
            turb_var.missing_data_value = str(nodata)
            
            date_var = out.createVariable('Dates', 'S8', ('Time',))
            date_var.long_name = 'Date of turbulence report (UTC)'
            
            lon_var = out.createVariable('Lons', 'f8', ('Y', 'X'))
            lon_var.long_name = 'Longitude (deg)'
            
            lat_var = out.createVariable('Lats', 'f8', ('Y', 'X'))
            lat_var.long_name = 'Latitude (deg)'
            
            # Save the data
            turb_var[:] = np.array(binaries)
            date_var[:] = np.array(dates)
            lon_var[:] = xg
            lat_var[:] = yg
            
            # Close the file
            out.close()

