"""
Configuration settings for hurricane tracking and intensity analysis.
"""

# HURDAT2 dataset URL
HURDAT2_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2022-042723.txt"

# Default basin
DEFAULT_BASIN = "north_atlantic"

# Intensity category bounds (wind speed in knots)
INTENSITY_BOUNDS = [0, 32, 64, 83, 96, 113, 137, 150]
INTENSITY_LABELS = ["TD", "TS", "Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5"]

# Default plotting parameters
DEFAULT_FIGURE_SIZE = (10, 6)
DEFAULT_DPI = 300
DEFAULT_FONT_SIZE = 14

# Default domain bounding box (lon_min, lon_max, lat_min, lat_max)
DEFAULT_DOMAIN_BB = [-110, -20, 5, 55]

# Default output directory
DEFAULT_OUTPUT_DIR = "./hurricane_figures"

