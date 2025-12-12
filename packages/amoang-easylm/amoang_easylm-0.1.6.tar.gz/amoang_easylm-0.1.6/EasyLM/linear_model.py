"""
LinearModel: Minimal orchestration layer.
All computations delegated to helper classes.
"""
import numpy as np
from .base_model import BaseModel
from .exceptions import FitError, PredictError
from .data_preprocessor import DataPreprocessor
from .regression_stats import RegressionStats
from .summary_formatter import SummaryFormatter


class LinearModel(BaseModel):
    """
    OLS linear regression (R's lm equivalent).
    Pure orchestration - no direct calculations.
    """
    
    def __init__(self, add_intercept=True):
        super().__init__()
        self.add_intercept = add_intercept
        self._stats = None  # RegressionStats object
        self._formatter = SummaryFormatter()
    
    def fit(self, X, y):
        """Fit OLS model via least squares."""
        try:
            # Prepare data
            X_prep = DataPreprocessor.prepare_features(X, self.add_intercept)
            y_prep = DataPreprocessor.prepare_target(y)
            DataPreprocessor.validate_shapes(X_prep, y_prep)
            
            # Solve least squares
            beta, residuals, rank, s = np.linalg.lstsq(X_prep, y_prep, rcond=None)
            
            # Delegate all statistics computation
            self._stats = RegressionStats(X_prep, y_prep, beta, residuals)
            
            # Store required BaseModel attributes
            self.params_ = self._stats.coefficients
            self.n_obs_ = self._stats.n_obs
            self.n_features_ = self._stats.n_params
            self.is_fitted = True
            
            # Store for compatibility
            self.residuals_ = self._stats.residuals
            self.fittedvalues_ = self._stats.fitted_values
            self.cov_params_ = self._stats.cov_matrix
            self.sigma2_ = self._stats.sigma2
            
            return self
            
        except Exception as e:
            raise FitError(f"Fitting failed: {e}") from e
    
    def predict(self, X):
        """Generate predictions."""
        if not self.is_fitted:
            raise PredictError("Model not fitted.")
        
        X_prep = DataPreprocessor.prepare_features(X, self.add_intercept)
        
        if X_prep.shape[1] != self.n_features_:
            raise PredictError(
                f"Expected {self.n_features_} features, got {X_prep.shape[1]}"
            )
        
        return X_prep @ self.params_
    
    def summary(self):
        """Generate R-style summary."""
        if not self.is_fitted:
            raise FitError("Model not fitted.")
        
        coef_table = self._stats.get_coefficient_table()
        info = self._stats.get_summary_info()
        
        return self._formatter.format(coef_table, info)
    
    # Expose metrics (for ModelComparator)
    def aic(self):
        """Return AIC."""
        if not self.is_fitted:
            raise FitError("Model not fitted.")
        return self._stats.compute_aic()
    
    def bic(self):
        """Return BIC."""
        if not self.is_fitted:
            raise FitError("Model not fitted.")
        return self._stats.compute_bic()
    
    def r_squared(self):
        """Return R²."""
        if not self.is_fitted:
            raise FitError("Model not fitted.")
        return self._stats.compute_r_squared()
    
# dunder kalimot hahaha
    
    def __repr__(self):
        """Developer-friendly representation."""
        status = "fitted" if self.is_fitted else "not fitted"
        if self.is_fitted:
            return f"LinearModel(n_features={self.n_features_}, n_obs={self.n_obs_}, {status})"
        return f"LinearModel(add_intercept={self.add_intercept}, {status})"

    def __str__(self):
        """User-friendly string representation."""
        if not self.is_fitted:
            return "LinearModel (not fitted yet)"
        return (f"LinearModel: {self.n_features_} parameters, "
                f"{self.n_obs_} observations, R²={self.r_squared():.4f}")

    def __eq__(self, other):
        """Equality comparison based on coefficients (polymorphism demo)."""
        if not isinstance(other, LinearModel):
            return NotImplemented
        if not (self.is_fitted and other.is_fitted):
            return False
        return np.allclose(self.params_, other.params_, rtol=1e-5)

    def __lt__(self, other):
        """Less-than comparison by AIC - lower AIC is better (polymorphism demo)."""
        if not isinstance(other, LinearModel):
            return NotImplemented
        if not (self.is_fitted and other.is_fitted):
            raise FitError("Both models must be fitted for comparison")
        return self.aic() < other.aic()

    def __len__(self):
        """Return number of observations."""
        if not self.is_fitted:
            return 0
        return self.n_obs_

    def __getitem__(self, idx):
        """Get coefficient by index - allows model[0], model[1], etc."""
        if not self.is_fitted:
            raise PredictError("Model not fitted")
        return self.params_[idx]