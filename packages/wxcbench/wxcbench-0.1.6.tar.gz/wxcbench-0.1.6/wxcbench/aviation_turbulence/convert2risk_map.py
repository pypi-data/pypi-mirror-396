"""
Convert to Risk Map Module

Visualizes PIREP spatial distribution by converting to risk maps.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt


def convert_to_risk_map(
    input_file: str,
    output_file: Optional[str] = None,
    **kwargs
) -> None:
    """
    Convert PIREP data to a risk map visualization.
    
    This function visualizes the spatial distribution of PIREPs by creating
    a risk map showing turbulence occurrence patterns.
    
    Parameters
    ----------
    input_file : str
        Path to input CSV file containing PIREP data
    output_file : str, optional
        Path to save the visualization. If None, saves to current directory
        with default name (default: None)
    **kwargs
        Additional keyword arguments for customization
        
    Examples
    --------
    >>> import wxcbench.aviation_turbulence as wab
    >>> wab.convert_to_risk_map('updated_CSVs/csv_fl_rem.csv')
    """
    # Read the input file
    df = pd.read_csv(input_file)
    
    # TODO: Add actual risk map conversion logic from the notebook
    # This should include:
    # - Creating spatial distribution visualization
    # - Converting to risk map format
    # - Saving visualization
    
    if output_file is None:
        output_file = "pirep_risk_map.png"
    
    # Placeholder: Create a simple visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot latitude vs longitude if available
    if 'LAT' in df.columns and 'LON' in df.columns:
        ax.scatter(df['LON'], df['LAT'], alpha=0.1, s=1)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('PIREP Spatial Distribution')
    
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Risk map saved to {output_file}")

