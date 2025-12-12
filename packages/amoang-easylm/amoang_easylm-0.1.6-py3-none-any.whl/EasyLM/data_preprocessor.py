"""
Data preprocessing and validation.
"""
import numpy as np
import pandas as pd


class DataPreprocessor:
    """Handles all data preparation for regression."""
    
    @staticmethod  # static method so di sha mag instantiate sa object
    def validate_and_convert(data, name="array"):  # convert input into array
        """Convert any input to numpy array."""
        if isinstance(data, (pd.DataFrame, pd.Series)):  # pandas to numpy
            return data.to_numpy()
        elif isinstance(data, (list, tuple)):  # if list/tuple convert as array
            return np.asarray(data)
        elif isinstance(data, np.ndarray):  # no change keep as is
            return data
        else:
            raise ValueError(f"{name} must be array-like")
    
    @staticmethod
    def ensure_2d(array):  # convert 1d to 2d etc etc
        """Reshape 1D to 2D if needed."""
        return array.reshape(-1, 1) if array.ndim == 1 else array  # -1 means "figure out this dimension automatically"
    
    @staticmethod
    def add_intercept(X):  # creates columns of 1 same dim as x
        """Prepend column of ones."""
        ones = np.ones((X.shape[0], 1))  # take shape of x
        return np.hstack([ones, X])  # stack ones to x 
        '''
        By adding this column, the regression solver (np.linalg.lstsq) can estimate 
        β₀ along with the other coefficients.
        '''
    
    @staticmethod
    def prepare_features(X, add_intercept=True):
        """Full feature preparation pipeline."""
        X = DataPreprocessor.validate_and_convert(X, "X")  # convert 2 numpy
        X = DataPreprocessor.ensure_2d(X)  # makes and ensures na 2d
        if add_intercept:
            X = DataPreprocessor.add_intercept(X)  # add intercept
        return X
    
    @staticmethod
    def prepare_target(y):
        """Full target preparation pipeline."""
        y = DataPreprocessor.validate_and_convert(y, "y")  # convert to numpy
        return y.ravel()  # flatten to 1d
    
    @staticmethod
    def validate_shapes(X, y):
        """Ensure X and y have compatible shapes."""
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"X has {X.shape[0]} rows but y has {y.shape[0]}")
        return X.shape[0], X.shape[1]