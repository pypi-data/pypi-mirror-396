import importlib.util
import logging
from pathlib import Path
from typing import Dict, Callable, Any, Optional

import numpy as np
from sklearn.base import BaseEstimator

from AutoImblearn.components.survival_unsup import RunSurvivalUnsupervised

try:
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseDockerModelClient = None

# Docker-based survival unsupervised models - factory functions
survival_unsupervised_models: Dict[str, Callable[..., Any]] = {
    'survival_tree': lambda **kw: RunSurvivalUnsupervised(model='survival_tree', **kw),
    'survival_kmeans': lambda **kw: RunSurvivalUnsupervised(model='survival_kmeans', **kw),
}
_BUILTIN_SURV_UNSUP = set(survival_unsupervised_models.keys())


def load_custom_unsup_models():
    registry_root = Path(__file__).resolve().parents[4] / "data" / "models" / "registry"
    components_root = Path(__file__).resolve().parents[1] / "components"

    def load_registry(fname):
        path = registry_root / fname
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text())
        except Exception:
            return []

    import json

    for entry in load_registry("survival_unsupervised_models.json"):
        mid = entry.get("id")
        if not mid or mid in survival_unsupervised_models:
            continue
        target = components_root / "survival_unsupervised_models" / mid / "run.py"
        if not target.exists():
            target = target.parent / "__init__.py"
        if not target.exists():
            continue
        spec = importlib.util.spec_from_file_location(f"AutoImblearn.components.survival_unsupervised_models.{mid}", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        def factory(mod=module, mid=mid, **kw):
            if hasattr(mod, "build_model"):
                return mod.build_model(**kw)
            if hasattr(mod, "get_model"):
                return mod.get_model(**kw)
            raise RuntimeError(f"Custom survival unsupervised model {mid} missing build_model/get_model")

        survival_unsupervised_models[mid] = factory


def reload_custom_unsup_models():
    """Reload custom survival unsupervised models, clearing previous custom entries first."""
    for key in [k for k in list(survival_unsupervised_models.keys()) if k not in _BUILTIN_SURV_UNSUP]:
        survival_unsupervised_models.pop(key, None)
    load_custom_unsup_models()


load_custom_unsup_models()


class CustomSurvivalUnsupervisedModel(BaseEstimator):
    """Unified survival unsupervised model wrapper built on registry `survival_unsupervised_models`."""

    def __init__(self,
                 method: str = "survival_tree",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 metric: str = "log_rank",
                 **model_kwargs: Any):

        self.method = method
        self.registry = survival_unsupervised_models if registry is None else registry
        self.data_folder = data_folder
        self.metric = metric
        self.model_kwargs = dict(model_kwargs)

        self._impl = self._build_impl()
        self.result = None

    def fit(self, args, X_train: np.ndarray, y_train: Optional[np.ndarray] = None):
        """Train survival unsupervised model."""
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        if isinstance(self._impl, BaseDockerModelClient):
            self._impl.fit(args, X_train, y_train)
        else:
            self._impl.fit(X_train, y_train)

        return self

    def cleanup(self):
        """Release Docker resources held by the model implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def predict(self, X_test: np.ndarray):
        """Generate clustering/assignment predictions."""
        return self._impl.predict(X_test)

    def score(self, X_test: np.ndarray, y_test: Optional[np.ndarray] = None):
        """Evaluate the model using the specified metric, if supported."""
        if hasattr(self._impl, "score"):
            return self._impl.score(X_test, y_test)
        return None

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
        """Instantiate the underlying survival unsupervised model from the registry."""
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown survival unsupervised model '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        self.model_kwargs["data_folder"] = self.data_folder
        factory = self.registry[self.method]
        impl = factory(**self.model_kwargs)

        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        return impl
