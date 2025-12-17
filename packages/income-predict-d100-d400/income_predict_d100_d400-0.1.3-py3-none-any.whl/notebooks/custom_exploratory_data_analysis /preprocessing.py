import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from notebooks.visualisations import eda_plots as plotting


def get_data_description(df: pd.DataFrame) -> dict:
    """
    Generates a description of the data and plots distributions.

    Parameters:
        df: The DataFrame to analyze.

    Returns:
        A dictionary containing data types and a dataframe of descriptive statistics.
    """
    plotting.plot_distributions(df)

    return {"dtypes": df.dtypes, "description": df.describe(include="all")}


def get_target_distribution(df: pd.DataFrame, target: str = "income") -> pd.DataFrame:
    """
    Calculates the distribution of the target variable.

    Parameters:
        df: The DataFrame containing the target column.
        target: The name of the target column.

    Returns:
        A DataFrame with the count and percentage distribution of the target.
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
    Identifies outliers in numeric columns using the IQR method and checks for missing values.

    Parameters:
        df: The DataFrame to analyze.

    Returns:
        A DataFrame summarizing outlier counts, bounds, and missing values for each column.
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

    Parameters:
        df: The DataFrame containing categorical features.
        target: The name of the target column.

    Returns:
        A Series of Cramér's V values for each categorical feature.
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
    Calculates Pearson correlation for numeric features and Cramér's V for categorical features.

    Parameters:
        df: The DataFrame to analyze.
        target: The target variable name.

    Returns:
        A dictionary containing two Series: 'numeric' correlations and 'categorical' correlations.
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
    Separates available columns into 'numeric' and 'categorical' lists.

    Parameters:
        df: The DataFrame to examine.

    Returns:
        A dictionary with keys 'numeric' and 'categorical', containing lists of column names.
    """
    target_col = "high_income"
    features = df.drop(columns=[target_col], errors="ignore")

    return {
        "numeric": features.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical": features.select_dtypes(
            include=["object", "category"]
        ).columns.tolist(),
    }
