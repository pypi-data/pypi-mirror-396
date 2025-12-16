from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

COLUMN_RENAMING = {
    "age": "age",
    "workclass": "work_class",
    "education": "education",
    "marital-status": "marital_status",
    "occupation": "occupation",
    "relationship": "relationship",
    "race": "race",
    "sex": "sex",
    "capital-gain": "capital_gain",
    "capital-loss": "capital_loss",
    "hours-per-week": "hours_per_week",
    "native-country": "native_country",
    "income": "income",
}

COLUMNS_TO_DROP = ["fnlwgt", "education-num", "income", "marital_status"]

EDUCATION_ORDER = {
    "Preschool": 1,
    "1st-4th": 2,
    "5th-6th": 3,
    "7th-8th": 4,
    "9th": 5,
    "10th": 6,
    "11th": 7,
    "12th": 8,
    "HS-grad": 9,
    "Some-college": 10,
    "Assoc-voc": 11,
    "Assoc-acdm": 12,
    "Bachelors": 13,
    "Masters": 14,
    "Prof-school": 15,
    "Doctorate": 16,
}


def encode_education(df: pd.DataFrame) -> pd.DataFrame:
    """Convert education to ordinal numeric values."""
    df["education"] = df["education"].map(EDUCATION_ORDER)
    return df


def combine_capital(df: pd.DataFrame) -> pd.DataFrame:
    """Combine capital_gain and capital_loss into single capital_net column."""
    df["capital_net"] = df["capital_gain"] - df["capital_loss"]
    df = df.drop(columns=["capital_gain", "capital_loss"])
    return df


def combine_married(df: pd.DataFrame) -> pd.DataFrame:
    """Combine Husband and Wife into Married in relationship column."""
    df["relationship"] = df["relationship"].replace(
        {"Husband": "Married", "Wife": "Married"}
    )
    return df


def binarize_race(df: pd.DataFrame) -> pd.DataFrame:
    """Convert race column to binary columns: is_white and is_black."""
    df["is_white"] = df["race"] == "White"
    df["is_black"] = df["race"] == "Black"
    df = df.drop(columns=["race"])
    return df


def binarize_sex(df: pd.DataFrame) -> pd.DataFrame:
    """Convert sex column to binary column: is_female."""
    df["is_female"] = df["sex"] == "Female"
    df = df.drop(columns=["sex"])
    return df


def add_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add interaction features for GLM modeling."""
    df["age_x_education"] = df["age"] * df["education"]
    return df


def add_unique_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a unique_id column to the dataframe as the first column.
    """
    df.insert(0, "unique_id", range(len(df)))
    return df


def clean_columns(
    df: pd.DataFrame,
    renaming_map: dict = COLUMN_RENAMING,
    columns_to_drop: list = COLUMNS_TO_DROP,
) -> pd.DataFrame:
    """
    Renames a standard set of columns to use snake_case and drops
    a predefined list of columns (fnlwgt, education-num, income).
    """
    columns_to_drop_in_df = [col for col in columns_to_drop if col in df.columns]
    if columns_to_drop_in_df:
        df = df.drop(columns=columns_to_drop_in_df)

    df = df.rename(columns=renaming_map)

    return df


def clean_and_binarize_income(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the 'income' column and converts it into a boolean field
    (True for '>50K', False for '=<50K').
    """
    income_col = "income"
    high_income_col = "high_income"
    cleaned_income = df[income_col].astype(str).str.strip().str.strip(".")
    df[income_col] = cleaned_income
    df[high_income_col] = cleaned_income == ">50K"

    return df


def replace_question_marks_with_nan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replaces '?' with np.nan across all columns in the dataframe.
    """
    return df.replace("?", np.nan)


def trim_string(value: Any) -> Any:
    """
    Trims leading and trailing whitespace from a single string.
    Returns the original value if it's not a string (e.g., NaN or numbers).
    """
    if isinstance(value, str):
        return value.strip()

    return value


def trim_dataframe_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Automatically detects string (object) columns in a Pandas DataFrame
    and strips whitespace from all values.
    """
    string_columns = df.select_dtypes(include=["object", "string"]).columns

    for col in string_columns:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].str.strip()
        else:
            df[col] = df[col].apply(trim_string)

    return df


def full_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master function that runs all cleaning steps in a logical order.
    """
    df = df.copy()
    df = add_unique_id(df)
    df = clean_and_binarize_income(df)
    df = clean_columns(df, COLUMN_RENAMING)
    df = trim_dataframe_whitespace(df)
    df = replace_question_marks_with_nan(df)
    df = encode_education(df)
    df = combine_capital(df)
    df = combine_married(df)
    df = binarize_race(df)
    df = binarize_sex(df)
    df = add_interaction_features(df)

    return df


def run_cleaning_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs full cleaning pipeline and saves result in parquet format.
    """
    df = full_clean(df)

    current_file = Path(__file__).resolve()
    src_directory = current_file.parent.parent

    data_dir = src_directory / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "cleaned_census_income.parquet"

    df.to_parquet(output_path)
    print(
        f"✅ Saved {df.shape[0]} rows, {df.shape[1]} columns to: {data_dir.name}/{output_path.name}"
    )
