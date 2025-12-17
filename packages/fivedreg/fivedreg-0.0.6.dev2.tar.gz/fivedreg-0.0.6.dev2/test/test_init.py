"""
Tests for fivedreg package initialization
"""
import fivedreg


def test_package_imports():
    """Test that main classes can be imported from package."""
    assert hasattr(fivedreg, 'LightweightNN')
    assert hasattr(fivedreg, '__version__')


def test_lightweight_nn_import():
    """Test that LightweightNN can be imported."""
    from fivedreg import LightweightNN
    assert LightweightNN is not None


def test_dataloader_import():
    """Test that DataLoader can be imported from data module."""
    from fivedreg.data import DataLoader
    assert DataLoader is not None

