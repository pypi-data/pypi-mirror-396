"""
Hurricane Track Visualization

This module provides functionality for plotting hurricane tracks on geographic maps,
with color-coding based on storm intensity.
"""

from typing import Optional, List, Union
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import tropycal.tracks as tracks
import tropycal

from wxcbench.hurricane.config import (
    HURDAT2_URL,
    DEFAULT_BASIN,
    INTENSITY_BOUNDS,
    INTENSITY_LABELS,
    DEFAULT_FIGURE_SIZE,
    DEFAULT_DPI,
    DEFAULT_DOMAIN_BB,
    DEFAULT_OUTPUT_DIR,
)


def plot_track_from_xarray(hurdat, ax):
    """
    Plot the hurricane track and intensity from xarray data on the given axis.

    Parameters:
        hurdat (xarray.Dataset): Hurricane data in xarray format containing
            "lon", "lat", and "vmax" variables.
        ax (matplotlib.axes.Axes): The axis on which to plot the hurricane track.

    Returns:
        tuple: A tuple containing:
            - ax (matplotlib.axes.Axes): The updated axis after plotting
            - scatter (matplotlib.collections.PathCollection): The scatter points
            - bounds (numpy.ndarray): Array of boundaries for the intensity categories
    """
    # Define colormap and bounds for the intensity categories
    cmap = plt.cm.jet
    bounds = np.array(INTENSITY_BOUNDS)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
    # Plot hurricane track
    ax.plot(hurdat["lon"], hurdat["lat"], "k")
    
    # Plot scatter points with color representing wind speed
    scatter = ax.scatter(
        hurdat["lon"],
        hurdat["lat"],
        c=hurdat["vmax"],
        cmap=cmap,
        norm=norm
    )
    
    return ax, scatter, bounds


def plot_track(
    year: Optional[int] = None,
    storm_name: Optional[str] = None,
    basin: str = None,
    domain_bb: Optional[List[float]] = None,
    output_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    figsize: Optional[tuple] = None,
    dpi: int = None,
    show: bool = False
) -> None:
    """
    Plot hurricane tracks on a geographic map.

    This function retrieves hurricane data from the HURDAT2 dataset and plots
    tracks on a geographic domain. It supports both single storms and entire
    hurricane seasons.

    Parameters:
        year (int, optional): Year to plot. If None and storm_name is provided,
            plots the specific storm. If None and storm_name is None, defaults to 2017.
        storm_name (str, optional): Name of specific storm to plot. If None,
            plots all storms for the given year.
        basin (str, optional): Hurricane basin to use (default: 'north_atlantic').
        domain_bb (list, optional): Bounding box for the domain plot as
            [lon_min, lon_max, lat_min, lat_max]. Defaults to [-110, -20, 5, 55].
        output_file (str, optional): Path to save the figure. If None, generates
            filename automatically.
        output_dir (str, optional): Directory to save the figure. If None, uses
            default output directory from config.
        figsize (tuple, optional): Figure size as (width, height). If None, uses
            default from config.
        dpi (int, optional): Resolution for saved figure. If None, uses default
            from config.
        show (bool): Whether to display the plot (default: False).

    Returns:
        None

    Example:
        >>> plot_track(year=2017)
        >>> plot_track(storm_name='harvey', year=2017)
    """
    # Set defaults
    if basin is None:
        basin = DEFAULT_BASIN
    
    if domain_bb is None:
        domain_bb = DEFAULT_DOMAIN_BB
    
    if year is None:
        year = 2017
    
    if figsize is None:
        figsize = DEFAULT_FIGURE_SIZE
    
    if dpi is None:
        dpi = DEFAULT_DPI
    
    # Set matplotlib parameters
    plt.rcParams.update({
        "font.size": 14,
        "font.weight": "bold",
        "savefig.dpi": dpi
    })
    
    # Load the basin hurricane data
    basin_data = tracks.TrackDataset(basin=basin, atlantic_url=HURDAT2_URL)
    
    # Get hurricane data
    if storm_name is not None:
        # Single storm
        hurdat = basin_data.get_storm((storm_name, year))
    else:
        # All storms for the year
        hurdat = [
            basin_data.get_storm((name, year))
            for name in basin_data.get_season(year).to_dataframe()["name"].values
        ]
    
    # Plot domain (using a simple approach if plot_domain is not available)
    # Note: The original code uses plot_domain from src_utils.coast, which may
    # not be available. We'll create a basic geographic plot instead.
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set domain bounds
    ax.set_xlim(domain_bb[0], domain_bb[1])
    ax.set_ylim(domain_bb[2], domain_bb[3])
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, alpha=0.3)
    
    # Plot tracks
    if isinstance(hurdat, tropycal.tracks.storm.Storm):
        # Single storm
        ax, scatter, bounds = plot_track_from_xarray(hurdat, ax)
        ax.set_title(f'{hurdat.attrs["name"]} ({hurdat.attrs["year"]})'.upper())
    else:
        # Multiple storms
        for hurdat_tracks in hurdat:
            ax, scatter, bounds = plot_track_from_xarray(hurdat_tracks, ax)
        ax.set_title(f'{year} Atlantic Hurricane Season'.upper())
    
    # Add color bar with intensity category labels
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_ticks((bounds[:-1] + bounds[1:]) / 2)
    cbar.set_ticklabels(INTENSITY_LABELS)
    cbar.set_label('Hurricane Category', rotation=270, labelpad=20)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save or show figure
    if output_file is None:
        import os
        if output_dir is None:
            output_dir = DEFAULT_OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        if storm_name:
            output_file = f'{output_dir}/Track_{storm_name.upper()}_{year}.png'
        else:
            output_file = f'{output_dir}/Track_Season_{year}.png'
    
    if output_file:
        plt.savefig(output_file, dpi=dpi)
    
    if show:
        plt.show()
    else:
        plt.close()

