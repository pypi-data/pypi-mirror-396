# d100_d400_income_predict

## Overview

This repository provides a reproducible Docker environment pre-configured with everything needed to run the GLM and LGBM models for predicting high income basaed on the 1994 US census dataset.

The main analysis can be found at: `src/notebooks/final_report.ipynb`

There is are other sub-analysis files, they are:
- `src/tests/benchmark_pandas_polars.py` script that highlights the performance differences between Polars and Pandas on loading and cleaning this specific dataset.
- `src/notebooks/eda_cleaning.ipynb` exploratory data analysis. Lots more charts and info on how and why certain decisions were made in building the models.


## Installation

There are two ways to install and run:
- Directly from PyPI as a package (easiest)
- Docker container (most robust, recommended for development)


### Install and Run - Method 1, PyPI

#### 1. Install the package
`pip install income_predict_d100_d400`

#### 2. Run the Pipeline
`python -m income_predict_d100_d400.training_pipeline`

or create a your own file and import income_predict_d100_d400:
```python
from income_predict_d100_d400.data import load_data
from income_predict_d100_d400.cleaning import run_cleaning_pipeline
from income_predict_d100_d400.evaluation import run_evaluation
from income_predict_d100_d400.model_training import (
    TARGET,
    load_training_outputs,
    run_split,
    run_training,
)

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

print("Pipeline finished.")
```


### Install and Run - Method 2, Docker

#### 1. Download and install Docker Desktop (if you don't have it already)

- link: [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. Clone the Repository
```bash
git clone https://github.com/caitpj/d100_d400_income_predict.git
cd d100_d400_income_predict
```

### 2. Build the Docker Image

`docker build -t conda-uciml .` (from root of d100_d400_income_predict)

### 3. Run the Model Pipeline
This runs the model in the Docker container, including downloading the data, cleaning, training, tuning, and saving key visualisations. It should take a minuite or so to run.
```bash
docker run --rm --shm-size=2g \
-e PYTHONUNBUFFERED=1 \
-e OMP_NUM_THREADS=1 \
conda-uciml python src/income_predict_d100_d400/training_pipeline.py
```

### 4. Run Notebooks
```bash
docker run --rm -it \
-p 8888:8888 \
-v "$(pwd):/app" \
conda-uciml \
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```
From the output of the above code, find and paste the URL into a browser. It should start with: `http://127.0.0.1:8888/?token=...`


#### Extra Steps for Development

If you want to contribute or modify the code, you can run a development shell inside the Docker container. This ensures you are using the exact same environment as the production build.

1. Enter the Development Shell This command mounts your local current directory to the container. Any changes you make to the code in your local editor will be instantly visible inside the container.
```bash
docker run --rm -it \
  -v "$(pwd):/app" \
  conda-uciml \
  /bin/bash
```

2. Activate the Environment Once inside the container, activate the specific environment:
`conda activate d100_d300_env`

3. Run Tests & Checks Since you are developing inside the container, you should run the quality checks manually before committing your code:
    - Run Unit Tests:
    `pytest`
    - Run Pre-commit Checks (Linting/Formatting):
    `pre-commit run --all-files`


## AI Use
Some code was AI generated, notably:
- Visualisations
- Pandas vs Polars benchmark test
- Pretty terminal outputs
- Full docstrings

In other areas, AI was used to help with debugging, notably:
- Docker related issues
- Performence issues with hypertunning

All code generated from AI is understood and reviewed by the author.
