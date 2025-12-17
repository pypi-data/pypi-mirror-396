"""
Lightweight neural network implementation using TensorFlow.
Designed for fast training on CPU with 5D pandas DataFrame input.
"""

import numpy as np
import pandas as pd
import keras
import tensorflow as tf
from typing import Union, List, Optional
from keras.backend import clear_session




class LightweightNN:
    """
    A lightweight neural network using TensorFlow with configurable architecture.

    Designed for fast training on CPU (< 1 minute for datasets up to 10,000 samples).
    Works with 5D pandas DataFrame input data.

    Parameters
    ----------
    hidden_layers : list of int, default=[64, 32, 16]
        Number of neurons in each hidden layer. The number of layers is determined
        by the length of this list.
    learning_rate : float, default=0.001
        Learning rate for the optimizer.
    max_iter : int, default=1000
        Maximum number of training iterations (epochs).
    activation : str, default='relu'
        Activation function for hidden layers ('relu', 'tanh', 'sigmoid').
    output_activation : str, default=None
        Activation function for output layer. None means linear activation.
    random_state : int, default=None
        Random seed for reproducibility.
    verbose : int, default=0
        Verbosity level. 0 = silent, 1 = progress updates.

    Attributes
    ----------
    model : tf.keras.Model
        The compiled TensorFlow Keras model.
    is_fitted_ : bool
        Whether the model has been fitted to data.
    input_dim_ : int
        Number of input features (determined during fit).
    output_dim_ : int
        Number of output features (determined during fit).

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> from fiveD_NN.neural_network import LightweightNN
    >>>
    >>> # Create sample 5D data
    >>> X = pd.DataFrame(np.random.randn(1000, 5))
    >>> y = pd.DataFrame(np.random.randn(1000, 1))
    >>>
    >>> # Initialize and train model
    >>> model = LightweightNN(hidden_layers=[64, 32, 16], learning_rate=0.001, max_iter=500)
    >>> model.fit(X, y)
    >>>
    >>> # Make predictions
    >>> predictions = model.predict(X)
    """

    def __init__(
        self,
        hidden_layers: List[int] = [64, 32, 16],
        learning_rate: float = 0.001,
        max_iter: int = 1000,
        activation: str = 'relu',
        output_activation: Optional[str] = None,
        random_state: Optional[int] = None,
        verbose: int = 0
    ):
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.activation = activation
        self.output_activation = output_activation
        self.random_state = random_state
        self.verbose = verbose

        # Model attributes (set during fit)
        self.model = None
        self.is_fitted_ = False
        self.input_dim_ = None
        self.output_dim_ = None
        self.history_ = None

        # Set random seeds for reproducibility
        if self.random_state is not None:
            np.random.seed(self.random_state)
            tf.random.set_seed(self.random_state)

    def reset_keras(self):
        """
        Reset the Keras session to clear memory and avoid memory leaks.
        """
        clear_session()
        self._is_fitted_ = False

    def _build_model(self, input_dim: int, output_dim: int):
        """
        Build the TensorFlow Keras model architecture.

        Parameters
        ----------
        input_dim : int
            Number of input features.
        output_dim : int
            Number of output features.
        """
        # Build sequential model
        model = keras.Sequential()

        # Input layer
        model.add(keras.layers.Input(shape=(input_dim,)))

        # Hidden layers
        for neurons in self.hidden_layers:
            model.add(keras.layers.Dense(
                neurons,
                activation=self.activation,
                kernel_initializer='glorot_uniform',
                bias_initializer='zeros'
            ))

        # Output layer
        model.add(keras.layers.Dense(
            output_dim,
            activation=self.output_activation,
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros'
        ))

        # Compile model with optimized settings for CPU
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',  # Mean squared error for regression
            metrics=['mae']  # Mean absolute error as additional metric
        )

        return model

    def _prepare_data(self, X: Union[pd.DataFrame, np.ndarray], y: Optional[Union[pd.DataFrame, np.ndarray]] = None):
        """
        Prepare input data for training or prediction.

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            Input features (5D for 5D_NN package).
        y : pd.DataFrame or np.ndarray, optional
            Target values (for training).

        Returns
        -------
        X_array : np.ndarray
            Prepared input features as numpy array.
        y_array : np.ndarray or None
            Prepared targets as numpy array (if y provided).
        """
        # Convert pandas DataFrame to numpy array if needed
        if isinstance(X, pd.DataFrame):
            X_array = X.values
        elif isinstance(X, np.ndarray):
            X_array = X
        else:
            raise TypeError(f"X must be pandas DataFrame or numpy array, got {type(X)}")

        # Ensure 2D array
        if X_array.ndim == 1:
            X_array = X_array.reshape(-1, 1)

        if y is not None:
            # Convert pandas DataFrame to numpy array if needed
            if isinstance(y, pd.DataFrame):
                y_array = y.values
            elif isinstance(y, np.ndarray):
                y_array = y
            else:
                raise TypeError(f"y must be pandas DataFrame or numpy array, got {type(y)}")

            # Ensure 2D array
            if y_array.ndim == 1:
                y_array = y_array.reshape(-1, 1)

            return X_array, y_array

        return X_array, None

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.DataFrame, np.ndarray],
        early_stopping: bool = True,
        vs: Optional[float] = None
    ) -> 'LightweightNN':
        """
        Train the neural network on the provided data.

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            Training input features (n_samples, n_features).
            For 5D_NN package, this should be 5 features.
        y : pd.DataFrame or np.ndarray
            Training target values (n_samples, n_outputs).
        early_stopping : bool, default=True
            Whether to use early stopping during training. If True, training will
            stop early if the loss does not improve for a certain number of epochs.
        vs : float, optional, default=None
            Validation split ratio. If None, no validation split is performed.
            If a float, indicates the proportion of data to use for validation (must be < 1.0).

        Returns
        -------
        self : LightweightNN
            Returns self for method chaining.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> from fiveD_NN.neural_network import LightweightNN
        >>>
        >>> X = pd.DataFrame(np.random.randn(1000, 5))
        >>> y = pd.DataFrame(np.random.randn(1000, 1))
        >>> model = LightweightNN(max_iter=500)
        >>> model.fit(X, y)
        >>> # Disable early stopping
        >>> model.fit(X, y, early_stopping=False)
        >>> # Use validation split
        >>> model.fit(X, y, vs=0.2)
        """
        # Validate vs parameter
        if vs is not None:
            if not isinstance(vs, (int, float)):
                raise TypeError(f"vs must be a float or None, got {type(vs)}")
            if vs >= 1.0 or vs <= 0.0:
                raise ValueError(f"vs must be between 0.0 and 1.0, got {vs}")

        # Prepare data
        X_array, y_array = self._prepare_data(X, y)

        # Determine dimensions
        self.input_dim_ = X_array.shape[1]
        self.output_dim_ = y_array.shape[1]

        # Build model
        self.model = self._build_model(self.input_dim_, self.output_dim_)

        # Training configuration for fast CPU training
        callbacks = []

        # Early stopping for efficiency (optional, but helps prevent overfitting)
        if early_stopping:
            # Use validation loss for monitoring if validation split is enabled
            monitor = 'val_loss' if vs is not None else 'loss'
            early_stopping_callback = keras.callbacks.EarlyStopping(
                monitor=monitor,
                patience=min(50, self.max_iter // 10),  # Adaptive patience
                restore_best_weights=False,
                verbose=0
            )
            callbacks.append(early_stopping_callback)

        # Train model with optimized settings
        # Adaptive batch size: use 32 for larger datasets, adjust for smaller datasets
        batch_size = min(32, len(X_array))
        batch_size = max(1, batch_size)  # Ensure at least 1

        # Set validation split
        validation_split = vs if vs is not None else 0.0

        self.history_ = self.model.fit(
            X_array,
            y_array,
            epochs=self.max_iter,
            batch_size=batch_size,
            verbose=self.verbose,
            callbacks=callbacks,
            shuffle=True,
            validation_split=validation_split
        )

        self.is_fitted_ = True
        return self

    def get_history(self) -> keras.callbacks.History:
        """
        Get the training history.

        Returns
        -------
        history : keras.callbacks.History
            Training history.
        """
        if self.history_ is None:
            raise ValueError("Model has not been fitted yet. Call fit(X, y) first.")
        return self.history_

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Make predictions using the trained model.

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            Input features for prediction (n_samples, n_features).

        Returns
        -------
        predictions : np.ndarray
            Predicted values (n_samples, n_outputs).

        Raises
        ------
        ValueError
            If the model has not been fitted yet.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> from fiveD_NN.neural_network import LightweightNN
        >>>
        >>> X_train = pd.DataFrame(np.random.randn(1000, 5))
        >>> y_train = pd.DataFrame(np.random.randn(1000, 1))
        >>> X_test = pd.DataFrame(np.random.randn(100, 5))
        >>>
        >>> model = LightweightNN(max_iter=500)
        >>> model.fit(X_train, y_train)
        >>> predictions = model.predict(X_test)
        """
        if not self.is_fitted_:
            raise ValueError("Model must be fitted before making predictions. Call fit(X, y) first.")

        # Prepare data
        X_array, _ = self._prepare_data(X)

        # Check input dimension matches
        if X_array.shape[1] != self.input_dim_:
            raise ValueError(
                f"Input dimension mismatch: expected {self.input_dim_} features, "
                f"got {X_array.shape[1]} features."
            )

        # Make predictions
        predictions = self.model.predict(X_array, verbose=0)

        return predictions

    def set_params(self, **params):
        """
        Set model parameters.

        Parameters
        ----------
        **params : dict
            Parameter names and values to set.

        Returns
        -------
        self : LightweightNN
            Returns self for method chaining.
        """
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid parameter: {key}")

        # Reset fitted state if architecture changes
        if any(k in params for k in ['hidden_layers', 'activation', 'output_activation']):
            self.is_fitted_ = False
            self.model = None

        return self
