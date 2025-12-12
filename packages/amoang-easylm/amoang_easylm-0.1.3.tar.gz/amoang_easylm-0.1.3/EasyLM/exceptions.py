# runtime errors for our model.

# unique errors for our model
"""
Custom exceptions for EasyLM.
"""

class EasyLMError(Exception):
    """Base exception for EasyLM"""
    pass

class FitError(EasyLMError):
    """Raised when model fitting fails"""
    pass

class PredictError(EasyLMError):
    """Raised when prediction fails"""
    pass

