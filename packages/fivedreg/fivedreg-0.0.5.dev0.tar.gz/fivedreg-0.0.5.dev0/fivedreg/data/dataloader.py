import pickle
import numpy as np
from typing import Dict, Any


class DataLoader:
    def __init__(self, data_path: str):
        """
        Initialize DataLoader with path to pickle file.

        Args:
            data_path: Path to the pickle file containing the dataset dictionary
        """
        self.data_path = data_path

    def load_data(self) -> Dict[str, Any]:
        """
        Load data from pickle file.

        Expected format:
        {
            'X': numpy array of shape (n_samples, n_features),
            'y': numpy array of shape (n_samples,),
            'metadata': dict with dataset information
        }

        Returns:
            Dictionary containing 'X', 'y', and 'metadata' keys
        """
        with open(self.data_path, 'rb') as f:
            return pickle.load(f)

    def print_data_summary(self, data: Dict[str, Any]) -> None:
        """
        Print a summary of the data dictionary.

        Args:
            data: Dictionary with 'X', 'y', and 'metadata' keys
        Returns:
            None
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary with 'X', 'y', and 'metadata' keys")

        # Check required keys
        required_keys = ['X', 'y', 'metadata']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        X = data['X']
        y = data['y']
        metadata = data['metadata']

        print("=" * 60)
        print("DATA SUMMARY")
        print("=" * 60)

        # Dataset structure
        print("\nDataset Structure:")
        print(f"  Type: {type(data).__name__}")
        print(f"  Keys: {list(data.keys())}")

        # X information
        print("\nFeature Matrix (X):")
        print(f"  Shape: {X.shape}")
        print(f"  Type: {type(X).__name__}")
        print(f"  Dtype: {X.dtype}")
        if hasattr(X, 'min') and hasattr(X, 'max'):
            print(f"  Min value: {X.min()}")
            print(f"  Max value: {X.max()}")
        if hasattr(X, 'mean'):
            print(f"  Mean: {X.mean():.4f}")
        if hasattr(X, 'std'):
            print(f"  Std: {X.std():.4f}")
        print(f"  First 5 rows:")
        print(X[:5] if len(X) >= 5 else X)

        # y information
        print("\nTarget Vector (y):")
        print(f"  Shape: {y.shape}")
        print(f"  Type: {type(y).__name__}")
        print(f"  Dtype: {y.dtype}")
        if hasattr(y, 'min') and hasattr(y, 'max'):
            print(f"  Min value: {y.min()}")
            print(f"  Max value: {y.max()}")
        if hasattr(y, 'mean'):
            print(f"  Mean: {y.mean():.4f}")
        if hasattr(y, 'std'):
            print(f"  Std: {y.std():.4f}")
        print(f"  First 10 values: {y[:10] if len(y) >= 10 else y}")

        # Metadata information
        print("\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # Data validation
        print("\nData Validation:")
        if isinstance(X, np.ndarray) and isinstance(y, np.ndarray):
            if X.shape[0] != y.shape[0]:
                print(f"  WARNING: Mismatch in sample sizes - X has {X.shape[0]} samples, y has {y.shape[0]} samples")
            else:
                print(f"  ✓ Sample sizes match: {X.shape[0]} samples")

            # Check for NaN values
            x_nan_count = np.isnan(X).sum() if X.dtype in [np.float32, np.float64] else 0
            y_nan_count = np.isnan(y).sum() if y.dtype in [np.float32, np.float64] else 0
            print(f"  NaN values in X: {x_nan_count}")
            print(f"  NaN values in y: {y_nan_count}")

        print("=" * 60)

    def get_data_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a structured summary of the data dictionary.

        Args:
            data: Dictionary with 'X', 'y', and 'metadata' keys
        Returns:
            Dictionary containing structured summary data
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary with 'X', 'y', and 'metadata' keys")

        # Check required keys
        required_keys = ['X', 'y', 'metadata']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        X = data['X']
        y = data['y']
        metadata = data['metadata']

        summary = {
            "dataset_structure": {
                "type": type(data).__name__,
                "keys": list(data.keys())
            },
            "feature_matrix": {
                "shape": list(X.shape),
                "type": type(X).__name__,
                "dtype": str(X.dtype),
                "first_5_rows": X[:5].tolist() if len(X) >= 5 else X.tolist()
            },
            "target_vector": {
                "shape": list(y.shape),
                "type": type(y).__name__,
                "dtype": str(y.dtype),
                "first_10_values": y[:10].tolist() if len(y) >= 10 else y.tolist()
            },
            "metadata": metadata,
            "validation": {}
        }

        # Add optional statistics for X
        if hasattr(X, 'min') and hasattr(X, 'max'):
            summary["feature_matrix"]["min"] = float(X.min())
            summary["feature_matrix"]["max"] = float(X.max())
        if hasattr(X, 'mean'):
            summary["feature_matrix"]["mean"] = float(X.mean())
        if hasattr(X, 'std'):
            summary["feature_matrix"]["std"] = float(X.std())

        # Add optional statistics for y
        if hasattr(y, 'min') and hasattr(y, 'max'):
            summary["target_vector"]["min"] = float(y.min())
            summary["target_vector"]["max"] = float(y.max())
        if hasattr(y, 'mean'):
            summary["target_vector"]["mean"] = float(y.mean())
        if hasattr(y, 'std'):
            summary["target_vector"]["std"] = float(y.std())

        # Data validation
        if isinstance(X, np.ndarray) and isinstance(y, np.ndarray):
            validation = {}
            if X.shape[0] != y.shape[0]:
                validation["sample_size_mismatch"] = True
                validation["message"] = f"Mismatch in sample sizes - X has {X.shape[0]} samples, y has {y.shape[0]} samples"
            else:
                validation["sample_size_mismatch"] = False
                validation["sample_count"] = int(X.shape[0])

            # Check for NaN values
            x_nan_count = int(np.isnan(X).sum()) if X.dtype in [np.float32, np.float64] else 0
            y_nan_count = int(np.isnan(y).sum()) if y.dtype in [np.float32, np.float64] else 0
            validation["nan_count_x"] = x_nan_count
            validation["nan_count_y"] = y_nan_count

            summary["validation"] = validation

        return summary