"""
Compute Momentum Flux from ERA5 Data

This module calculates resolved momentum fluxes using Helmholtz decomposition
to separate rotational and divergent components for nonlocal parameterization.
"""

import calendar
from pathlib import Path
from typing import Optional
import numpy as np
from netCDF4 import Dataset
from windspharm.standard import VectorWind

from wxcbench.nonlocal_parameterization.config import (
    HELMHOLTZ_TRUNCATION,
    GRAVITY_CONSTANT,
    DEFAULT_ERA5_DATA_DIR,
    DEFAULT_MOMENTUM_FLUX_DIR,
)


def get_days_in_month(year: int, month: int) -> int:
    """Calculate the number of days in a given month and year."""
    return calendar.monthrange(year, month)[1]


def compute_momentum_flux_from_era5(
    year: int,
    month: int,
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
    era5_data_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    truncation: Optional[int] = None,
    log_file: Optional[str] = None,
) -> list:
    """
    Calculate resolved momentum fluxes from ERA5 data using Helmholtz decomposition.

    Computes zonal (uw) and meridional (vw) momentum fluxes by separating the wind
    field into rotational and divergent components using spherical harmonic decomposition.

    Parameters:
        year (int): The year.
        month (int): The month (1-12).
        start_day (int, optional): The start day of the month (1-31). If None, uses 1.
        end_day (int, optional): The end day of the month (1-31). If None, uses last day of month.
        era5_data_dir (str, optional): Directory containing ERA5 model level data.
                                      Defaults to DEFAULT_ERA5_DATA_DIR.
        output_dir (str, optional): Directory to save computed momentum flux files.
                                   Defaults to DEFAULT_MOMENTUM_FLUX_DIR.
        truncation (int, optional): Truncation wavenumber for scale separation (default: T21).
        log_file (str, optional): Path to log file. If None, prints to console.

    Returns:
        list: List of paths to output NetCDF files containing computed momentum fluxes.
    """
    if truncation is None:
        truncation = HELMHOLTZ_TRUNCATION

    if era5_data_dir is None:
        era5_data_dir = DEFAULT_ERA5_DATA_DIR

    if output_dir is None:
        output_dir = DEFAULT_MOMENTUM_FLUX_DIR

    era5_path = Path(era5_data_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Calculate number of days in the month
    ndays = get_days_in_month(year, month)

    # Set default day range if not specified
    if start_day is None:
        start_day = 1
    if end_day is None:
        end_day = ndays

    # Month names for output files
    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    month_name = month_names[month]

    output_files = []
    frq = 24  # Hourly data

    # Logging function
    def write_log(*args):
        """Write log messages to file and/or console."""
        message = ' '.join([str(a) for a in args])
        if log_file:
            with open(log_file, "a") as f:
                f.write(message + '\n')
        print(message)

    # Process each day
    for day in range(start_day, end_day + 1):
        date_code = f"{year}{month:02d}{day:02d}"

        # Input file paths
        u_file = era5_path / f"U{date_code}_ml.nc"
        v_file = era5_path / f"V{date_code}_ml.nc"
        w_file = era5_path / f"W{date_code}_ml.nc"

        # Check if input files exist
        if not all(f.exists() for f in [u_file, v_file, w_file]):
            write_log(f"Warning: Missing input files for {year}-{month:02d}-{day:02d}")
            continue

        # Output filename
        outfile = output_path / f"helmholtz_fluxes_hourly_era5_{day}{month_name}{year}.nc"

        write_log(f"Processing {year}-{month:02d}-{day:02d}...")

        # Load ERA5 data
        nc1 = Dataset(str(u_file), "r")
        nc2 = Dataset(str(v_file), "r")
        nc3 = Dataset(str(w_file), "r")

        # Get dimensions (assume same for all files)
        if day == start_day:
            lon = nc1.variables['longitude'][:]
            lat = nc1.variables['latitude'][:]
            nx = len(lon)
            ny = len(lat)
            nz = 137

        ucomp = nc1.variables['u']
        vcomp = nc2.variables['v']
        wcomp = nc3.variables['w']

        # Create or open output file
        file_exists = outfile.exists()
        if not file_exists:
            out = Dataset(str(outfile), "w", format="NETCDF4")
            write_log('Creating new output file...')

            # Define dimensions
            out.createDimension("time", frq)
            out.createDimension("level", nz)
            out.createDimension("lat", ny)
            out.createDimension("lon", nx)

            # Create dimension variables
            times = out.createVariable("time", "i4", ("time",))
            levels = out.createVariable("level", "f4", ("level",))
            levels.units = 'hPa'
            lats = out.createVariable("lat", "f4", ("lat",))
            lats.units = 'degrees_north'
            lons = out.createVariable("lon", "f4", ("lon",))
            lons.units = 'degrees_east'

            # Create data variables
            o_uw = out.createVariable("uw", "f4", ("time", "level", "lat", "lon"))
            o_uw.units = 'Pa'
            o_uw.long_name = 'uw/g: Zonal flux of vertical momentum'

            o_vw = out.createVariable("vw", "f4", ("time", "level", "lat", "lon"))
            o_vw.units = 'Pa'
            o_vw.long_name = 'vw/g: Meridional flux of vertical momentum'

            # Set dimension variables
            times[:] = np.arange(0, frq, 1)
            # Note: levels would need to be loaded from model levels file
            # For now, use indices 0 to nz-1
            levels[:] = np.arange(1, nz + 1)
            lats[:] = lat[:]
            lons[:] = lon[:]
        else:
            out = Dataset(str(outfile), "a", format="NETCDF4")
            write_log('Appending to existing file...')
            o_uw = out.variables['uw']
            o_vw = out.variables['vw']

        # Loop through each time step and level
        for ind in range(frq):
            write_log(f"Processing time step {ind}...")
            for iz in range(nz):
                # Extract wind fields at this time and level
                u = ucomp[ind, iz, :, :]
                v = vcomp[ind, iz, :, :]
                w = wcomp[ind, iz, :, :]

                # Compute wind vector decomposition
                fld = VectorWind(u, v, legfunc='computed')
                udiv, vdiv = fld.irrotationalcomponent()

                # Truncate to T21 (or specified truncation)
                udiv_trunc = fld.truncate(udiv, truncation=truncation)
                vdiv_trunc = fld.truncate(vdiv, truncation=truncation)

                # Compute eddy flux
                wmean = np.mean(w, axis=0)
                w_eddy = w - wmean[np.newaxis, :]

                # Compute momentum fluxes (high-pass filtered divergent component)
                uw = (udiv - udiv_trunc) * w_eddy
                vw = (vdiv - vdiv_trunc) * w_eddy

                # Write results (normalized by gravity)
                o_uw[ind, iz, :, :] = uw / GRAVITY_CONSTANT
                o_vw[ind, iz, :, :] = vw / GRAVITY_CONSTANT

        # Close files
        nc1.close()
        nc2.close()
        nc3.close()
        out.close()

        output_files.append(str(outfile))
        write_log('Done processing day.')

    return output_files

