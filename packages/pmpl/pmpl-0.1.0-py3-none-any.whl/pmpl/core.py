"""Core style definitions for pmpl (Python Matplotlib Plotting Library).

This module defines the base styles and variants used throughout the package.
"""

from typing import Any

# Base style for all plots - presentation-ready defaults
BASE_STYLE: dict[str, Any] = {
    "font.family": "Arial",
    "axes.labelsize": 14,
    "figure.dpi": 95,
    "savefig.dpi": 95,
    "axes.spines.top": False,
    "axes.spines.left": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "axes.axisbelow": True,
    "axes.titlesize": 16,
    "figure.titlesize": 16,
    "grid.alpha": 0.3,
    "ytick.major.size": 0,
    "ytick.minor.size": 0,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.frameon": False,
    "legend.fontsize": 11,
}

# Horizontal plot style (e.g., horizontal bar charts)
# Shows left spine, vertical gridlines
HORIZONTAL_STYLE: dict[str, Any] = {
    **BASE_STYLE,
    "axes.spines.left": True,
    "axes.spines.bottom": False,
    "axes.grid.axis": "x",
    "xtick.major.size": 0,
    "xtick.minor.size": 0,
    "ytick.major.size": 5,
    "ytick.minor.size": 0,
}

# Vertical plot style (e.g., line charts, vertical bar charts)
# Shows bottom spine, horizontal gridlines
VERTICAL_STYLE: dict[str, Any] = {
    **BASE_STYLE,
    "axes.spines.bottom": True,
    "axes.spines.left": False,
    "axes.grid.axis": "y",
    "xtick.major.size": 5,
    "xtick.minor.size": 0,
    "ytick.major.size": 0,
    "ytick.minor.size": 0,
}

# Registry of available styles
STYLES: dict[str, dict[str, Any]] = {
    "base": BASE_STYLE,
    "horizontal": HORIZONTAL_STYLE,
    "vertical": VERTICAL_STYLE,
}
