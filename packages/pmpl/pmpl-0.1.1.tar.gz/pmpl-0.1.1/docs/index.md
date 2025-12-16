# pmpl - Pretty Matplotlib

**pmpl** (Pretty Matplotlib) is a Python library that makes it easy to create presentation-ready matplotlib plots with minimal effort.

## Features

- 🎨 **Pre-configured styles** for professional-looking plots
- 🔧 **Easy-to-use formatters** for common plot types
- 🎯 **Context managers** for temporary style changes
- 📊 **Optimized for presentations** and publications

## Installation

```bash
pip install pmpl
```

## Quick Start

```python
import matplotlib.pyplot as plt
import pmpl

# Use a context manager for temporary styling
with pmpl.style("horizontal"):
    fig, ax = plt.subplots()
    ax.barh(['A', 'B', 'C'], [1, 2, 3])
    plt.show()

# Or set global defaults
pmpl.set_defaults("vertical")
fig, ax = plt.subplots()
ax.bar(['A', 'B', 'C'], [1, 2, 3])
plt.show()

# Or format individual axes
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 2])
pmpl.format_vertical(ax)
plt.show()
```

## Contents

```{toctree}
:maxdepth: 2

api/index
examples
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
