"""Tests for core style definitions."""

import pmpl


def test_base_style_exists():
    """Test that BASE_STYLE is defined and contains expected keys."""
    assert pmpl.BASE_STYLE is not None
    assert isinstance(pmpl.BASE_STYLE, dict)
    assert "font.family" in pmpl.BASE_STYLE
    assert "axes.grid" in pmpl.BASE_STYLE
    assert pmpl.BASE_STYLE["font.family"] == "Arial"


def test_horizontal_style_exists():
    """Test that HORIZONTAL_STYLE is defined correctly."""
    assert pmpl.HORIZONTAL_STYLE is not None
    assert isinstance(pmpl.HORIZONTAL_STYLE, dict)
    assert pmpl.HORIZONTAL_STYLE["axes.spines.left"] is True
    assert pmpl.HORIZONTAL_STYLE["axes.spines.bottom"] is False
    assert pmpl.HORIZONTAL_STYLE["axes.grid.axis"] == "x"


def test_vertical_style_exists():
    """Test that VERTICAL_STYLE is defined correctly."""
    assert pmpl.VERTICAL_STYLE is not None
    assert isinstance(pmpl.VERTICAL_STYLE, dict)
    assert pmpl.VERTICAL_STYLE["axes.spines.bottom"] is True
    assert pmpl.VERTICAL_STYLE["axes.spines.left"] is False
    assert pmpl.VERTICAL_STYLE["axes.grid.axis"] == "y"


def test_styles_registry():
    """Test that STYLES registry contains all expected styles."""
    assert pmpl.STYLES is not None
    assert isinstance(pmpl.STYLES, dict)
    assert "base" in pmpl.STYLES
    assert "horizontal" in pmpl.STYLES
    assert "vertical" in pmpl.STYLES
    assert pmpl.STYLES["base"] is pmpl.BASE_STYLE
    assert pmpl.STYLES["horizontal"] is pmpl.HORIZONTAL_STYLE
    assert pmpl.STYLES["vertical"] is pmpl.VERTICAL_STYLE


def test_style_inheritance():
    """Test that specialized styles inherit from BASE_STYLE."""
    # Horizontal should have all base style keys plus its own
    assert "font.family" in pmpl.HORIZONTAL_STYLE
    assert pmpl.HORIZONTAL_STYLE["font.family"] == pmpl.BASE_STYLE["font.family"]

    # Vertical should have all base style keys plus its own
    assert "font.family" in pmpl.VERTICAL_STYLE
    assert pmpl.VERTICAL_STYLE["font.family"] == pmpl.BASE_STYLE["font.family"]
