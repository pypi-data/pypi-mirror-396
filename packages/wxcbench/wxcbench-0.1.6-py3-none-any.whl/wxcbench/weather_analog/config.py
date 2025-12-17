"""
Configuration settings for weather analog processing.
"""

from datetime import datetime
from typing import Tuple

# Default geographic bounds for the region of interest
# (Longitude, Latitude) in degrees
DEFAULT_LON_BOUNDS: Tuple[float, float] = (-15, 0)  # 15°W to 0°E
DEFAULT_LAT_BOUNDS: Tuple[float, float] = (42, 58)  # 42°N to 58°N

# Default time period
DEFAULT_START_DATE = datetime(2019, 1, 1)
DEFAULT_END_DATE = datetime(2021, 12, 31)

# MERRA2 variables to extract
MERRA2_VARIABLES = ["SLP", "T2M"]  # Sea Level Pressure, 2-meter Temperature

# MERRA2 file naming pattern
MERRA2_FILE_PATTERN = "MERRA2*.{date}.SUB.nc"
MERRA2_OUTPUT_PATTERN = "MERRA2_SLP_T2M_{date}.nc"

# Default paths
DEFAULT_INPUT_DIR = "./MERRA2_data"
DEFAULT_OUTPUT_DIR = "./MERRA2_processed"

# Default time index to extract (0 = first time step)
DEFAULT_TIME_INDEX = [0]

