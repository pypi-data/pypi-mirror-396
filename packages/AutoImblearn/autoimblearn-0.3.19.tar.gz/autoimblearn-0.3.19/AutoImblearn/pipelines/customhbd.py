import os
import json
from types import SimpleNamespace
from typing import Dict, Callable, Any, Optional
from pathlib import Path
import importlib.util

import numpy as np
from sklearn.base import BaseEstimator

from ..components.hybrids import RunAutoSmote, RunAutoRSP


hybrid_factories: Dict[str, Callable[..., Any]] = {
    "autosmote": lambda **kwargs: RunAutoSmote(**kwargs),
    "autorsp": lambda **kwargs: RunAutoRSP(**kwargs),
}
_BUILTIN_HYBRIDS = set(hybrid_factories.keys())


def load_custom_components():
    registry_path = Path(__file__).resolve().parents[4] / "data" / "models" / "registry" / "hybrids.json"
    if not registry_path.exists():
        registry = []
    else:
        try:
            registry = json.loads(registry_path.read_text())
        except Exception:
            registry = []
    components_root = Path(__file__).resolve().parents[1] / "components"
    for entry in registry:
        model_id = entry.get("id")
        if not model_id or model_id in hybrid_factories:
            continue
        target = components_root / "hybrids" / model_id / "run.py"
        if not target.exists():
            target = target.parent / "__init__.py"
        if not target.exists():
            continue
        spec = importlib.util.spec_from_file_location(f"AutoImblearn.components.hybrids.{model_id}", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        def factory(mod=module, mid=model_id, **kw):
            if hasattr(mod, "build_model"):
                return mod.build_model(**kw)
            if hasattr(mod, "get_model"):
                return mod.get_model(**kw)
            raise RuntimeError(f"Custom hybrid {mid} missing build_model/get_model")

        hybrid_factories[model_id] = factory


def reload_custom_components():
    """Reload custom hybrid factories, clearing previous custom entries first."""
    for key in [k for k in list(hybrid_factories.keys()) if k not in _BUILTIN_HYBRIDS]:
        hybrid_factories.pop(key, None)
    load_custom_components()


load_custom_components()


class CustomHybrid(BaseEstimator):
    """
    Unified wrapper for hybrid resampler/classifier pipelines.

    The implementation mirrors the style of CustomResamplar and CustomClassifier,
    providing sklearn-like APIs (`fit`, `predict`, `get_params`, `set_params`) while
    managing Docker-backed components under the hood.
    """

    def __init__(
        self,
        method: str = "autosmote",
        registry: Optional[Dict[str, Callable[..., Any]]] = None,
        data_folder: Optional[str] = None,
        dataset_name: Optional[str] = None,
        metric: str = "auroc",
        result_file_path: Optional[str] = None,
        imputer_method: Optional[str] = None,
        runtime_params: Optional[Dict[str, Any]] = None,
        **hybrid_kwargs: Any,
    ):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")
        if dataset_name is None:
            raise ValueError("dataset_name cannot be None")

        self.method = method
        self.registry = hybrid_factories if registry is None else registry
        self.data_folder = data_folder
        self.dataset_name = dataset_name
        self.metric = metric
        self.imputer_method = imputer_method
        self.hybrid_kwargs = dict(hybrid_kwargs)
        self.default_runtime_params = dict(runtime_params or {})

        self.result_file_path = result_file_path
        self.result_file_name = None
        self._ensure_result_path()

        self._impl = self._build_impl()
        self.result = None

    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
        runtime_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Train the hybrid component.

        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Optional validation/test features
            y_test: Optional validation/test labels
            runtime_params: Optional dict of runtime parameters to merge into the
                arguments passed to the underlying component (e.g., val_ratio, device).
        """
        args = self._build_runtime_args(runtime_params)
        self.result = self._impl.fit(
            args,
            X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
        )
        return self

    def predict(self, X_test: np.ndarray, y_test: Optional[np.ndarray] = None):
        """
        Generate predictions or results from the trained hybrid component.
        """
        result = self._impl.predict(X_test)
        self.result = result
        return result

    def cleanup(self):
        """
        Release Docker resources held by the underlying implementation.
        """
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def get_params(self, deep: bool = True):
        """
        Return estimator parameters for compatibility with sklearn tooling.
        """
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "dataset_name": self.dataset_name,
            "metric": self.metric,
            "result_file_path": self.result_file_path,
            "imputer_method": self.imputer_method,
            "runtime_params": dict(self.default_runtime_params),
            **{f"impl__{k}": v for k, v in self.hybrid_kwargs.items()},
        }
        if deep and hasattr(self._impl, "get_params"):
            for k, v in self._impl.get_params(deep=True).items():
                params.setdefault(f"impl__{k}", v)
        return params

    def set_params(self, **params):
        """
        Set estimator parameters and rebuild the underlying implementation when needed.
        """
        if "method" in params:
            self.method = params.pop("method")
        if "registry" in params:
            self.registry = params.pop("registry")
        if "data_folder" in params:
            self.data_folder = params.pop("data_folder")
        if "dataset_name" in params:
            self.dataset_name = params.pop("dataset_name")
        if "metric" in params:
            self.metric = params.pop("metric")
        if "result_file_path" in params:
            self.result_file_path = params.pop("result_file_path")
        if "imputer_method" in params:
            self.imputer_method = params.pop("imputer_method")
        if "runtime_params" in params:
            self.default_runtime_params = dict(params.pop("runtime_params") or {})

        impl_updates = {
            k[len("impl__"):]: v
            for k, v in list(params.items())
            if k.startswith("impl__")
        }
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.hybrid_kwargs.update(params)
        self._ensure_result_path()
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_result_path(self):
        """
        Ensure a result path exists and record the file name for downstream use.
        """
        if self.result_file_path is None and self.data_folder and self.dataset_name:
            self.result_file_path = os.path.join(
                self.data_folder,
                "interim",
                self.dataset_name,
                f"hybrid_{self.method}.p",
            )

        if self.result_file_path:
            os.makedirs(os.path.dirname(self.result_file_path), exist_ok=True)
            self.result_file_name = os.path.basename(self.result_file_path)

    def _build_impl(self):
        """
        Instantiate the underlying hybrid implementation from the registry.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown hybrid method '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        factory = self.registry[self.method]
        factory_kwargs = dict(self.hybrid_kwargs)
        factory_kwargs.setdefault("data_folder", self.data_folder)
        factory_kwargs.setdefault("result_file_path", self.result_file_path)
        factory_kwargs.setdefault("metric", self.metric)
        if self.imputer_method is not None:
            factory_kwargs.setdefault("imputer_method", self.imputer_method)

        impl = factory(**factory_kwargs)
        if hasattr(impl, "result_file_name") and self.result_file_name:
            impl.result_file_name = self.result_file_name
        return impl

    def _build_runtime_args(self, overrides: Optional[Dict[str, Any]] = None):
        """
        Construct a lightweight namespace with runtime arguments for the component.
        """
        args_dict = {
            "dataset": self.dataset_name,
            "path": self.data_folder,
            "metric": self.metric,
        }
        args_dict.update(self.default_runtime_params)
        if overrides:
            args_dict.update(overrides)
        return SimpleNamespace(**args_dict)
