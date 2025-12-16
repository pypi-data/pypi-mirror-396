import itertools
import sys
import threading
import time
from pathlib import Path
from typing import Any, Literal, Optional

import pandas as pd
from ucimlrepo import fetch_ucirepo


def fetch_census_data() -> pd.DataFrame:
    """Fetches the dataset from UCI with a loading animation."""
    container: dict[str, Optional[Any]] = {"data": None, "error": None}

    def _download():
        try:
            container["data"] = fetch_ucirepo(id=2)
        except Exception as e:
            container["error"] = e

    thread = threading.Thread(target=_download)
    thread.start()

    spinner = itertools.cycle([".", "..", "..."])
    max_width = len("⬇️  Downloading... Done!")

    sys.stdout.write("\033[?25l")  # Hide cursor
    try:
        while thread.is_alive():
            message = f"\r⬇️  Downloading{next(spinner)}"
            sys.stdout.write(message.ljust(max_width))
            sys.stdout.flush()
            time.sleep(0.5)

        thread.join()

        if container["error"]:
            sys.stdout.write("\r" + " " * max_width + "\r")
            raise container["error"]

        sys.stdout.write("\r⬇️  Downloading... Done!\n")
        sys.stdout.flush()
    finally:
        sys.stdout.write("\033[?25h")  # Show cursor
        sys.stdout.flush()

    data = container["data"]

    if data is None:
        raise RuntimeError("Failed to fetch data from UCI repository")

    if data.data.original is not None:
        return data.data.original

    return pd.concat([data.data.features, data.data.targets], axis=1)


def run_data_fetch_pipeline(
    output_format: Literal["csv", "parquet"] = "parquet"
) -> Path:
    """
    Downloads Census Income dataset and saves it to the data directory
    relative to the project root.
    """
    try:
        df = fetch_census_data()
    except Exception as e:
        raise RuntimeError(f"Error downloading data: {e}") from e

    if (Path.cwd() / "src").exists():
        data_dir = Path.cwd() / "src" / "data"
    else:
        data_dir = Path.cwd() / "data"

    data_dir.mkdir(parents=True, exist_ok=True)
    file_name = "census_income"
    output_path = data_dir / f"{file_name}.{output_format}"

    if output_format == "csv":
        df.to_csv(output_path, index=False)
    else:
        df.to_parquet(output_path, index=False)

    print(
        f"✅ Saved {df.shape[0]} rows, {df.shape[1]} columns to: {data_dir.name}/{output_path.name}"
    )

    return output_path
