import os
import uuid
import requests
import pandas as pd
import numpy as np
from .base_model_client import BaseDockerModelClient


class BaseEstimator(BaseDockerModelClient):
    """Abstract base class for sklearn-like estimators/classifiers."""

    def payload(self):
        pass

    def predict(self, X):
        """Predict with data X"""
        try:
            self.ensure_container_running()
            payload = {
                # "data": self.(X).to_dict(orient="records")
            }
            response = requests.post(f"{self.api_url}/predict", json=payload)
            response.raise_for_status()
            result = response.json().get("balanced_data", [])
            return pd.DataFrame(result)
        finally:
            self.stop_container()

    def predict_proba(self, X):
        """Predict class probabilities for data X."""
        if not hasattr(self, "args") or self.args is None:
            raise RuntimeError("Estimator must be fitted before calling predict_proba().")

        inference_dir = os.path.join(self.args.path, "interim", self.args.dataset)
        os.makedirs(inference_dir, exist_ok=True)
        inference_file_name = f"X_predict_{self.container_name}_{uuid.uuid4().hex}.csv"
        inference_file_path = os.path.join(inference_dir, inference_file_name)

        try:
            self.ensure_container_running()

            if isinstance(X, pd.DataFrame):
                X_to_save = X
            else:
                X_to_save = pd.DataFrame(X)
                if X_to_save.ndim == 1 or X_to_save.shape[1] == 0:
                    X_to_save = X_to_save.to_frame(name="feature_0")
                else:
                    X_to_save.columns = [f"feature_{idx}" for idx in range(X_to_save.shape[1])]

            X_to_save.to_csv(inference_file_path, index=False, header=True)

            payload = {
                "dataset_name": self.args.dataset,
                "predict_file": f"{self.args.dataset}/{inference_file_name}",
            }

            response = requests.post(f"{self.api_url}/predict_proba", json=payload)
            response.raise_for_status()

            probabilities = response.json().get("probabilities", [])
            return np.asarray(probabilities)

        finally:
            try:
                if os.path.exists(inference_file_path):
                    os.remove(inference_file_path)
            except OSError:
                pass
            self.stop_container()
