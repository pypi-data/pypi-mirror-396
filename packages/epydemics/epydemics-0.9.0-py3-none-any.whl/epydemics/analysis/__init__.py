"""
Analysis module for epydemics package.

This module provides visualization and evaluation functionality
for epidemiological models and forecasts.

Modules:
    visualization: Functions for plotting and visualizing epidemic data and forecasts
    evaluation: Metrics and evaluation functions for model performance assessment
    formatting: Utilities for professional plot formatting and styling
"""

from .evaluation import evaluate_forecast, evaluate_model
from .visualization import visualize_results
from .formatting import (
    format_time_axis,
    format_subplot_grid,
    add_forecast_highlight,
    set_professional_style,
)

__all__ = [
    "evaluate_forecast",
    "evaluate_model",
    "visualize_results",
    "format_time_axis",
    "format_subplot_grid",
    "add_forecast_highlight",
    "set_professional_style",
]
