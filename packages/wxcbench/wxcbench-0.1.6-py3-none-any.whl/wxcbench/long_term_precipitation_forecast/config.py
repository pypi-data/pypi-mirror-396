"""
Configuration settings for long-term precipitation forecast processing.
"""

import numpy as np

# MERRA grid parameters
MERRA_GRID = {
    "dx": 0.625,  # degrees longitude
    "dy": 0.5,    # degrees latitude
    "nx": 576,
    "ny": 361,
    "lon_min": -180,
    "lon_max": 179.375,
    "lat_min": -90,
    "lat_max": 90,
}

# Default latitude range for evaluation (degrees)
DEFAULT_LAT_RANGE = (-60, 60)

# Forecast lead times (days)
MAX_LEAD_TIME_DAYS = 28
DEFAULT_LEAD_TIMES = list(range(1, MAX_LEAD_TIME_DAYS + 1))

# Number of input observation days
INPUT_OBSERVATION_DAYS = 8

# Data source specifications
DATA_SOURCES = {
    "gridsat": {
        "name": "GridSat B1",
        "channels": 3,  # VIS/IR channels
        "temporal_resolution": "3-hourly",
        "years": (1980, 2023),
    },
    "patmosx": {
        "name": "PATMOS-x",
        "imager_channels": 15,
        "sounder_channels": 8,
        "total_channels": 23,
        "years": (1979, 2023),
    },
    "ssmi": {
        "name": "SSMI",
        "channels": 7,
        "years": (1987, 2023),
    },
    "persiann": {
        "name": "PERSIANN CDR",
        "years": (1983, 2000),
    },
    "imerg": {
        "name": "IMERG Final",
        "years": (2000, None),  # Ongoing
    },
}

# Evaluation metrics configuration
EVALUATION_METRICS = ["bias", "mse", "rmse", "correlation", "mae"]

# Default output directories
DEFAULT_OUTPUT_DIR = "./precipitation_data"
DEFAULT_EVALUATION_OUTPUT_DIR = "./evaluation_results"
DEFAULT_VISUALIZATION_OUTPUT_DIR = "./precipitation_figures"

# Figure settings
DEFAULT_FIGURE_SIZE = (12, 8)
DEFAULT_DPI = 300

# Precipitation units
PRECIPITATION_UNITS = "mm/day"

# Time step for daily accumulation (minutes)
DAILY_TIME_STEP_MINUTES = 1440

# Default normalization methods
NORMALIZATION_METHODS = ["standard", "minmax", "robust", "log"]

