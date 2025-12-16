import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def visualize_missing_data(df):
    """
    Visualizes data quality issues in a DataFrame by showing counts of NaN and '?' values
    for each column in a horizontal stacked bar chart.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze for data quality issues

    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    nan_counts = df.isna().sum()
    question_counts = pd.Series(0, index=df.columns)
    for col in df.columns:
        question_counts[col] = (df[col] == "?").sum()

    # Sort by total issues (ascending for horizontal bar chart)
    total_issues = nan_counts + question_counts
    sorted_indices = total_issues.sort_values(ascending=True).index
    nan_counts = nan_counts[sorted_indices]
    question_counts = question_counts[sorted_indices]

    fig, ax = plt.subplots(figsize=(10, max(6, len(nan_counts) * 0.4)))

    y_pos = np.arange(len(nan_counts))

    ax.barh(y_pos, nan_counts, label="NaN", color="#e74c3c", alpha=0.8)
    ax.barh(
        y_pos, question_counts, left=nan_counts, label="'?'", color="#f39c12", alpha=0.8
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(nan_counts.index)
    ax.set_xlabel("Count of Issues", fontsize=12, fontweight="bold")
    ax.set_ylabel("Column Name", fontsize=12, fontweight="bold")
    ax.set_title(
        "Data Quality Issues: NaN and '?' Values by Column",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.legend(loc="lower right", frameon=True, shadow=True)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    for i, (nan_val, q_val) in enumerate(zip(nan_counts, question_counts)):
        if nan_val > 0:
            ax.text(
                nan_val / 2,
                i,
                str(int(nan_val)),
                ha="center",
                va="center",
                fontweight="bold",
                color="white",
            )
        if q_val > 0:
            ax.text(
                nan_val + q_val / 2,
                i,
                str(int(q_val)),
                ha="center",
                va="center",
                fontweight="bold",
                color="white",
            )

    plt.tight_layout()

    plt.show()
