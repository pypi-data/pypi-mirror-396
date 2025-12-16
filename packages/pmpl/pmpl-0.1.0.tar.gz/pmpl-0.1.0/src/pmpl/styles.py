"""Context managers for temporarily applying matplotlib styles."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import matplotlib.pyplot as plt

from .core import STYLES


@contextmanager
def style(preset: str = "base", **overrides: Any) -> Generator[None, None, None]:
    """Apply a matplotlib style temporarily within a context.

    Args:
        preset: Name of the style preset to apply ('base', 'horizontal', 'vertical')
        **overrides: Additional rcParams to override or extend the preset

    Yields:
        None

    Raises:
        ValueError: If the preset name is not recognized

    Example:
        >>> import matplotlib.pyplot as plt
        >>> import pmpl
        >>> with pmpl.style('horizontal'):
        ...     fig, ax = plt.subplots()
        ...     ax.barh(['A', 'B', 'C'], [1, 2, 3])
        ...     plt.show()
    """
    if preset not in STYLES:
        msg = (
            f"Unknown style preset: '{preset}'. "
            f"Available presets: {', '.join(STYLES.keys())}"
        )
        raise ValueError(msg)

    # Save current rcParams
    original_params = plt.rcParams.copy()

    try:
        # Apply the preset style
        style_params = STYLES[preset].copy()
        # Apply any overrides
        style_params.update(overrides)
        plt.rcParams.update(style_params)
        yield
    finally:
        # Restore original rcParams
        plt.rcParams.update(original_params)


def set_defaults(preset: str = "base", **overrides: Any) -> None:
    """Permanently set matplotlib rcParams to a preset style.

    Unlike the context manager, this persists for the entire session
    until explicitly changed again.

    Args:
        preset: Name of the style preset to apply ('base', 'horizontal', 'vertical')
        **overrides: Additional rcParams to override or extend the preset

    Raises:
        ValueError: If the preset name is not recognized

    Example:
        >>> import pmpl
        >>> pmpl.set_defaults('vertical')
        >>> # All subsequent plots will use the vertical style
    """
    if preset not in STYLES:
        msg = (
            f"Unknown style preset: '{preset}'. "
            f"Available presets: {', '.join(STYLES.keys())}"
        )
        raise ValueError(msg)

    style_params = STYLES[preset].copy()
    style_params.update(overrides)
    plt.rcParams.update(style_params)
