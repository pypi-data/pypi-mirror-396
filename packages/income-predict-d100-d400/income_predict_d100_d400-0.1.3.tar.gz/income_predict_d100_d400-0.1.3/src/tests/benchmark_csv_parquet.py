"""
Benchmark comparing CSV vs Parquet for loading, cleaning, and saving census data.
Run multiple iterations for accuracy.

Result:
While Parquet is significantly faster than CSV relativley speaking (around 2x speedup),
the absolute time difference is small for this dataset size. It's also worth pointing out
that Parquet files are typically much smaller on disk census_income.parquet is 500kb vs
census_income.csv at 5.3MB, 10x smaller. Given these results, Parquet is the recommended
format for performance and storage efficiency.
"""

import statistics
import sys
import time
from pathlib import Path

import pandas as pd

current_file = Path(__file__).resolve()
src_directory = current_file.parent.parent
if str(src_directory) not in sys.path:
    sys.path.append(str(src_directory))

from income_predict_d100_d400.cleaning import full_clean

# Configuration
NUM_ITERATIONS = 10
DATA_FILE_PATH = src_directory / "data" / "census_income.parquet"


def setup_files():
    """Checks for source data and creates temporary test files."""
    print("--- Setup: Generating Temporary Files ---")

    if not DATA_FILE_PATH.exists():
        print(f"ERROR: Source file not found at {DATA_FILE_PATH}")
        print(
            "Please run 'src/income_predict_d100_d400/training_pipeline.py' "
            "first to generate the dataset."
        )
        sys.exit(1)

    print(f"Source data found: {DATA_FILE_PATH}")
    df_raw = pd.read_parquet(DATA_FILE_PATH)

    # Define temporary filenames
    source_csv = Path("temp_csv.csv")
    source_parquet = Path("temp_parquet.parquet")

    # Create source files for the benchmark
    print(f"Creating {source_csv}...")
    df_raw.to_csv(source_csv, index=False)

    print(f"Creating {source_parquet}...")
    df_raw.to_parquet(source_parquet, index=False)

    print("Setup complete.\n")
    return source_csv, source_parquet


def run_benchmark_cycle(source_file, output_file, format_type):
    """Runs a single load-clean-save cycle and returns the time taken."""
    start_time = time.perf_counter()

    # Load
    if format_type == "csv":
        df = pd.read_csv(source_file)
    else:
        df = pd.read_parquet(source_file)

    # Clean
    df = full_clean(df)

    # Save
    if format_type == "csv":
        df.to_csv(output_file, index=False)
    else:
        df.to_parquet(output_file, index=False)

    return time.perf_counter() - start_time


def main():
    source_csv, source_parquet = setup_files()
    output_csv = Path("temp_result.csv")
    output_parquet = Path("temp_result.parquet")

    csv_times = []
    parquet_times = []

    print(f"--- Starting Benchmark ({NUM_ITERATIONS} iterations) ---")

    try:
        for i in range(NUM_ITERATIONS):
            print(f"Iteration {i+1}/{NUM_ITERATIONS}...")

            # Benchmark CSV
            t_csv = run_benchmark_cycle(source_csv, output_csv, "csv")
            csv_times.append(t_csv)

            # Benchmark Parquet
            t_pq = run_benchmark_cycle(source_parquet, output_parquet, "parquet")
            parquet_times.append(t_pq)

    finally:
        # cleanup in finally block to ensure files are removed even if error occurs
        files_to_delete = [source_csv, source_parquet, output_csv, output_parquet]
        for file_path in files_to_delete:
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    # --- Results ---
    avg_csv = statistics.mean(csv_times)
    avg_pq = statistics.mean(parquet_times)

    print("\n" + "=" * 40)
    print(f"BENCHMARK RESULTS (Average over {NUM_ITERATIONS} runs)")
    print("=" * 40)
    print(f"CSV Average Time:     {avg_csv:.4f}s")
    print(f"Parquet Average Time: {avg_pq:.4f}s")
    print("-" * 40)

    if avg_csv < avg_pq:
        speedup = avg_pq / avg_csv
        print(f"Winner: CSV ({speedup:.2f}x faster)")
    else:
        speedup = avg_csv / avg_pq
        print(f"Winner: Parquet ({speedup:.2f}x faster)")


if __name__ == "__main__":
    main()
