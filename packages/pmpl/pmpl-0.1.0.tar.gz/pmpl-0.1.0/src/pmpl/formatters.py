"""Axis-level formatting utilities for matplotlib plots.

These functions allow you to format existing axes objects directly,
without using context managers or changing global rcParams.
"""

from typing import Any

from matplotlib.axes import Axes


def format_horizontal(
    ax: Axes,
    grid: bool = True,
    grid_alpha: float = 0.3,
    **spine_kwargs: Any,
) -> Axes:
    """Format an axis for horizontal plots (e.g., horizontal bar charts).

    Shows only the left spine with vertical gridlines.

    Args:
        ax: The matplotlib Axes object to format
        grid: Whether to show gridlines
        grid_alpha: Transparency of gridlines (0-1)
        **spine_kwargs: Additional kwargs passed to spine configuration

    Returns:
        The formatted Axes object (for chaining)

    Example:
        >>> import matplotlib.pyplot as plt
        >>> import pmpl
        >>> fig, ax = plt.subplots()
        >>> ax.barh(['A', 'B', 'C'], [1, 2, 3])
        >>> pmpl.format_horizontal(ax)
        >>> plt.show()
    """
    # Configure spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(True)

    # Apply any custom spine styling
    for spine_name, visible in spine_kwargs.items():
        if hasattr(ax.spines, spine_name):
            ax.spines[spine_name].set_visible(visible)

    # Configure grid
    if grid:
        ax.grid(True, axis="x", alpha=grid_alpha)
        ax.set_axisbelow(True)
    else:
        ax.grid(False)

    # Remove tick marks on x-axis, keep them on y-axis
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", length=5)

    return ax


def format_vertical(
    ax: Axes,
    grid: bool = True,
    grid_alpha: float = 0.3,
    **spine_kwargs: Any,
) -> Axes:
    """Format an axis for vertical plots (e.g., line charts, bar charts).

    Shows only the bottom spine with horizontal gridlines.

    Args:
        ax: The matplotlib Axes object to format
        grid: Whether to show gridlines
        grid_alpha: Transparency of gridlines (0-1)
        **spine_kwargs: Additional kwargs passed to spine configuration

    Returns:
        The formatted Axes object (for chaining)

    Example:
        >>> import matplotlib.pyplot as plt
        >>> import pmpl
        >>> fig, ax = plt.subplots()
        >>> ax.plot([1, 2, 3], [1, 4, 2])
        >>> pmpl.format_vertical(ax)
        >>> plt.show()
    """
    # Configure spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(True)

    # Apply any custom spine styling
    for spine_name, visible in spine_kwargs.items():
        if hasattr(ax.spines, spine_name):
            ax.spines[spine_name].set_visible(visible)

    # Configure grid
    if grid:
        ax.grid(True, axis="y", alpha=grid_alpha)
        ax.set_axisbelow(True)
    else:
        ax.grid(False)

    # Remove tick marks on y-axis, keep them on x-axis
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=5)

    return ax


def format_base(
    ax: Axes,
    grid: bool = True,
    grid_axis: str = "y",
    grid_alpha: float = 0.3,
) -> Axes:
    """Apply base formatting to an axis (no spines, customizable grid).

    Args:
        ax: The matplotlib Axes object to format
        grid: Whether to show gridlines
        grid_axis: Which axis to show gridlines on ('x', 'y', or 'both')
        grid_alpha: Transparency of gridlines (0-1)

    Returns:
        The formatted Axes object (for chaining)

    Example:
        >>> import matplotlib.pyplot as plt
        >>> import pmpl
        >>> fig, ax = plt.subplots()
        >>> ax.scatter([1, 2, 3], [1, 4, 2])
        >>> pmpl.format_base(ax, grid_axis='both')
        >>> plt.show()
    """
    # Hide all spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Configure grid
    if grid:
        ax.grid(True, axis=grid_axis, alpha=grid_alpha)
        ax.set_axisbelow(True)
    else:
        ax.grid(False)

    # Remove all tick marks
    ax.tick_params(axis="both", length=0)

    return ax
