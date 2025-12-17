import matplotlib.pyplot as plt
import pandas as pd


def occupation_correlation(df: pd.DataFrame) -> None:
    """
    Plots a 100% stacked bar chart for occupation vs high_income.
    Bars are ordered by the proportion with high_income=True (descending).
    """
    target = "high_income"
    feature = "occupation"

    # Create crosstab with proportions
    crosstab = pd.crosstab(df[feature], df[target], normalize="index")

    # Sort by the proportion with high_income=True (descending)
    if True in crosstab.columns:
        crosstab = crosstab.sort_values(by=True, ascending=False)

    # Create figure and plot on the same axes
    fig, ax = plt.subplots(figsize=(12, 6))
    crosstab.plot(kind="bar", stacked=True, ax=ax)

    ax.set_title(f"{feature} Distribution by {target}", fontsize=12)
    ax.set_ylabel("Proportion")
    ax.set_xlabel(feature)
    ax.legend(title=target, bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    plt.tight_layout()
    plt.show()
