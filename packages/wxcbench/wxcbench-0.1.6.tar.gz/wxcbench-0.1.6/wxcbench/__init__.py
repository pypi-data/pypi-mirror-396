"""
WxC-Bench: Multi-modal dataset toolkit for weather and climate downstream tasks
"""

__version__ = "0.1.6"
__author__ = "Prajun Trital"
__license__ = "MIT"

from wxcbench import aviation_turbulence
from wxcbench import forecast_report_generation
from wxcbench import hurricane
from wxcbench import weather_analog
from wxcbench import long_term_precipitation_forecast

# Lazy import for optional dependency (nonlocal_parameterization requires windspharm)
# Import only when explicitly accessed to avoid errors if windspharm is not installed
_nonlocal_parameterization = None

def __getattr__(name):
    """Lazy import for nonlocal_parameterization module."""
    if name == "nonlocal_parameterization":
        global _nonlocal_parameterization
        if _nonlocal_parameterization is None:
            try:
                from wxcbench import nonlocal_parameterization
                _nonlocal_parameterization = nonlocal_parameterization
            except ImportError as e:
                raise ImportError(
                    "The nonlocal_parameterization module requires windspharm. "
                    "Install it with: pip install wxcbench[nonlocal_parameterization]"
                ) from e
        return _nonlocal_parameterization
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "aviation_turbulence",
    "forecast_report_generation",
    "hurricane",
    "weather_analog",
    "long_term_precipitation_forecast",
    "nonlocal_parameterization",
]
