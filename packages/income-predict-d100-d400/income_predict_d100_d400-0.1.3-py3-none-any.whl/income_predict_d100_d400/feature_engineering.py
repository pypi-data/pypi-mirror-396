from typing import Optional

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_array, check_is_fitted


class SimpleStandardScaler(BaseEstimator, TransformerMixin):
    """
    A simplified re-implementation of sklearn's StandardScaler.
    Standardizes features by removing the mean and scaling to unit variance.
    """

    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(
        self, X: np.ndarray, y: Optional[np.ndarray] = None
    ) -> "SimpleStandardScaler":
        """
        Compute the mean and std to be used for later scaling.

        Parameters:
            X: The data used to compute the mean and standard deviation.
            y: Ignored.

        Returns:
            self: The fitted scaler.
        """
        X = check_array(X)
        self.mean_ = np.mean(X, axis=0)
        self.scale_ = np.std(X, axis=0)

        # Handle constant features (zero variance) to avoid division by zero
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Perform standardization by centering and scaling.

        Parameters:
            X: The data to transform.

        Returns:
            The transformed data array.
        """
        check_is_fitted(self, ["mean_", "scale_"])
        X = check_array(X)
        return (X - self.mean_) / self.scale_
