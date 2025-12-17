import pandas as pd
import pytest

from income_predict_d100_d400.cleaning import (
    encode_education,
    replace_question_marks_with_nan,
)


@pytest.fixture
def sample_df():
    """Creates a basic sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "education": ["Bachelors", "HS-grad", "Masters"],
            "age": [25, 30, 45],
            "workclass": [" Private ", "Self-emp-not-inc", "?"],
        }
    )


def test_encode_education(sample_df):
    """Test that education strings are correctly mapped to ordinal integers."""
    df_result = encode_education(sample_df.copy())
    expected_values = [13, 9, 14]
    assert df_result["education"].tolist() == expected_values
    assert pd.api.types.is_integer_dtype(df_result["education"])


def test_replace_question_marks_with_nan(sample_df):
    """Test that '?' strings are replaced with numpy NaN."""
    df_result = replace_question_marks_with_nan(sample_df.copy())

    assert pd.isna(df_result["workclass"][2])
    assert df_result["workclass"][0] == " Private "
