"""
Tests for fivedreg.neural_network.LightweightNN
"""
import pytest
import numpy as np
import pandas as pd
from fivedreg.neural_network import LightweightNN


class TestLightweightNN:
    """Test suite for LightweightNN class."""

    def test_initialization_defaults(self):
        """Test that LightweightNN initializes with default parameters."""
        model = LightweightNN()
        assert model.hidden_layers == [64, 32, 16]
        assert model.learning_rate == 0.001
        assert model.max_iter == 1000
        assert model.activation == 'relu'
        assert model.output_activation is None
        assert model.random_state is None
        assert model.verbose == 0
        assert not model.is_fitted_

    def test_initialization_custom_params(self):
        """Test that LightweightNN initializes with custom parameters."""
        model = LightweightNN(
            hidden_layers=[32, 16],
            learning_rate=0.01,
            max_iter=500,
            activation='tanh',
            output_activation='sigmoid',
            random_state=42,
            verbose=1
        )
        assert model.hidden_layers == [32, 16]
        assert model.learning_rate == 0.01
        assert model.max_iter == 500
        assert model.activation == 'tanh'
        assert model.output_activation == 'sigmoid'
        assert model.random_state == 42
        assert model.verbose == 1

    def test_set_params(self):
        """Test that set_params updates parameters correctly."""
        model = LightweightNN()
        model.set_params(learning_rate=0.01, max_iter=500)
        assert model.learning_rate == 0.01
        assert model.max_iter == 500

    def test_fit_with_dataframe(self):
        """Test that fit works with pandas DataFrame input."""
        X = pd.DataFrame(np.random.randn(100, 5))
        y = pd.DataFrame(np.random.randn(100, 1))
        model = LightweightNN(max_iter=10, random_state=42)
        model.fit(X, y)
        assert model.is_fitted_
        assert model.input_dim_ == 5
        assert model.output_dim_ == 1

    def test_fit_with_numpy_array(self):
        """Test that fit works with numpy array input."""
        X = np.random.randn(100, 5)
        y = np.random.randn(100, 1)
        model = LightweightNN(max_iter=10, random_state=42)
        model.fit(X, y)
        assert model.is_fitted_
        assert model.input_dim_ == 5
        assert model.output_dim_ == 1

    def test_predict_after_fit(self):
        """Test that predict works after fitting."""
        X_train = pd.DataFrame(np.random.randn(100, 5))
        y_train = pd.DataFrame(np.random.randn(100, 1))
        X_test = pd.DataFrame(np.random.randn(10, 5))

        model = LightweightNN(max_iter=10, random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        assert predictions.shape == (10, 1)
        assert isinstance(predictions, np.ndarray)

    def test_predict_with_numpy_array(self):
        """Test that predict works with numpy array input."""
        X_train = pd.DataFrame(np.random.randn(100, 5))
        y_train = pd.DataFrame(np.random.randn(100, 1))
        X_test = np.random.randn(10, 5)

        model = LightweightNN(max_iter=10, random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        assert predictions.shape == (10, 1)

    def test_predict_before_fit_raises_error(self):
        """Test that predict raises error if called before fit."""
        model = LightweightNN()
        X = pd.DataFrame(np.random.randn(10, 5))
        with pytest.raises(ValueError, match="Model must be fitted"):
            model.predict(X)

    def test_predict_wrong_dimension_raises_error(self):
        """Test that predict raises error if input dimension doesn't match."""
        X_train = pd.DataFrame(np.random.randn(100, 5))
        y_train = pd.DataFrame(np.random.randn(100, 1))
        X_test = pd.DataFrame(np.random.randn(10, 3))  # Wrong dimension

        model = LightweightNN(max_iter=10, random_state=42)
        model.fit(X_train, y_train)
        with pytest.raises(ValueError, match="Input dimension mismatch"):
            model.predict(X_test)

    def test_prepare_data_with_1d_array(self):
        """Test that _prepare_data handles 1D arrays correctly."""
        X = np.array([1, 2, 3, 4, 5])
        y = np.array([1])

        model = LightweightNN()
        X_array, y_array = model._prepare_data(X, y)

        assert X_array.shape == (5, 1)
        assert y_array.shape == (1, 1)



