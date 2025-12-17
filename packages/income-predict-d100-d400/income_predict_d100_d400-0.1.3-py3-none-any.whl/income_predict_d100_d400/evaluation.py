from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, roc_auc_score

from income_predict_d100_d400.plotting import (
    plot_confusion_matrices,
    plot_partial_dependence,
)


def evaluate_predictions(
    df: pd.DataFrame,
    outcome_column: str,
    *,
    preds_column: Optional[str] = None,
    model: Optional[Any] = None,
    sample_weight_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Evaluate predictions against actual outcomes for binary classification.

    Parameters:
        df: DataFrame used for evaluation.
        outcome_column: Name of outcome column (binary: 0/1 or True/False).
        preds_column: Name of predictions column (probabilities).
        model: Fitted model with predict_proba method (optional).
        sample_weight_column: Name of sample weight column (optional).

    Returns:
        A DataFrame containing evaluation metrics (mean_preds, mse, gini, etc.).
    """

    evals = {}

    if preds_column is not None:
        preds = df[preds_column]
    elif model is not None:
        preds = model.predict_proba(df)[:, 1]
    else:
        raise ValueError(
            "provide column name of the pre-computed predictions or model to predict from."
        )

    if sample_weight_column:
        weights = df[sample_weight_column]
    else:
        weights = np.ones(len(df))

    actuals = df[outcome_column].astype(float)

    evals["mean_preds"] = np.average(preds, weights=weights)
    evals["mean_outcome"] = np.average(actuals, weights=weights)
    evals["bias"] = (evals["mean_preds"] - evals["mean_outcome"]) / evals[
        "mean_outcome"
    ]

    evals["mse"] = np.average((preds - actuals) ** 2, weights=weights)
    evals["rmse"] = np.sqrt(evals["mse"])
    evals["mae"] = np.average(np.abs(preds - actuals), weights=weights)

    # Bernoulli deviance (log loss) for binary classification
    evals["deviance"] = log_loss(actuals, preds, sample_weight=weights)

    # Formula: Gini = 2 * AUC - 1
    auc_score = roc_auc_score(actuals, preds, sample_weight=weights)
    evals["gini"] = 2 * auc_score - 1

    return pd.DataFrame(evals, index=[0]).T


def get_feature_importance(
    importances: np.ndarray, feature_names: np.ndarray
) -> pd.DataFrame:
    """
    Return sorted DataFrame of feature importances.

    Parameters:
        importances: Array of importance scores.
        feature_names: Array of feature names.

    Returns:
        DataFrame with 'feature' and 'importance' columns, sorted by importance.
    """
    return (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def run_evaluation(
    test_df: pd.DataFrame,
    target: str,
    glm_model: Any,
    lgbm_model: Any,
    train_features: pd.DataFrame,
) -> None:
    """
    Run full evaluation pipeline for GLM and LGBM models.

    Parameters:
        test_df: The test dataset.
        target: The name of the target column.
        glm_model: The trained GLM model.
        lgbm_model: The trained LGBM model.
        train_features: The training features (used for partial dependence plots).
    """

    test_X = test_df.drop(columns=[target, "unique_id"])
    test_y = test_df[target]

    test_eval_df = test_X.copy()
    test_eval_df[target] = test_y.values
    test_eval_df["glm_preds"] = glm_model.predict_proba(test_X)[:, 1]
    test_eval_df["lgbm_preds"] = lgbm_model.predict_proba(test_X)[:, 1]

    glm_eval = evaluate_predictions(test_eval_df, target, preds_column="glm_preds")
    print("\nTuned GLM Evaluation Metrics:")
    print(glm_eval)

    lgbm_eval = evaluate_predictions(test_eval_df, target, preds_column="lgbm_preds")
    print("\nTuned LGBM Evaluation Metrics:")
    print(lgbm_eval)

    plot_confusion_matrices(
        test_eval_df[target].astype(int).values,
        test_eval_df["glm_preds"].values,
        test_eval_df["lgbm_preds"].values,
    )

    glm_preprocessor = glm_model.named_steps["preprocessor"]
    glm_transformed_names = glm_preprocessor.get_feature_names_out()

    glm_clf = glm_model.named_steps["classifier"]
    glm_importance = get_feature_importance(
        np.abs(glm_clf.coef_).flatten(), glm_transformed_names
    )
    print("\nTuned GLM Feature Importance (Top 15):")
    print(glm_importance.head(15))

    lgbm_preprocessor = lgbm_model.named_steps["preprocessor"]
    lgbm_transformed_names = lgbm_preprocessor.get_feature_names_out()

    lgbm_clf = lgbm_model.named_steps["classifier"]
    lgbm_importance = get_feature_importance(
        lgbm_clf.feature_importances_, lgbm_transformed_names
    )
    print("\nTuned LGBM Feature Importance (Top 15):")
    print(lgbm_importance.head(15))

    top_features = lgbm_importance.head(5)["feature"].tolist()

    original_features = []
    for feat in top_features:
        if feat.startswith("cat__"):
            original = feat.replace("cat__", "").rsplit("_", 1)[0]
        elif feat.startswith("num__"):
            original = feat.replace("num__", "")
        else:
            original = feat
        if original not in original_features and original in train_features.columns:
            original_features.append(original)

    plot_partial_dependence(
        glm_model, lgbm_model, train_features, original_features[:5]
    )
