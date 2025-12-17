"""
Make Training Data Module

Extracts MERRA-2 profiles matching turbulence detections from PIREPs
to create training data for deep learning models.
"""

import numpy as np
import netCDF4 as nc
from pathlib import Path
from typing import List, Optional

from wxcbench.aviation_turbulence.config import (
    FLIGHT_LEVELS,
    DEFAULT_GRIDDED_DATA_DIR,
    DEFAULT_TRAINING_DATA_DIR
)


def create_training_data(
    turbulence_dir: Optional[str] = None,
    merra2_dir: Optional[str] = None,
    years: Optional[List[int]] = None,
    levels: Optional[List[str]] = None,
    output_dir: Optional[str] = None
) -> None:
    """
    Create training data by extracting MERRA-2 profiles matching turbulence detections.
    
    This function extracts MERRA-2 weather profiles at locations where turbulence
    was detected from PIREPs, creating training data files for deep learning models.
    
    Parameters
    ----------
    turbulence_dir : str, optional
        Directory containing the gridded turbulence files.
        If None, uses default from config (default: None)
    merra2_dir : str, optional
        Directory containing MERRA-2 data files (default: None)
    years : List[int], optional
        Years to process. If None, uses [2021, 2022] (default: None)
    levels : List[str], optional
        Flight levels to process. If None, uses ['low', 'med', 'high'] (default: None)
    output_dir : str, optional
        Directory to save training data files. If None, uses default from config (default: None)
        
    Examples
    --------
    >>> import wxcbench.aviation_turbulence as wab
    >>> wab.create_training_data(
    ...     turbulence_dir='./gridded_data',
    ...     merra2_dir='./MERRA2_2021-2022_1000hPa-100hPa',
    ...     years=[2021, 2022]
    ... )
    """
    # Use defaults if not provided
    if turbulence_dir is None:
        turbulence_dir = DEFAULT_GRIDDED_DATA_DIR
    if output_dir is None:
        output_dir = DEFAULT_TRAINING_DATA_DIR
    if years is None:
        years = [2021, 2022]
    if levels is None:
        levels = FLIGHT_LEVELS
    
    if merra2_dir is None:
        raise ValueError("merra2_dir must be provided")
    
    # Create output directory
    sdir = Path(output_dir)
    sdir.mkdir(parents=True, exist_ok=True)
    
    tdir = Path(turbulence_dir)
    mdir = Path(merra2_dir)
    
    # Create indices that match the MERRA-2 grid
    yinds = np.arange(0, 361, dtype='int')
    xinds = np.arange(0, 576, dtype='int')
    xg, yg = np.meshgrid(xinds, yinds)
    
    # Loop over the levels
    for level in levels:
        # Dictionary to hold the data for writing
        data = {
            'TURB': [],
            'OMEGA': [],
            'RH': [],
            'T': [],
            'U': [],
            'V': [],
            'H': [],
            'PL': [],
            'PHIS': []
        }
        
        # Loop over the years
        for year in years:
            # Open the Turbulence file
            tfn = nc.Dataset(str(tdir / f'{year}_{level}_fl.nc'))
            dates = tfn.variables['Dates'][:]
            turbulence = tfn.variables['Turbulence'][:]
            tfn.close()
            
            # Loop over the dates
            mdate = '00000000'
            mfn1 = None
            mfn2 = None
            
            for i, d in enumerate(dates):
                # Decode date if it's bytes
                if isinstance(d, bytes):
                    d = d.decode('utf-8')
                
                # Check if currently open MERRA-2 file is correct
                if d != mdate:
                    # Close previous files
                    try:
                        if mfn1:
                            mfn1.close()
                        if mfn2:
                            mfn2.close()
                    except:
                        pass
                    
                    # Open matching MERRA-2 file
                    try:
                        mfn1 = nc.Dataset(
                            str(mdir / 'U_V_T_RH_OMEGA' / 
                                f'MERRA2_400.inst3_3d_asm_Nv.{d}.SUB.nc')
                        )
                        mfn2 = nc.Dataset(
                            str(mdir / 'H_PL_PHIS' / 
                                f'MERRA2_400.inst3_3d_asm_Nv.{d}.SUB.nc')
                        )
                        mdate = d
                    except Exception as err:
                        try:
                            mfn1 = nc.Dataset(
                                str(mdir / 'U_V_T_RH_OMEGA' / 
                                    f'MERRA2_401.inst3_3d_asm_Nv.{d}.SUB.nc')
                            )
                            mfn2 = nc.Dataset(
                                str(mdir / 'H_PL_PHIS' / 
                                    f'MERRA2_401.inst3_3d_asm_Nv.{d}.SUB.nc')
                            )
                            mdate = d
                        except:
                            print(f"Error opening MERRA-2 files for date {d}: {err}")
                            continue
                
                # Extract points that have turbulence (and their indices)
                mask = turbulence[i, :, :] != 2
                turb = turbulence[i, :, :][mask]
                xinds_mask = xg[mask]
                yinds_mask = yg[mask]
                
                # Loop over just those points
                for xind, yind, t in zip(xinds_mask, yinds_mask, turb):
                    # Store the turbulence data
                    data['TURB'].append(t)
                    
                    # Extract the MERRA-2 weather profile
                    for v in ['OMEGA', 'RH', 'T', 'U', 'V']:
                        data[v].append(
                            np.squeeze(mfn1.variables[v][0, :, int(yind), int(xind)])
                        )
                    
                    for v in ['H', 'PL']:
                        data[v].append(
                            np.squeeze(mfn2.variables[v][0, :, int(yind), int(xind)])
                        )
                    
                    data['PHIS'].append(
                        np.squeeze(mfn2.variables['PHIS'][0, int(yind), int(xind)])
                    )
            
            # Close any MERRA-2 files that remain open
            try:
                if mfn1:
                    mfn1.close()
                if mfn2:
                    mfn2.close()
            except:
                pass
        
        # Save to output file
        out = nc.Dataset(str(sdir / f'training_data_{level}_fl.nc'), 'w')
        out.description = (
            'Training data for the turbulence prediction benchmark model.\n'
            'Weather data are MERRA 2 profiles at 18Z.'
        )
        
        # Create the dimensions
        s_dim = out.createDimension('samples', len(data['TURB']))
        z_dim = out.createDimension('z', 34)
        
        # Create variables
        turb_var = out.createVariable('TURBULENCE', 'float32', ('samples',))
        turb_var.long_name = 'Turbulence Prediction (training labels, 1=turbulence, 0=none)'
        turb_var[:] = np.array(data['TURB'])
        
        # Temperature
        t_var = out.createVariable('T', 'float32', ('samples', 'z'))
        t_var.long_name = 'MERRA 2 Temperature Profile'
        t_var.units = 'K'
        t_var.fill_value = 1e+15
        t_var[:] = np.array(data['T'], dtype=np.float32)
        
        # U Wind
        u_var = out.createVariable('U', 'float32', ('samples', 'z'))
        u_var.long_name = 'MERRA 2 U Wind Profile'
        u_var.units = 'm s-1'
        u_var.fill_value = 1e+15
        u_var[:] = np.array(data['U'], dtype=np.float32)
        
        # V Wind
        v_var = out.createVariable('V', 'float32', ('samples', 'z'))
        v_var.long_name = 'MERRA 2 V Wind Profile'
        v_var.units = 'm s-1'
        v_var.fill_value = 1e+15
        v_var[:] = np.array(data['V'], dtype=np.float32)
        
        # Vertical Velocity
        o_var = out.createVariable('OMEGA', 'float32', ('samples', 'z'))
        o_var.long_name = 'MERRA 2 Vertical Velocity Profile'
        o_var.units = 'Pa s-1'
        o_var.fill_value = 1e+15
        o_var[:] = np.array(data['OMEGA'], dtype=np.float32)
        
        # Relative Humidity
        q_var = out.createVariable('RH', 'float32', ('samples', 'z'))
        q_var.long_name = 'MERRA 2 Relative Humidity Profile'
        q_var.units = '1'
        q_var.fill_value = 1e+15
        q_var[:] = np.array(data['RH'], dtype=np.float32)
        
        # Height
        h_var = out.createVariable('H', 'float32', ('samples', 'z'))
        h_var.long_name = 'MERRA 2 Height Levels'
        h_var.units = 'm'
        h_var.fill_value = 1e+15
        h_var[:] = np.array(data['H'], dtype=np.float32)
        
        # Surface Geopotential
        s_var = out.createVariable('PHIS', 'float32', ('samples',))
        s_var.long_name = 'MERRA 2 Surface Geopotential'
        s_var.units = 'm2 s-2'
        s_var.fill_value = 1e+15
        s_var[:] = np.array(data['PHIS'], dtype=np.float32)
        
        # Pressure
        p_var = out.createVariable('PL', 'float32', ('samples', 'z'))
        p_var.long_name = 'MERRA 2 Pressure at mid-level'
        p_var.units = 'Pa'
        p_var.fill_value = 1e+15
        p_var[:] = np.array(data['PL'], dtype=np.float32)
        
        # Close the output file
        out.close()
        
        print(f"Created training data for {level} flight level with {len(data['TURB'])} samples")

