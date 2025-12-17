# WxC-Bench Python Package

When working with a foundation model, you can design and generalize your own scripts to adapt the model to different tasks. This allows you to customize preprocessing, fine-tuning, and evaluation pipelines, making the model more flexible, reusable, and scalable across multiple use cases. In this work, a modular pipeline was developed to preprocess, grid, and align multi-source meteorological data for machine learning model training and evaluation.

## Installation

### Basic Installation

```bash
pip install wxcbench
```

### Optional Dependencies

If you plan to use the `nonlocal_parameterization` module, you'll need to install `windspharm`:

```bash
pip install wxcbench[nonlocal_parameterization]
```

**Note:** `windspharm` has a build dependency issue with `pyspharm`. If you encounter build errors, use:

```bash
pip install "numpy>=1.20.0" setuptools wheel
pip install --no-build-isolation wxcbench[nonlocal_parameterization]
```

Or install `windspharm` separately first:

```bash
pip install "numpy>=1.20.0" setuptools wheel
pip install --no-build-isolation "windspharm>=1.7.0"
pip install wxcbench[nonlocal_parameterization]
```

## Usage

### Aviation Turbulence Module

The `aviation_turbulence` module provides a complete workflow for processing pilot reports (PIREPs) and preparing turbulence data for machine learning applications. Here's how to use each function:

#### Import the Module

```python
import wxcbench.aviation_turbulence as wab
```

#### 1. Download PIREP Data

**Function:** `get_pirep_data()`

**What it does:** Downloads historical pilot report (PIREP) data from Iowa State University archive (2003-present). The function:

- Creates URLs for monthly data downloads
- Downloads CSV files containing PIREP reports
- Removes duplicate reports and invalid entries
- Optionally combines all monthly files into a single `all_pireps.csv` file
- Creates a `pirep_downloads` folder containing monthly data files

**Parameters:**

- `start_year` (int, optional): Starting year for data download (default: 2003)
- `end_year` (int, optional): Ending year for data download. If None, uses current year (default: None)
- `output_dir` (str, optional): Directory to save downloaded files (default: `./pirep_downloads`)
- `combine_files` (bool, optional): If True, combines all files into `all_pireps.csv` (default: True)

**Example:**

```python
# Download PIREP data from 2020 to 2023
df = wab.get_pirep_data(start_year=2020, end_year=2023)
print(f"Downloaded {len(df)} PIREP records")
```

**Output:**

- Creates `pirep_downloads/` directory with monthly CSV files
- Creates `pirep_downloads/all_pireps.csv` (if `combine_files=True`)
- Returns a pandas DataFrame containing all PIREP data

---

#### 2. Preprocess Turbulence EDA

**Function:** `preprocess_turb_eda()`

**What it does:** Performs exploratory data analysis and preprocessing on PIREP data. The function:

- Adds new columns and filters data
- Categorizes reports by flight level (low, medium, high)
- Creates flight-level specific files: `low_fl.csv`, `med_fl.csv`, `high_fl.csv`
- Saves processed data to `updated_CSVs/csv_fl_rem.csv`

**Parameters:**

- `input_file` (str): Path to input CSV file (e.g., `'pirep_downloads/all_pireps.csv'`)
- `output_dir` (str, optional): Directory to save processed files (default: current directory)

**Example:**

```python
# Preprocess the downloaded PIREP data
df_processed = wab.preprocess_turb_eda('pirep_downloads/all_pireps.csv')
```

**Output:**

- Creates `updated_CSVs/` directory
- Creates `updated_CSVs/csv_fl_rem.csv` (processed data)
- Creates flight-level specific files: `low_fl.csv`, `med_fl.csv`, `high_fl.csv`
- Returns processed DataFrame

---

#### 3. Filter Moderate-or-Greater (MODG) Turbulence

**Function:** `preprocess_modg()`

**What it does:** Filters PIREP data for moderate-or-greater (MODG) turbulence reports. The function:

- Filters for reports indicating moderate or greater turbulence intensity
- Creates MODG-specific files: `low_fl_modg.csv`, `med_fl_modg.csv`, `high_fl_modg.csv`
- Saves filtered data to `updated_CSVs/csv_modg_all.csv`

**Parameters:**

- `input_file` (str): Path to input CSV file (e.g., `'updated_CSVs/csv_fl_rem.csv'`)
- `output_dir` (str, optional): Directory to save processed files (default: current directory)

**Example:**

```python
# Filter for MODG turbulence reports
df_modg = wab.preprocess_modg('updated_CSVs/csv_fl_rem.csv')
```

**Output:**

- Creates `updated_CSVs/csv_modg_all.csv` (all MODG reports)
- Creates MODG flight-level files: `low_fl_modg.csv`, `med_fl_modg.csv`, `high_fl_modg.csv`
- Returns filtered DataFrame

---

#### 4. Visualize PIREP Risk Map (Optional)

**Function:** `convert_to_risk_map()`

**What it does:** Visualizes the spatial distribution of PIREPs by creating a risk map. The function:

- Creates a visualization showing where turbulence reports are concentrated
- Generates a spatial distribution map of PIREP locations
- Helps understand geographic patterns of turbulence occurrence

**Parameters:**

- `input_file` (str): Path to input CSV file containing PIREP data
- `output_file` (str, optional): Path to save the visualization (default: `pirep_risk_map.png`)
- `**kwargs`: Additional keyword arguments for customization

**Example:**

```python
# Create a risk map visualization
wab.convert_to_risk_map('updated_CSVs/csv_fl_rem.csv', output_file='turbulence_risk_map.png')
```

**Output:**

- Creates a PNG image file showing PIREP spatial distribution

---

#### 5. Grid PIREPs onto MERRA-2 Grid

**Function:** `grid_pireps()`

**What it does:** Grids PIREP data onto the MERRA-2 atmospheric model grid. The function:

- Filters and bins PIREPs by day onto the MERRA-2 grid (0.625° x 0.5° resolution)
- Converts data to binary classification: 1 = turbulence present, 0 = no turbulence, 2 = no data
- Applies a threshold: cell is classified as turbulent if fraction of MOG reports ≥ threshold (default: 0.25)
- Creates daily NetCDF files organized by year and flight level

**Parameters:**

- `pirep_files` (List[str]): List of paths to PIREP CSV files (e.g., `['updated_CSVs/low_fl.csv', 'updated_CSVs/med_fl.csv']`)
- `output_dir` (str, optional): Directory to save gridded data (default: `./gridded_data`)
- `threshold` (float, optional): Fraction threshold for turbulence classification (default: 0.25)
- `nodata` (int, optional): Value for cells with no data (default: 2)

**Example:**

```python
# Grid PIREPs onto MERRA-2 grid
wab.grid_pireps(
    pirep_files=['updated_CSVs/low_fl.csv', 'updated_CSVs/med_fl.csv', 'updated_CSVs/high_fl.csv'],
    output_dir='./gridded_data',
    threshold=0.25
)
```

**Output:**

- Creates `gridded_data/` directory
- Creates NetCDF files: `YYYY_level_fl.nc` (e.g., `2023_low_fl.nc`)
- Each file contains daily gridded turbulence data with variables:
  - `Turbulence`: Binary turbulence presence (1=Yes, 0=No, 2=No data)
  - `Dates`: Date strings for each time step
  - `Lons`, `Lats`: Longitude and latitude grids

---

#### 6. Create Training Data

**Function:** `create_training_data()`

**What it does:** Extracts MERRA-2 atmospheric profiles matching turbulence detections from gridded PIREPs. The function:

- Matches turbulence locations from gridded PIREP data with MERRA-2 weather profiles
- Extracts 34-level atmospheric profiles (temperature, wind, humidity, pressure, etc.)
- Creates training data files for deep learning models
- Organizes data by flight level (low, med, high)

**Parameters:**

- `turbulence_dir` (str, optional): Directory containing gridded turbulence NetCDF files (default: `./gridded_data`)
- `merra2_dir` (str, required): Directory containing MERRA-2 data files
- `years` (List[int], optional): Years to process (default: `[2021, 2022]`)
- `levels` (List[str], optional): Flight levels to process (default: `['low', 'med', 'high']`)
- `output_dir` (str, optional): Directory to save training data (default: `./training_data`)

**Example:**

```python
# Create training data from gridded PIREPs and MERRA-2 profiles
wab.create_training_data(
    turbulence_dir='./gridded_data',
    merra2_dir='./MERRA2_2021-2022_1000hPa-100hPa',
    years=[2021, 2022],
    levels=['low', 'med', 'high'],
    output_dir='./training_data_20240126'
)
```

**Output:**

- Creates `training_data/` directory (or specified directory)
- Creates NetCDF files: `training_data_low_fl.nc`, `training_data_med_fl.nc`, `training_data_high_fl.nc`
- Each file contains:
  - `TURBULENCE`: Training labels (1=turbulence, 0=none)
  - `T`: Temperature profile (34 levels)
  - `U`, `V`: Wind velocity profiles (34 levels)
  - `OMEGA`: Vertical velocity profile (34 levels)
  - `RH`: Relative humidity profile (34 levels)
  - `H`: Height levels (34 levels)
  - `PL`: Pressure levels (34 levels)
  - `PHIS`: Surface geopotential

---

### Complete Aviation Turbulence Workflow Example

Here's a complete example that demonstrates the full pipeline:

```python
import wxcbench.aviation_turbulence as wab

# Step 1: Download PIREP data
print("Step 1: Downloading PIREP data...")
df = wab.get_pirep_data(start_year=2020, end_year=2023)
print(f"Downloaded {len(df)} records")

# Step 2: Preprocess and categorize by flight level
print("Step 2: Preprocessing data...")
wab.preprocess_turb_eda('pirep_downloads/all_pireps.csv')

# Step 3: Filter for MODG turbulence (optional)
print("Step 3: Filtering MODG turbulence...")
wab.preprocess_modg('updated_CSVs/csv_fl_rem.csv')

# Step 4: Grid PIREPs onto MERRA-2 grid
print("Step 4: Gridding PIREPs...")
wab.grid_pireps(
    pirep_files=[
        'updated_CSVs/low_fl.csv',
        'updated_CSVs/med_fl.csv',
        'updated_CSVs/high_fl.csv'
    ],
    output_dir='./gridded_data'
)

# Step 5: Create training data
print("Step 5: Creating training data...")
wab.create_training_data(
    turbulence_dir='./gridded_data',
    merra2_dir='./MERRA2_2021-2022_1000hPa-100hPa',
    years=[2021, 2022],
    output_dir='./training_data'
)

print("Workflow complete!")
```

---

### Aviation Turbulence Configuration

All default settings are built into the package and can be customized through function parameters. You don't need to edit any configuration files - simply pass the desired values as arguments when calling functions:

- **MERRA-2 Grid Parameters:** Grid resolution and dimensions (built-in defaults)
- **Turbulence Threshold:** Can be customized via `threshold` parameter in `grid_pireps()` (default: 0.25)
- **Flight Levels:** Can be customized via `levels` parameter in `create_training_data()` (default: ['low', 'med', 'high'])
- **Output Directories:** Can be customized via `output_dir` parameters in each function (defaults: `./pirep_downloads`, `./gridded_data`, `./training_data`)

---

### Forecast Report Generation Module

The `forecast_report_generation` module provides functionality for downloading HRRR weather data, scraping weather forecast reports, and creating metadata files for machine learning applications. Here's how to use each function:

#### Import the Forecast Report Generation Module

```python
import wxcbench.forecast_report_generation as frg
```

#### 1. Scrape Weather Reports

**Function:** `scrape_weather_reports()`

**What it does:** Scrapes textual weather forecast reports from SPC (Storm Prediction Center). The function:

- Fetches weather reports within a specified date range from the SPC website
- Extracts summary discussions from the reports
- Saves extracted data as CSV files for pairing with HRRR weather data
- Organizes reports by date for easy matching with weather data files

**Parameters:**

- `start_date` (str, required): Start date of the time range in YYYY-MM-DD format (e.g., "2021-06-27")
- `end_date` (str, required): End date of the time range in YYYY-MM-DD format (e.g., "2021-06-27")
- `output_dir` (str, optional): Directory to save the output CSV files (default: `./csv_reports`)

**Example:**

```python
# Scrape weather reports for a specific date range
df = frg.scrape_weather_reports(
    start_date="2021-06-27",
    end_date="2021-06-27"
)
```

**Output:**

- Creates `csv_reports/` directory (or specified directory)
- Creates CSV files for each date: `YYYYMMDD.csv`
- Each CSV file contains columns: `date`, `time`, `url`, `discussion`
- Returns a pandas DataFrame containing all scraped data

---

#### 2. Download HRRR Weather Data

**Function:** `download_hrrr()`

**What it does:** Downloads HRRR (High-Resolution Rapid Refresh) weather data files from NOAA's public S3 bucket. The function:

- Downloads HRRR grib2 files from NOAA's S3 bucket
- Supports configurable date ranges and time intervals
- Supports different forecast hours and dataset types (pressure, natural, surface)
- Automatically creates storage directory if it doesn't exist

**Parameters:**

- `start_date` (str, required): Start date for downloading HRRR data (format: "YYYYMMDD-HH", e.g., "20180101-01")
- `end_date` (str, required): End date for downloading HRRR data (format: "YYYYMMDD-HH", e.g., "20180102-01")
- `forecast_hours` (List[int], optional): Forecast hours to download (0 represents analysis files) (default: `[0]`)
- `time_interval` (int, optional): Interval between downloads in hours (default: `24`)
- `dataset_type` (str, optional): HRRR dataset type. Options: `"prs"` (pressure), `"nat"` (natural), `"sfc"` (surface) (default: `"nat"`)
- `output_dir` (str, optional): Local directory to save downloaded HRRR files (default: `./hrrr`)

**Example:**

```python
# Download HRRR analysis data for a date range
frg.download_hrrr(
    start_date="20180101-01",
    end_date="20180102-01",
    forecast_hours=[0],
    dataset_type="nat",
    output_dir="./hrrr"
)
```

**Output:**

- Creates `hrrr/` directory (or specified directory)
- Downloads HRRR grib2 files with naming format: `hrrr.YYYYMMDD.tHHZ.wrfDATATYPEfFF.grib2`
- Example: `hrrr.20180101.t01z.wrfnatf00.grib2`

---

#### 3. Create Metadata File

**Function:** `create_metadata()`

**What it does:** Creates a metadata CSV file that pairs HRRR weather data files with their corresponding forecast discussions. The function:

- Matches HRRR grib2 files with their corresponding caption files
- Extracts forecast discussions from CSV files
- Creates a metadata file suitable for machine learning training
- Output format: CSV with columns `file_name` and `text`

**Parameters:**

- `image_dir` (str, required): Path to the directory containing HRRR image files (.grib2)
- `caption_dir` (str, required): Path to the directory containing caption files (.csv)
- `output_file` (str, optional): Path to save the generated metadata CSV file (default: `./metadata.csv`)

**Example:**

```python
# Create metadata file pairing HRRR files with forecast discussions
df_metadata = frg.create_metadata(
    image_dir="./hrrr",
    caption_dir="./csv_reports",
    output_file="./metadata.csv"
)
```

**Output:**

- Creates metadata CSV file at specified location
- CSV format with columns:
  - `file_name`: Name of the HRRR grib2 file (e.g., `hrrr.20180101.t01z.wrfnatf00.grib2`)
  - `text`: Corresponding forecast discussion text extracted from CSV caption files
- Returns a pandas DataFrame containing the metadata

---

### Complete Forecast Report Generation Workflow Example

Here's a complete example that demonstrates the full pipeline:

```python
import wxcbench.forecast_report_generation as frg

# Step 1: Scrape weather reports from SPC
print("Step 1: Scraping weather reports...")
df_reports = frg.scrape_weather_reports(
    start_date="2021-06-27",
    end_date="2021-06-27",
    output_dir="./csv_reports"
)
print(f"Scraped {len(df_reports)} reports")

# Step 2: Download HRRR weather data
print("Step 2: Downloading HRRR data...")
frg.download_hrrr(
    start_date="20180101-01",
    end_date="20180102-01",
    forecast_hours=[0],
    dataset_type="nat",
    output_dir="./hrrr"
)

# Step 3: Create metadata file
print("Step 3: Creating metadata file...")
df_metadata = frg.create_metadata(
    image_dir="./hrrr",
    caption_dir="./csv_reports",
    output_file="./metadata.csv"
)
print(f"Created metadata with {len(df_metadata)} entries")

print("Workflow complete!")
```

---

### File Format Conventions

The module follows these file naming conventions:

- **HRRR files:** `hrrr.YYYYMMDD.tHHZ.wrfDATATYPEfFF.grib2`
  - Example: `hrrr.20180101.t01z.wrfnatf00.grib2`
- **Caption files:** `YYYYMMDD.csv`
  - Example: `20180101.csv`
- **Output metadata:** `metadata.csv` (customizable)

The metadata creation function automatically matches HRRR files with caption files based on the date portion of the filename.

---

### Forecast Report Generation Configuration

All default settings are built into the package and can be customized through function parameters. You don't need to edit any configuration files - simply pass the desired values as arguments when calling functions:

- **HRRR Archive URL:** NOAA's S3 bucket URL (built-in default)
- **HRRR Dataset Types:** Available types: `"prs"` (pressure), `"nat"` (natural), `"sfc"` (surface). Can be customized via `dataset_type` parameter in `download_hrrr()` (default: `"nat"`)
- **Forecast Hours:** Can be customized via `forecast_hours` parameter in `download_hrrr()` (default: `[0]` for analysis files)
- **Time Interval:** Can be customized via `time_interval` parameter in `download_hrrr()` (default: 24 hours)
- **Output Directories:** Can be customized via `output_dir` parameters in each function (defaults: `./hrrr`, `./csv_reports`)
- **Metadata Output:** Can be customized via `output_file` parameter in `create_metadata()` (default: `./metadata.csv`)

---

### Hurricane Module

The `hurricane` module provides functionality for analyzing and visualizing hurricane tracks and intensities from the HURDAT2 dataset maintained by the National Hurricane Center (NHC). Here's how to use each function:

#### Import the Hurricane Module

```python
import wxcbench.hurricane as hurricane
```

#### 1. Plot Hurricane Intensity

**Function:** `plot_intensity()`

**What it does:** Creates time series plots of hurricane intensity metrics over time. The function:

- Plots maximum sustained wind speed and minimum sea level pressure on dual y-axes
- Displays intensity evolution throughout the storm's lifetime
- Supports analysis of individual storms with customizable time ranges
- Saves high-resolution visualizations

**Parameters:**

- `name` (str, optional): The name of the hurricane (default: `'michael'`)
- `year` (int, optional): The year of the hurricane (default: `2018`)
- `start` (int, optional): The index to start plotting the data (default: `1`)
- `skip` (int, optional): The number of data points to skip when plotting (default: `10`)
- `output_file` (str, optional): Path to save the figure. If None, generates filename automatically
- `output_dir` (str, optional): Directory to save the figure (default: `./hurricane_figures`)
- `figsize` (tuple, optional): Figure size as (width, height) (default: `(10, 6)`)
- `dpi` (int, optional): Resolution for saved figure (default: `300`)

**Example:**

```python
# Plot intensity for Hurricane Harvey (2017)
hurricane.plot_intensity(name='harvey', year=2017, start=2)

# Plot intensity for Hurricane Laura (2020)
hurricane.plot_intensity(name='laura', year=2020, start=2)
```

**Output:**

- Creates `hurricane_figures/` directory (or specified directory)
- Saves PNG file: `Intensity_HARVEY_2017.jpeg`
- Figure shows dual y-axes: wind speed (kt) and pressure (hPa) over time

---

#### 2. Plot Hurricane Track

**Function:** `plot_track()`

**What it does:** Plots hurricane tracks on a geographic map with color-coding based on storm intensity. The function:

- Visualizes hurricane paths on a geographic domain
- Color-codes track points based on wind speed intensity
- Supports visualization of both single storms and entire hurricane seasons
- Uses a color scale representing different hurricane categories (TD, TS, Cat 1-5)
- Includes a color bar legend for intensity categories

**Parameters:**

- `year` (int, optional): Year to plot. If None and storm_name is provided, uses the storm's year. If both None, defaults to 2017
- `storm_name` (str, optional): Name of specific storm to plot. If None, plots all storms for the given year
- `basin` (str, optional): Hurricane basin to use (default: `'north_atlantic'`)
- `domain_bb` (list, optional): Bounding box for the domain plot as `[lon_min, lon_max, lat_min, lat_max]` (default: `[-110, -20, 5, 55]`)
- `output_file` (str, optional): Path to save the figure. If None, generates filename automatically
- `output_dir` (str, optional): Directory to save the figure (default: `./hurricane_figures`)
- `figsize` (tuple, optional): Figure size as (width, height) (default: `(10, 6)`)
- `dpi` (int, optional): Resolution for saved figure (default: `300`)
- `show` (bool, optional): Whether to display the plot (default: `False`)

**Example:**

```python
# Plot all hurricanes from the 2017 Atlantic season
hurricane.plot_track(year=2017)

# Plot a specific hurricane track
hurricane.plot_track(storm_name='harvey', year=2017)

# Plot with custom domain
hurricane.plot_track(
    year=2020,
    domain_bb=[-100, -60, 20, 40],
    output_dir='./custom_output'
)
```

**Output:**

- Creates `hurricane_figures/` directory (or specified directory)
- Saves PNG file: `Track_SEASON_2017.png` or `Track_HARVEY_2017.png`
- Figure shows geographic map with hurricane tracks color-coded by intensity
- Includes color bar legend showing intensity categories

---

### Complete Hurricane Analysis Workflow Example

Here's a complete example that demonstrates the full pipeline:

```python
import wxcbench.hurricane as hurricane

# Step 1: Plot intensity for multiple hurricanes
print("Step 1: Plotting hurricane intensities...")
hurricane.plot_intensity(name='alicia', year=1983, start=2)
hurricane.plot_intensity(name='harvey', year=2017, start=2)
hurricane.plot_intensity(name='laura', year=2020, start=2)
hurricane.plot_intensity(name='ike', year=2008, start=2)
hurricane.plot_intensity(name='rita', year=2005, start=2)

# Step 2: Plot tracks for specific hurricanes
print("Step 2: Plotting hurricane tracks...")
hurricane.plot_track(storm_name='harvey', year=2017)
hurricane.plot_track(storm_name='laura', year=2020)

# Step 3: Plot entire season
print("Step 3: Plotting 2017 Atlantic hurricane season...")
hurricane.plot_track(year=2017)

print("Analysis complete!")
```

---

### Hurricane Module Configuration

All default settings are built into the package and can be customized through function parameters. You don't need to edit any configuration files - simply pass the desired values as arguments when calling functions:

- **HURDAT2 Dataset URL:** NOAA's HURDAT2 database URL (built-in default)
- **Basin:** Can be customized via `basin` parameter in `plot_track()` (default: `'north_atlantic'`)
- **Domain Bounding Box:** Can be customized via `domain_bb` parameter in `plot_track()` (default: `[-110, -20, 5, 55]`)
- **Intensity Categories:** Built-in bounds for TD, TS, Cat 1-5 classification
- **Output Directories:** Can be customized via `output_dir` parameters in each function (default: `./hurricane_figures`)
- **Figure Settings:** Can be customized via `figsize` and `dpi` parameters (defaults: `(10, 6)`, `300`)

---

### Long-Term Precipitation Forecast Module

The `long_term_precipitation_forecast` module provides utilities for evaluating and analyzing long-term precipitation forecasts (up to 4 weeks lead time) from satellite observations. This module focuses on evaluation, data loading, preprocessing, and visualization utilities for working with precipitation forecast data.

#### Import the Long-Term Precipitation Forecast Module

```python
import wxcbench.long_term_precipitation_forecast as precip
```

#### 1. Load Precipitation Data

**Function:** `load_precipitation_data()`

**What it does:** Loads precipitation data from NetCDF files. The function:

- Supports both PERSIANN CDR and IMERG Final precipitation datasets
- Auto-detects precipitation variable names if not specified
- Returns xarray DataArray or Dataset with coordinates

**Parameters:**

- `file_path` (str or Path, required): Path to the NetCDF file
- `variable_name` (str, optional): Name of the precipitation variable. If None, auto-detects (default: None)
- `return_coords` (bool, optional): If True, returns Dataset with coordinates; if False, returns DataArray (default: False)

**Example:**

```python
# Load precipitation data
precip_data = precip.load_precipitation_data('precipitation_data.nc')

# Load with coordinates
precip_dataset = precip.load_precipitation_data(
    'precipitation_data.nc',
    return_coords=True
)
```

**Output:**

- Returns xarray DataArray or Dataset containing precipitation values
- Includes latitude and longitude coordinates

---

#### 2. Load Satellite Observations

**Function:** `load_satellite_observations()`

**What it does:** Loads satellite observation data from NetCDF files. The function:

- Supports GridSat, PATMOS-x, and SSMI observation datasets
- Handles multiple data variables in a single file
- Returns observations with coordinates

**Parameters:**

- `file_path` (str or Path, required): Path to the NetCDF file
- `return_coords` (bool, optional): If True, returns Dataset with coordinates; if False, returns DataArray (default: False)

**Example:**

```python
# Load satellite observations
obs_data = precip.load_satellite_observations('gridsat_observations.nc')

# Load with all coordinates
obs_dataset = precip.load_satellite_observations(
    'patmosx_observations.nc',
    return_coords=True
)
```

**Output:**

- Returns xarray DataArray or Dataset containing satellite observation values
- Includes all available channels/variables

---

#### 3. Combine Observations

**Function:** `combine_observations()`

**What it does:** Combines multiple daily observation files into a single dataset. The function:

- Creates sequences of observations from consecutive days (typically 8 days)
- Sorts files by date automatically
- Combines observations along time dimension

**Parameters:**

- `obs_files` (list, required): List of paths to observation NetCDF files (consecutive days)
- `n_days` (int, optional): Number of days to combine (default: 8)
- `sort_by_date` (bool, optional): If True, sort files by date before combining (default: True)

**Example:**

```python
# Combine 8 days of observations
obs_files = [
    'obs_20200101.nc',
    'obs_20200102.nc',
    'obs_20200103.nc',
    'obs_20200104.nc',
    'obs_20200105.nc',
    'obs_20200106.nc',
    'obs_20200107.nc',
    'obs_20200108.nc'
]
combined = precip.combine_observations(obs_files, n_days=8)
```

**Output:**

- Returns xarray Dataset with combined observations
- Includes time dimension with day indices (0 to n_days-1)

---

#### 4. Regrid to MERRA Grid

**Function:** `regrid_to_merra()`

**What it does:** Regrids data to the MERRA grid (0.625° x 0.5° resolution). The function:

- Supports multiple interpolation methods (nearest, linear, cubic)
- Handles multi-dimensional data (preserves time/lead_time dimensions)
- Creates xarray DataArray on MERRA grid

**Parameters:**

- `data` (np.ndarray or xr.DataArray, required): Data to regrid
- `source_lon` (np.ndarray or xr.DataArray, optional): Source longitude coordinates. If None and data is xr.DataArray, uses coordinates
- `source_lat` (np.ndarray or xr.DataArray, optional): Source latitude coordinates. If None and data is xr.DataArray, uses coordinates
- `method` (str, optional): Interpolation method: 'nearest', 'linear', 'cubic' (default: 'nearest')

**Example:**

```python
# Regrid satellite observations to MERRA grid
regridded_data = precip.regrid_to_merra(
    obs_data,
    method='linear'
)
```

**Output:**

- Returns xarray DataArray on MERRA grid
- Resolution: 0.625° longitude x 0.5° latitude

---

#### 5. Normalize Data

**Function:** `normalize_data()`

**What it does:** Normalizes or standardizes data using various methods. The function:

- Supports multiple normalization methods (standard, minmax, robust, log)
- Handles NaN values appropriately
- Preserves data structure and coordinates

**Parameters:**

- `data` (np.ndarray or xr.DataArray, required): Data to normalize
- `method` (str, optional): Normalization method: 'standard', 'minmax', 'robust', 'log' (default: 'standard')
- `axis` (int, optional): Axis along which to compute statistics. If None, normalizes over entire array (default: None)
- `return_scaler` (bool, optional): If True, also return the scaler object for inverse transformation (default: False)

**Example:**

```python
# Standardize data
normalized = precip.normalize_data(precip_data, method='standard')

# Min-max normalization
normalized = precip.normalize_data(precip_data, method='minmax')

# With scaler for inverse transformation
normalized, scaler = precip.normalize_data(
    precip_data,
    method='standard',
    return_scaler=True
)
```

**Output:**

- Returns normalized xarray DataArray or numpy array
- If `return_scaler=True`, returns tuple (normalized_data, scaler)

---

#### 6. Compute Evaluation Metrics

**Functions:** `compute_bias()`, `compute_mse()`, `compute_rmse()`, `compute_correlation()`, `compute_mae()`

**What they do:** Compute various evaluation metrics between predictions and observations. The functions:

- Support area-weighted calculations over specified latitude ranges
- Handle NaN values appropriately
- Work with both numpy arrays and xarray DataArrays

**Parameters:**

- `predictions` (np.ndarray or xr.DataArray, required): Predicted precipitation values
- `observations` (np.ndarray or xr.DataArray, required): Observed precipitation values
- `lat` (np.ndarray or xr.DataArray, optional): Latitude coordinates for area weighting
- `lat_range` (tuple, optional): Latitude range for evaluation (default: (-60, 60))

**Example:**

```python
# Compute bias
bias = precip.compute_bias(forecasts, observations)

# Compute MSE with area weighting
mse = precip.compute_mse(
    forecasts,
    observations,
    lat=lat_coords,
    lat_range=(-60, 60)
)

# Compute correlation
correlation = precip.compute_correlation(forecasts, observations)

# Compute RMSE
rmse = precip.compute_rmse(forecasts, observations)
```

**Output:**

- Returns float or array of metric values
- Positive bias indicates over-prediction
- Correlation ranges from -1 to 1

---

#### 7. Evaluate Forecasts Comprehensively

**Function:** `evaluate_forecasts()`

**What it does:** Comprehensive evaluation of precipitation forecasts across multiple lead times. The function:

- Computes multiple metrics (bias, MSE, RMSE, correlation, MAE) for each lead time
- Supports area-weighted evaluation
- Returns dictionary with all computed metrics

**Parameters:**

- `forecasts` (np.ndarray or xr.DataArray, required): Forecast precipitation values. Shape: (lead_time, lat, lon) or (time, lead_time, lat, lon)
- `observations` (np.ndarray or xr.DataArray, required): Observed precipitation values. Shape should match forecasts
- `lead_times` (list, optional): List of lead times in days. If None, uses indices 0, 1, 2, ... (default: None)
- `lat` (np.ndarray or xr.DataArray, optional): Latitude coordinates
- `lat_range` (tuple, optional): Latitude range for evaluation (default: (-60, 60))
- `metrics` (list, optional): List of metrics to compute. Options: 'bias', 'mse', 'rmse', 'correlation', 'mae'. If None, computes all (default: None)

**Example:**

```python
# Evaluate forecasts for all lead times
results = precip.evaluate_forecasts(
    forecasts=forecast_data,
    observations=observation_data,
    lead_times=list(range(1, 29)),  # Days 1-28
    lat_range=(-60, 60)
)

# Access specific metrics
bias_values = results['bias']
correlation_values = results['correlation']
lead_times = results['lead_times']
```

**Output:**

- Returns dictionary with metric names as keys
- Each metric contains array of values (one per lead time)
- Includes 'lead_times' key with lead time array

---

#### 8. Visualize Precipitation Comparison

**Function:** `plot_precipitation_comparison()`

**What it does:** Creates side-by-side comparison plots of forecast and observation precipitation. The function:

- Displays forecast, observation, and difference maps
- Uses consistent color scales for comparison
- Supports saving to file

**Parameters:**

- `forecast` (np.ndarray or xr.DataArray, required): Forecast precipitation data
- `observation` (np.ndarray or xr.DataArray, required): Observed precipitation data
- `lead_time` (int, optional): Lead time index to plot if data is 3D
- `lon` (np.ndarray or xr.DataArray, optional): Longitude coordinates
- `lat` (np.ndarray or xr.DataArray, optional): Latitude coordinates
- `output_file` (str or Path, optional): Path to save the figure
- `figsize` (tuple, optional): Figure size (width, height) (default: (12, 8))
- `dpi` (int, optional): Figure resolution (default: 300)
- `vmax` (float, optional): Maximum value for color scale
- `cmap` (str, optional): Colormap name (default: 'YlGnBu')

**Example:**

```python
# Plot comparison for specific lead time
fig = precip.plot_precipitation_comparison(
    forecast=forecast_data[7, :, :],  # 7-day lead time
    observation=observation_data[7, :, :],
    lead_time=7,
    output_file='forecast_comparison_7day.png'
)
```

**Output:**

- Creates matplotlib figure with 3 subplots (forecast, observation, difference)
- Saves to file if `output_file` specified

---

#### 9. Plot Evaluation Metrics

**Function:** `plot_evaluation_metrics()`

**What it does:** Plots evaluation metrics as a function of lead time. The function:

- Creates subplots for each metric
- Shows how metrics degrade with increasing lead time
- Supports custom metric selection

**Parameters:**

- `metrics_dict` (dict, required): Dictionary with metric names as keys and arrays of values. Should include 'lead_times' key
- `lead_times` (list, optional): List of lead times in days. If None, uses 'lead_times' from metrics_dict (default: None)
- `output_file` (str or Path, optional): Path to save the figure
- `figsize` (tuple, optional): Figure size (width, height) (default: (12, 8))
- `dpi` (int, optional): Figure resolution (default: 300)
- `metrics_to_plot` (list, optional): List of metrics to plot. If None, plots all except 'lead_times' (default: None)

**Example:**

```python
# Plot evaluation results
fig = precip.plot_evaluation_metrics(
    metrics_dict=results,
    output_file='evaluation_metrics.png'
)

# Plot specific metrics only
fig = precip.plot_evaluation_metrics(
    metrics_dict=results,
    metrics_to_plot=['bias', 'correlation', 'rmse']
)
```

**Output:**

- Creates matplotlib figure with subplots for each metric
- Shows metric evolution with lead time

---

#### 10. Plot Spatial Distribution

**Function:** `plot_spatial_distribution()`

**What it does:** Creates spatial distribution plots of precipitation data. The function:

- Displays global or regional precipitation patterns
- Supports custom color scales
- Handles multi-dimensional data (averages over time if needed)

**Parameters:**

- `data` (np.ndarray or xr.DataArray, required): Precipitation data. Shape: (lat, lon) or (time, lat, lon)
- `title` (str, optional): Plot title (default: 'Precipitation Distribution')
- `lon` (np.ndarray or xr.DataArray, optional): Longitude coordinates
- `lat` (np.ndarray or xr.DataArray, optional): Latitude coordinates
- `output_file` (str or Path, optional): Path to save the figure
- `figsize` (tuple, optional): Figure size (width, height) (default: (12, 8))
- `dpi` (int, optional): Figure resolution (default: 300)
- `cmap` (str, optional): Colormap name (default: 'YlGnBu')
- `vmax` (float, optional): Maximum value for color scale

**Example:**

```python
# Plot spatial distribution
fig = precip.plot_spatial_distribution(
    data=precip_data,
    title='Daily Precipitation (mm/day)',
    output_file='precipitation_map.png'
)
```

**Output:**

- Creates matplotlib figure with spatial precipitation map
- Includes colorbar with units

---

### Complete Long-Term Precipitation Forecast Workflow Example

Here's a complete example that demonstrates the full pipeline:

```python
import wxcbench.long_term_precipitation_forecast as precip
import xarray as xr

# Step 1: Load precipitation data
print("Step 1: Loading precipitation data...")
obs_data = precip.load_precipitation_data('observations.nc')
forecast_data = precip.load_precipitation_data('forecasts.nc')

# Step 2: Regrid to MERRA grid if needed
print("Step 2: Regridding to MERRA grid...")
obs_regridded = precip.regrid_to_merra(obs_data, method='linear')
forecast_regridded = precip.regrid_to_merra(forecast_data, method='linear')

# Step 3: Evaluate forecasts
print("Step 3: Evaluating forecasts...")
results = precip.evaluate_forecasts(
    forecasts=forecast_regridded,
    observations=obs_regridded,
    lead_times=list(range(1, 29)),  # 28 days
    lat_range=(-60, 60)
)

# Step 4: Print results
print("\nEvaluation Results:")
print(f"Bias (7 days): {results['bias'][6]:.4f} mm/day")
print(f"RMSE (7 days): {results['rmse'][6]:.4f} mm/day")
print(f"Correlation (7 days): {results['correlation'][6]:.4f}")

# Step 5: Visualize comparison
print("\nStep 5: Creating visualizations...")
precip.plot_precipitation_comparison(
    forecast=forecast_regridded[6, :, :],  # 7-day lead time
    observation=obs_regridded[6, :, :],
    lead_time=7,
    output_file='forecast_comparison_7day.png'
)

# Step 6: Plot evaluation metrics
precip.plot_evaluation_metrics(
    metrics_dict=results,
    output_file='evaluation_metrics.png'
)

print("Analysis complete!")
```

---

### Long-Term Precipitation Forecast Module Configuration

All default settings are built into the package and can be customized through function parameters. You don't need to edit any configuration files - simply pass the desired values as arguments when calling functions:

- **MERRA Grid:** Grid resolution (0.625° x 0.5°), dimensions (576 x 361), and bounds (built-in defaults)
- **Evaluation Latitude Range:** Can be customized via `lat_range` parameter in evaluation functions (default: (-60, 60))
- **Lead Times:** Can be customized via `lead_times` parameter in evaluation functions (default: 1-28 days)
- **Input Observation Days:** 8 consecutive days of observations (built-in default)
- **Normalization Methods:** Available methods: 'standard', 'minmax', 'robust', 'log'
- **Output Directories:** Can be customized via `output_file` parameters (defaults: `./precipitation_figures`)
- **Figure Settings:** Can be customized via `figsize` and `dpi` parameters (defaults: `(12, 8)`, `300`)

---

### Nonlocal Parameterization Module

**Note:** This module requires the optional `windspharm` dependency. Install it with:

```bash
pip install wxcbench[nonlocal_parameterization]
```

The `nonlocal_parameterization` module provides functionality for processing ERA5 reanalysis data to compute and analyze momentum fluxes for nonlocal parameterization schemes in atmospheric models. This module consists of a three-step pipeline: downloading ERA5 model level data, computing momentum fluxes using Helmholtz decomposition, and coarse-graining the results to a T42 grid.

#### Import the Nonlocal Parameterization Module

```python
import wxcbench.nonlocal_parameterization as nonlocal
```

#### 1. Download ERA5 Model Level Data

**Function:** `download_era5_modellevel_data()`

**What it does:** Downloads ERA5 model level analysis fields from the CDS API. The function:

- Downloads temperature (T), zonal wind (U), meridional wind (V), and vertical velocity (W) fields
- Supports configurable date ranges (year, month, day range)
- Downloads hourly data at 0.3° resolution across 137 model levels
- Creates organized output files for each field and day

**Parameters:**

- `year` (int, required): The year for data download
- `month` (int, required): The month (1-12) for data download
- `start_day` (int, optional): The start day of the month (1-31). If None, uses 1 (default: None)
- `end_day` (int, optional): The end day of the month (1-31). If None, uses last day of month (default: None)
- `output_dir` (str, optional): Directory to save downloaded files (default: `./ERA5_data_ml`)
- `fields` (list, optional): List of field names to download. Options: ['T', 'U', 'V', 'W']. If None, downloads all fields (default: None)

**Example:**

```python
# Download ERA5 data for January 2020
files = nonlocal.download_era5_modellevel_data(
    year=2020,
    month=1,
    start_day=1,
    end_day=31,
    output_dir='./ERA5_data'
)

# Download specific fields only
files = nonlocal.download_era5_modellevel_data(
    year=2020,
    month=1,
    fields=['U', 'V', 'W'],
    output_dir='./ERA5_data'
)
```

**Output:**

- Creates output directory (default: `./ERA5_data_ml`)
- Downloads NetCDF files for each field and day:
  - Temperature: `T{YYYYMMDD}_ml.nc`
  - Zonal wind: `U{YYYYMMDD}_ml.nc`
  - Meridional wind: `V{YYYYMMDD}_ml.nc`
  - Vertical wind: `W{YYYYMMDD}_ml.nc`
- Returns list of paths to downloaded files

---

#### 2. Compute Momentum Fluxes

**Function:** `compute_momentum_flux_from_era5()`

**What it does:** Calculates resolved momentum fluxes from ERA5 data using Helmholtz decomposition. The function:

- Separates wind fields into rotational and divergent components using spherical harmonics
- Applies T21 truncation for scale separation (filtering large-scale patterns)
- Computes eddy momentum fluxes (uw, vw) for nonlocal parameterization
- Processes hourly data across all 137 model levels

**Parameters:**

- `year` (int, required): The year to process
- `month` (int, required): The month (1-12) to process
- `start_day` (int, optional): The start day of the month (1-31). If None, uses 1 (default: None)
- `end_day` (int, optional): The end day of the month (1-31). If None, uses last day of month (default: None)
- `era5_data_dir` (str, optional): Directory containing ERA5 model level data (default: `./ERA5_data_ml`)
- `output_dir` (str, optional): Directory to save computed momentum flux files (default: `./momentum_fluxes`)
- `truncation` (int, optional): Truncation wavenumber for scale separation (default: T21)
- `log_file` (str, optional): Path to log file. If None, prints to console (default: None)

**Example:**

```python
# Compute momentum fluxes for January 2020
flux_files = nonlocal.compute_momentum_flux_from_era5(
    year=2020,
    month=1,
    era5_data_dir='./ERA5_data_ml',
    output_dir='./momentum_fluxes'
)

# Use custom truncation
flux_files = nonlocal.compute_momentum_flux_from_era5(
    year=2020,
    month=1,
    truncation=42,  # T42 truncation
    log_file='./flux_compute.log'
)
```

**Output:**

- Creates output directory (default: `./momentum_fluxes`)
- Creates NetCDF files: `helmholtz_fluxes_hourly_era5_{day}{month_name}{year}.nc`
- Each file contains:
  - `uw`: Zonal flux of vertical momentum (Pa)
  - `vw`: Meridional flux of vertical momentum (Pa)
  - Dimensions: time (24 hours), level (137), lat, lon
- Returns list of paths to output files

---

#### 3. Coarse-grain Momentum Fluxes

**Function:** `coarsegrain_computed_momentum_fluxes()`

**What it does:** Regrids high-resolution momentum flux data to a coarser T42 grid and creates comprehensive training datasets. The function:

- Uses conservative regridding (xESMF) to preserve flux quantities
- Combines resolved momentum fluxes with additional derived fields
- Creates training-ready datasets with input/output fields for ML models
- Processes multiple months efficiently

**Parameters:**

- `year` (int, required): The year to process
- `start_month` (int, required): Starting month (1-12)
- `end_month` (int, required): Ending month (1-12)
- `start_day` (int, optional): Starting day of month (1-31). If None, uses 1 (default: None)
- `end_day` (int, optional): Ending day of month (1-31). If None, uses last day of month (default: None)
- `momentum_flux_dir` (str, optional): Directory containing momentum flux files (default: `./momentum_fluxes`)
- `training_data_dir` (str, optional): Directory to save training data files (default: `./training_data`)
- `t42_grid_file` (str, required): Path to T42 grid definition file (must contain 'lon', 'lat', 'lonb', 'latb' variables)
- `era5_data_dir` (str, optional): Directory containing original ERA5 data
- `model_levels_file` (str, optional): Path to ERA5 model levels Excel file
- `regridder_weights_file` (str, optional): Path to save/load regridding weights

**Example:**

```python
# Coarse-grain momentum fluxes for January-March 2020
training_files = nonlocal.coarsegrain_computed_momentum_fluxes(
    year=2020,
    start_month=1,
    end_month=3,
    t42_grid_file='./t42_lat_and_latb.nc',
    momentum_flux_dir='./momentum_fluxes',
    training_data_dir='./training_data'
)
```

**Output:**

- Creates output directory (default: `./training_data`)
- Creates NetCDF files: `era5_training_data_hourly_era5_{year}{month}{day}.nc`
- Each file contains input fields (u, v, w, temperature, pressure, gradients) and output fields (momentum fluxes)
- Returns list of paths to training data files

---

### Complete Nonlocal Parameterization Workflow Example

Here's a complete example that demonstrates the full pipeline:

```python
import wxcbench.nonlocal_parameterization as nonlocal

# Step 1: Download ERA5 model level data
print("Step 1: Downloading ERA5 data...")
nonlocal.download_era5_modellevel_data(
    year=2020,
    month=1,
    start_day=1,
    end_day=31,
    output_dir='./ERA5_data_ml'
)

# Step 2: Compute momentum fluxes
print("Step 2: Computing momentum fluxes...")
nonlocal.compute_momentum_flux_from_era5(
    year=2020,
    month=1,
    era5_data_dir='./ERA5_data_ml',
    output_dir='./momentum_fluxes'
)

# Step 3: Coarse-grain to T42 grid
print("Step 3: Coarse-graining to T42 grid...")
nonlocal.coarsegrain_computed_momentum_fluxes(
    year=2020,
    start_month=1,
    end_month=1,
    t42_grid_file='./t42_lat_and_latb.nc',
    momentum_flux_dir='./momentum_fluxes',
    training_data_dir='./training_data'
)

print("Processing complete!")
```

---

### Nonlocal Parameterization Module Configuration

All default settings are built into the package and can be customized through function parameters. You don't need to edit any configuration files - simply pass the desired values as arguments when calling functions:

- **ERA5 Grid Resolution:** 0.3° x 0.3° (built-in default)
- **ERA5 Model Levels:** 137 levels (1-137) (built-in default)
- **ERA5 Time Steps:** Hourly data (00-23) (built-in default)
- **Helmholtz Truncation:** T21 truncation for scale separation (default, can be customized)
- **T42 Grid:** 128 x 64 longitude/latitude points (built-in default)
- **Regridding Method:** Conservative regridding (preserves flux quantities)
- **Output Directories:** Can be customized via `output_dir` parameters (defaults: `./ERA5_data_ml`, `./momentum_fluxes`, `./training_data`)

---

### Weather Analog Module

The `weather_analog` module provides functionality for processing MERRA2 meteorological data by extracting specific variables (Sea Level Pressure and 2-meter Temperature) for defined geographic regions and time periods. This module is designed for creating weather analog datasets used in machine learning applications.

#### Import the Weather Analog Module

```python
import wxcbench.weather_analog as weather_analog
```

#### 1. Process Single File

**Function:** `process_single_file()`

**What it does:** Processes a single MERRA2 NetCDF file by extracting specified variables for a geographic region. The function:

- Opens MERRA2 NetCDF file
- Extracts selected variables (default: SLP and T2M)
- Filters data for specified geographic region
- Saves processed data to a new NetCDF file

**Parameters:**

- `input_file` (str, required): Path to input MERRA2 NetCDF file
- `output_file` (str, required): Path to output NetCDF file
- `variables` (list, optional): List of variable names to extract. Defaults to ['SLP', 'T2M'] (default: None)
- `lon_bounds` (tuple, optional): Longitude bounds as (min, max) in degrees. Defaults to (-15, 0) (default: None)
- `lat_bounds` (tuple, optional): Latitude bounds as (min, max) in degrees. Defaults to (42, 58) (default: None)
- `time_index` (list, optional): List of time indices to extract. Defaults to [0] (first time step) (default: None)

**Example:**

```python
# Process a single MERRA2 file
success = weather_analog.process_single_file(
    input_file='MERRA2.20190101.SUB.nc',
    output_file='MERRA2_SLP_T2M_20190101.nc',
    lon_bounds=(-15, 0),
    lat_bounds=(42, 58)
)

# Extract different variables
success = weather_analog.process_single_file(
    input_file='MERRA2.20190101.SUB.nc',
    output_file='MERRA2_processed.nc',
    variables=['SLP', 'T2M', 'T10M'],  # Add 10m temperature
    lon_bounds=(-20, 5),
    lat_bounds=(40, 60)
)
```

**Output:**

- Creates output directory if it doesn't exist
- Saves processed NetCDF file with extracted variables and region
- Returns True if processing succeeded, False otherwise

---

#### 2. Preprocess Weather Analog Data

**Function:** `preprocess_weather_analog()`

**What it does:** Main processing function that processes MERRA2 data files for a specified time period. The function:

- Iterates through dates in the specified range
- Automatically discovers MERRA2 input files using file naming patterns
- Processes each file to extract variables for the specified region
- Skips existing output files to avoid reprocessing
- Provides progress tracking

**Parameters:**

- `start_date` (datetime, optional): Start date for processing. Defaults to 2019-01-01 (default: None)
- `end_date` (datetime, optional): End date for processing. Defaults to 2021-12-31 (default: None)
- `input_dir` (str, optional): Directory containing MERRA2 input files (default: `./MERRA2_data`)
- `output_dir` (str, optional): Directory to save processed output files (default: `./MERRA2_processed`)
- `lon_bounds` (tuple, optional): Longitude bounds as (min, max) in degrees. Defaults to (-15, 0) (default: None)
- `lat_bounds` (tuple, optional): Latitude bounds as (min, max) in degrees. Defaults to (42, 58) (default: None)
- `variables` (list, optional): List of variable names to extract. Defaults to ['SLP', 'T2M'] (default: None)
- `skip_existing` (bool, optional): Skip processing if output file exists. Defaults to True (default: True)

**Example:**

```python
from datetime import datetime

# Process data for a specific time period
processed_files = weather_analog.preprocess_weather_analog(
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2019, 12, 31),
    input_dir='./MERRA2_data',
    output_dir='./MERRA2_processed',
    lon_bounds=(-15, 0),
    lat_bounds=(42, 58)
)

# Process with different geographic bounds
processed_files = weather_analog.preprocess_weather_analog(
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2020, 6, 30),
    input_dir='./MERRA2_data',
    output_dir='./MERRA2_processed',
    lon_bounds=(-20, 10),
    lat_bounds=(35, 65),
    skip_existing=False  # Reprocess even if output exists
)
```

**Output:**

- Creates output directory if it doesn't exist
- Processes each day in the date range
- Creates daily NetCDF files: `MERRA2_SLP_T2M_{YYYYMMDD}.nc`
- Prints progress messages for each file processed
- Returns list of paths to successfully processed output files

---

### Complete Weather Analog Workflow Example

Here's a complete example that demonstrates the full pipeline:

```python
import wxcbench.weather_analog as weather_analog
from datetime import datetime

# Process MERRA2 data for 2019
print("Step 1: Processing MERRA2 data...")
processed_files = weather_analog.preprocess_weather_analog(
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2019, 12, 31),
    input_dir='./MERRA2_data/M2I1NXASM',
    output_dir='./MERRA2_processed',
    lon_bounds=(-15, 0),
    lat_bounds=(42, 58)
)

print(f"Processed {len(processed_files)} files")

# Process a single file for verification
print("\nStep 2: Processing single file for verification...")
success = weather_analog.process_single_file(
    input_file='./MERRA2_data/M2I1NXASM/MERRA2.20190101.SUB.nc',
    output_file='./MERRA2_processed/test_20190101.nc',
    variables=['SLP', 'T2M'],
    lon_bounds=(-15, 0),
    lat_bounds=(42, 58)
)

if success:
    print("Single file processing successful!")
else:
    print("Single file processing failed!")

print("Workflow complete!")
```

---

### Weather Analog Module Configuration

All default settings are built into the package and can be customized through function parameters. You don't need to edit any configuration files - simply pass the desired values as arguments when calling functions:

- **Geographic Bounds:** Default region: 42°N-58°N, 15°W-0°E. Can be customized via `lon_bounds` and `lat_bounds` parameters
- **Time Period:** Default: 2019-01-01 to 2021-12-31. Can be customized via `start_date` and `end_date` parameters
- **Variables:** Default: ['SLP', 'T2M']. Can be customized via `variables` parameter
- **MERRA2 File Pattern:** `MERRA2*.{date}.SUB.nc` (built-in default)
- **Output File Pattern:** `MERRA2_SLP_T2M_{date}.nc` (built-in default)
- **Time Index:** Default: [0] (first time step). Can be customized via `time_index` parameter
- **Output Directories:** Can be customized via `input_dir` and `output_dir` parameters (defaults: `./MERRA2_data`, `./MERRA2_processed`)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.
