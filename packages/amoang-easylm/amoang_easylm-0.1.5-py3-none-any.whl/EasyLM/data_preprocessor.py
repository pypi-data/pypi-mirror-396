"""
Data preprocessing and validation.
"""
import numpy as np
import pandas as pd


class DataPreprocessor:
    """Handles all data preparation for regression."""
    
    @staticmethod
    def validate_and_convert(data, name="array"):
        """Convert any input to numpy array."""
        if isinstance(data, (pd.DataFrame, pd.Series)):
            return data.to_numpy()
        elif isinstance(data, (list, tuple)):
            return np.asarray(data)
        elif isinstance(data, np.ndarray):
            return data
        else:
            raise ValueError(f"{name} must be array-like")
    
    @staticmethod
    def ensure_2d(array):
        """Reshape 1D to 2D if needed."""
        return array.reshape(-1, 1) if array.ndim == 1 else array
    
    @staticmethod
    def add_intercept(X):
        """Prepend column of ones."""
        ones = np.ones((X.shape[0], 1))
        return np.hstack([ones, X])
    
    @staticmethod
    def prepare_features(X, add_intercept=True):
        """Full feature preparation pipeline."""
        X = DataPreprocessor.validate_and_convert(X, "X")
        X = DataPreprocessor.ensure_2d(X)
        if add_intercept:
            X = DataPreprocessor.add_intercept(X)
        return X
    
    @staticmethod
    def prepare_target(y):
        """Full target preparation pipeline."""
        y = DataPreprocessor.validate_and_convert(y, "y")
        return y.ravel()
    
    @staticmethod
    def validate_shapes(X, y):
        """Ensure X and y have compatible shapes."""
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"X has {X.shape[0]} rows but y has {y.shape[0]}")
        return X.shape[0], X.shape[1]
