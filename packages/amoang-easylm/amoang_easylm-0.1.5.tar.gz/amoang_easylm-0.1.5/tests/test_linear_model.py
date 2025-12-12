import numpy as np
import pytest
from EasyLM.linear_model import LinearModel
from EasyLM.exceptions import FitError, PredictError

def test_linear_model_fit_basic():
    # Simple linear: y = 3 + 2x
    X = np.array([1, 2, 3, 4]).reshape(-1, 1)
    y = 3 + 2 * X.ravel()

    lm = LinearModel()
    lm.fit(X, y)

    assert lm.is_fitted
    assert lm.params_.shape[0] == 2  # intercept + slope

    intercept, slope = lm.params_
    assert np.isclose(intercept, 3, atol=1e-6)
    assert np.isclose(slope, 2, atol=1e-6)

def test_linear_model_predict_basic():
    X = np.array([1, 2, 3]).reshape(-1, 1)
    y = 4 + 0.5 * X.ravel()

    lm = LinearModel()
    lm.fit(X, y)

    preds = lm.predict(np.array([[10]]))
    assert preds.shape == (1,)

def test_linear_model_wrong_shapes():
    X = np.array([1, 2, 3]).reshape(-1, 1)
    y = np.array([5, 6])   # wrong size

    lm = LinearModel()
    with pytest.raises(FitError):
        lm.fit(X, y)

def test_predict_not_fitted():
    lm = LinearModel()
    with pytest.raises(PredictError):
        lm.predict([[1]])
