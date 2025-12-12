# at first ako unta i reg sum formatter, but since we also have plans of model expansion ako ra i summary formatter 
# so that we can use it in other models we might plan on adding in the future
"""
SummaryFormatter: produce R-like summaries for LinearModel results.
"""

import numpy as np
import pandas as pd

class SummaryFormatter:
    """
    Given coefficient arrays and info dict, produce a readable string summary or pandas DataFrame.
    """

    def __init__(self, float_format="{:.4f}"):
        self.float_format = float_format

    def _coef_dataframe(self, coef_dict):
        coef = np.asarray(coef_dict["coef"])
        se = np.asarray(coef_dict["std_err"])
        t = np.asarray(coef_dict["t"])
        p = np.asarray(coef_dict["p"])
        df = pd.DataFrame({
            "Coef.": coef,
            "Std.Err.": se,
            "t value": t,
            "Pr(>|t|)": p
        })
        return df

    def format(self, coef_dict, info):
        """
        Return multi-line string with summary. Also helpful to return DataFrame when needed.
        """
        df = self._coef_dataframe(coef_dict)
        buf = []
        buf.append("Call: EasyLM LinearModel")
        buf.append("")
        buf.append(f"Observations: {info.get('n_obs')}")
        buf.append(f"Parameters: {info.get('n_params')}")
        buf.append(f"Degrees of Freedom (resid): {info.get('df_resid')}")
        buf.append("")
        buf.append("Coefficients:")
        buf.append(df.to_string(float_format=lambda x: self.float_format.format(x)))
        buf.append("")
        buf.append(f"Residual variance (sigma^2): {self.float_format.format(info.get('sigma2'))}")
        buf.append(f"R-squared: {self.float_format.format(info.get('r_squared'))}")
        buf.append(f"AIC: {self.float_format.format(info.get('aic'))}")
        buf.append(f"BIC: {self.float_format.format(info.get('bic'))}")
        return "\n".join(buf)
