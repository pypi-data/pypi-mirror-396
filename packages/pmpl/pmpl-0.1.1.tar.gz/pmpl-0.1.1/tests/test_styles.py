"""Tests for style context managers and setters."""

import matplotlib.pyplot as plt
import pytest

import pmpl


def test_style_context_manager():
    """Test that style context manager applies and reverts styles."""
    original_family = plt.rcParams["font.family"]

    with pmpl.style("base"):
        assert plt.rcParams["font.family"] == ["Arial"]

    # Should revert after context
    assert plt.rcParams["font.family"] == original_family


def test_style_horizontal_context():
    """Test horizontal style context manager."""
    with pmpl.style("horizontal"):
        assert plt.rcParams["axes.spines.left"] is True
        assert plt.rcParams["axes.spines.bottom"] is False
        assert plt.rcParams["axes.grid.axis"] == "x"


def test_style_vertical_context():
    """Test vertical style context manager."""
    with pmpl.style("vertical"):
        assert plt.rcParams["axes.spines.bottom"] is True
        assert plt.rcParams["axes.spines.left"] is False
        assert plt.rcParams["axes.grid.axis"] == "y"


def test_style_with_overrides():
    """Test that style context manager accepts override parameters."""
    with pmpl.style("base", **{"figure.dpi": 150}):
        assert plt.rcParams["font.family"] == ["Arial"]
        assert plt.rcParams["figure.dpi"] == 150


def test_style_invalid_preset():
    """Test that invalid preset raises ValueError."""
    with (
        pytest.raises(ValueError, match="Unknown style preset"),
        pmpl.style("nonexistent"),
    ):
        pass


def test_set_defaults():
    """Test set_defaults function."""
    original = plt.rcParams.copy()

    try:
        pmpl.set_defaults("vertical")
        assert plt.rcParams["axes.spines.bottom"] is True
        assert plt.rcParams["font.family"] == ["Arial"]
    finally:
        # Restore original settings
        plt.rcParams.update(original)


def test_set_defaults_with_overrides():
    """Test set_defaults with override parameters."""
    original = plt.rcParams.copy()

    try:
        pmpl.set_defaults("base", **{"grid.alpha": 0.5})
        assert plt.rcParams["font.family"] == ["Arial"]
        assert plt.rcParams["grid.alpha"] == 0.5
    finally:
        plt.rcParams.update(original)


def test_set_defaults_invalid_preset():
    """Test that set_defaults raises ValueError for invalid preset."""
    with pytest.raises(ValueError, match="Unknown style preset"):
        pmpl.set_defaults("invalid")
