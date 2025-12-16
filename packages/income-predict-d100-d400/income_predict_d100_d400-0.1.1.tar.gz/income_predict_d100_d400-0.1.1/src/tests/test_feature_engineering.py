import sys
from pathlib import Path

import numpy as np
import pytest

current_file = Path(__file__).resolve()
src_directory = current_file.parent.parent
sys.path.append(str(src_directory))

from income_predict_d100_d400.feature_engineering import SimpleStandardScaler


def test_simple_standard_scaler_integration():
    """Tests the scaler against known inputs and outputs."""
    data = np.array([[1, 2], [3, 4], [5, 6]])
    scaler = SimpleStandardScaler().fit(data)

    expected_mean = np.array([3.0, 4.0])
    expected_std = np.array([1.63299, 1.63299])

    np.testing.assert_allclose(scaler.mean_, expected_mean, rtol=1e-5)

    transformed = scaler.transform(data)
    expected_transformed = (data - expected_mean) / expected_std
    np.testing.assert_allclose(transformed, expected_transformed, rtol=1e-5)


def test_constant_column():
    """Tests that constant columns (zero variance) do not cause division by zero."""
    data_const = np.array([[1], [1], [1]])
    scaler = SimpleStandardScaler().fit(data_const)

    assert scaler.scale_[0] == 1.0
    transformed = scaler.transform(data_const)
    np.testing.assert_array_equal(transformed, np.zeros((3, 1)))


@pytest.mark.parametrize(
    "input_data", [np.array([[10, 20], [30, 40]]), np.array([[-1.5, 2.5], [0.5, -0.5]])]
)
def test_scaler_output_shape(input_data):
    scaler = SimpleStandardScaler().fit(input_data)
    assert scaler.transform(input_data).shape == input_data.shape
