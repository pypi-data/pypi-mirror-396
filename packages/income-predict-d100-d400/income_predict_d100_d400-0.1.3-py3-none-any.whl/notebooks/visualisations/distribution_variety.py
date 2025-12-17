import matplotlib.pyplot as plt
import pandas as pd


def distribution_variety(df):
    """
    Visualizes the distribution comparison between two columns:
    1. 'age' - showing smooth distribution
    2. 'hours-per-week' - showing sharp peaks

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing 'age' and 'hours-per-week' columns

    Returns:
    --------
    fig, axes : matplotlib figure and axes objects
    """
    # Check if both columns exist
    if "age" not in df.columns or "hours-per-week" not in df.columns:
        print("Error: Required columns not found in DataFrame!")
        return None, None

    # Get the data for both columns, removing NaN values
    age_data = pd.to_numeric(df["age"].dropna(), errors="coerce").dropna()
    hours_data = pd.to_numeric(df["hours-per-week"].dropna(), errors="coerce").dropna()

    if len(age_data) == 0 or len(hours_data) == 0:
        print("No valid numeric data found in required columns!")
        return None, None

    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # LEFT PLOT: Age - Smooth distribution
    age_counts = age_data.value_counts().sort_index()

    # Fill in missing integer values with 0 to ensure one bar per integer
    age_min = int(age_data.min())
    age_max = int(age_data.max())
    all_ages = pd.Series(0, index=range(age_min, age_max + 1))
    all_ages.update(age_counts)
    age_counts = all_ages

    # Find bars around median that total 46.7% of count
    age_median = age_data.median()
    target_pct = 0.467
    target_count = len(age_data) * target_pct

    # Sort by distance from median and accumulate counts
    cumulative = 0
    highlighted_ages = set()

    # Expand outward from median until we reach target
    ages_sorted = sorted(age_counts.index, key=lambda x: abs(x - age_median))
    for age in ages_sorted:
        if cumulative >= target_count:
            break
        highlighted_ages.add(age)
        cumulative += age_counts[age]

    # Color bars based on whether they're in the highlighted set
    colors = []
    for age in age_counts.index:
        if age in highlighted_ages:
            colors.append("#e74c3c")  # Red for highlighted bars
        else:
            colors.append("#95a5a6")  # Gray for others

    ax1.bar(
        age_counts.index,
        age_counts.values,
        color=colors,
        alpha=0.8,
        width=0.8,
        edgecolor="none",
    )

    ax1.set_xlabel("Age", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Frequency", fontsize=12, fontweight="bold")
    ax1.set_title(
        "Age Distribution (Relativley Smoothly Distrubuted)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax1.grid(axis="y", alpha=0.3, linestyle="--")

    # RIGHT PLOT: Hours per week - Sharp peaks
    hours_counts = hours_data.value_counts().sort_index()

    # Fill in missing integer values with 0 to ensure one bar per integer
    hours_min = int(hours_data.min())
    hours_max = int(hours_data.max())
    all_hours = pd.Series(0, index=range(hours_min, hours_max + 1))
    all_hours.update(hours_counts)
    hours_counts = all_hours

    # Color bars - only the highest frequency bar is red, rest are gray
    max_count = hours_counts.max()
    colors = []
    for count in hours_counts.values:
        if count == max_count:  # Only the peak
            colors.append("#e74c3c")  # Red for the highest peak
        else:
            colors.append("#95a5a6")  # Gray for all others

    ax2.bar(
        hours_counts.index,
        hours_counts.values,
        color=colors,
        alpha=0.8,
        width=0.8,
        edgecolor="none",
    )

    ax2.set_xlabel("Hours per Week", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Frequency", fontsize=12, fontweight="bold")
    ax2.set_title(
        "Hours per Week Distribution (Highly concentrated)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax2.grid(axis="y", alpha=0.3, linestyle="--")

    # Add single shared legend for both plots
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(
            facecolor="#e74c3c", alpha=0.8, label="Represents 46.7% around the median"
        )
    ]

    # Position legend centered between the two plots
    fig.legend(
        handles=legend_elements,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        frameon=True,
        shadow=True,
        fontsize=15,
        ncol=1,
    )

    # Overall title
    fig.suptitle(
        "Distribution Diversity: Spread vs. Concentrated Data",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )

    plt.tight_layout()
    plt.show()
