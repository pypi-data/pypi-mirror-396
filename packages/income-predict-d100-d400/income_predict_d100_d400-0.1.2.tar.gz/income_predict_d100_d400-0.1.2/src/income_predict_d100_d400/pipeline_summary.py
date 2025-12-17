from pathlib import Path
from typing import Dict, Tuple

from income_predict_d100_d400.robust_paths import DATA_DIR, PLOTS_DIR

EXPECTED_ARTIFACTS: Dict[str, Path] = {
    "Raw Data": DATA_DIR / "census_income.parquet",
    "Cleaned Data": DATA_DIR / "cleaned_census_income.parquet",
    "Train Split": DATA_DIR / "train_split.parquet",
    "Test Split": DATA_DIR / "test_split.parquet",
    "GLM Model": DATA_DIR / "glm_model.joblib",
    "LGBM Model": DATA_DIR / "lgbm_model.joblib",
    "Train Features": DATA_DIR / "train_features.parquet",
    "Confusion Matrix Plot": PLOTS_DIR / "classification_plot.png",
    "Partial Dependence Plot": PLOTS_DIR / "feature_dependence_plot.png",
}


def check_files(artifacts: Dict[str, Path]) -> Dict[str, Tuple[bool, str]]:
    """
    Checks if files exist and resolves their relative paths.

    Parameters:
        artifacts: Dictionary mapping descriptions to file paths.

    Returns:
        A dictionary mapping description to (exists_bool, display_path_string).
    """
    results = {}

    for desc, path in artifacts.items():
        exists = path.exists()

        try:
            display_path = str(path.relative_to(Path.cwd()))
        except ValueError:
            display_path = str(path)

        results[desc] = (exists, display_path)

    return results


def print_pipeline_summary() -> None:
    """
    Orchestrates the checking of artifacts and prints a formatted summary table.
    """
    results = check_files(EXPECTED_ARTIFACTS)

    print("\n" + "=" * 50)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 50)
    print(f"{'Status':<10} | {'Description':<25} | {'Location'}")
    print("-" * 80)

    for desc, (exists, path) in results.items():
        status = "✅" if exists else "❌"
        print(f"{status:<10} | {desc:<25} | {path}")

    print("-" * 80)
