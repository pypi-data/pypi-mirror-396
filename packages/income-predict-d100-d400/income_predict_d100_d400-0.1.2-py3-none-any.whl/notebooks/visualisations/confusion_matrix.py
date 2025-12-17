import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np


def confusion_matrix():
    """Plot confusion matrices for tuned GLM and tuned LGBM models."""
    # Hardcoded confusion matrix values for tuned models
    glm_tuned_cm = np.array([[7021, 495], [1025, 1269]])
    lgbm_tuned_cm = np.array([[7064, 452], [796, 1498]])

    # Calculate percentages
    glm_total = glm_tuned_cm.sum()
    lgbm_total = lgbm_tuned_cm.sum()
    glm_pct = glm_tuned_cm / glm_total * 100
    lgbm_pct = lgbm_tuned_cm / lgbm_total * 100

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    labels = ["<=50K", ">50K"]

    for idx, (ax, cm, pct, title) in enumerate(
        zip(
            axes,
            [glm_tuned_cm, lgbm_tuned_cm],
            [glm_pct, lgbm_pct],
            ["Tuned GLM", "Tuned LGBM"],
        )
    ):
        # Create heatmap
        ax.imshow(cm, cmap="Blues", aspect="auto")

        # Add text annotations
        for i in range(2):
            for j in range(2):
                count = cm[i, j]
                percent = pct[i, j]
                # Use white text for dark cells, dark text for light cells
                text_color = "white" if cm[i, j] > cm.max() / 2 else "darkblue"
                ax.text(
                    j,
                    i,
                    f"{count}\n({percent:.1f}%)",
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=12,
                )

        # Add star to LGBM cells (idx=1)
        if idx == 1:
            for i in range(2):
                for j in range(2):
                    ax.annotate(
                        "★",
                        xy=(j, i - 0.3),
                        ha="center",
                        va="center",
                        fontsize=14,
                        color="gold",
                        path_effects=[pe.withStroke(linewidth=1.5, foreground="black")],
                    )

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)
        ax.set_xlabel("Predicted", fontsize=11)
        ax.set_ylabel("Actual", fontsize=11)
        ax.set_title(title, fontsize=13)

    # Add legend for star
    star_marker = plt.Line2D(
        [0],
        [0],
        marker="*",
        color="w",
        markerfacecolor="gold",
        markeredgecolor="black",
        markeredgewidth=0.5,
        markersize=14,
        label="Best",
    )
    fig.legend(handles=[star_marker], loc="upper right", fontsize=9)

    plt.suptitle("Confusion Matrices: Predicted vs Actual", y=1.02, fontsize=14)
    plt.tight_layout()
