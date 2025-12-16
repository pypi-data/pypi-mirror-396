import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import auc, log_loss

current_file = Path(__file__).resolve()
src_directory = current_file.parent.parent
sys.path.append(str(src_directory))

from income_predict_d100_d400.plotting import plot_confusion_matrices, plot_partial_dependence


def evaluate_predictions(
    df,
    outcome_column,
    *,
    preds_column=None,
    model=None,
    sample_weight_column=None,
):
    """Evaluate predictions against actual outcomes for binary classification.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame used for evaluation
    outcome_column : str
        Name of outcome column (binary: 0/1 or True/False)
    preds_column : str, optional
        Name of predictions column (probabilities), by default None
    model :
        Fitted model with predict_proba method, by default None
    sample_weight_column : str, optional
        Name of sample weight column, by default None

    Returns
    -------
    evals
        DataFrame containing metrics
    """

    evals = {}

    assert (
        preds_column or model
    ), "provide column name of the pre-computed predictions or model to predict from."

    if preds_column is None:
        preds = model.predict_proba(df)[:, 1]
    else:
        preds = df[preds_column]

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

    ordered_samples, cum_actuals = lorenz_curve(actuals, preds, weights)
    evals["gini"] = 1 - 2 * auc(ordered_samples, cum_actuals)

    return pd.DataFrame(evals, index=[0]).T


def lorenz_curve(y_true, y_pred, exposure):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    exposure = np.asarray(exposure)

    # order samples by increasing predicted risk:
    ranking = np.argsort(y_pred)
    ranked_exposure = exposure[ranking]
    ranked_pure_premium = y_true[ranking]
    cumulated_claim_amount = np.cumsum(ranked_pure_premium * ranked_exposure)
    cumulated_claim_amount /= cumulated_claim_amount[-1]
    cumulated_samples = np.linspace(0, 1, len(cumulated_claim_amount))
    return cumulated_samples, cumulated_claim_amount


def get_feature_importance(importances, feature_names):
    """Return sorted DataFrame of feature importances."""
    return (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def run_evaluation(test_df, target, glm_model, lgbm_model, train_X):
    """Run full evaluation pipeline for GLM and LGBM models."""

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

    # Partial dependence - use top 5 features from LGBM importance
    top_features = lgbm_importance.head(5)["feature"].tolist()

    original_features = []
    for feat in top_features:
        if feat.startswith("cat__"):
            original = feat.replace("cat__", "").rsplit("_", 1)[0]
        elif feat.startswith("num__"):
            original = feat.replace("num__", "")
        else:
            original = feat
        if original not in original_features and original in train_X.columns:
            original_features.append(original)

    plot_partial_dependence(glm_model, lgbm_model, train_X, original_features[:5])
