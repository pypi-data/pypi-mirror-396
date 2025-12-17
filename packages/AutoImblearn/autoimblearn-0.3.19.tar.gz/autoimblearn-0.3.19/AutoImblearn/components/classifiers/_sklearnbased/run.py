import pandas as pd

# from ..model_client.base_model_client import BaseDockerModelClient
from AutoImblearn.components.model_client.base_estimator import BaseEstimator
import os


class RunSklearnClf(BaseEstimator):
    # TODO make model parameter work

    def __init__(self, model="svm", data_folder=None, result_file_path=None, result_file_name=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        self.model = model
        self.result_file_path = result_file_path
        if result_file_name:
            self.result_file_name = result_file_name
        elif result_file_path:
            self.result_file_name = os.path.basename(result_file_path)
        else:
            self.result_file_name = f"model_{model}.p"

        super().__init__(
            image_name=f"sklearnclf-api",
            container_name=f"{model}_container",
            # TODO make port dynamic
            container_port=8080,
            volume_mounts={
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
                "/var/run/docker.sock": "/var/run/docker.sock",  # give container full control of docker
            },  # mount current dir
            dockerfile_dir = os.path.dirname(os.path.abspath(__file__)),
        )

    @property
    def payload(self):
        # Get hyperparameters for this specific model (if provided)
        hyperparams = None
        model_name = self.model
        if hasattr(self.args, 'hyperparams') and self.args.hyperparams:
            # args.hyperparams is a dict: {'lr': {'C': 0.1, 'penalty': 'l1'}, 'smote': {...}}
            hyperparams = self.args.hyperparams.get(model_name, None)

        return {
            "metric": self.args.metric,
            "model": model_name,
            "dataset_name": self.args.dataset,  # Required for saving fitted models
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
                f"{self.args.dataset}/X_test_{self.container_name}.csv",
                f"{self.args.dataset}/y_test_{self.container_name}.csv"
            ],
            "params": hyperparams,  # Pass hyperparameters (or None for defaults)
            "result_file_name": self.result_file_name,
        }
