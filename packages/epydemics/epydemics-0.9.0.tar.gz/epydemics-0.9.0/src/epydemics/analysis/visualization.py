"""
Visualization functions for epidemiological models and forecasts.

This module provides functions to visualize epidemic data, model results,
and forecasts with various plotting options.
"""

from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd

from ..core.constants import (
    CENTRAL_TENDENCY_METHODS,
    COMPARTMENT_LABELS,
    METHOD_COLORS,
    METHOD_NAMES,
)
from .formatting import format_time_axis


def visualize_results(
    results: Dict[str, Any],
    compartment_code: str,
    testing_data: Optional[pd.DataFrame] = None,
    log_response: bool = False,
    alpha: float = 0.3,
    format_axis: bool = True,
) -> None:
    """
    Visualize forecast results for a specific compartment.

    Args:
        results: Dictionary containing forecast results for each compartment
        compartment_code: Code of the compartment to visualize (e.g., 'C', 'D', 'I')
        testing_data: Optional DataFrame with actual values for comparison
        log_response: Whether to use logarithmic scale for y-axis
        alpha: Transparency for simulation paths
        format_axis: Apply professional time axis formatting (default: True)

    Raises:
        KeyError: If compartment_code is not found in results

    Examples:
        >>> results = model.results
        >>> visualize_results(
        ...     results,
        ...     "C",
        ...     testing_data=test_df,
        ...     log_response=True,
        ...     format_axis=True
        ... )
    """
    if compartment_code not in results:
        raise KeyError(f"Compartment '{compartment_code}' not found in results")

    compartment = results[compartment_code]

    # Plot individual simulation paths with low alpha
    for col in compartment.columns:
        if col not in CENTRAL_TENDENCY_METHODS:  # Skip central tendency methods
            plt.plot(
                compartment.index,
                compartment[col].values,
                color="gray",
                alpha=alpha,
                linestyle="--",
            )

    # Plot central tendency methods
    for i, method in enumerate(CENTRAL_TENDENCY_METHODS):
        if method in compartment:
            central_tendency = compartment[method]
            plt.plot(
                central_tendency.index,
                central_tendency.values,
                color=METHOD_COLORS[method],
                label=METHOD_NAMES[method],
                linewidth=2,
            )

    # Plot actual testing data if provided
    if testing_data is not None and compartment_code in testing_data.columns:
        plt.plot(
            testing_data.index,
            testing_data[compartment_code],
            color="red",
            label="Actual",
            linewidth=2,
        )

    plt.xlabel("Date")
    plt.ylabel(f"{COMPARTMENT_LABELS[compartment_code]} Cases")
    plt.title(f"Forecast for {COMPARTMENT_LABELS[compartment_code]}")
    plt.legend()
    plt.grid(True, alpha=0.3)

    if log_response:
        plt.yscale("log")

    # Apply professional time axis formatting if requested
    if format_axis:
        ax = plt.gca()
        format_time_axis(ax, compartment.index, time_range="auto")

    plt.tight_layout()
    plt.show()
