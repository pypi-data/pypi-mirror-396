import numpy as np
import pandas as pd
from EasyLM.utils import add_constant, check_array

def test_add_constant_numpy():
    X = np.array([[2], [3], [4]])
    out = add_constant(X)
    assert out.shape == (3, 2)
    assert np.all(out[:, 0] == 1)

def test_add_constant_dataframe():
    df = pd.DataFrame({"x": [2, 3, 4]})
    out = add_constant(df)
    assert out.shape == (3, 2)
    assert np.all(out[:, 0] == 1)

def test_check_array_1d():
    x = [1, 2, 3]
    arr = check_array(x)
    assert arr.shape == (3, 1)

def test_check_array_2d():
    x = [[1, 2], [3, 4]]
    arr = check_array(x)
    assert arr.shape == (2, 2)
