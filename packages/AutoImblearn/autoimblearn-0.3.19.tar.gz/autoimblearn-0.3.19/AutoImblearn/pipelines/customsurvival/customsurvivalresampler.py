import logging
from typing import Dict, Callable, Any, Optional
from pathlib import Path
import importlib.util

import numpy as np
from sklearn.base import BaseEstimator

from AutoImblearn.components.survival_rsp import RunSurvivalResampler

try:
    from AutoImblearn.components.model_client.base_transformer import BaseTransformer
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseTransformer = None
    BaseDockerModelClient = None

# Docker-based survival resamplers - factory functions
survival_resamplers: Dict[str, Callable[..., Any]] = {
    'rus': lambda **kw: RunSurvivalResampler(model='rus', **kw),
    'ros': lambda **kw: RunSurvivalResampler(model='ros', **kw),
    'smote': lambda **kw: RunSurvivalResampler(model='smote', **kw),
}
_BUILTIN_SURVIVAL_RESAMPLERS = set(survival_resamplers.keys())


def load_custom_resamplers():
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

    for entry in load_registry("survival_resamplers.json"):
        mid = entry.get("id")
        if not mid or mid in survival_resamplers:
            continue
        target = components_root / "survival_rsp" / mid / "run.py"
        if not target.exists():
            target = target.parent / "__init__.py"
        if not target.exists():
            continue
        spec = importlib.util.spec_from_file_location(f"AutoImblearn.components.survival_rsp.{mid}", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        def factory(mod=module, mid=mid, **kw):
            if hasattr(mod, "build_model"):
                return mod.build_model(**kw)
            if hasattr(mod, "get_model"):
                return mod.get_model(**kw)
            raise RuntimeError(f"Custom survival resampler {mid} missing build_model/get_model")

        survival_resamplers[mid] = factory


def reload_custom_resamplers():
    """Reload custom survival resamplers, clearing previous custom entries first."""
    for key in [k for k in list(survival_resamplers.keys()) if k not in _BUILTIN_SURVIVAL_RESAMPLERS]:
        survival_resamplers.pop(key, None)
    load_custom_resamplers()


load_custom_resamplers()


def value_counter(Y: np.ndarray):
    """Count and log events and censored observations in survival data"""
    values, counts = np.unique(Y['event'], return_counts=True)
    for value, count in zip(values, counts):
        dist = count / Y.shape[0] * 100
        label = "Event" if value else "Censored"
        logging.info("\t\t {}={}, n={},\t ({:.2f}%)".format(label, value, count, dist))


class CustomSurvivalResamplar(BaseEstimator):
    """Unified survival resampler wrapper built on registry `survival_resamplers`.

    Survival-aware resampler that preserves censoring information.
    """

    def __init__(self,
                 method: str = "smote",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 sampling_strategy: Optional[float] = None,
                 **resampler_kwargs: Any):

        self.method = method
        self.registry = survival_resamplers if registry is None else registry
        self.data_folder = data_folder
        self.sampling_strategy = sampling_strategy
        self.resampler_kwargs = dict(resampler_kwargs)

        self._impl = self._build_impl()

    def fit_resample(self, args, X: np.ndarray, y: np.ndarray):
        """
        Fit and resample the survival data.
        """
        logging.info("\t Before Re-Sampling")
        value_counter(y)

        # Update data_folder if provided via args
        if hasattr(args, 'path') and args.path:
            if hasattr(self._impl, 'set_params'):
                self._impl.set_params(data_folder=args.path)

        # Update sampling strategy if set
        if self.sampling_strategy is not None and hasattr(self._impl, 'set_params'):
            self._impl.set_params(sampling_strategy=self.sampling_strategy)

        # Perform resampling
        if isinstance(self._impl, BaseTransformer):
            X_res, y_res = self._impl.fit_resample(args, X, y)
        else:
            # For non-Docker resamplers (if any exist in the future)
            X_res, y_res = self._impl.fit_resample(X, y)

        logging.info("\t After Re-Sampling")
        value_counter(y_res)

        return X_res, y_res

    def need_resample(self, Y: np.ndarray, samratio: Optional[float] = None):
        """
        Test if resampling is needed based on event/censored ratio.
        """
        if samratio is None:
            return True

        _, counts = np.unique(Y['Status'], return_counts=True)
        if len(counts) < 2:
            return False

        # ratio of events to censored
        ratio = counts[1] / counts[0]
        return ratio < samratio

    def get_params(self, deep: bool = True):
        """Get parameters for this estimator."""
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "sampling_strategy": self.sampling_strategy,
            **{f"impl__{k}": v for k, v in self.resampler_kwargs.items()},
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
        if "sampling_strategy" in params:
            self.sampling_strategy = params.pop("sampling_strategy")

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.resampler_kwargs.update(params)
        self._impl = self._build_impl()

        if impl_updates and hasattr(self._impl, "set_params"):
            self._impl.set_params(**impl_updates)
        return self

    def _build_impl(self):
        """
        Instantiate the underlying resampler from the registry.
        """
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown survival resampling method '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.resampler_kwargs["data_folder"] = self.data_folder
        factory = self.registry[self.method]
        impl = factory(**self.resampler_kwargs)

        # Set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        # Set sampling_strategy if provided and supported
        if self.sampling_strategy is not None:
            if hasattr(impl, "set_params"):
                impl.set_params(sampling_strategy=self.sampling_strategy)

        return impl

    def cleanup(self):
        """Release Docker resources held by the resampler implementation."""
        impl = getattr(self, "_impl", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()
