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

    def __init__(self, models: List): # list of fitted models
        self.models = models

    def compare(self):
        rows = []
        for i, m in enumerate(self.models): #loop thru models
            label = getattr(m, "name", f"Model_{i}") # try ti get model name, f way name, mahimog Model_i
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
            rows.append({ # update empty list to store metrics 
                "model": label,
                "aic": aic,
                "bic": bic,
                "r_squared": r2,
                "n_params": getattr(m, "n_features_", None),
                "n_obs": getattr(m, "n_obs_", None),
            })
        return pd.DataFrame(rows).set_index("model") # create df wtih all metrics from rows(list)

    def coef_table(self):
        """
        Return a combined DataFrame of coefficients for all models.
        Non-matching coefficient counts are filled with NaN.
        """
        all_coefs = {} # dict to store coef for esahc model
        maxlen = 0 # track max number of coef
        for i, m in enumerate(self.models): #loop thru models
            label = getattr(m, "name", f"Model_{i}") #same logic if no name fallback to modeli
            try: # get models coefficeints(_params)
                coefs = getattr(m, "params_")
                all_coefs[label] = coefs # stores it here
                maxlen = max(maxlen, len(coefs)) # update maxlen
            except Exception:
                all_coefs[label] = np.array([np.nan]*maxlen) # if way _params fill it with NaN
        df = pd.DataFrame(dict((k, np.pad(v, (0, maxlen - len(v)), constant_values=np.nan)) for k, v in all_coefs.items())) # build df from dict
        return df
   
#dunder mifflin
    def __repr__(self):
        """Developer representation."""
        return f"ModelComparator(n_models={len(self.models)})"

    def __str__(self):
        """User-friendly string with comparison table."""
        df = self.compare()
        return f"Model Comparison ({len(self.models)} models):\n{df.to_string()}"

    def __len__(self):
        """Return number of models being compared."""
        return len(self.models)

    def __getitem__(self, idx):
        """Get model by index - allows comparator[0], comparator[1], etc."""
        return self.models[idx]
