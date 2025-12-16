"""Generate example images for README documentation."""

import matplotlib.pyplot as plt
import numpy as np

import pmpl

# Set random seed for reproducibility
np.random.seed(42)


def save_example_horizontal():
    """Generate horizontal bar chart example."""
    categories = ["Engineering", "Marketing", "Sales", "Operations", "HR"]
    headcount = [45, 23, 67, 34, 12]

    with pmpl.style("horizontal"):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(categories, headcount, color="steelblue")
        ax.set_xlabel("Number of Employees")
        ax.set_title("Headcount by Department")
        plt.tight_layout()
        plt.savefig("docs/images/example_horizontal.png", dpi=150, bbox_inches="tight")
        plt.close()


def save_example_vertical():
    """Generate vertical line chart example."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    revenue = [120, 135, 142, 158, 171, 185]
    costs = [80, 85, 90, 95, 100, 105]

    with pmpl.style("vertical"):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(
            months, revenue, marker="o", linewidth=2, label="Revenue", color="seagreen"
        )
        ax.plot(months, costs, marker="s", linewidth=2, label="Costs", color="coral")
        ax.set_ylabel("Amount ($M)")
        ax.set_title("Revenue vs Costs - H1 2024")
        ax.legend()
        plt.tight_layout()
        plt.savefig("docs/images/example_vertical.png", dpi=150, bbox_inches="tight")
        plt.close()


def save_example_comparison():
    """Generate comparison of all three styles."""
    data_q = ["Q1", "Q2", "Q3", "Q4"]
    sales = [100, 120, 140, 160]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Horizontal style
    axes[0].barh(data_q, sales, color="coral")
    axes[0].set_xlabel("Sales ($M)")
    axes[0].set_title("Horizontal Style")
    pmpl.format_horizontal(axes[0])

    # Vertical style
    axes[1].bar(data_q, sales, color="steelblue")
    axes[1].set_ylabel("Sales ($M)")
    axes[1].set_title("Vertical Style")
    pmpl.format_vertical(axes[1])

    # Base style
    axes[2].bar(data_q, sales, color="mediumpurple")
    axes[2].set_ylabel("Sales ($M)")
    axes[2].set_title("Base Style")
    pmpl.format_base(axes[2])

    plt.tight_layout()
    plt.savefig("docs/images/example_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()


def save_example_grouped():
    """Generate grouped bar chart example."""
    regions = ["North", "South", "East", "West"]
    q1 = [45, 38, 52, 41]
    q2 = [48, 42, 55, 44]
    q3 = [52, 45, 58, 47]

    x = np.arange(len(regions))
    width = 0.25

    with pmpl.style("vertical"):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width, q1, width, label="Q1", color="#1f77b4")
        ax.bar(x, q2, width, label="Q2", color="#ff7f0e")
        ax.bar(x + width, q3, width, label="Q3", color="#2ca02c")

        ax.set_ylabel("Sales ($M)")
        ax.set_title("Regional Sales Performance")
        ax.set_xticks(x)
        ax.set_xticklabels(regions)
        ax.legend()
        plt.tight_layout()
        plt.savefig("docs/images/example_grouped.png", dpi=150, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    print("Generating example images...")
    save_example_horizontal()
    print("✓ Generated horizontal bar chart example")
    save_example_vertical()
    print("✓ Generated vertical line chart example")
    save_example_comparison()
    print("✓ Generated style comparison example")
    save_example_grouped()
    print("✓ Generated grouped bar chart example")
    print("\nAll example images saved to docs/images/")
