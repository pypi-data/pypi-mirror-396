import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

current_file = Path(__file__).resolve()
src_directory = current_file.parent.parent
sys.path.append(str(src_directory))

import income_predict_d100_d400.plotting as plotting


def get_data_description(df: pd.DataFrame) -> dict:
    """
    1. Describe your data.
    Returns a dictionary containing data types and descriptive statistics.
    Plots the distribution of all columns.
    """
    plotting.plot_distributions(df)

    return {"dtypes": df.dtypes, "description": df.describe(include="all")}


def get_target_distribution(df: pd.DataFrame, target: str = "income") -> pd.DataFrame:
    """
    2. What is the distribution of the target variable?
    Returns the count and percentage distribution of 'high_income'.
    Side effect: Displays/Saves a bar chart of the distribution.
    """
    if target not in df.columns:
        raise ValueError(f"Column '{target}' not found in dataframe.")

    counts = df[target].value_counts()
    percents = df[target].value_counts(normalize=True) * 100

    dist_df = pd.DataFrame({"Count": counts, "Percent": percents})

    plotting.plot_target_distribution(dist_df, target)

    return dist_df


def get_outliers_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    3. Do we face outliers and missing values?
    Identifies outliers in numeric columns using the IQR method.
    Returns a summary including outlier counts, bounds, and missing values.
    For non-numeric columns, only reports missing values if present.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    outlier_summary = []

    # Process numeric columns (outliers + missing values)
    for col in numeric_cols:
        missing_count = df[col].isnull().sum()
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - (1.5 * IQR)
        upper_bound = Q3 + (1.5 * IQR)
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        count = len(outliers)

        if count > 0 or missing_count > 0:
            outlier_summary.append(
                {
                    "Column": col,
                    "Outlier Count": count,
                    "Percent": (count / len(df)) * 100,
                    "Lower Bound": lower_bound,
                    "Upper Bound": upper_bound,
                    "Missing Values": missing_count,
                }
            )

    # Process non-numeric columns (only missing values)
    for col in non_numeric_cols:
        missing_count = df[col].isnull().sum()

        if missing_count > 0:
            outlier_summary.append(
                {
                    "Column": col,
                    "Outlier Count": None,
                    "Percent": None,
                    "Lower Bound": None,
                    "Upper Bound": None,
                    "Missing Values": missing_count,
                }
            )

    if not outlier_summary:
        return pd.DataFrame(
            columns=[
                "Column",
                "Outlier Count",
                "Percent",
                "Lower Bound",
                "Upper Bound",
                "Missing Values",
            ]
        )

    plotting.plot_numeric_boxplots(df)

    return pd.DataFrame(outlier_summary).sort_values(
        "Percent", ascending=False, na_position="last"
    )


def calculate_categorical_correlations(
    df: pd.DataFrame, target: str = "income"
) -> pd.Series:
    """
    Calculate Cramér's V correlation between categorical features and the target.

    Args:
        df: DataFrame with categorical features
        target: Target column name

    Returns:
        Series of Cramér's V values for each categorical feature
    """
    if target not in df.columns:
        raise ValueError(f"Column '{target}' not found in dataframe.")

    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns
    categorical_cols = [col for col in categorical_cols if col != target]

    cramers_v_values = {}

    for col in categorical_cols:
        # Create contingency table
        contingency_table = pd.crosstab(df[col], df[target])

        # Calculate chi-square statistic
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)

        # Calculate Cramér's V
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim))

        cramers_v_values[col] = cramers_v

    return pd.Series(cramers_v_values).sort_values(ascending=False)


def get_feature_correlations(df: pd.DataFrame, target="income") -> pd.Series:
    """
    4. How do specific features correlate with the target variable?
    Calculates Pearson correlation of numeric features with 'high_income'.
    """
    results = {}

    # Numeric correlations (Pearson)
    df_temp = df.copy()
    if not pd.api.types.is_numeric_dtype(df_temp[target]):
        df_temp[target] = df_temp[target].astype("category").cat.codes

    numeric_corr = df_temp.corr(numeric_only=True)[target].sort_values(ascending=False)
    results["numeric"] = numeric_corr.drop(index=target, errors="ignore")

    # Categorical correlations (Cramér's V)
    results["categorical"] = calculate_categorical_correlations(df, target)

    plotting.plot_numeric_strip(df, target)
    plotting.plot_feature_correlations(
        results["numeric"], target, title_suffix="(Numeric - Pearson)"
    )
    plotting.plot_categorical_stack(df, target)
    plotting.plot_feature_correlations(
        results["categorical"], target, title_suffix="(Categorical - Cramér's V)"
    )

    return results


def identify_features_by_type(df: pd.DataFrame) -> dict:
    """
    5. What features can we use for the specific prediction task?
    Separates available columns into 'numeric' and 'categorical' lists,
    excluding 'high_income'.
    """
    target_col = "high_income"
    features = df.drop(columns=[target_col], errors="ignore")

    return {
        "numeric": features.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical": features.select_dtypes(
            include=["object", "category"]
        ).columns.tolist(),
    }
