"""
Configuration settings for nonlocal parameterization processing.
"""

# ERA5 download settings
ERA5_GRID_RESOLUTION = "0.3/0.3"  # degrees
ERA5_LEVELS = "1/to/137/by/1"  # Model levels 1-137
ERA5_TIME_STEPS = "00/to/23/by/1"  # Hourly data
ERA5_STREAM = "oper"  # Operational stream
ERA5_TYPE = "an"  # Analysis fields
ERA5_FORMAT = "netcdf"  # Output format

# Parameter codes for ERA5 fields
ERA5_PARAM_CODES = {
    "temperature": "130",  # T
    "zonal_wind": "131",   # U
    "meridional_wind": "132",  # V
    "vertical_wind": "135",  # W (Pa/s)
}

# Momentum flux computation settings
HELMHOLTZ_TRUNCATION = 21  # T21 truncation for scale separation
GRAVITY_CONSTANT = -9.81  # m/s^2

# Coarse-graining settings
T42_GRID_NLON = 128  # Longitude points
T42_GRID_NLAT = 64   # Latitude points
REGRIDDING_METHOD = "conservative"  # xESMF regridding method

# Physical constants
REFERENCE_PRESSURE = 1e5  # Pa
POISSON_CONSTANT = -0.286
GAS_CONSTANT = 287.053  # J/(kg*K)
GRAVITATIONAL_ACCELERATION = 9.81  # m/s^2

# Default paths
DEFAULT_ERA5_DATA_DIR = "./ERA5_data_ml"
DEFAULT_MOMENTUM_FLUX_DIR = "./momentum_fluxes"
DEFAULT_TRAINING_DATA_DIR = "./training_data"
DEFAULT_MODEL_LEVELS_FILE = "./era5_model_levels_table.xlsx"

# Default output directories
DEFAULT_OUTPUT_DIR = "./nonlocal_parameterization_output"

