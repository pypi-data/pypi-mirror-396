"""
All regression statistics computation.
Encapsulates the complete state from fitting.
"""
import numpy as np
from scipy import stats


class RegressionStats:
    """
    Stores and computes all statistics from a fitted regression.
    This class holds the complete statistical state.
    """
    
    def __init__(self, X, y, coefficients, lstsq_residuals):
        """
        Initialize from raw fitting results.
        
        Parameters:
        -----------
        X : ndarray
            Design matrix (with intercept if used)
        y : ndarray
            Target vector
        coefficients : ndarray
            OLS coefficients
        lstsq_residuals : ndarray
            Residuals from np.linalg.lstsq
        """
        self.X = X
        self.y = y
        self.coefficients = coefficients
        self.n_obs = X.shape[0]
        self.n_params = X.shape[1]
        
        # Compute derived quantities
        self.fitted_values = X @ coefficients
        self.residuals = y - self.fitted_values
        self.df_resid = max(0, self.n_obs - self.n_params)
        
        # Compute core statistics
        self.rss = self._compute_rss(lstsq_residuals)
        self.sigma2 = self._compute_sigma2()
        self.cov_matrix = self._compute_covariance()
    
    def _compute_rss(self, lstsq_residuals):
        """Extract RSS from lstsq or compute manually."""
        if lstsq_residuals.size:
            return float(lstsq_residuals[0])
        return float(np.sum(self.residuals ** 2))
    
    def _compute_sigma2(self):
        """Compute residual variance."""
        if self.df_resid > 0:
            return self.rss / self.df_resid
        return np.nan
    
    def _compute_covariance(self):
        """Compute parameter covariance matrix with safety."""
        try:
            xtx_inv = np.linalg.inv(self.X.T @ self.X)
            return xtx_inv * self.sigma2
        except np.linalg.LinAlgError:
            return np.full((self.n_params, self.n_params), np.nan)
    
    def get_standard_errors(self):
        """Extract standard errors from covariance matrix."""
        if self.cov_matrix is None or np.all(np.isnan(self.cov_matrix)):
            return np.full_like(self.coefficients, np.nan)
        diagonal = np.diag(self.cov_matrix)
        return np.sqrt(np.clip(diagonal, a_min=0, a_max=None))
    
    def get_t_values(self):
        """Compute t-statistics."""
        se = self.get_standard_errors()
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.divide(self.coefficients, se, where=(se != 0))
            return np.where(se == 0, 0.0, t)
    
    def get_p_values(self):
        """Compute p-values from t-statistics."""
        if self.df_resid == 0:
            return np.ones_like(self.coefficients)
        t_vals = self.get_t_values()
        return 2 * stats.t.sf(np.abs(t_vals), df=self.df_resid)
    
    def get_coefficient_table(self):
        """Generate complete coefficient table."""
        return {
            "coef": self.coefficients,
            "std_err": self.get_standard_errors(),
            "t": self.get_t_values(),
            "p": self.get_p_values(),
        }
    
    def compute_aic(self):
        """Akaike Information Criterion."""
        if self.rss <= 0:
            return float("-inf")
        return 2 * self.n_params + self.n_obs * np.log(self.rss / self.n_obs)
    
    def compute_bic(self):
        """Bayesian Information Criterion."""
        if self.rss <= 0:
            return float("-inf")
        return np.log(self.n_obs) * self.n_params + self.n_obs * np.log(self.rss / self.n_obs)
    
    def compute_r_squared(self):
        """Coefficient of determination."""
        ss_total = float(np.sum((self.y - np.mean(self.y)) ** 2))
        if ss_total == 0:
            return 1.0 if self.rss == 0 else np.nan
        return 1 - self.rss / ss_total
    
    def get_summary_info(self):
        """Package all info for summary formatter."""
        return {
            "n_obs": int(self.n_obs),
            "n_params": int(self.n_params),
            "df_resid": int(self.df_resid),
            "sigma2": float(self.sigma2),
            "aic": float(self.compute_aic()),
            "bic": float(self.compute_bic()),
            "r_squared": float(self.compute_r_squared()),
        }
