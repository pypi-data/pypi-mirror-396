"""
EasyLM package init
"""

from .base_model import BaseModel
from .linear_model import LinearModel
from .model_comparator import ModelComparator
from .plot_helper import PlotHelper
from .summary_formatter import SummaryFormatter
from .exceptions import EasyLMError, FitError, PredictError
from .data_preprocessor import DataPreprocessor
from .regression_stats import RegressionStats

# Backward compatibility
from .utils import add_constant, check_array

__all__ = [
    "BaseModel",
    "LinearModel",
    "ModelComparator",
    "PlotHelper",
    "SummaryFormatter",
    "EasyLMError",
    "FitError",
    "PredictError",
    "DataPreprocessor",
    "RegressionStats",
    "add_constant",
    "check_array",
]