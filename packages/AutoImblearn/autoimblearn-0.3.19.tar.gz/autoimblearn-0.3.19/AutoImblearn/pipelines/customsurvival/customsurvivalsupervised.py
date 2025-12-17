import importlib.util
import logging
from pathlib import Path
from typing import Dict, Callable, Any, Optional

import numpy as np
from sklearn.base import BaseEstimator

from AutoImblearn.components.survival_supv import RunSkSurvivalModel

try:
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseDockerModelClient = None

# Docker-based survival models - factory functions
survival_models: Dict[str, Callable[..., Any]] = {
    'CPH': lambda **kw: RunSkSurvivalModel(model='CPH', **kw),
    'RSF': lambda **kw: RunSkSurvivalModel(model='RSF', **kw),
    'SVM': lambda **kw: RunSkSurvivalModel(model='SVM', **kw),
    'KSVM': lambda **kw: RunSkSurvivalModel(model='KSVM', **kw),
    'LASSO': lambda **kw: RunSkSurvivalModel(model='LASSO', **kw),
    'L1': lambda **kw: RunSkSurvivalModel(model='L1', **kw),
    'L2': lambda **kw: RunSkSurvivalModel(model='L2', **kw),
    'CSA': lambda **kw: RunSkSurvivalModel(model='CSA', **kw),
    'LRSF': lambda **kw: RunSkSurvivalModel(model='LRSF', **kw),
}
_BUILTIN_SURVIVAL_MODELS = set(survival_models.keys())


def load_custom_models():
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

    for entry in load_registry("survival_models.json"):
        mid = entry.get("id")
        if not mid or mid in survival_models:
            continue
        target = components_root / "survival_models" / mid / "run.py"
        if not target.exists():
            target = target.parent / "__init__.py"
        if not target.exists():
            continue
        spec = importlib.util.spec_from_file_location(f"AutoImblearn.components.survival_models.{mid}", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        def factory(mod=module, mid=mid, **kw):
            if hasattr(mod, "build_model"):
                return mod.build_model(**kw)
            if hasattr(mod, "get_model"):
                return mod.get_model(**kw)
            raise RuntimeError(f"Custom survival model {mid} missing build_model/get_model")

        survival_models[mid] = factory


def reload_custom_models():
    """Reload custom survival models, clearing previous custom entries first."""
    for key in [k for k in list(survival_models.keys()) if k not in _BUILTIN_SURVIVAL_MODELS]:
        survival_models.pop(key, None)
    load_custom_models()


load_custom_models()


class CustomSurvivalModel(BaseEstimator):
    """Unified survival model wrapper built on registry `survival_models`."""

    def __init__(self,
                 method: str = "CPH",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 metric: str = "c_index",
                 **model_kwargs: Any):

        self.method = method
        self.registry = survival_models if registry is None else registry
        self.data_folder = data_folder
        self.metric = metric
        self.model_kwargs = dict(model_kwargs)

        self._impl = self._build_impl()
        self.result = None

    def fit(self, args, X_train: np.ndarray, y_train: np.ndarray):
        """Train survival model."""
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        if isinstance(self._impl, BaseDockerModelClient):
            self._impl.fit(args, X_train, y_train)
        else:
            self._impl.fit(X_train, y_train)

        return self

    def cleanup(self):
        """Release Docker resources held by the survival model implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def predict(self, X_test: np.ndarray):
        """Make risk predictions."""
        return self._impl.predict(X_test)

    def score(self, X_test: np.ndarray, y_test: np.ndarray, y_train: Optional[np.ndarray] = None):
        """Evaluate the survival model using the specified metric."""
        if self.metric == "c_index":
            predictions = self.predict(X_test)
            from sksurv.metrics import concordance_index_censored, concordance_index_ipcw

            c_index = concordance_index_censored(
                y_test['Status'],
                y_test['Survival_in_days'],
                predictions
            )[0]

            c_uno = None
            if y_train is not None:
                try:
                    c_uno = concordance_index_ipcw(y_train, y_test, predictions)[0]
                except Exception:
                    c_uno = None

            self.result = {
                'c_index': c_index,
                'c_uno': c_uno,
                'n_events': int(y_test['Status'].sum())
            }

            logging.info(
                "\t Survival Model: {}, C-index: {:.4f}, C-uno: {}, Events: {}".format(
                    self.method,
                    c_index,
                    f"{c_uno:.4f}" if c_uno else "N/A",
                    int(y_test['Status'].sum())
                )
            )

            return c_index
        else:
            raise ValueError(f"Metric '{self.metric}' is not supported for survival analysis")

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
        """Instantiate the underlying survival model from the registry."""
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown survival model '{self.method}'. "
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
