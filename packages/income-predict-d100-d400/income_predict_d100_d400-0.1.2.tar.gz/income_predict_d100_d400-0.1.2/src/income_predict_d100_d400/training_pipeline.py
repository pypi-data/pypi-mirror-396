import warnings

warnings.filterwarnings(
    "ignore",
    message=".*X does not have valid feature names, but LGBMClassifier was fitted with feature names.*",  # noqa: E501
)

import pandas as pd

from income_predict_d100_d400.cleaning import run_cleaning_pipeline
from income_predict_d100_d400.data import load_data
from income_predict_d100_d400.evaluation import run_evaluation
from income_predict_d100_d400.model_training import (
    TARGET,
    load_training_outputs,
    run_split,
    run_training,
)
from income_predict_d100_d400.pipeline_summary import print_pipeline_summary

print("Starting Pipeline...")

file_path = load_data()
df_raw = pd.read_parquet(file_path)

run_cleaning_pipeline(df_raw)
run_split()
run_training()

results = load_training_outputs()

run_evaluation(
    results["test"],
    TARGET,
    results["glm_model"],
    results["lgbm_model"],
    results["train_features"],
)

print_pipeline_summary()

print("Pipeline finished.")
