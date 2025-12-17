from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo

from income_predict_d100_d400.robust_paths import DATA_DIR


def fetch_census_data() -> pd.DataFrame:
    """
    Fetches the dataset from UCI.

    Returns:
        A DataFrame containing the merged features and targets from the dataset.
    """
    print("⬇️  Downloading data...")

    try:
        data = fetch_ucirepo(id=2)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data from UCI repository: {e}") from e

    print("⬇️  Downloading... Done!")

    if data.data.original is not None:
        return data.data.original

    return pd.concat([data.data.features, data.data.targets], axis=1)


def load_data() -> Path:
    """
    Checks if data exists locally. If not, downloads Census Income dataset.

    Returns:
        The Path to the saved parquet file.
    """
    output_path = DATA_DIR / "census_income.parquet"

    if output_path.exists():
        print(
            f"""
No need to download since data already exists at:
{output_path.name} (good, because it means
we're less likley to get blocked by UCI for spamming downloads)
            """
        )
        return output_path

    try:
        df = fetch_census_data()
    except Exception as e:
        raise RuntimeError(f"Error downloading data: {e}") from e

    df.to_parquet(output_path, index=False)

    return output_path
