"""
Tests for fivedreg.data.DataLoader
"""
import pytest
import numpy as np
import tempfile
import pickle
import os
from fivedreg.data import DataLoader


class TestDataLoader:
    """Test suite for DataLoader class."""

    def test_initialization(self):
        """Test that DataLoader initializes with a data path."""
        data_path = "/path/to/data.pkl"
        loader = DataLoader(data_path)
        assert loader.data_path == data_path

    def test_load_data_from_pickle(self):
        """Test that load_data loads a dictionary from a pickle file."""
        # Create test data matching expected format
        n_samples = 100
        n_features = 5
        test_data = {
            'X': np.random.randn(n_samples, n_features),
            'y': np.random.randn(n_samples),
            'metadata': {
                'n_samples': n_samples,
                'n_features': n_features,
                'seed': 123,
                'feature_names': ['x1', 'x2', 'x3', 'x4', 'x5'],
                'target_name': 'y'
            }
        }

        # Create a temporary pickle file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            pickle.dump(test_data, f)
            temp_path = f.name

        try:
            # Test loading
            loader = DataLoader(temp_path)
            loaded_data = loader.load_data()

            assert isinstance(loaded_data, dict)
            assert 'X' in loaded_data
            assert 'y' in loaded_data
            assert 'metadata' in loaded_data
            assert loaded_data['X'].shape == test_data['X'].shape
            assert loaded_data['y'].shape == test_data['y'].shape
            assert loaded_data['metadata'] == test_data['metadata']
            np.testing.assert_array_equal(loaded_data['X'], test_data['X'])
            np.testing.assert_array_equal(loaded_data['y'], test_data['y'])
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_data_nonexistent_file_raises_error(self):
        """Test that load_data raises an error for nonexistent file."""
        loader = DataLoader("/nonexistent/path/data.pkl")
        with pytest.raises((FileNotFoundError, IOError)):
            loader.load_data()



