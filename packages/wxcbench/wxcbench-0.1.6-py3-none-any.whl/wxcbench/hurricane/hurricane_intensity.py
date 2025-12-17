"""
Hurricane Intensity Analysis

This module provides functionality for plotting hurricane intensity metrics
over time, including maximum sustained wind speed and minimum sea level pressure.
"""

from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import tropycal.tracks as tracks

from wxcbench.hurricane.config import (
    HURDAT2_URL,
    DEFAULT_FIGURE_SIZE,
    DEFAULT_DPI,
    DEFAULT_OUTPUT_DIR,
)


def plot_intensity(
    name: str = 'michael',
    year: int = 2018,
    start: int = 1,
    skip: int = 10,
    output_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    figsize: Optional[tuple] = None,
    dpi: int = None
) -> None:
    """
    Plot the intensity of a hurricane over time using maximum sustained wind speed
    and minimum sea pressure.

    Parameters:
        name (str): The name of the hurricane (default: 'michael').
        year (int): The year of the hurricane (default: 2018).
        start (int): The index to start plotting the data (default: 1).
        skip (int): The number of data points to skip when plotting (default: 10).
        output_file (str, optional): Path to save the figure. If None, generates
            filename automatically.
        output_dir (str, optional): Directory to save the figure. If None, uses
            default output directory from config.
        figsize (tuple, optional): Figure size as (width, height). If None, uses
            default from config.
        dpi (int, optional): Resolution for saved figure. If None, uses default
            from config.

    Returns:
        None

    Example:
        >>> plot_intensity(name='harvey', year=2017, start=2)
    """
    # Set output directory
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    # Set figure size
    if figsize is None:
        figsize = DEFAULT_FIGURE_SIZE
    
    # Set DPI
    if dpi is None:
        dpi = DEFAULT_DPI
    
    # Load hurricane data
    basin = tracks.TrackDataset(basin='north_atlantic', atlantic_url=HURDAT2_URL)
    storm = basin.get_storm((name, year))
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Plot maximum sustained wind speed
    color = 'tab:blue'
    ax.plot(storm['date'][start:-skip], storm['vmax'][start:-skip], color=color, marker='d')
    ax.set_ylabel('Maximum Sustained Wind Speed (kt)', color=color)
    ax.set_xlabel('Date (YYYY-MM-DD)', color='k')
    ax.set_yticks(np.arange(0, 150, 30))
    ax.tick_params(axis='y', labelcolor=color)
    
    # Plot minimum sea level pressure on secondary axis
    ax2 = ax.twinx()
    color = 'tab:red'
    ax2.plot(storm['date'][start:-skip], storm['mslp'][start:-skip], color=color, marker='d')
    ax2.set_ylabel('Minimum Sea Pressure Level (hPa)', color=color)
    ax.tick_params(axis='x', which='major', rotation=30, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Add grid and title
    ax.grid()
    ax.set_title(f'{name.upper()} {year}')
    plt.tight_layout()
    
    # Save or show figure
    if output_file is None:
        import os
        os.makedirs(output_dir, exist_ok=True)
        output_file = f'{output_dir}/Intensity_{name.upper()}_{year}.jpeg'
    
    plt.savefig(output_file, dpi=dpi)
    plt.close()

