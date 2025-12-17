from .base_model_api import BaseModelAPI
from abc import abstractmethod
import pickle
import os
import logging


class BaseTransformerAPI(BaseModelAPI):
    """
    Abstract base class for sklearn-like transformers.

    This class provides automatic persistence of fitted models to disk,
    allowing transform() to work even after container restarts.

    Subclasses should:
    1. Set self.fitted_model = <trained_model> after training in fit()
    2. Set self.columns if needed for column metadata
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fitted_model = None  # Subclasses should set this after training
        self.columns = None  # Optional: column names for DataFrames

    def fit_train(self, params, *args, **kwargs):
        """
        Fit the transformer and return the transformed training data.

        This method automatically saves the fitted model to disk after training.
        """
        # Call subclass's fit method - it RETURNS the fitted model (sklearn pattern!)
        self.fitted_model = self.fit(params, *args, **kwargs)

        # Save the fitted model to disk for persistence
        self._save_fitted_model(params)

        # Transform and return result
        # No need to load - fitted_model is already in memory
        result = self.transform(*args, **kwargs)
        return result

    def _save_fitted_model(self, params):
        """
        Save the fitted model to disk so it persists across container restarts.

        This is called automatically after fit() completes.
        """
        if self.fitted_model is None:
            logging.warning("No fitted_model to save. Skipping persistence.")
            return

        dataset_name = params.dataset_name
        model_dir = os.path.join("/data/interim", dataset_name)

        # Ensure directory exists
        os.makedirs(model_dir, exist_ok=True)

        # Save the fitted model
        model_path = os.path.join(model_dir, "fitted_transformer.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(self.fitted_model, f)

        # Save metadata (columns, etc.)
        metadata = {
            'columns': self.columns,
            'model_class': type(self.fitted_model).__name__
        }
        metadata_path = os.path.join(model_dir, "fitted_transformer_metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

        logging.info(f"✓ Saved fitted model to {model_path}")

    def _load_fitted_model(self, params):
        """
        Load the fitted model from disk if it exists.

        This is called automatically before transform() if fitted_model is None.
        """
        dataset_name = params.dataset_name
        model_path = os.path.join("/data/interim", dataset_name, "fitted_transformer.pkl")
        metadata_path = os.path.join("/data/interim", dataset_name, "fitted_transformer_metadata.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Fitted model not found at {model_path}. "
                f"Make sure fit() was called before transform()."
            )

        # Load the fitted model
        with open(model_path, 'rb') as f:
            self.fitted_model = pickle.load(f)

        # Load metadata
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.columns = metadata.get('columns')

        logging.info(f"✓ Loaded fitted model from {model_path}")

    @abstractmethod
    def fit(self, params, *args, **kwargs):
        """
        Fit the transformer on training data.

        Subclasses MUST return the fitted model (sklearn pattern).

        Returns:
            The fitted model/transformer
        """
        pass

    @abstractmethod
    def transform(self, *args, **kwargs):
        """
        Transform data using the fitted model.

        The fitted model is automatically loaded from disk if not in memory.
        """
        pass
