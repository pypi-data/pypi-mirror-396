# BASE MODEL
"""
BaseModel abstract class.
"""

from abc import ABC, abstractmethod

class BaseModel(ABC):
    """
    Base abstract model. Methods fit, predict, summary must be implemented.
    """

    def __init__(self):
        self.is_fitted = False # default has the model been trained? answer: no
        self.params_ = None # models coefficients
        self.n_obs_ = None #model'snumber of observarions
        self.n_features_ = None #number of features and/or parameters

    @abstractmethod
    def fit(self, X, y): # forces child classes to implement fit else mag error
        """
        Fit the model. Must set is_fitted True and params_.
        """
        raise NotImplementedError

    @abstractmethod
    def predict(self, X): # same forces child classes to rpedict kay duhhhhhh no  prediction = no actual model dbna
        """
        Predict using model parameters.
        """
        raise NotImplementedError
    # Property accessors for encapsulation
    @property
    def params(self):
        """Get model coefficients."""
        return self.params_

    @property
    def n_obs(self):
        """Get number of observations."""
        return self.n_obs_

    @property
    def n_features(self):
        """Get number of features."""
        return self.n_features_

