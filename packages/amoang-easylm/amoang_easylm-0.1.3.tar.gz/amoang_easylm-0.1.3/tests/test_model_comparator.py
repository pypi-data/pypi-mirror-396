import numpy as np
from EasyLM.linear_model import LinearModel
from EasyLM.model_comparator import ModelComparator

def test_model_comparator():
    X = np.array([[1], [2], [3], [4]])
    y1 = 2 + 1.5 * X.ravel()
    y2 = 1 + 0.7 * X.ravel()

    m1 = LinearModel()
    m1.name = "m1"
    m1.fit(X, y1)

    m2 = LinearModel()
    m2.name = "m2"
    m2.fit(X, y2)

    comp = ModelComparator([m1, m2])
    df = comp.compare()

    assert "m1" in df.index
    assert "m2" in df.index
    assert "aic" in df.columns
    assert "bic" in df.columns
