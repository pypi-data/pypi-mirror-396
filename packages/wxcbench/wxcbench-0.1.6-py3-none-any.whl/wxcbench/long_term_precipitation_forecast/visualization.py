"""
Visualization Utilities for Long-Term Precipitation Forecasts

This module provides functions for visualizing precipitation forecasts,
observations, and evaluation metrics.
"""

from typing import Optional, Union, Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
import xarray as xr

from wxcbench.long_term_precipitation_forecast.config import (
    DEFAULT_FIGURE_SIZE,
    DEFAULT_DPI,
    DEFAULT_VISUALIZATION_OUTPUT_DIR,
    MAX_LEAD_TIME_DAYS,
)


def plot_precipitation_comparison(
    forecast: Union[np.ndarray, xr.DataArray],
    observation: Union[np.ndarray, xr.DataArray],
    lead_time: Optional[int] = None,
    lon: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    output_file: Optional[Union[str, Path]] = None,
    figsize: Optional[Tuple[int, int]] = None,
    dpi: int = None,
    vmax: Optional[float] = None,
    cmap: str = "YlGnBu",
) -> plt.Figure:
    """
    Plot side-by-side comparison of forecast and observation precipitation.

    Parameters:
        forecast (np.ndarray or xr.DataArray): Forecast precipitation data.
            Shape: (lat, lon) or (lead_time, lat, lon).
        observation (np.ndarray or xr.DataArray): Observed precipitation data.
            Shape: (lat, lon) or (lead_time, lat, lon).
        lead_time (int, optional): Lead time index to plot if data is 3D.
        lon (np.ndarray or xr.DataArray, optional): Longitude coordinates.
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates.
        output_file (str or Path, optional): Path to save the figure.
        figsize (tuple, optional): Figure size (width, height).
        dpi (int, optional): Figure resolution (default: 300).
        vmax (float, optional): Maximum value for color scale.
        cmap (str): Colormap name (default: 'YlGnBu').

    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    if figsize is None:
        figsize = DEFAULT_FIGURE_SIZE
    if dpi is None:
        dpi = DEFAULT_DPI

    # Extract coordinates if xarray
    if isinstance(forecast, xr.DataArray):
        if lon is None:
            lon = forecast.coords.get("lon", forecast.coords.get("longitude"))
        if lat is None:
            lat = forecast.coords.get("lat", forecast.coords.get("latitude"))
        forecast = forecast.values

    if isinstance(observation, xr.DataArray):
        obs_lon = observation.coords.get("lon", observation.coords.get("longitude"))
        obs_lat = observation.coords.get("lat", observation.coords.get("latitude"))
        observation = observation.values
        if lon is None:
            lon = obs_lon
        if lat is None:
            lat = obs_lat

    forecast = np.asarray(forecast)
    observation = np.asarray(observation)

    # Select lead time if 3D
    if forecast.ndim == 3:
        if lead_time is None:
            lead_time = 0
        forecast = forecast[lead_time, :, :]

    if observation.ndim == 3:
        if lead_time is None:
            lead_time = 0
        observation = observation[lead_time, :, :]

    lon = np.asarray(lon)
    lat = np.asarray(lat)

    # Create meshgrid for plotting
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    # Determine color scale limits
    if vmax is None:
        vmax = max(np.nanmax(forecast), np.nanmax(observation))

    # Create figure with subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(figsize[0] * 1.5, figsize[1]))

    # Plot forecast
    im1 = ax1.contourf(lon_grid, lat_grid, forecast, levels=20, cmap=cmap, vmin=0, vmax=vmax)
    ax1.set_title(f"Forecast (Lead Time: {lead_time} days)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Longitude")
    ax1.set_ylabel("Latitude")
    ax1.grid(True, alpha=0.3)
    plt.colorbar(im1, ax=ax1, label="Precipitation (mm/day)")

    # Plot observation
    im2 = ax2.contourf(lon_grid, lat_grid, observation, levels=20, cmap=cmap, vmin=0, vmax=vmax)
    ax2.set_title("Observation", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Longitude")
    ax2.set_ylabel("Latitude")
    ax2.grid(True, alpha=0.3)
    plt.colorbar(im2, ax=ax2, label="Precipitation (mm/day)")

    # Plot difference
    difference = forecast - observation
    vmax_diff = np.nanmax(np.abs(difference))
    im3 = ax3.contourf(
        lon_grid,
        lat_grid,
        difference,
        levels=20,
        cmap="RdBu_r",
        vmin=-vmax_diff,
        vmax=vmax_diff,
    )
    ax3.set_title("Difference (Forecast - Observation)", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Longitude")
    ax3.set_ylabel("Latitude")
    ax3.grid(True, alpha=0.3)
    plt.colorbar(im3, ax=ax3, label="Precipitation Difference (mm/day)")

    plt.tight_layout()

    # Save figure if output file specified
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()

    return fig


def plot_evaluation_metrics(
    metrics_dict: Dict[str, Union[np.ndarray, List[float]]],
    lead_times: Optional[List[int]] = None,
    output_file: Optional[Union[str, Path]] = None,
    figsize: Optional[Tuple[int, int]] = None,
    dpi: int = None,
    metrics_to_plot: Optional[List[str]] = None,
) -> plt.Figure:
    """
    Plot evaluation metrics as a function of lead time.

    Parameters:
        metrics_dict (dict): Dictionary with metric names as keys and arrays
            of values as values. Should include 'lead_times' key.
        lead_times (list, optional): List of lead times in days.
            If None, uses 'lead_times' from metrics_dict (default: None).
        output_file (str or Path, optional): Path to save the figure.
        figsize (tuple, optional): Figure size (width, height).
        dpi (int, optional): Figure resolution (default: 300).
        metrics_to_plot (list, optional): List of metrics to plot.
            If None, plots all metrics except 'lead_times' (default: None).

    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    if figsize is None:
        figsize = DEFAULT_FIGURE_SIZE
    if dpi is None:
        dpi = DEFAULT_DPI

    # Extract lead times
    if lead_times is None:
        lead_times = metrics_dict.get("lead_times", list(range(len(next(iter(metrics_dict.values()))))))
    lead_times = np.asarray(lead_times)

    # Determine which metrics to plot
    if metrics_to_plot is None:
        metrics_to_plot = [k for k in metrics_dict.keys() if k != "lead_times"]

    if not metrics_to_plot:
        raise ValueError("No metrics to plot")

    # Create subplots
    n_metrics = len(metrics_to_plot)
    fig, axes = plt.subplots(
        n_metrics, 1, figsize=(figsize[0], figsize[1] * n_metrics), sharex=True
    )

    if n_metrics == 1:
        axes = [axes]

    # Plot each metric
    for i, metric in enumerate(metrics_to_plot):
        if metric not in metrics_dict:
            continue

        values = np.asarray(metrics_dict[metric])
        axes[i].plot(lead_times, values, marker="o", linewidth=2, markersize=6)

        # Add labels and formatting
        metric_label = metric.upper().replace("_", " ")
        axes[i].set_ylabel(metric_label, fontweight="bold")
        axes[i].grid(True, alpha=0.3)
        axes[i].set_title(f"{metric_label} vs Lead Time", fontsize=11, fontweight="bold")

    axes[-1].set_xlabel("Lead Time (days)", fontweight="bold")
    plt.tight_layout()

    # Save figure if output file specified
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()

    return fig


def plot_spatial_distribution(
    data: Union[np.ndarray, xr.DataArray],
    title: str = "Precipitation Distribution",
    lon: Optional[Union[np.ndarray, xr.DataArray]] = None,
    lat: Optional[Union[np.ndarray, xr.DataArray]] = None,
    output_file: Optional[Union[str, Path]] = None,
    figsize: Optional[Tuple[int, int]] = None,
    dpi: int = None,
    cmap: str = "YlGnBu",
    vmax: Optional[float] = None,
) -> plt.Figure:
    """
    Plot spatial distribution of precipitation data.

    Parameters:
        data (np.ndarray or xr.DataArray): Precipitation data. Shape: (lat, lon)
            or (time, lat, lon).
        title (str): Plot title (default: 'Precipitation Distribution').
        lon (np.ndarray or xr.DataArray, optional): Longitude coordinates.
        lat (np.ndarray or xr.DataArray, optional): Latitude coordinates.
        output_file (str or Path, optional): Path to save the figure.
        figsize (tuple, optional): Figure size (width, height).
        dpi (int, optional): Figure resolution (default: 300).
        cmap (str): Colormap name (default: 'YlGnBu').
        vmax (float, optional): Maximum value for color scale.

    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    if figsize is None:
        figsize = DEFAULT_FIGURE_SIZE
    if dpi is None:
        dpi = DEFAULT_DPI

    # Extract coordinates if xarray
    if isinstance(data, xr.DataArray):
        if lon is None:
            lon = data.coords.get("lon", data.coords.get("longitude"))
        if lat is None:
            lat = data.coords.get("lat", data.coords.get("latitude"))
        data = data.values

    data = np.asarray(data)
    lon = np.asarray(lon)
    lat = np.asarray(lat)

    # Handle 3D data (average over time)
    if data.ndim == 3:
        data = np.nanmean(data, axis=0)

    # Create meshgrid
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Determine color scale limits
    if vmax is None:
        vmax = np.nanmax(data)

    # Plot
    im = ax.contourf(lon_grid, lat_grid, data, levels=20, cmap=cmap, vmin=0, vmax=vmax)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitude", fontweight="bold")
    ax.set_ylabel("Latitude", fontweight="bold")
    ax.grid(True, alpha=0.3)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Precipitation (mm/day)", fontweight="bold")

    plt.tight_layout()

    # Save figure if output file specified
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()

    return fig


def plot_lead_time_comparison(
    forecasts: Union[np.ndarray, xr.DataArray],
    observations: Union[np.ndarray, xr.DataArray],
    lead_times: Optional[List[int]] = None,
    n_lead_times: int = 4,
    output_file: Optional[Union[str, Path]] = None,
    figsize: Optional[Tuple[int, int]] = None,
    dpi: int = None,
) -> plt.Figure:
    """
    Plot forecast and observation comparison for multiple lead times.

    Creates a grid of subplots showing forecasts and observations at different lead times.

    Parameters:
        forecasts (np.ndarray or xr.DataArray): Forecast data. Shape: (lead_time, lat, lon).
        observations (np.ndarray or xr.DataArray): Observation data. Shape: (lead_time, lat, lon).
        lead_times (list, optional): List of lead times to plot.
        n_lead_times (int): Number of lead times to plot (default: 4).
        output_file (str or Path, optional): Path to save the figure.
        figsize (tuple, optional): Figure size (width, height).
        dpi (int, optional): Figure resolution (default: 300).

    Returns:
        matplotlib.figure.Figure: The created figure.
    """
    if figsize is None:
        figsize = DEFAULT_FIGURE_SIZE
    if dpi is None:
        dpi = DEFAULT_DPI

    # Extract data
    if isinstance(forecasts, xr.DataArray):
        forecasts = forecasts.values
    if isinstance(observations, xr.DataArray):
        observations = observations.values

    forecasts = np.asarray(forecasts)
    observations = np.asarray(observations)

    # Determine which lead times to plot
    if lead_times is None:
        n_total = forecasts.shape[0]
        step = max(1, n_total // n_lead_times)
        lead_times = list(range(0, n_total, step))[:n_lead_times]
    else:
        lead_times = lead_times[:n_lead_times]

    # Create subplots
    fig, axes = plt.subplots(
        len(lead_times), 2, figsize=(figsize[0] * 1.5, figsize[1] * len(lead_times))
    )
    if len(lead_times) == 1:
        axes = axes.reshape(1, -1)

    vmax = max(np.nanmax(forecasts), np.nanmax(observations))

    for i, lt in enumerate(lead_times):
        # Plot forecast
        im1 = axes[i, 0].imshow(
            forecasts[lt, :, :],
            aspect="auto",
            cmap="YlGnBu",
            vmin=0,
            vmax=vmax,
            origin="lower",
        )
        axes[i, 0].set_title(f"Forecast (Lead Time: {lt} days)", fontweight="bold")
        plt.colorbar(im1, ax=axes[i, 0])

        # Plot observation
        im2 = axes[i, 1].imshow(
            observations[lt, :, :],
            aspect="auto",
            cmap="YlGnBu",
            vmin=0,
            vmax=vmax,
            origin="lower",
        )
        axes[i, 1].set_title(f"Observation (Lead Time: {lt} days)", fontweight="bold")
        plt.colorbar(im2, ax=axes[i, 1])

    plt.tight_layout()

    # Save figure if output file specified
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=dpi, bbox_inches="tight")
    else:
        plt.show()

    return fig

