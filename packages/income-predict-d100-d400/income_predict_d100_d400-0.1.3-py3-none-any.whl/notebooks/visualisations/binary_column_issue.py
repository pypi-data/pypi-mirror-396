import matplotlib.pyplot as plt
import numpy as np


def binary_column_issue(df, column_name, expected_values=["<=50K", ">50K"]):
    """
    Visualizes data quality issues in a binary column by showing counts of each unique value.
    Values that don't match the expected binary values are highlighted in red.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the column to analyze
    column_name : str
        The name of the column to analyze
    expected_values : list, optional
        List of expected valid values (default: ['<=50K', '>50K'])

    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    # Get value counts for the column
    value_counts = df[column_name].value_counts().sort_values(ascending=False)

    # Determine which values are correct vs incorrect
    colors = []
    labels = []
    for value in value_counts.index:
        if value in expected_values:
            colors.append("#2ecc71")  # Green for correct values
            labels.append("Correctly labeled")
        else:
            colors.append("#e74c3c")  # Red for incorrect values
            labels.append("Not correctly labeled")

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(10, 6))

    x_pos = np.arange(len(value_counts))
    bars = ax.bar(x_pos, value_counts.values, color=colors, alpha=0.8)

    # Customize the plot
    ax.set_xticks(x_pos)
    ax.set_xticklabels(value_counts.index, rotation=45, ha="right")
    ax.set_xlabel("Unique Values", fontsize=12, fontweight="bold")
    ax.set_ylabel("Count", fontsize=12, fontweight="bold")
    ax.set_title(
        "Data Quality Issues: Target Variable Is Not Currently Binary",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Add value labels on top of bars
    for i, (bar, count) in enumerate(zip(bars, value_counts.values)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(value_counts) * 0.01,
            str(int(count)),
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

    # Create custom legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="#2ecc71", alpha=0.8, label="Correctly labeled"),
        Patch(facecolor="#e74c3c", alpha=0.8, label="Not correctly labeled"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, shadow=True)

    plt.tight_layout()
    plt.show()
