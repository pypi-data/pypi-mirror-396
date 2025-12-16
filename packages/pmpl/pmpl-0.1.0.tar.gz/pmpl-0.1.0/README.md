# pmpl - Pretty Matplotlib

[![Tests](https://github.com/RensterMaat/pmpl/workflows/Tests/badge.svg)](https://github.com/RensterMaat/pmpl/actions/workflows/test.yml)
[![Documentation](https://github.com/RensterMaat/pmpl/workflows/Documentation/badge.svg)](https://github.com/RensterMaat/pmpl/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/RensterMaat/pmpl/branch/main/graph/badge.svg)](https://codecov.io/gh/RensterMaat/pmpl)
[![PyPI version](https://badge.fury.io/py/pmpl.svg)](https://badge.fury.io/py/pmpl)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Create presentation-ready plots with minimal effort.**

`pmpl` (Pretty Matplotlib) is a Python library that provides clean, consistent styling for matplotlib plots. Perfect for creating client-ready visualizations in Jupyter notebooks with just a few lines of code.

![Style Comparison](docs/images/example_comparison.png)

## Features

- 🎨 **Pre-configured styles** for common plot types (horizontal, vertical, base)
- 🔄 **Context managers** for temporary style application
- 🎯 **Direct formatters** for fine-grained control
- 📊 **Presentation-ready** defaults optimized for clarity
- 🔧 **Extensible** - easy to add custom styles
- ⚡ **Lightweight** - minimal dependencies

## Installation

```bash
pip install pmpl
```

Or with uv:
```bash
uv add pmpl
```

## Quick Start

### Using Context Managers

Perfect for applying styles temporarily:

```python
import pmpl
import matplotlib.pyplot as plt

# Horizontal plots (e.g., bar charts)
with pmpl.style('horizontal'):
    fig, ax = plt.subplots()
    ax.barh(['Product A', 'Product B', 'Product C'], [23, 45, 67])
    ax.set_xlabel('Sales ($M)')
    plt.show()

# Vertical plots (e.g., line charts)
with pmpl.style('vertical'):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 25, 30, 45])
    ax.set_ylabel('Revenue ($M)')
    plt.show()
```

### Using Direct Formatters

Apply formatting to existing axes:

```python
import pmpl
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.barh(['Q1', 'Q2', 'Q3', 'Q4'], [100, 120, 140, 160])

# Format after plot creation
pmpl.format_horizontal(ax)
plt.show()
```

### Setting Global Defaults

Apply a style for the entire session:

```python
import pmpl

# All subsequent plots will use vertical style
pmpl.set_defaults('vertical')
```

## Documentation

Full documentation is available in the `docs/` folder. Build it locally with:

```bash
cd docs
uv run sphinx-build -b html . _build/html
```

Then open `docs/_build/html/index.html` in your browser.

The documentation includes:
- **API Reference** - Complete function and class documentation
- **Examples** - Common use cases and patterns
- **Module Guides** - Deep dives into styles, formatters, and core

## Available Styles

### `horizontal`
- Shows **left spine** only
- **Vertical gridlines** (for x-axis)
- Perfect for: horizontal bar charts, horizontal plots

### `vertical`
- Shows **bottom spine** only
- **Horizontal gridlines** (for y-axis)
- Perfect for: line charts, vertical bar charts, scatter plots

### `base`
- **No spines**
- Customizable gridlines
- Perfect for: minimal plots, custom layouts

## Style Features

All styles include presentation-ready defaults:
- Clean Arial font
- Optimized DPI (95) for screen display
- Subtle gridlines (30% opacity)
- No tick marks on gridded axes
- Frameless legends
- Titles and labels sized for readability

## More Examples

### Horizontal Bar Chart with Custom Colors

![Horizontal Bar Chart](docs/images/example_horizontal.png)

```python
import pmpl
import matplotlib.pyplot as plt

categories = ['Engineering', 'Marketing', 'Sales', 'Operations', 'HR']
headcount = [45, 23, 67, 34, 12]

with pmpl.style('horizontal'):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(categories, headcount, color='steelblue')
    ax.set_xlabel('Number of Employees')
    ax.set_title('Headcount by Department')
    plt.tight_layout()
    plt.show()
```

### Time Series Line Chart

![Vertical Line Chart](docs/images/example_vertical.png)

```python
import pmpl
import matplotlib.pyplot as plt
import numpy as np

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
revenue = [120, 135, 142, 158, 171, 185]
costs = [80, 85, 90, 95, 100, 105]

with pmpl.style('vertical'):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(months, revenue, marker='o', linewidth=2, label='Revenue', color='seagreen')
    ax.plot(months, costs, marker='s', linewidth=2, label='Costs', color='coral')
    ax.set_ylabel('Amount ($M)')
    ax.set_title('Revenue vs Costs - H1 2024')
    ax.legend()
    plt.tight_layout()
    plt.show()
```

### Multiple Subplots with Different Styles

```python
import pmpl
import matplotlib.pyplot as plt

data_q = ['Q1', 'Q2', 'Q3', 'Q4']
sales = [100, 120, 140, 160]
growth = [5, 8, 12, 15]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left plot - horizontal style
ax1.barh(data_q, sales, color='mediumpurple')
ax1.set_xlabel('Sales ($M)')
ax1.set_title('Quarterly Sales')
pmpl.format_horizontal(ax1)

# Right plot - vertical style
ax2.bar(data_q, growth, color='coral')
ax2.set_ylabel('Growth Rate (%)')
ax2.set_title('Quarterly Growth')
pmpl.format_vertical(ax2)

plt.tight_layout()
plt.show()
```

### Scatter Plot with Base Style

```python
import pmpl
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100) * 0.5

with pmpl.style('base'):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(x, y, alpha=0.6, s=50, color='dodgerblue')
    ax.set_xlabel('Feature X')
    ax.set_ylabel('Feature Y')
    ax.set_title('Correlation Analysis')
    # Use both gridlines for scatter plots
    ax.grid(True, axis='both', alpha=0.3)
    plt.tight_layout()
    plt.show()
```

### Combining Multiple Datasets

![Grouped Bar Chart](docs/images/example_grouped.png)

```python
import pmpl
import matplotlib.pyplot as plt

regions = ['North', 'South', 'East', 'West']
q1 = [45, 38, 52, 41]
q2 = [48, 42, 55, 44]
q3 = [52, 45, 58, 47]

x = range(len(regions))
width = 0.25

with pmpl.style('vertical'):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([i - width for i in x], q1, width, label='Q1', color='#1f77b4')
    ax.bar(x, q2, width, label='Q2', color='#ff7f0e')
    ax.bar([i + width for i in x], q3, width, label='Q3', color='#2ca02c')

    ax.set_ylabel('Sales ($M)')
    ax.set_title('Regional Sales Performance')
    ax.set_xticks(x)
    ax.set_xticklabels(regions)
    ax.legend()
    plt.tight_layout()
    plt.show()
```
- Subtle gridlines (30% opacity)
- No tick marks on gridded axes
- Frameless legends
- Titles and labels sized for readability

## Examples

Check out the [examples directory](./examples/) for a complete demo notebook showcasing all features.

## Advanced Usage

### Custom Overrides

```python
# Override specific parameters
with pmpl.style('vertical', **{'figure.dpi': 150, 'grid.alpha': 0.5}):
    fig, ax = plt.subplots()
    ax.plot(data)
```

### Formatter Options

```python
# Customize grid appearance
pmpl.format_vertical(ax, grid=True, grid_alpha=0.2)

# Disable grid
pmpl.format_horizontal(ax, grid=False)

# Base formatter with custom grid axis
pmpl.format_base(ax, grid_axis='both')
```

### Accessing Style Dictionaries

For advanced users who want to customize or create new styles:

```python
import pmpl

# View available styles
print(pmpl.STYLES.keys())  # ['base', 'horizontal', 'vertical']

# Access style parameters
base_params = pmpl.BASE_STYLE
horizontal_params = pmpl.HORIZONTAL_STYLE
```

## Requirements

- Python ≥ 3.12
- matplotlib ≥ 3.10.8

## Development

This project uses:
- [uv](https://github.com/astral-sh/uv) for dependency management
- [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [pre-commit](https://pre-commit.com/) for code quality checks
- [pytest](https://pytest.org/) for testing
- [semantic-release](https://python-semantic-release.readthedocs.io/) for versioning

```bash
# Clone the repository
git clone https://github.com/RensterMaat/pmpl.git
cd pmpl

# Install with dev dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=pmpl --cov-report=term-missing

# Build documentation
cd docs
uv run sphinx-build -b html . _build/html

# Run example notebook
jupyter lab examples/test_pmpl.ipynb

# Generate example images
uv run python generate_examples.py
```

### Running Tests

The test suite covers:
- Style definitions and registry
- Context managers and style application
- Axis formatters and their options
- Error handling for invalid inputs

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=pmpl

# Run specific test file
uv run pytest tests/test_formatters.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Created by [RensterMaat](https://github.com/RensterMaat)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
