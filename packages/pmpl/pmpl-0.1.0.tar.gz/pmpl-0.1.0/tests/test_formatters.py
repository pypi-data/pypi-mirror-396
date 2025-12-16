"""Tests for axis formatting functions."""

import matplotlib.pyplot as plt

import pmpl


def test_format_horizontal():
    """Test format_horizontal function."""
    fig, ax = plt.subplots()

    result = pmpl.format_horizontal(ax)

    assert result is ax  # Should return the axis for chaining
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert not ax.spines["bottom"].get_visible()
    assert ax.spines["left"].get_visible()

    plt.close(fig)


def test_format_horizontal_no_grid():
    """Test format_horizontal with grid disabled."""
    fig, ax = plt.subplots()

    pmpl.format_horizontal(ax, grid=False)

    # Grid should be disabled
    assert not ax.xaxis._major_tick_kw["gridOn"]
    assert not ax.yaxis._major_tick_kw["gridOn"]

    plt.close(fig)


def test_format_horizontal_custom_alpha():
    """Test format_horizontal with custom grid alpha."""
    fig, ax = plt.subplots()

    pmpl.format_horizontal(ax, grid_alpha=0.5)

    # Grid should be enabled
    assert ax.get_axisbelow()

    plt.close(fig)


def test_format_horizontal_custom_spines():
    """Test format_horizontal with custom spine kwargs."""
    fig, ax = plt.subplots()

    # Override default spine visibility
    pmpl.format_horizontal(ax, top=True, right=True)

    # Custom spine settings should be applied
    assert ax.spines["top"].get_visible()
    assert ax.spines["right"].get_visible()

    plt.close(fig)


def test_format_vertical():
    """Test format_vertical function."""
    fig, ax = plt.subplots()

    result = pmpl.format_vertical(ax)

    assert result is ax  # Should return the axis for chaining
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert not ax.spines["left"].get_visible()
    assert ax.spines["bottom"].get_visible()

    plt.close(fig)


def test_format_vertical_no_grid():
    """Test format_vertical with grid disabled."""
    fig, ax = plt.subplots()

    pmpl.format_vertical(ax, grid=False)

    # Grid should be disabled
    assert not ax.xaxis._major_tick_kw["gridOn"]
    assert not ax.yaxis._major_tick_kw["gridOn"]

    plt.close(fig)


def test_format_vertical_custom_spines():
    """Test format_vertical with custom spine kwargs."""
    fig, ax = plt.subplots()

    # Override default spine visibility
    pmpl.format_vertical(ax, left=True, top=True)

    # Custom spine settings should be applied
    assert ax.spines["left"].get_visible()
    assert ax.spines["top"].get_visible()

    plt.close(fig)


def test_format_base():
    """Test format_base function."""
    fig, ax = plt.subplots()

    result = pmpl.format_base(ax)

    assert result is ax  # Should return the axis for chaining
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert not ax.spines["left"].get_visible()
    assert not ax.spines["bottom"].get_visible()

    plt.close(fig)


def test_format_base_grid_axis():
    """Test format_base with different grid axis options."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)

    pmpl.format_base(ax1, grid_axis="x")
    pmpl.format_base(ax2, grid_axis="y")
    pmpl.format_base(ax3, grid_axis="both")

    # All should have grid enabled
    assert ax1.get_axisbelow()
    assert ax2.get_axisbelow()
    assert ax3.get_axisbelow()

    plt.close(fig)


def test_format_base_no_grid():
    """Test format_base with grid disabled."""
    fig, ax = plt.subplots()

    pmpl.format_base(ax, grid=False)

    # Grid should be disabled
    assert not ax.xaxis._major_tick_kw["gridOn"]
    assert not ax.yaxis._major_tick_kw["gridOn"]

    plt.close(fig)


def test_formatter_chaining():
    """Test that formatters return the axis for chaining."""
    fig, ax = plt.subplots()

    # Formatters should return the axis
    result = pmpl.format_vertical(ax)

    assert result is ax
    # Can use axis methods after formatting
    ax.set_title("Test")
    assert ax.get_title() == "Test"

    plt.close(fig)
