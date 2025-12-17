"""
Hurricane Module

This module provides functionality for analyzing and visualizing hurricane tracks
and intensities from the HURDAT2 dataset maintained by the National Hurricane Center (NHC).
"""

from wxcbench.hurricane.hurricane_intensity import plot_intensity
from wxcbench.hurricane.hurricane_track import plot_track, plot_track_from_xarray

__all__ = [
    "plot_intensity",
    "plot_track",
    "plot_track_from_xarray",
]

