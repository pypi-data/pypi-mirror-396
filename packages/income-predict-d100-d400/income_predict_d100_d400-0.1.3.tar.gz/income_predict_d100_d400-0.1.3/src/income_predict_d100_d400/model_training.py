import random
import zlib
from typing import Any, Dict, List, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from scipy.stats import loguniform, randint, uniform
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from income_predict_d100_d400.robust_paths import DATA_DIR

RANDOM_SEED = 42

TARGET = "high_income"

NUMERIC_FEATURES = [
    "age",
    "capital_net",
    "hours_per_week",
    "education",
    "is_white",
    "is_black",
    "is_female",
]

# GLM gets interaction features. LGBM learns them automatically
NUMERIC_FEATURES_GLM = NUMERIC_FEATURES + ["age_x_education"]

CATEGORICAL_FEATURES = [
    "work_class",
    "occupation",
    "relationship",
    "native_country",
]


def set_random_seeds(seed: int = RANDOM_SEED) -> None:
    """
    Set random seeds for reproducibility.

    Parameters:
        seed: The random seed to use.
    """
    random.seed(seed)
    np.random.seed(seed)
    # Note: For full LGBM reproducibility, set environment variable
    # PYTHONHASHSEED=0 before running the script


def split_data_with_id_hash(
    data: pd.DataFrame, test_ratio: float, id_column: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data based on a hash of an identifier column.

    Parameters:
        data: The input DataFrame.
        test_ratio: The proportion of data to put in the test set.
        id_column: The name of the unique identifier column.

    Returns:
        A tuple containing (train_set, test_set) DataFrames.
    """

    def test_set_check(identifier: Any) -> bool:
        return (
            zlib.crc32(bytes(str(identifier), "utf-8")) & 0xFFFFFFFF
            < test_ratio * 2**32
        )

    ids = data[id_column]
    in_test_set = ids.apply(test_set_check)
    return data.loc[~in_test_set], data.loc[in_test_set]


def run_split() -> None:
    """
    Split data into train/test and save to parquet.

    Reads the cleaned parquet file, splits it using hash-based splitting,
    and saves 'train_split.parquet' and 'test_split.parquet'.
    """
    parquet_path = DATA_DIR / "cleaned_census_income.parquet"
    df = pd.read_parquet(parquet_path)

    train, test = split_data_with_id_hash(df, 0.2, "unique_id")

    train.to_parquet(DATA_DIR / "train_split.parquet", index=False)
    test.to_parquet(DATA_DIR / "test_split.parquet", index=False)


def load_split() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load train/test split from parquet.

    Returns:
        A tuple containing the train and test DataFrames.
    """
    train = pd.read_parquet(DATA_DIR / "train_split.parquet")
    test = pd.read_parquet(DATA_DIR / "test_split.parquet")
    return train, test


def create_preprocessor(
    numeric_features: List[str], categorical_features: List[str]
) -> ColumnTransformer:
    """
    Create a sklearn ColumnTransformer for numeric and categorical data.

    Parameters:
        numeric_features: List of numeric column names.
        categorical_features: List of categorical column names.

    Returns:
        A ColumnTransformer configured with imputation, scaling, and one-hot encoding.
    """
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    preprocessor.set_output(transform="pandas")

    return preprocessor


def train_and_tune_model(
    model_name: str,
    pipeline: Pipeline,
    param_dist: Dict[str, Any],
    train_X: pd.DataFrame,
    train_y: pd.Series,
    test_X: pd.DataFrame,
    test_y: pd.Series,
    n_iter: int = 10,
) -> BaseEstimator:
    """
    Fits a baseline model, evaluates it, and then runs RandomizedSearchCV.

    Parameters:
        model_name: Name of the model (for logging).
        pipeline: The sklearn Pipeline to tune.
        param_dist: Dictionary of parameters for RandomizedSearchCV.
        train_X: Training features.
        train_y: Training target.
        test_X: Test features (used for baseline evaluation only).
        test_y: Test target (used for baseline evaluation only).
        n_iter: Number of parameter settings that are sampled.

    Returns:
        The best estimator found by RandomizedSearchCV.
    """
    print(f"\nProcessing {model_name}...")

    pipeline.fit(train_X, train_y)
    preds = pipeline.predict(test_X)
    acc = accuracy_score(test_y, preds)

    print(f"{model_name} Baseline Accuracy: {acc:.4f}")

    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    random_search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_dist,
        n_iter=n_iter,
        cv=cv_strategy,
        scoring="accuracy",
        n_jobs=-1,
        random_state=RANDOM_SEED,
    )

    random_search.fit(train_X, train_y)

    print(f"{model_name} Tuned Accuracy: {random_search.best_score_:.4f}")
    print(f"Tuned Params: {random_search.best_params_}")

    return random_search.best_estimator_


def execute_model_pipeline(
    model_name: str,
    classifier: BaseEstimator,
    numeric_features: List[str],
    param_dist: Dict[str, Any],
    train_X: pd.DataFrame,
    train_y: pd.Series,
    test_X: pd.DataFrame,
    test_y: pd.Series,
    n_iter: int,
) -> BaseEstimator:
    """
    Constructs and executes the training and tuning pipeline for a specific model.

    Parameters:
        model_name: Name of the model.
        classifier: The sklearn estimator to use.
        numeric_features: List of numeric features to use.
        param_dist: Parameter distribution for tuning.
        train_X: Training features.
        train_y: Training target.
        test_X: Test features.
        test_y: Test target.
        n_iter: Number of iterations for tuning.

    Returns:
        The best tuned model pipeline.
    """
    preprocessor = create_preprocessor(numeric_features, CATEGORICAL_FEATURES)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    return train_and_tune_model(
        model_name=model_name,
        pipeline=pipeline,
        param_dist=param_dist,
        train_X=train_X,
        train_y=train_y,
        test_X=test_X,
        test_y=test_y,
        n_iter=n_iter,
    )


def run_training() -> None:
    """
    Main training execution function.

    Loads split data, trains and tunes both GLM and LGBM models,
    and saves the best models and training features to disk.
    """
    set_random_seeds(RANDOM_SEED)

    train, test = load_split()
    train_y = train[TARGET]
    train_X = train.drop(columns=[TARGET, "unique_id"])
    test_y = test[TARGET]
    test_X = test.drop(columns=[TARGET, "unique_id"])

    best_glm_model = execute_model_pipeline(
        model_name="GLM",
        classifier=SGDClassifier(
            loss="log_loss", max_iter=1000, random_state=RANDOM_SEED
        ),
        numeric_features=NUMERIC_FEATURES_GLM,
        param_dist={
            "classifier__l1_ratio": uniform(0, 1),
            "classifier__alpha": loguniform(1e-4, 1e-1),
        },
        train_X=train_X,
        train_y=train_y,
        test_X=test_X,
        test_y=test_y,
        n_iter=20,
    )

    best_lgbm_model = execute_model_pipeline(
        model_name="LGBM",
        classifier=LGBMClassifier(
            objective="binary", random_state=RANDOM_SEED, verbose=-1
        ),
        numeric_features=NUMERIC_FEATURES,
        param_dist={
            "classifier__learning_rate": loguniform(0.01, 0.2),
            "classifier__n_estimators": randint(50, 200),
            "classifier__num_leaves": randint(10, 60),
            "classifier__min_child_weight": loguniform(0.0001, 0.002),
        },
        train_X=train_X,
        train_y=train_y,
        test_X=test_X,
        test_y=test_y,
        n_iter=5,
    )

    joblib.dump(best_glm_model, DATA_DIR / "glm_model.joblib")
    joblib.dump(best_lgbm_model, DATA_DIR / "lgbm_model.joblib")
    train_X.to_parquet(DATA_DIR / "train_features.parquet", index=False)


def load_training_outputs() -> Dict[str, Union[BaseEstimator, pd.DataFrame]]:
    """
    Load trained models and data for evaluation.

    Returns:
        A dictionary containing the trained GLM model, LGBM model,
        training features, and test dataset.
    """
    return {
        "glm_model": joblib.load(DATA_DIR / "glm_model.joblib"),
        "lgbm_model": joblib.load(DATA_DIR / "lgbm_model.joblib"),
        "train_features": pd.read_parquet(DATA_DIR / "train_features.parquet"),
        "test": pd.read_parquet(DATA_DIR / "test_split.parquet"),
    }
