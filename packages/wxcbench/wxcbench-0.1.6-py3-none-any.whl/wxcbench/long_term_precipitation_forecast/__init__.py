"""
Long-Term Precipitation Forecast Module

This module provides utilities for evaluating and analyzing long-term
precipitation forecasts (up to 4 weeks lead time) from satellite observations.
"""

# Evaluation functions
from wxcbench.long_term_precipitation_forecast.evaluation import (
    compute_bias,
    compute_mse,
    compute_rmse,
    compute_correlation,
    compute_mae,
    evaluate_forecasts,
    area_weighted_mean,
)

# Data loading functions
from wxcbench.long_term_precipitation_forecast.data_loading import (
    load_precipitation_data,
    load_satellite_observations,
    combine_observations,
    prepare_training_data,
    load_evaluation_data,
)

# Preprocessing functions
from wxcbench.long_term_precipitation_forecast.preprocessing import (
    regrid_to_merra,
    normalize_data,
    align_temporal_data,
    create_merra_grid,
)

# Visualization functions
from wxcbench.long_term_precipitation_forecast.visualization import (
    plot_precipitation_comparison,
    plot_evaluation_metrics,
    plot_spatial_distribution,
    plot_lead_time_comparison,
)

__all__ = [
    # Evaluation
    "compute_bias",
    "compute_mse",
    "compute_rmse",
    "compute_correlation",
    "compute_mae",
    "evaluate_forecasts",
    "area_weighted_mean",
    # Data loading
    "load_precipitation_data",
    "load_satellite_observations",
    "combine_observations",
    "prepare_training_data",
    "load_evaluation_data",
    # Preprocessing
    "regrid_to_merra",
    "normalize_data",
    "align_temporal_data",
    "create_merra_grid",
    # Visualization
    "plot_precipitation_comparison",
    "plot_evaluation_metrics",
    "plot_spatial_distribution",
    "plot_lead_time_comparison",
]

