import os
import random
import sys
import zlib
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from scipy.stats import loguniform, randint, uniform
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_SEED = 42

# Docker-compatible path resolution
if os.path.exists("/app/src/data"):
    DATA_DIR = Path("/app/src/data")
else:
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"

sys.path.append(str(Path(__file__).resolve().parent.parent))

TARGET = "high_income"

numeric_features = [
    "age",
    "capital_net",
    "hours_per_week",
    "education",
    "is_white",
    "is_black",
    "is_female",
]

# GLM gets interaction features. LGBM learns them automatically
numeric_features_glm = numeric_features + ["age_x_education"]

categorical_features = [
    "work_class",
    "occupation",
    "relationship",
    "native_country",
]


def set_random_seeds(seed: int = RANDOM_SEED):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    # Note: For full LGBM reproducibility, set environment variable
    # PYTHONHASHSEED=0 before running the script


def split_data_with_id_hash(data, test_ratio, id_column):
    def test_set_check(identifier):
        return (
            zlib.crc32(bytes(str(identifier), "utf-8")) & 0xFFFFFFFF
            < test_ratio * 2**32
        )

    ids = data[id_column]
    in_test_set = ids.apply(test_set_check)
    return data.loc[~in_test_set], data.loc[in_test_set]


def run_split():
    """Split data into train/test and save to parquet."""
    parquet_path = DATA_DIR / "cleaned_census_income.parquet"
    df = pd.read_parquet(parquet_path)

    train, test = split_data_with_id_hash(df, 0.2, "unique_id")

    train.to_parquet(DATA_DIR / "train_split.parquet", index=False)
    test.to_parquet(DATA_DIR / "test_split.parquet", index=False)

    print(f"✅ Saved train split: {train.shape[0]} rows")
    print(f"✅ Saved test split: {test.shape[0]} rows")


def load_split():
    """Load train/test split from parquet."""
    train = pd.read_parquet(DATA_DIR / "train_split.parquet")
    test = pd.read_parquet(DATA_DIR / "test_split.parquet")
    return train, test


def run_training():
    """Train GLM and LGBM models and save to disk."""
    set_random_seeds(RANDOM_SEED)

    train, test = load_split()

    train_y = train[TARGET]
    train_X = train.drop(columns=[TARGET, "unique_id"])

    test_y = test[TARGET]
    test_X = test.drop(columns=[TARGET, "unique_id"])

    # GLM preprocessor (with interaction features)
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    glm_preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features_glm),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    # GLM Classifier Pipeline
    glm_pipeline = Pipeline(
        steps=[
            ("preprocessor", glm_preprocessor),
            (
                "classifier",
                SGDClassifier(loss="log_loss", max_iter=1000, random_state=RANDOM_SEED),
            ),
        ]
    )

    glm_pipeline.fit(train_X, train_y)
    preds = glm_pipeline.predict(test_X)
    acc = accuracy_score(test_y, preds)
    baseline_clf = glm_pipeline.named_steps["classifier"]
    baseline_params = {
        "classifier__alpha": baseline_clf.alpha,
        "classifier__l1_ratio": baseline_clf.l1_ratio,
    }

    print(f"GLM Baseline Accuracy: {acc:.4f}")
    print(f"Baseline Params: {baseline_params}")

    # Tuning GLM with Randomized Search
    param_dist = {
        "classifier__l1_ratio": uniform(0, 1),
        "classifier__alpha": loguniform(1e-4, 1e-1),
    }
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    random_search = RandomizedSearchCV(
        glm_pipeline,
        param_distributions=param_dist,
        n_iter=20,
        cv=cv_strategy,
        scoring="accuracy",
        n_jobs=-1,
        random_state=RANDOM_SEED,
    )
    random_search.fit(train_X, train_y)

    print(f"GLM Tuned Accuracy: {random_search.best_score_:.4f}")
    print(f"Tuned Params: {random_search.best_params_}")

    # LGBM preprocessor (without interaction features)
    lgbm_preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    # LGBM Classifier Pipeline
    lgbm_pipeline = Pipeline(
        steps=[
            ("preprocessor", lgbm_preprocessor),
            (
                "classifier",
                LGBMClassifier(
                    objective="binary", random_state=RANDOM_SEED, verbose=-1
                ),
            ),
        ]
    )

    lgbm_pipeline.fit(train_X, train_y)
    preds = lgbm_pipeline.predict(test_X)
    acc = accuracy_score(test_y, preds)
    baseline_clf = lgbm_pipeline.named_steps["classifier"]
    baseline_params = {
        "classifier__learning_rate": baseline_clf.learning_rate,
        "classifier__min_child_weight": baseline_clf.min_child_weight,
        "classifier__n_estimators": baseline_clf.n_estimators,
        "classifier__num_leaves": baseline_clf.num_leaves,
    }

    print(f"LGBM Baseline Accuracy: {acc:.4f}")
    print(f"Baseline Params: {baseline_params}")

    # Tuning LGBM with Randomized Search
    param_dist = {
        "classifier__learning_rate": loguniform(0.01, 0.2),
        "classifier__n_estimators": randint(50, 200),
        "classifier__num_leaves": randint(10, 60),
        "classifier__min_child_weight": loguniform(0.0001, 0.002),
    }
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    random_search_lgbm = RandomizedSearchCV(
        lgbm_pipeline,
        param_distributions=param_dist,
        n_iter=5,
        cv=cv_strategy,
        scoring="accuracy",
        n_jobs=-1,
        random_state=RANDOM_SEED,
    )
    random_search_lgbm.fit(train_X, train_y)

    print(f"LGBM Tuned Accuracy: {random_search_lgbm.best_score_:.4f}")
    print(f"Tuned Params: {random_search_lgbm.best_params_}")

    # Save models and train_X
    glm_model = random_search.best_estimator_
    lgbm_model = random_search_lgbm.best_estimator_

    joblib.dump(glm_model, DATA_DIR / "glm_model.joblib")
    joblib.dump(lgbm_model, DATA_DIR / "lgbm_model.joblib")
    train_X.to_parquet(DATA_DIR / "train_X.parquet", index=False)

    print("✅ Saved GLM model")
    print("✅ Saved LGBM model")
    print("✅ Saved train_X")


def load_training_outputs():
    """Load trained models and data for evaluation."""
    return {
        "glm_model": joblib.load(DATA_DIR / "glm_model.joblib"),
        "lgbm_model": joblib.load(DATA_DIR / "lgbm_model.joblib"),
        "train_X": pd.read_parquet(DATA_DIR / "train_X.parquet"),
        "test": pd.read_parquet(DATA_DIR / "test_split.parquet"),
    }
