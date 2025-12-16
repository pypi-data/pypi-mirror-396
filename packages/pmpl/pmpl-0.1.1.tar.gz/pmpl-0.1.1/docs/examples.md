# Examples

This page demonstrates various use cases for pmpl.

## Horizontal Bar Chart

```python
import matplotlib.pyplot as plt
import pmpl

# Using context manager
with pmpl.style("horizontal"):
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    values = [23, 45, 56, 78]
    ax.barh(categories, values)
    ax.set_xlabel('Value')
    plt.tight_layout()
    plt.show()
```

## Vertical Bar Chart

```python
import matplotlib.pyplot as plt
import pmpl

# Using formatter
fig, ax = plt.subplots(figsize=(8, 5))
categories = ['Q1', 'Q2', 'Q3', 'Q4']
values = [100, 150, 120, 180]
ax.bar(categories, values)
pmpl.format_vertical(ax)
ax.set_ylabel('Revenue ($M)')
plt.tight_layout()
plt.show()
```

## Line Plot

```python
import matplotlib.pyplot as plt
import numpy as np
import pmpl

# Set global defaults
pmpl.set_defaults("vertical")

fig, ax = plt.subplots(figsize=(8, 5))
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')
ax.legend()
ax.set_xlabel('x')
ax.set_ylabel('y')
plt.tight_layout()
plt.show()
```

## Grouped Bar Chart

```python
import matplotlib.pyplot as plt
import numpy as np
import pmpl

with pmpl.style("vertical"):
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ['A', 'B', 'C', 'D']
    group1 = [20, 35, 30, 35]
    group2 = [25, 32, 34, 20]

    x = np.arange(len(categories))
    width = 0.35

    ax.bar(x - width/2, group1, width, label='Group 1')
    ax.bar(x + width/2, group2, width, label='Group 2')

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    plt.tight_layout()
    plt.show()
```

## Custom Spine Configuration

```python
import matplotlib.pyplot as plt
import pmpl

# Format with custom spine visibility
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 2])
pmpl.format_vertical(ax, grid=True, grid_alpha=0.2, left=True, top=True)
plt.show()
```

## Style Override

```python
import matplotlib.pyplot as plt
import pmpl

# Apply style with custom overrides
with pmpl.style("horizontal", **{"figure.dpi": 150, "font.size": 12}):
    fig, ax = plt.subplots()
    ax.barh(['A', 'B', 'C'], [1, 2, 3])
    plt.show()
```
