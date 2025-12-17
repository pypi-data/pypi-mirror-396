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

    def test_print_data_summary(self, capsys):
        """Test that print_data_summary prints data information."""
        test_data = {
            'X': np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]),
            'y': np.array([10.0, 20.0, 30.0]),
            'metadata': {
                'n_samples': 3,
                'n_features': 2,
                'seed': 42,
                'feature_names': ['x1', 'x2'],
                'target_name': 'y'
            }
        }

        loader = DataLoader("/dummy/path")
        loader.print_data_summary(test_data)

        captured = capsys.readouterr()
        assert "DATA SUMMARY" in captured.out
        assert "Feature Matrix (X)" in captured.out
        assert "Target Vector (y)" in captured.out
        assert "Metadata" in captured.out
        assert "Shape" in captured.out

    def test_print_data_summary_invalid_input(self):
        """Test that print_data_summary raises error for invalid input."""
        loader = DataLoader("/dummy/path")

        # Test with non-dict input
        with pytest.raises(ValueError, match="Data must be a dictionary"):
            loader.print_data_summary("not a dict")

        # Test with missing keys
        with pytest.raises(ValueError, match="Missing required keys"):
            loader.print_data_summary({'X': np.array([1, 2, 3])})

        with pytest.raises(ValueError, match="Missing required keys"):
            loader.print_data_summary({'X': np.array([1, 2, 3]), 'y': np.array([1, 2, 3])})



