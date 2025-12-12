"""
Complete Test Suite for EasyLM OOP Features
Place in tests/ folder as separate files
"""

# ============================================================================
# FILE 1: tests/test_base_model_dunders.py
# ============================================================================
"""
Test dunder methods and properties for BaseModel
"""
import pytest
import numpy as np
from EasyLM import LinearModel

class TestBaseModelProperties:
    """Test property accessors (encapsulation)."""
    
    def test_params_property(self):
        """Test params property returns correct coefficients."""
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([1, 2, 3])
        
        model = LinearModel()
        model.fit(X, y)
        
        # Access via property
        params = model.params
        
        assert params is not None
        assert len(params) == 3  # intercept + 2 features
        assert isinstance(params, np.ndarray)
    
    def test_n_obs_property(self):
        """Test n_obs property returns observation count."""
        X = np.random.randn(50, 3)
        y = np.random.randn(50)
        
        model = LinearModel()
        model.fit(X, y)
        
        assert model.n_obs == 50
    
    def test_n_features_property(self):
        """Test n_features property returns feature count."""
        X = np.random.randn(30, 4)
        y = np.random.randn(30)
        
        model = LinearModel()
        model.fit(X, y)
        
        # 4 features + 1 intercept = 5
        assert model.n_features == 5
    
    def test_properties_before_fit(self):
        """Test properties return None before fitting."""
        model = LinearModel()
        
        assert model.params is None
        assert model.n_obs is None
        assert model.n_features is None


