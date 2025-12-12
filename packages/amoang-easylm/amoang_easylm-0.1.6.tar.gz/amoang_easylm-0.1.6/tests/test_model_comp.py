# ============================================================================
# FILE 3: tests/test_model_comparator_dunders.py
# ============================================================================
"""
Test dunder methods for ModelComparator
"""
import pytest
import numpy as np
from EasyLM import LinearModel, ModelComparator

class TestModelComparatorRepr:
    """Test __repr__ method."""
    
    def test_repr_shows_model_count(self):
        """Test repr displays number of models."""
        models = [LinearModel() for _ in range(3)]
        comp = ModelComparator(models)
        
        repr_str = repr(comp)
        assert "ModelComparator" in repr_str
        assert "3" in repr_str


class TestModelComparatorStr:
    """Test __str__ method."""
    
    def test_str_shows_comparison_table(self):
        """Test str displays comparison table."""
        np.random.seed(42)
        X = np.random.randn(50, 2)
        y = np.random.randn(50)
        
        model1 = LinearModel()
        model1.fit(X, y)
        model1.name = "Model A"
        
        model2 = LinearModel()
        model2.fit(X[:40], y[:40])
        model2.name = "Model B"
        
        comp = ModelComparator([model1, model2])
        str_output = str(comp)
        
        assert "Model Comparison" in str_output
        assert "models" in str_output


class TestModelComparatorLen:
    """Test __len__ method."""
    
    def test_len_returns_model_count(self):
        """Test len returns number of models."""
        models = [LinearModel() for _ in range(5)]
        comp = ModelComparator(models)
        
        assert len(comp) == 5
    
    def test_len_empty_comparator(self):
        """Test len with no models."""
        comp = ModelComparator([])
        assert len(comp) == 0


class TestModelComparatorGetitem:
    """Test __getitem__ method."""
    
    def test_getitem_access_models(self):
        """Test indexing returns correct model."""
        model1 = LinearModel()
        model2 = LinearModel()
        model3 = LinearModel()
        
        comp = ModelComparator([model1, model2, model3])
        
        assert comp[0] is model1
        assert comp[1] is model2
        assert comp[2] is model3
    
    def test_getitem_negative_indexing(self):
        """Test negative indexing works."""
        models = [LinearModel() for _ in range(3)]
        comp = ModelComparator(models)
        
        assert comp[-1] is models[-1]
        assert comp[-2] is models[-2]
