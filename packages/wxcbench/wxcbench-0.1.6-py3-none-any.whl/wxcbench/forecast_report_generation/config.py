"""
Configuration settings for forecast report generation processing.
"""

# HRRR download settings
HRRR_ARCHIVE_URL = "https://noaa-hrrr-bdp-pds.s3.amazonaws.com"

# HRRR dataset types
HRRR_DATASET_TYPES = ["prs", "nat", "sfc"]  # pressure, natural, surface

# Default paths
DEFAULT_HRRR_OUTPUT_DIR = "./hrrr"
DEFAULT_CAPTION_OUTPUT_DIR = "./csv_reports"
DEFAULT_METADATA_OUTPUT_FILE = "./metadata.csv"

# SPC scraping settings
SPC_BASE_URL = "https://www.spc.noaa.gov"
SPC_DATE_RANGE_URL_TEMPLATE = "https://www.spc.noaa.gov/cgi-bin-spc/getacrange-aws.pl"

