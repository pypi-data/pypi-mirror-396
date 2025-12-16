# d100_d400_income_predict

## Overview

This repository provides a reproducible Docker environment pre-configured with everything needed to run the GLM and LGBM models for predicting high income basaed on the 1994 US census dataset.

The main analysis can be found at: `src/notebooks/final_report.ipynb`

There is are other sub-analysis files, they are:
- `src/tests/benchmark_pandas_polars.py` script that highlights the performance differences between Polars and Pandas on loading and cleaning the dataset.
- `src/notebooks/eda_cleaning.ipynb` exploratory data analysis. Lots more charts and info on how and why certain decisions were made in building the models.

## Running the model

### 1. Download and install Docker Desktop (if you don't have it already)

- link: [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. Clone the Repository

    ```
    git clone https://github.com/caitpj/d100_d400_income_predict.git
    cd d100_d400_income_predict
    ```

### 2. Build the Docker Image

    `docker build -t conda-uciml .`

### 3. Run the Model Pipeline
This runs the model in the Docker container, including downloading the data, cleaning, training, tuning, and saving key visualisations. It should take a minuite or so to run.

    ```
    docker run --rm --shm-size=2g \
    -e PYTHONWARNINGS=ignore \
    -e PYTHONUNBUFFERED=1 \
    -e OMP_NUM_THREADS=1 \
    conda-uciml python src/income_predict/training_pipeline.py
    ```

### 4. Run the `final_report.ipynb` Notebook

    ```
    docker run --rm -it \
    -p 8888:8888 \
    -v "$(pwd):/app" \
    conda-uciml \
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
    ```
From the output of the above code, find and paste the URL into a browser. It should start with: `http://127.0.0.1:8888/?token=...`


## Development

There are a few more steps needed if you want to develop this repo on your local machine.

To ensure code quality, I use `pre-commit` hooks that run locally on your machine before every commit. This requires a local Conda environment on your host machine (not in Docker).

### 1. Download and install Miniconda (if you don't have it already)

- link: [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed on your machine (for local development and git hooks).

### 2. This installs pre-commit, black, mypy, etc. based on environment.yml
    `conda env update --file environment.yml --prune`

### 3. initialize conda (will need to reset terminal)
    `conda init zsh`

### 4. Activate the environment
    `conda activate d100_d300_env`

### 5. Install the git hooks
    `pre-commit install`

Now, every time you run `git commit`, your local machine will fist check it meets the rules stated in .`pre-commit-config.yaml` automatically.


## AI Use
Some code was AI generated, notably:
- Visualisations
- Pandas vs Polars benchmark test

In other areas, AI was used to help with debugging, notably:
- Docker related issues
