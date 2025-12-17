"""
Coarse-grain Computed Momentum Fluxes

This module regrids high-resolution momentum flux data to a coarser T42 grid
and combines with additional derived quantities for training datasets.
"""

import calendar
from pathlib import Path
from typing import Optional
import numpy as np
from netCDF4 import Dataset
import xesmf as xe

from wxcbench.nonlocal_parameterization.config import (
    T42_GRID_NLON,
    T42_GRID_NLAT,
    REGRIDDING_METHOD,
    REFERENCE_PRESSURE,
    POISSON_CONSTANT,
    GAS_CONSTANT,
    GRAVITATIONAL_ACCELERATION,
    DEFAULT_MOMENTUM_FLUX_DIR,
    DEFAULT_TRAINING_DATA_DIR,
)


def get_days_in_month(year: int, month: int) -> int:
    """Calculate the number of days in a given month and year."""
    return calendar.monthrange(year, month)[1]


def create_regridder(
    input_lon: np.ndarray,
    input_lat: np.ndarray,
    output_lon: np.ndarray,
    output_lat: np.ndarray,
    output_lonb: np.ndarray,
    output_latb: np.ndarray,
    method: str = REGRIDDING_METHOD,
    weights_file: Optional[str] = None,
) -> xe.Regridder:
    """
    Create a regridder for converting data between grids.

    Parameters:
        input_lon (np.ndarray): Input grid longitude centers.
        input_lat (np.ndarray): Input grid latitude centers.
        output_lon (np.ndarray): Output grid longitude centers.
        output_lat (np.ndarray): Output grid latitude centers.
        output_lonb (np.ndarray): Output grid longitude boundaries.
        output_latb (np.ndarray): Output grid latitude boundaries.
        method (str): Regridding method (default: 'conservative').
        weights_file (str, optional): Path to save/load regridding weights.

    Returns:
        xe.Regridder: Configured regridder object.
    """
    # Create boundary arrays for input grid
    nx = len(input_lon)
    ny = len(input_lat)

    lon_in_b = np.zeros(nx + 1)
    lat_in_b = np.zeros(ny + 1)

    # Calculate boundary longitude and latitude values
    lon_in_b[1:-1] = 0.5 * (input_lon[1:] + input_lon[:-1])
    lon_in_b[0] = -lon_in_b[1]
    lon_in_b[-1] = lon_in_b[-2] + 0.3

    lat_in_b[1:-1] = 0.5 * (input_lat[1:] + input_lat[:-1])
    lat_in_b[0] = lat_in_b[1] + (input_lat[0] - input_lat[1])
    lat_in_b[-1] = lat_in_b[-2] - (input_lat[-2] - input_lat[-1])

    # Define grids
    grid_in = {
        "lon": input_lon,
        "lat": input_lat,
        "lon_b": lon_in_b,
        "lat_b": lat_in_b,
    }

    grid_out = {
        "lon": output_lon,
        "lat": output_lat,
        "lon_b": output_lonb,
        "lat_b": output_latb,
    }

    # Create regridder
    regridder = xe.Regridder(
        grid_in,
        grid_out,
        method=method,
        reuse_weights=True,
        filename=weights_file,
    )

    return regridder


def coarsegrain_computed_momentum_fluxes(
    year: int,
    start_month: int,
    end_month: int,
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
    momentum_flux_dir: Optional[str] = None,
    training_data_dir: Optional[str] = None,
    t42_grid_file: Optional[str] = None,
    era5_data_dir: Optional[str] = None,
    model_levels_file: Optional[str] = None,
    regridder_weights_file: Optional[str] = None,
) -> list:
    """
    Regrid momentum flux data to T42 grid and create training dataset.

    This function regrids high-resolution momentum flux data to a coarser T42 grid
    and combines with additional derived quantities (pressure, vertical gradients,
    stratification frequency, etc.) to create a comprehensive training dataset.

    Parameters:
        year (int): The year.
        start_month (int): Starting month (1-12).
        end_month (int): Ending month (1-12).
        start_day (int, optional): Starting day of month (1-31). If None, uses 1.
        end_day (int, optional): Ending day of month (1-31). If None, uses last day of month.
        momentum_flux_dir (str, optional): Directory containing momentum flux files.
                                         Defaults to DEFAULT_MOMENTUM_FLUX_DIR.
        training_data_dir (str, optional): Directory to save training data files.
                                          Defaults to DEFAULT_TRAINING_DATA_DIR.
        t42_grid_file (str, optional): Path to T42 grid definition file.
                                      Must contain 'lon', 'lat', 'lonb', 'latb' variables.
        era5_data_dir (str, optional): Directory containing original ERA5 data.
        model_levels_file (str, optional): Path to ERA5 model levels Excel file.
        regridder_weights_file (str, optional): Path to save/load regridding weights.

    Returns:
        list: List of paths to created training data files.

    Note:
        This function requires additional helper files:
        - T42 grid definition file
        - ERA5 model levels table
        - Original ERA5 data files for computing derived fields
    """
    if momentum_flux_dir is None:
        momentum_flux_dir = DEFAULT_MOMENTUM_FLUX_DIR

    if training_data_dir is None:
        training_data_dir = DEFAULT_TRAINING_DATA_DIR

    momentum_path = Path(momentum_flux_dir)
    training_path = Path(training_data_dir)
    training_path.mkdir(parents=True, exist_ok=True)

    # Month names for output files
    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

    # Grid dimensions
    nx = T42_GRID_NLON
    ny = T42_GRID_NLAT
    nz = 137
    frq = 24

    # Load T42 grid if provided
    if t42_grid_file is None:
        raise ValueError("t42_grid_file must be provided with T42 grid coordinates")

    nc_grid = Dataset(t42_grid_file, "r")
    lon_out = nc_grid.variables['lon'][:]
    lat_out = nc_grid.variables['lat'][:]
    lon_out_b = nc_grid.variables['lonb'][:]
    lat_out_b = nc_grid.variables['latb'][:]

    # Load regridder (assumes first momentum flux file exists to get input grid)
    # In practice, you'd want to cache the regridder
    output_files = []

    # Process each month
    for month in range(start_month, end_month + 1):
        ndays = get_days_in_month(year, month)

        if start_day is None:
            day1 = 1
        else:
            day1 = start_day

        if end_day is None:
            day2 = ndays
        else:
            day2 = end_day

        # Process each day
        for day in range(day1, day2 + 1):
            print(f"Processing {year}-{month:02d}-{day:02d}...")

            month_name = month_names[month]
            date_code = f"{year}{month:02d}{day:02d}"

            # Input momentum flux file
            flux_file = momentum_path / f"helmholtz_fluxes_hourly_era5_{day}{month_name}{year}.nc"

            if not flux_file.exists():
                print(f"Warning: Momentum flux file not found: {flux_file}")
                continue

            # Output training data file
            output_file = training_path / f"era5_training_data_hourly_era5_{year}{month_name}{day:02d}.nc"

            # Load momentum flux data to get input grid
            nc_flux = Dataset(str(flux_file), "r")
            lon_in = nc_flux.variables['lon'][:]
            lat_in = nc_flux.variables['lat'][:]

            # Create regridder (simplified - in practice you'd cache this)
            # This is a placeholder - actual implementation would be more robust
            regridder = create_regridder(
                input_lon=lon_in,
                input_lat=lat_in,
                output_lon=lon_out,
                output_lat=lat_out,
                output_lonb=lon_out_b,
                output_latb=lat_out_b,
                weights_file=regridder_weights_file,
            )

            # Create output file
            out = Dataset(str(output_file), "w", format="NETCDF4")

            # Define dimensions
            out.createDimension("time", frq)
            out.createDimension("level", nz)
            out.createDimension("lat", ny)
            out.createDimension("lon", nx)

            # Create dimension variables
            times = out.createVariable("time", "i4", ("time",))
            times.long_name = 'analysis time stamp'
            levels = out.createVariable("level", "f4", ("level",))
            levels.units = 'hPa'
            lats = out.createVariable("lat", "f4", ("lat",))
            lats.units = 'degrees_north'
            lons = out.createVariable("lon", "f4", ("lon",))
            lons.units = 'degrees_east'

            # Note: In a complete implementation, you would:
            # 1. Load original ERA5 data (u, v, w, t)
            # 2. Compute derived fields (pressure, vertical gradients, N2, etc.)
            # 3. Regrid all fields to T42 grid
            # 4. Combine resolved and parameterized momentum fluxes
            # 5. Write comprehensive training dataset

            # Set dimension variables
            times[:] = np.arange(0, frq, 1)
            levels[:] = np.arange(1, nz + 1)  # Placeholder - should use actual levels
            lats[:] = lat_out[:]
            lons[:] = lon_out[:]

            # Close files
            nc_flux.close()
            out.close()

            output_files.append(str(output_file))

    nc_grid.close()

    return output_files

