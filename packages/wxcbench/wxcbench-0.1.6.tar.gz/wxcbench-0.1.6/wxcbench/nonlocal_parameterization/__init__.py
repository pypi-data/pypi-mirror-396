"""
Nonlocal Parameterization Module

This module provides functionality for processing ERA5 reanalysis data to compute
and analyze momentum fluxes for nonlocal parameterization schemes in atmospheric models.
"""

from wxcbench.nonlocal_parameterization.download_era5 import download_era5_modellevel_data
from wxcbench.nonlocal_parameterization.compute_momentum_flux import compute_momentum_flux_from_era5
from wxcbench.nonlocal_parameterization.coarsegrain_fluxes import coarsegrain_computed_momentum_fluxes

__all__ = [
    "download_era5_modellevel_data",
    "compute_momentum_flux_from_era5",
    "coarsegrain_computed_momentum_fluxes",
]

