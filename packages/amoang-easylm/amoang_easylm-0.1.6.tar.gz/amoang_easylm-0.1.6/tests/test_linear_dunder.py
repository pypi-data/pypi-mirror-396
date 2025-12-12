# ============================================================================
# FILE 2: tests/test_linear_model_dunders.py
# ============================================================================
"""
Test dunder methods for LinearModel
"""
import pytest
import numpy as np
from EasyLM import LinearModel
from EasyLM.exceptions import FitError, PredictError

class TestLinearModelRepr:
    """Test __repr__ method."""
    
    def test_repr_before_fit(self):
        """Test repr shows 'not fitted' before training."""
        model = LinearModel()
        repr_str = repr(model)
        
        assert "not fitted" in repr_str
        assert "LinearModel" in repr_str
    
    def test_repr_after_fit(self):
        """Test repr shows stats after training."""
        X = np.random.randn(100, 2)
        y = np.random.randn(100)
        
        model = LinearModel()
        model.fit(X, y)
        repr_str = repr(model)
        
        assert "fitted" in repr_str
        assert "n_features" in repr_str
        assert "n_obs" in repr_str


class TestLinearModelStr:
    """Test __str__ method."""
    
    def test_str_before_fit(self):
        """Test str before fitting."""
        model = LinearModel()
        str_output = str(model)
        
        assert "not fitted" in str_output.lower()
    
    def test_str_after_fit(self):
        """Test str shows readable summary after fitting."""
        X = np.random.randn(80, 3)
        y = np.random.randn(80)
        
        model = LinearModel()
        model.fit(X, y)
        str_output = str(model)
        
        assert "LinearModel" in str_output
        assert "parameters" in str_output
        assert "observations" in str_output
        assert "R²" in str_output or "R-squared" in str_output


class TestLinearModelEq:
    """Test __eq__ method (polymorphism - operator overloading)."""
    
    def test_equal_models_same_data(self):
        """Test two models trained on same data are equal."""
        X = np.random.seed(42)
        X = np.random.randn(50, 2)
        y = 2 + 3*X[:, 0] - 1*X[:, 1]
        
        model1 = LinearModel()
        model1.fit(X, y)
        
        model2 = LinearModel()
        model2.fit(X, y)
        
        assert model1 == model2
    
    def test_unequal_models_different_data(self):
        """Test models trained on different data are not equal."""
        X1 = np.random.randn(50, 2)
        y1 = np.random.randn(50)
        
        X2 = np.random.randn(50, 2)
        y2 = np.random.randn(50)
        
        model1 = LinearModel()
        model1.fit(X1, y1)
        
        model2 = LinearModel()
        model2.fit(X2, y2)
        
        assert model1 != model2
    
    def test_eq_unfitted_models(self):
        """Test unfitted models return False."""
        model1 = LinearModel()
        model2 = LinearModel()
        
        assert model1 != model2
    
    def test_eq_with_non_model(self):
        """Test equality with non-LinearModel returns NotImplemented."""
        X = np.random.randn(30, 2)
        y = np.random.randn(30)
        
        model = LinearModel()
        model.fit(X, y)
        
        assert (model == "not a model") == False
        assert (model == 42) == False


class TestLinearModelLt:
    """Test __lt__ method (polymorphism - operator overloading)."""
    
    def test_compare_by_aic(self):
        """Test models can be compared by AIC (lower is better)."""
        np.random.seed(42)
        X = np.random.randn(100, 2)
        y = 2 + 3*X[:, 0] + np.random.randn(100)*0.1
        
        # Simple model (fewer parameters)
        model1 = LinearModel(add_intercept=False)
        model1.fit(X[:, 0].reshape(-1, 1), y)
        
        # Complex model (more parameters)
        model2 = LinearModel()
        model2.fit(X, y)
        
        # One should be "better" (lower AIC)
        can_compare = (model1 < model2) or (model2 < model1)
        assert can_compare
    
    def test_lt_unfitted_raises_error(self):
        """Test comparing unfitted models raises error."""
        model1 = LinearModel()
        model2 = LinearModel()
        
        with pytest.raises(FitError):
            _ = model1 < model2


class TestLinearModelLen:
    """Test __len__ method."""
    
    def test_len_before_fit(self):
        """Test len returns 0 before fitting."""
        model = LinearModel()
        assert len(model) == 0
    
    def test_len_after_fit(self):
        """Test len returns number of observations."""
        X = np.random.randn(75, 3)
        y = np.random.randn(75)
        
        model = LinearModel()
        model.fit(X, y)
        
        assert len(model) == 75


class TestLinearModelGetitem:
    """Test __getitem__ method."""
    
    def test_getitem_access_coefficients(self):
        """Test indexing returns correct coefficients."""
        X = np.array([[1], [2], [3], [4]])
        y = np.array([2, 4, 6, 8])
        
        model = LinearModel()
        model.fit(X, y)
        
        # Should be able to access coefficients by index
        intercept = model[0]
        slope = model[1]
        
        assert isinstance(intercept, (float, np.number))
        assert isinstance(slope, (float, np.number))
        
        # Check it matches params_
        assert np.isclose(model[0], model.params_[0])
        assert np.isclose(model[1], model.params_[1])
    
    def test_getitem_before_fit_raises_error(self):
        """Test accessing coefficients before fit raises error."""
        model = LinearModel()
        
        with pytest.raises(PredictError):
            _ = model[0]
    
    def test_getitem_all_coefficients(self):
        """Test accessing all coefficients via indexing."""
        X = np.random.randn(50, 3)
        y = np.random.randn(50)
        
        model = LinearModel()
        model.fit(X, y)
        
        # Should have 4 coefficients (intercept + 3 features)
        for i in range(4):
            coef = model[i]
            assert coef == model.params_[i]




