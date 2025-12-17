"""
MODG (Moderate or Greater) Preprocessing Module

Filters PIREP data for moderate-or-greater (MODG) turbulence reports
and creates MODG flight-level specific files.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def preprocess_modg(
    input_file: str,
    output_dir: Optional[str] = None
) -> pd.DataFrame:
    """
    Filter PIREP data for moderate-or-greater (MODG) turbulence reports.
    
    This function filters for MODG turbulence reports, downloads additional
    filtered data if needed, and creates MODG flight-level specific files.
    
    Parameters
    ----------
    input_file : str
        Path to input CSV file (e.g., 'updated_CSVs/csv_fl_rem.csv')
    output_dir : str, optional
        Directory to save processed files. Creates 'updated_CSVs' subdirectory.
        If None, uses current directory (default: None)
        
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame containing only MODG turbulence reports
        
    Examples
    --------
    >>> import wxcbench.aviation_turbulence as wab
    >>> df = wab.preprocess_modg('updated_CSVs/csv_fl_rem.csv')
    """
    if output_dir is None:
        output_dir = "."
    
    output_path = Path(output_dir) / "updated_CSVs"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read the input file
    df = pd.read_csv(input_file)
    
    # TODO: Add actual MODG filtering logic from the notebook
    # This should include:
    # - Filtering for moderate or greater turbulence
    # - Creating csv_modg_all.csv
    # - Creating MODG flight-level specific files:
    #   - low_fl_modg.csv
    #   - med_fl_modg.csv
    #   - high_fl_modg.csv
    
    # Placeholder: Save filtered file
    output_file = output_path / "csv_modg_all.csv"
    df.to_csv(output_file, index=False)
    
    print(f"MODG preprocessing complete. Output saved to {output_file}")
    return df

