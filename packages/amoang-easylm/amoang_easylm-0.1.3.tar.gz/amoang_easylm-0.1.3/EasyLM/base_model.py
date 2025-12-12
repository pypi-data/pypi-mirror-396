"""
BaseModel abstract class.
"""

from abc import ABC, abstractmethod

class BaseModel(ABC):
    """
    Base abstract model. Methods fit, predict, summary must be implemented.
    """

    def __init__(self):
        self.is_fitted = False
        self.params_ = None
        self.n_obs_ = None
        self.n_features_ = None

    @abstractmethod
    def fit(self, X, y):
        """
        Fit the model. Must set is_fitted True and params_.
        """
        raise NotImplementedError

    @abstractmethod
    def predict(self, X):
        """
        Predict using model parameters.
        """
        raise NotImplementedError
