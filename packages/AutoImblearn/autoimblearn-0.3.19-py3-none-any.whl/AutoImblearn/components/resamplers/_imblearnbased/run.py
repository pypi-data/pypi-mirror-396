import pandas as pd

# from ..model_client.base_model_client import BaseDockerModelClient
from AutoImblearn.components.model_client.base_transformer import BaseTransformer
import os


class RunImblearnSampler(BaseTransformer):
    # TODO make model parameter work

    def __init__(self, model="rus", data_folder=None, result_file_path=None, **resampler_kwargs):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"imblearnsampler-api",
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
            keep_alive=False,
        )
        self.model = model
        self.result_file_path = result_file_path
        self.result_file_name = os.path.basename(self.result_file_path) if self.result_file_path else None
        self.resampler_kwargs = resampler_kwargs

    @property
    def payload(self):
        # Get hyperparameters: first check args.hyperparams, then fall back to self.resampler_kwargs
        resampler_params = dict(self.resampler_kwargs or {})  # From constructor
        if hasattr(self.args, 'hyperparams') and self.args.hyperparams:
            # Override with hyperparams from args if provided
            resampler_params = dict(self.args.hyperparams.get(self.model, resampler_params) or {})

        # Pop meta fields that are not hyperparameters (defensive even if user passed them via hyperparams)
        meta_result = resampler_params.pop("result_file_name", None)
        meta_path = resampler_params.pop("result_file_path", None)
        if self.result_file_name is None and meta_result:
            self.result_file_name = meta_result
        if self.result_file_path is None and meta_path:
            self.result_file_path = meta_path

        # Resamplers only work on training data to balance classes
        # Test data should NEVER be resampled - it must maintain real-world distribution
        return {
            "metric": self.args.metric,
            "model": self.model,
            "dataset_name": self.args.dataset,  # Required for saving results
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
            ],
            # "params": resampler_params,  # Pass hyperparameters
            "resampler_kwargs": resampler_params,  # Pass hyperparameters
            "result_file_name": self.result_file_name,
        }
