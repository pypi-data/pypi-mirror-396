import sys
from pathlib import Path

import pandas as pd

current_file = Path(__file__).resolve()
src_directory = current_file.parent.parent
sys.path.append(str(src_directory))

from income_predict_d100_d400.cleaning import run_cleaning_pipeline
from income_predict_d100_d400.evaluation import run_evaluation
from income_predict_d100_d400.model_training import (
    TARGET,
    load_training_outputs,
    run_split,
    run_training,
)

print("Starting Pipeline...")

# file_path = run_data_fetch_pipeline()
# Seem to have been blocked from downloading from UCI repo, so using local file for now
file_path = src_directory / "data" / "census_income.parquet"
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
    results["train_X"],
)

print("Pipeline finished.")
