import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def correlation_compare(df: pd.DataFrame) -> None:
    """
    Plots strip plots for unique_id and age against the target to show pattern contrast.
    """
    target = "high_income"
    # Only plot these two specific columns
    features = ["unique_id", "age"]

    # Check if columns exist
    for col in features + [target]:
        if col not in df.columns:
            print(f"Error: Column '{col}' not found in DataFrame!")
            return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left plot: unique_id (no pattern)
    sns.stripplot(
        data=df, x=target, y="unique_id", jitter=0.45, alpha=0.05, legend=False, ax=ax1
    )
    ax1.set_title("Unique ID (No Pattern)", fontsize=13, fontweight="bold")
    ax1.set_xlabel(target.replace("_", " ").title(), fontsize=11, fontweight="bold")
    ax1.set_ylabel("Unique ID", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.3)

    # Right plot: age (clear pattern)
    sns.stripplot(
        data=df, x=target, y="age", jitter=0.45, alpha=0.05, legend=False, ax=ax2
    )
    ax2.set_title("Age (Clear Pattern)", fontsize=13, fontweight="bold")
    ax2.set_xlabel(target.replace("_", " ").title(), fontsize=11, fontweight="bold")
    ax2.set_ylabel("Age", fontsize=11, fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.3)

    # Overall title
    fig.suptitle(
        "Pattern Contrast: No Relationship vs. Clear Separation",
        fontsize=15,
        fontweight="bold",
        y=1.00,
    )

    plt.tight_layout()
    plt.show()
