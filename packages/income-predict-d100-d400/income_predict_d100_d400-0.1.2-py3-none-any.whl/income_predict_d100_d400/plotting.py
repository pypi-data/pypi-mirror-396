from pathlib import Path
from typing import Any, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.inspection import partial_dependence
from sklearn.metrics import confusion_matrix

PLOTS_DIR = Path.cwd().resolve() / "data" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def _save_plot(name: Optional[str] = None) -> None:
    """
    Save current figure to file instead of displaying.

    Parameters:
        name: Optional name for the file. If None, uses a counter.
    """
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = PLOTS_DIR / f"{name}.png"
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved plot to: {filepath}")


def plot_partial_dependence(
    glm_model: Any,
    lgbm_model: Any,
    X: pd.DataFrame,
    top_features: List[str],
) -> None:
    """
    Plot partial dependence for top features with both GLM and LGBM models.

    Parameters:
        glm_model: The fitted GLM model.
        lgbm_model: The fitted LGBM model.
        X: The dataset used for computing partial dependence.
        top_features: List of feature names to plot.
    """
    n_features = len(top_features)
    _, axes = plt.subplots(1, n_features, figsize=(5 * n_features, 4))

    if n_features == 1:
        axes = [axes]

    for i, feature in enumerate(top_features):
        ax = axes[i]

        # Compute partial dependence for LGBM
        lgbm_pd = partial_dependence(
            lgbm_model,
            X,
            features=[feature],
            kind="average",
            categorical_features=(
                [feature]
                if X[feature].dtype == "object" or str(X[feature].dtype) == "category"
                else None
            ),
        )
        lgbm_grid = lgbm_pd["grid_values"][0]
        lgbm_avg = lgbm_pd["average"][0]

        # Compute partial dependence for GLM
        glm_pd = partial_dependence(
            glm_model,
            X,
            features=[feature],
            kind="average",
            categorical_features=(
                [feature]
                if X[feature].dtype == "object" or str(X[feature].dtype) == "category"
                else None
            ),
        )
        glm_grid = glm_pd["grid_values"][0]
        glm_avg = glm_pd["average"][0]

        # Check if feature is categorical
        is_categorical = (
            X[feature].dtype == "object" or str(X[feature].dtype) == "category"
        )

        if is_categorical:
            # For categorical features, use bar plot with offset
            x_positions = np.arange(len(lgbm_grid))
            width = 0.35

            ax.bar(
                x_positions - width / 2,
                lgbm_avg,
                width,
                color="blue",
                label="LGBM",
                alpha=0.8,
            )
            ax.bar(
                x_positions + width / 2,
                glm_avg,
                width,
                color="orange",
                label="GLM",
                alpha=0.8,
            )

            ax.set_xticks(x_positions)
            ax.set_xticklabels(lgbm_grid, rotation=45, ha="right")
        else:
            # For numeric features, use line plot
            ax.plot(lgbm_grid, lgbm_avg, color="blue", label="LGBM", linewidth=2)
            ax.plot(glm_grid, glm_avg, color="orange", label="GLM", linewidth=2)

        ax.set_xlabel(feature)
        ax.set_ylabel("Partial Dependence")
        ax.legend(loc="best")
        ax.set_title(f"Partial Dependence: {feature}")
        ax.grid(True, alpha=0.3)

    plt.suptitle("Partial Dependence Plots - Top Features (GLM vs LGBM)", y=1.02)
    plt.tight_layout()
    _save_plot(name="feature_dependence_plot")


def plot_confusion_matrices(
    y_true: np.ndarray, glm_preds: np.ndarray, lgbm_preds: np.ndarray
) -> None:
    """
    Plots confusion matrix heatmaps for GLM and LGBM side by side.

    Parameters:
        y_true: Array of true labels.
        glm_preds: Array of GLM prediction probabilities.
        lgbm_preds: Array of LGBM prediction probabilities.
    """
    _, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, preds, title in zip(
        axes,
        [glm_preds, lgbm_preds],
        ["Tuned GLM", "Tuned LGBM"],
    ):
        y_pred = (preds >= 0.5).astype(int)
        cm = confusion_matrix(y_true, y_pred)
        cm_pct = cm / cm.sum() * 100

        annotations = np.array(
            [
                [f"{count}\n({pct:.1f}%)" for count, pct in zip(row_counts, row_pcts)]
                for row_counts, row_pcts in zip(cm, cm_pct)
            ]
        )

        sns.heatmap(
            cm,
            annot=annotations,
            fmt="",
            cmap="Blues",
            xticklabels=["<=50K", ">50K"],
            yticklabels=["<=50K", ">50K"],
            ax=ax,
            cbar=False,
        )
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title(title)

    plt.suptitle("Confusion Matrices: Predicted vs Actual", y=1.02)
    plt.tight_layout()
    _save_plot(name="classification_plot")
