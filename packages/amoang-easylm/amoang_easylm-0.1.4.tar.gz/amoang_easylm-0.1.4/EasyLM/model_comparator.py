"""
ModelComparator: compare two or more fitted models.
"""

from typing import List
import numpy as np
import pandas as pd

class ModelComparator:
    """
    Compare models using AIC, BIC, R-squared, and side-by-side coefficient table.
    Expects objects with attributes:
      - params_
      - cov_params_
      - aic()
      - bic()
      - r_squared()
      - summary() (optional)
    """

    def __init__(self, models: List):
        self.models = models

    def compare(self):
        rows = []
        for i, m in enumerate(self.models):
            label = getattr(m, "name", f"Model_{i}")
            try:
                aic = m.aic()
            except Exception:
                aic = float("nan")
            try:
                bic = m.bic()
            except Exception:
                bic = float("nan")
            try:
                r2 = m.r_squared()
            except Exception:
                r2 = float("nan")
            rows.append({
                "model": label,
                "aic": aic,
                "bic": bic,
                "r_squared": r2,
                "n_params": getattr(m, "n_features_", None),
                "n_obs": getattr(m, "n_obs_", None),
            })
        return pd.DataFrame(rows).set_index("model")

    def coef_table(self):
        """
        Return a combined DataFrame of coefficients for all models.
        Non-matching coefficient counts are filled with NaN.
        """
        all_coefs = {}
        maxlen = 0
        for i, m in enumerate(self.models):
            label = getattr(m, "name", f"Model_{i}")
            try:
                coefs = getattr(m, "params_")
                all_coefs[label] = coefs
                maxlen = max(maxlen, len(coefs))
            except Exception:
                all_coefs[label] = np.array([np.nan]*maxlen)
        df = pd.DataFrame(dict((k, np.pad(v, (0, maxlen - len(v)), constant_values=np.nan)) for k, v in all_coefs.items()))
        return df
