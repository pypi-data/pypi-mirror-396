"""
Configuration settings for aviation turbulence processing.
"""

# Default MERRA-2 grid parameters
MERRA2_GRID = {
    "dx": 0.625,  # degrees
    "dy": 0.5,    # degrees
    "nx": 576,
    "ny": 361,
    "x_start": -180,
    "y_start": -90,
}

# Turbulence classification thresholds
TURBULENCE_THRESHOLD = 0.25  # Fraction of reports that must be MOG before cell is classified as turbulence
NO_DATA_VALUE = 2  # No data value

# Flight level categories
FLIGHT_LEVELS = ["low", "med", "high"]

# PIREP download settings
PIREP_DOWNLOAD_BASE_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/gis/pireps.py"

# Default paths
DEFAULT_PIREP_OUTPUT_DIR = "./pirep_downloads"
DEFAULT_GRIDDED_DATA_DIR = "./gridded_data"
DEFAULT_TRAINING_DATA_DIR = "./training_data"

