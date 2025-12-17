"""
Survival analysis API using BaseSurvivalEstimatorAPI.

Supports scikit-survival models:
- CPH: Cox Proportional Hazards
- RSF: Random Survival Forest
- SVM: Fast Survival SVM
- KSVM: Fast Kernel Survival SVM
- LASSO, L1, L2, CSA: Coxnet variants
"""

import logging
from AutoImblearn.components.api import BaseSurvivalEstimatorAPI
from sksurv.ensemble import RandomSurvivalForest
from sksurv.linear_model import CoxPHSurvivalAnalysis, CoxnetSurvivalAnalysis
from sksurv.svm import FastSurvivalSVM, FastKernelSurvivalSVM
from sksurv.metrics import concordance_index_censored, concordance_index_ipcw


# Hyperparameter search spaces
hyperparameter_search_space = {
    'CPH': {
        'alpha': {
            'type': 'float_log',
            'low': 1e-5,
            'high': 1.0,
            'default': 0.0001
        }
    },
    'RSF': {
        'n_estimators': {
            'type': 'int',
            'low': 10,
            'high': 500,
            'default': 100
        },
        'max_depth': {
            'type': 'int',
            'low': 3,
            'high': 30,
            'default': 10
        },
        'min_samples_split': {
            'type': 'int',
            'low': 2,
            'high': 20,
            'default': 6
        },
        'min_samples_leaf': {
            'type': 'int',
            'low': 1,
            'high': 10,
            'default': 3
        }
    },
    'SVM': {
        'alpha': {
            'type': 'float_log',
            'low': 1e-5,
            'high': 1.0,
            'default': 1.0
        }
    },
    'KSVM': {
        'kernel': {
            'type': 'categorical',
            'choices': ['linear', 'poly', 'rbf'],
            'default': 'poly'
        },
        'alpha': {
            'type': 'float_log',
            'low': 1e-5,
            'high': 1.0,
            'default': 1.0
        }
    },
    'LASSO': {
        'l1_ratio': {
            'type': 'float',
            'low': 0.8,
            'high': 1.0,
            'default': 1.0
        },
        'alpha_min_ratio': {
            'type': 'float',
            'low': 0.001,
            'high': 0.1,
            'default': 0.01
        }
    },
    'L1': {
        'l1_ratio': {
            'type': 'float',
            'low': 0.8,
            'high': 1.0,
            'default': 1.0
        }
    },
    'L2': {
        'l1_ratio': {
            'type': 'float',
            'low': 0.0,
            'high': 0.2,
            'default': 1e-16
        }
    },
    'CSA': {
        'l1_ratio': {
            'type': 'float',
            'low': 0.0,
            'high': 1.0,
            'default': 0.5
        }
    },
    'LRSF': {
        'max_depth': {
            'type': 'int',
            'low': 5,
            'high': 20,
            'default': 10
        },
        'n_estimators': {
            'type': 'int',
            'low': 10,
            'high': 100,
            'default': 20
        },
        'max_samples': {
            'type': 'float',
            'low': 0.2,
            'high': 0.8,
            'default': 0.4
        }
    }
}


class RunSkSurvivalAPI(BaseSurvivalEstimatorAPI):
    """Survival analysis API with standardized interface."""

    def __init__(self):
        super().__init__(__name__)
        self.model_name = None
        self.model_type = 'supervised'
        self.param_space = hyperparameter_search_space
        self.y_train_cache = None  # Cache for Uno's C-index calculation

    def get_hyperparameter_search_space(self) -> dict:
        """Return hyperparameter search space for HPO integration."""
        model_name = self.params.get('model', 'CPH')
        return self.param_space.get(model_name, {})

    def _get_default_params(self, model_name: str) -> dict:
        """Get default hyperparameters."""
        if model_name not in self.param_space:
            return {}
        defaults = {}
        for param_name, param_config in self.param_space[model_name].items():
            if 'default' in param_config:
                defaults[param_name] = param_config['default']
        return defaults

    def _validate_kwargs(self, model_name: str, kwargs: dict):
        """Validate hyperparameters."""
        if model_name not in self.param_space:
            return
        allowed = set(self.param_space[model_name].keys())
        unknown = set(kwargs) - allowed
        if unknown:
            raise ValueError(
                f"Unsupported parameters for '{model_name}': {sorted(unknown)}. "
                f"Allowed: {sorted(allowed)}"
            )

    def fit(self, args, X_train, y_train, X_test=None, y_test=None):
        """Fit survival model."""
        model_name = args.model
        self.model_name = model_name

        # Normalize survival target columns if provided
        event_col = getattr(args, "event_column", None) or getattr(self.params, "event_column", None) or getattr(self.params, "target_name", None)
        time_col = getattr(args, "time_column", None) or getattr(self.params, "time_column", None)
        if event_col and time_col:
            if isinstance(y_train, pd.DataFrame):
                y_train = y_train.rename(columns={time_col: "time", event_col: "event"})
            if isinstance(y_test, pd.DataFrame):
                y_test = y_test.rename(columns={time_col: "time", event_col: "event"})

        self.y_train_cache = y_train  # Cache for Uno's C-index

        # Get hyperparameters
        try:
            model_kwargs = args.params if hasattr(args, 'params') and args.params else {}
        except AttributeError:
            model_kwargs = {}

        # Validate and merge with defaults
        self._validate_kwargs(model_name, model_kwargs)
        final_params = {**self._get_default_params(model_name), **model_kwargs}

        logging.info(f"Training {model_name} with params: {final_params}")

        # Create model
        if model_name == 'CPH':
            model = CoxPHSurvivalAnalysis(**final_params)
        elif model_name == 'RSF':
            model = RandomSurvivalForest(random_state=42, n_jobs=-1, **final_params)
        elif model_name == 'KSVM':
            model = FastKernelSurvivalSVM(random_state=42, **final_params)
        elif model_name == 'SVM':
            model = FastSurvivalSVM(random_state=42, **final_params)
        elif model_name == 'LASSO':
            model = CoxnetSurvivalAnalysis(l1_ratio=1, **final_params)
        elif model_name == 'L1':
            model = CoxnetSurvivalAnalysis(l1_ratio=1, **final_params)
        elif model_name == 'L2':
            model = CoxnetSurvivalAnalysis(l1_ratio=1e-16, **final_params)
        elif model_name == 'CSA':
            model = CoxnetSurvivalAnalysis(**final_params)
        elif model_name == 'LRSF':
            model = RandomSurvivalForest(random_state=42, **final_params)
        else:
            raise ValueError(f"Unknown model: {model_name}")

        # Fit model
        model.fit(X_train, y_train)
        logging.info("✓ Finished training")

        return model

    def predict(self, X_test, y_test):
        """Predict and evaluate."""
        # Make predictions
        predictions = self.fitted_model.predict(X_test)

        # Calculate C-index
        c_index = concordance_index_censored(
            y_test['Status'],
            y_test['Survival_in_days'],
            predictions
        )[0]

        # Calculate Uno's C-index if training data available
        c_uno = None
        if self.y_train_cache is not None:
            try:
                c_uno = concordance_index_ipcw(self.y_train_cache, y_test, predictions)[0]
            except:
                c_uno = None

        result = {
            'c_index': float(c_index),
            'c_uno': float(c_uno) if c_uno is not None else None,
            'n_events': int(y_test['Status'].sum()),
            'n_samples': len(y_test)
        }

        logging.info(f"✓ C-index: {c_index:.4f}")
        return result


if __name__ == '__main__':
    RunSkSurvivalAPI().run()
