import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


def model_comparison():
    """Plot comparison of GLM, GLM_tuned, LGBM, and LGBM_tuned evaluation metrics."""
    metrics = [
        "Mean Prediction",
        "Bias",
        "MSE",
        "RMSE",
        "MAE",
        "Deviance",
        "Gini",
        "Accuracy",
    ]

    # Hard coded outcomes from running pipeline with and without tuning
    glm_values = [
        0.246279,
        0.053182,
        0.107211,
        0.327432,
        0.216885,
        0.336309,
        0.599456,
        0.845260,
    ]
    glm_tuned_values = [
        0.236305,
        0.010528,
        0.106986,
        0.327088,
        0.217394,
        0.334899,
        0.601942,
        0.845872,
    ]
    lgbm_values = [
        0.238292,
        0.019024,
        0.087443,
        0.295708,
        0.176602,
        0.275612,
        0.653701,
        0.874108,
    ]
    lgbm_tuned_values = [
        0.237590,
        0.016022,
        0.087067,
        0.295071,
        0.174207,
        0.274527,
        0.654307,
        0.872783,
    ]
    mean_outcome = 0.233843

    metric_direction = {
        "Mean Prediction": "closer",
        "Bias": "lower",
        "MSE": "lower",
        "RMSE": "lower",
        "MAE": "lower",
        "Deviance": "lower",
        "Gini": "higher",
        "Accuracy": "higher",
    }

    all_values = [glm_values, glm_tuned_values, lgbm_values, lgbm_tuned_values]

    winners = []
    for i, metric in enumerate(metrics):
        direction = metric_direction[metric]
        metric_values = [v[i] for v in all_values]

        if direction == "lower":
            winner_idx = np.argmin(metric_values)
        elif direction == "higher":
            winner_idx = np.argmax(metric_values)
        else:  # closer to mean_outcome
            diffs = [abs(v - mean_outcome) for v in metric_values]
            winner_idx = np.argmin(diffs)

        winners.append(winner_idx)

    x = np.arange(len(metrics))
    width = 0.18  # Width of each bar

    _, ax = plt.subplots(figsize=(16, 8))

    # Define colors for each model
    colors = [
        "#5B9BD5",
        "#2E75B6",
        "#ED7D31",
        "#C55A11",
    ]  # Light blue, dark blue, light orange, dark orange

    # Plot bars for each model
    bars = []
    offsets = [-1.5, -0.5, 0.5, 1.5]
    for idx, (values, offset) in enumerate(zip(all_values, offsets)):
        bar = ax.bar(
            x + offset * width,
            values,
            width,
            color=colors[idx],
            edgecolor="black",
            linewidth=0.5,
        )
        bars.append(bar)

    # Add horizontal line for mean_outcome spanning the mean_preds bars
    ax.hlines(
        y=mean_outcome,
        xmin=x[0] - 2 * width,
        xmax=x[0] + 2 * width,
        colors="black",
        linestyles="dashed",
        linewidth=2,
    )

    # Add winner stars above the winning bar
    for i, winner_idx in enumerate(winners):
        winner_offset = offsets[winner_idx]
        winner_value = all_values[winner_idx][i]
        ax.annotate(
            "★",
            xy=(x[i] + winner_offset * width, winner_value),
            ha="center",
            va="bottom",
            fontsize=16,
            color="gold",
            path_effects=[pe.withStroke(linewidth=1.5, foreground="black")],
        )

    # Add direction indicators below metric names
    direction_symbols = {
        "lower": "lower is better",
        "higher": "higher is better",
        "closer": "closer to outcome is better",
    }

    # Create x-axis labels with direction
    metric_labels = [
        f"{m}\n({direction_symbols[metric_direction[m]]})" for m in metrics
    ]

    ax.set_title(
        "Model Comparison: GLM vs LGBM (Base and Tuned)",
        fontsize=18,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, fontsize=9)

    # Custom legend
    star_marker = plt.Line2D(
        [0],
        [0],
        marker="*",
        color="w",
        markerfacecolor="gold",
        markeredgecolor="black",
        markeredgewidth=0.5,
        markersize=14,
        label="Winner",
    )
    legend_elements = [
        Patch(facecolor=colors[0], edgecolor="black", label="GLM"),
        Patch(facecolor=colors[1], edgecolor="black", label="GLM_tuned"),
        Patch(facecolor=colors[2], edgecolor="black", label="LGBM"),
        Patch(facecolor=colors[3], edgecolor="black", label="LGBM_tuned"),
        star_marker,
        plt.Line2D(
            [0],
            [0],
            color="black",
            linestyle="dashed",
            linewidth=2,
            label="mean_outcome",
        ),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=9)

    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()


if __name__ == "__main__":
    model_comparison()
