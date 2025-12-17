"""
Turbulence EDA Preprocessing Module

Performs exploratory data analysis and preprocessing on PIREP data.
Adds new columns, filters data, and creates flight-level specific files.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def preprocess_turb_eda(
    input_file: str,
    output_dir: Optional[str] = None
) -> pd.DataFrame:
    """
    Perform exploratory data analysis and preprocessing on PIREP data.
    
    This function performs EDA, adds new columns, filters data, and creates
    flight-level specific files (low_fl.csv, med_fl.csv, high_fl.csv).
    
    Parameters
    ----------
    input_file : str
        Path to input CSV file (e.g., 'pirep_downloads/all_pireps.csv')
    output_dir : str, optional
        Directory to save processed files. Creates 'updated_CSVs' subdirectory.
        If None, uses current directory (default: None)
        
    Returns
    -------
    pd.DataFrame
        Processed DataFrame
        
    Examples
    --------
    >>> import wxcbench.aviation_turbulence as wab
    >>> df = wab.preprocess_turb_eda('pirep_downloads/all_pireps.csv')
    """
    if output_dir is None:
        output_dir = "."
    
    output_path = Path(output_dir) / "updated_CSVs"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read the input file
    df = pd.read_csv(input_file)
    
    # TODO: Add actual preprocessing logic from the notebook
    # This should include:
    # - Adding new columns
    # - Filtering data
    # - Creating flight-level specific files
    
    # Placeholder: Save processed file
    output_file = output_path / "csv_fl_rem.csv"
    df.to_csv(output_file, index=False)
    
    # TODO: Create flight-level specific files
    # - low_fl.csv
    # - med_fl.csv
    # - high_fl.csv
    
    print(f"Preprocessing complete. Output saved to {output_file}")
    return df

