"""pmpl - Python Matplotlib Plotting Library.

A library for quickly formatting matplotlib plots in a consistent,
presentation-ready style.

Main features:
    - Context managers for temporary style application
    - Direct axis formatting functions
    - Preset styles for horizontal and vertical plots
    - Easy extensibility for custom styles

Example usage:
    >>> import pmpl
    >>> import matplotlib.pyplot as plt
    >>>
    >>> # Using context manager
    >>> with pmpl.style('horizontal'):
    ...     fig, ax = plt.subplots()
    ...     ax.barh(['A', 'B'], [1, 2])
    >>>
    >>> # Direct axis formatting
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 2])
    >>> pmpl.format_vertical(ax)
    >>>
    >>> # Set global defaults
    >>> pmpl.set_defaults('vertical')
"""

from .core import BASE_STYLE, HORIZONTAL_STYLE, STYLES, VERTICAL_STYLE
from .formatters import format_base, format_horizontal, format_vertical
from .styles import set_defaults, style

__all__ = [
    # Context managers and style setters
    "style",
    "set_defaults",
    # Axis formatters
    "format_horizontal",
    "format_vertical",
    "format_base",
    # Style dictionaries (for advanced users)
    "BASE_STYLE",
    "HORIZONTAL_STYLE",
    "VERTICAL_STYLE",
    "STYLES",
]
