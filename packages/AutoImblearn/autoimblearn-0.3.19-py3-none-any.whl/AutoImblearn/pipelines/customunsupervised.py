# AutoImblearn/pipelines/customunsupervised.py
"""
Pipeline wrappers for clustering (unsupervised learning).
"""

import logging
import json
from typing import Dict, Callable, Any, Optional
from pathlib import Path
import importlib.util

import numpy as np
from sklearn.base import BaseEstimator

from AutoImblearn.components.unsupervised import RunClusteringModel

try:
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseDockerModelClient = None


# Clustering models - factory functions
unsupervised_models: Dict[str, Callable[..., Any]] = {
    'kmeans': lambda **kw: RunClusteringModel(model='kmeans', **kw),
    'dbscan': lambda **kw: RunClusteringModel(model='dbscan', **kw),
    'hierarchical': lambda **kw: RunClusteringModel(model='hierarchical', **kw),
    'gmm': lambda **kw: RunClusteringModel(model='gmm', **kw),
    'meanshift': lambda **kw: RunClusteringModel(model='meanshift', **kw),
    'spectral': lambda **kw: RunClusteringModel(model='spectral', **kw),
}

def load_custom_components():
    registry_root = Path(__file__).resolve().parents[4] / "data" / "models" / "registry"
    components_root = Path(__file__).resolve().parents[1] / "components"

    def load_registry(fname):
        path = registry_root / fname
        if not path.exists():
            return []
        import json
        try:
            return json.loads(path.read_text())
        except Exception:
            return []

    def _load(model_type: str, registry_dict: Dict[str, Callable[..., Any]]):
        for entry in load_registry(f"{model_type}.json"):
            mid = entry.get("id")
            if not mid or mid in registry_dict:
                continue
            target = components_root / model_type / mid / "run.py"
            if not target.exists():
                target = target.parent / "__init__.py"
            if not target.exists():
                continue
            spec = importlib.util.spec_from_file_location(f"AutoImblearn.components.{model_type}.{mid}", target)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore

            def factory(mod=module, mid=mid, **kw):
                if hasattr(mod, "build_model"):
                    return mod.build_model(**kw)
                if hasattr(mod, "get_model"):
                    return mod.get_model(**kw)
                raise RuntimeError(f"Custom {model_type} model {mid} missing build_model/get_model")

            registry_dict[mid] = factory

    _load("clustering_models", unsupervised_models)
    combined = {**unsupervised_models}
    return combined


def reload_custom_components():
    """Reload custom unsupervised models, clearing previous custom entries first."""
    builtin = set(unsupervised_models.keys())
    for key in [k for k in list(unsupervised_models.keys()) if k not in builtin]:
        unsupervised_models.pop(key, None)
    return load_custom_components()


unsupervised_models = load_custom_components()


class CustomUnsupervisedModel(BaseEstimator):
    """Unified unsupervised model wrapper built on registry `unsupervised_models`.

    Wrapper for clustering models.

    method:           key in `registry` (e.g., 'kmeans', 'pca', 'isoforest').
    registry:         mapping from method name -> factory that returns a model.
    data_folder:      base folder where data is stored.
    metric:           evaluation metric (e.g., 'silhouette', 'calinski', 'f1').
    **model_kwargs:   forwarded to the underlying model factory.
    """

    def __init__(self,
                 method: str = "kmeans",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 metric: str = "silhouette",
                 **model_kwargs: Any):

        self.method = method
        self.registry = unsupervised_models if registry is None else registry
        self.data_folder = data_folder
        self.metric = metric
        self.model_kwargs = dict(model_kwargs)

        # Determine model type before building impl
        self.model_type = self._determine_model_type()
        self._impl = self._build_impl()
        self.result = None

    def _determine_model_type(self) -> str:
        """Determine the model type based on the method name."""
        if self.method in unsupervised_models:
            return 'clustering'
        else:
            raise ValueError(f"Unknown clustering model: {self.method}")

    def fit(self, args, X_train: np.ndarray, y_train: Optional[np.ndarray] = None):
        """
        Train unsupervised model.

        Args:
            args: Arguments object with .path for data_folder
            X_train: Training features
            y_train: Optional labels (not used for training, only for evaluation)

        Returns:
            self
        """
        # Update data_folder if provided via args
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        # Fit the model
        if isinstance(self._impl, BaseDockerModelClient):
            self._impl.fit(args, X_train, y_train)
        else:
            # For non-Docker models (if any exist in the future)
            self._impl.fit(X_train, y_train)

        return self

    def cleanup(self):
        """Release Docker resources held by the unsupervised model implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def predict(self, X_test: np.ndarray):
        """
        Make predictions.

        Args:
            X_test: Test features

        Returns:
            Predictions (cluster labels, reduced dimensions, or anomaly scores)
        """
        return self._impl.predict(X_test)

    def score(self, X_test: np.ndarray, y_test: Optional[np.ndarray] = None):
        """
        Evaluate the unsupervised model using the specified metric.

        Args:
            X_test: Test features
            y_test: Optional ground truth labels (for evaluation)

        Returns:
            Evaluation score
        """
        predictions = self.predict(X_test)

        # Evaluate based on metric
        if self.metric == "silhouette" and self.model_type == 'clustering':
            from sklearn.metrics import silhouette_score
            unique_labels = np.unique(predictions)
            if len(unique_labels) > 1:
                score = silhouette_score(X_test, predictions)
            else:
                score = 0.0

        elif self.metric == "calinski" and self.model_type == 'clustering':
            from sklearn.metrics import calinski_harabasz_score
            score = calinski_harabasz_score(X_test, predictions)

        elif self.metric == "davies_bouldin" and self.model_type == 'clustering':
            from sklearn.metrics import davies_bouldin_score
            score = davies_bouldin_score(X_test, predictions)
            # Lower is better, so negate for consistency
            score = -score

        else:
            from sklearn.metrics import silhouette_score
            unique_labels = np.unique(predictions)
            if len(unique_labels) > 1:
                score = silhouette_score(X_test, predictions)
            else:
                score = 0.0

        self.result = score

        logging.info(
            f"\t {self.model_type.capitalize()} Model: {self.method}, "
            f"Metric: {self.metric}, Score: {score:.4f}"
        )

        return score

    def get_params(self, deep: bool = True):
        """Get parameters for this estimator."""
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "metric": self.metric,
            **{f"impl__{k}": v for k, v in self.model_kwargs.items()},
        }
        if deep and hasattr(self._impl, "get_params"):
            for k, v in self._impl.get_params(deep=True).items():
                params.setdefault(f"impl__{k}", v)
        return params

    def set_params(self, **params):
        """Set parameters for this estimator."""
        if "method" in params:
            self.method = params.pop("method")
            self.model_type = self._determine_model_type()
        if "registry" in params:
            self.registry = params.pop("registry")
        if "data_folder" in params:
            self.data_folder = params.pop("data_folder")
        if "metric" in params:
            self.metric = params.pop("metric")

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.model_kwargs.update(params)
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    def _build_impl(self):
        """
        Instantiate the underlying model from the registry.

        Looks up `self.method` in the registry and instantiates the factory.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown unsupervised model '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.model_kwargs["data_folder"] = self.data_folder
        factory = self.registry[self.method]
        impl = factory(**self.model_kwargs)

        # Set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        return impl
