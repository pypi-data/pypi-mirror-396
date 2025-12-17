from typing import Any

import numpy as np
import pandas as pd

from income_predict_d100_d400.robust_paths import DATA_DIR

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
    """
    Convert education to ordinal numeric values.

    Parameters:
        df: The DataFrame containing the 'education' column.

    Returns:
        The DataFrame with the 'education' column mapped to integers.
    """
    df["education"] = df["education"].map(EDUCATION_ORDER)
    return df


def combine_capital(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine capital_gain and capital_loss into single capital_net column.

    Parameters:
        df: The DataFrame containing 'capital_gain' and 'capital_loss'.

    Returns:
        The DataFrame with a new 'capital_net' column and original columns removed.
    """
    df["capital_net"] = df["capital_gain"] - df["capital_loss"]
    df = df.drop(columns=["capital_gain", "capital_loss"])
    return df


def combine_married(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine Husband and Wife into Married in relationship column.

    Parameters:
        df: The DataFrame containing the 'relationship' column.

    Returns:
        The DataFrame with updated 'relationship' values.
    """
    df["relationship"] = df["relationship"].replace(
        {"Husband": "Married", "Wife": "Married"}
    )
    return df


def binarize_race(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert race column to binary columns: is_white and is_black.

    Parameters:
        df: The DataFrame containing the 'race' column.

    Returns:
        The DataFrame with 'is_white' and 'is_black' columns added and 'race' removed.
    """
    df["is_white"] = df["race"] == "White"
    df["is_black"] = df["race"] == "Black"
    df = df.drop(columns=["race"])
    return df


def binarize_sex(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert sex column to binary column: is_female.

    Parameters:
        df: The DataFrame containing the 'sex' column.

    Returns:
        The DataFrame with 'is_female' column added and 'sex' removed.
    """
    df["is_female"] = df["sex"] == "Female"
    df = df.drop(columns=["sex"])
    return df


def add_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add interaction features for GLM modeling.

    Parameters:
        df: The DataFrame containing 'age' and 'education'.

    Returns:
        The DataFrame with a new 'age_x_education' column.
    """
    df["age_x_education"] = df["age"] * df["education"]
    return df


def add_unique_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a unique_id column to the dataframe as the first column.

    Parameters:
        df: The input DataFrame.

    Returns:
        The DataFrame with a 'unique_id' column inserted at index 0.
    """
    df.insert(0, "unique_id", range(len(df)))
    return df


def clean_columns(
    df: pd.DataFrame,
    renaming_map: dict = COLUMN_RENAMING,
    columns_to_drop: list = COLUMNS_TO_DROP,
) -> pd.DataFrame:
    """
    Renames a standard set of columns to use snake_case and drops predefined columns.

    Parameters:
        df: The input DataFrame.
        renaming_map: A dictionary mapping old column names to new ones.
        columns_to_drop: A list of column names to remove.

    Returns:
        The cleaned DataFrame with renamed columns and dropped features.
    """
    columns_to_drop_in_df = [col for col in columns_to_drop if col in df.columns]
    if columns_to_drop_in_df:
        df = df.drop(columns=columns_to_drop_in_df)

    df = df.rename(columns=renaming_map)

    return df


def clean_and_binarize_income(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the 'income' column and converts it into a boolean field.

    Parameters:
        df: The DataFrame containing the 'income' column.

    Returns:
        The DataFrame with a cleaned 'income' column and a new 'high_income' boolean column.
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

    Parameters:
        df: The input DataFrame.

    Returns:
        The DataFrame with '?' strings replaced by numpy NaNs.
    """
    return df.replace("?", np.nan)


def trim_string(value: Any) -> Any:
    """
    Trims leading and trailing whitespace from a single string.

    Parameters:
        value: The value to trim.

    Returns:
        The trimmed string, or the original value if it is not a string.
    """
    if isinstance(value, str):
        return value.strip()

    return value


def trim_dataframe_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Automatically detects string columns and strips whitespace from all values.

    Parameters:
        df: The input DataFrame.

    Returns:
        The DataFrame with whitespace stripped from all string columns.
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

    Parameters:
        df: The raw input DataFrame.

    Returns:
        The fully cleaned and preprocessed DataFrame.
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


def run_cleaning_pipeline(df: pd.DataFrame) -> None:
    """
    Runs full cleaning pipeline and saves result in parquet format.

    Parameters:
        df: The raw input DataFrame.
    """
    df = full_clean(df)

    output_path = DATA_DIR / "cleaned_census_income.parquet"

    df.to_parquet(output_path)
