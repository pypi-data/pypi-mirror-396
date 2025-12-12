# Custom runtime errors for EasyML
# stores other libraries' math equations here for us
"""
Utility functions for EasyLM.
"""

# pip-install hint (team: run install_requirements.py to install required packages)
# pip install numpy pandas matplotlib scipy

import numpy as np
import pandas as pd

def add_constant(X, prepend=True):
    """
    Add intercept column of ones to X.
    Accepts numpy arrays or pandas DataFrame/Series.
    """
    if isinstance(X, (pd.Series, pd.DataFrame)):
        arr = X.values
    else:
        arr = np.asarray(X)

    ones = np.ones((arr.shape[0], 1))
    if prepend:
        return np.hstack([ones, arr])
    else:
        return np.hstack([arr, ones])

def check_array(x, name="array"):
    """
    Ensure input is a numpy 2D array (or 1D reshaped).
    Accepts numpy arrays, lists/tuples, and pandas DataFrame/Series.
    """
    import numpy as np
    import pandas as pd

    # Convert pandas objects
    if isinstance(x, (pd.DataFrame, pd.Series)):
        x = x.to_numpy()

    # Convert lists/tuples
    elif isinstance(x, (list, tuple)):
        x = np.asarray(x)

    # Already numpy
    elif isinstance(x, np.ndarray):
        pass

    # Anything else → error
    else:
        raise ValueError(f"{name} must be convertible to a numpy.ndarray")

    # Ensure 2D shape
    if x.ndim == 1:
        x = x.reshape(-1, 1)

    return x


def design_from_df(df, predictors, add_intercept=True):
    """
    Convenience: form design matrix X from DataFrame and list of predictors
    """
    if hasattr(df, "loc"):
        X = df.loc[:, predictors]
    else:
        X = df[:, predictors]
    if add_intercept:
        return add_constant(X, prepend=True)
    else:
        return check_array(X, "X")

