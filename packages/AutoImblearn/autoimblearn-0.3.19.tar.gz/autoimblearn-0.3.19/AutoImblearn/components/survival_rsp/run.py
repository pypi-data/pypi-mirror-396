from AutoImblearn.components.model_client.base_transformer import BaseTransformer
import os


class RunSurvivalResampler(BaseTransformer):
    """
    Docker-based survival resampler client.

    Supports resampling methods that preserve survival data structure:
    - rus: Random Under Sampling (preserves censoring info)
    - ros: Random Over Sampling (treats time as feature)
    - smote: SMOTE (treats time as feature, then reconstructs)
    """

    def __init__(self, model="rus", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")
        self.model = model

        super().__init__(
            image_name=f"survivalresampler-api",
            container_name=f"{model}_survival_resampler_container",
            container_port=8080,
            volume_mounts={
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
                "/var/run/docker.sock": "/var/run/docker.sock",
            },
            dockerfile_dir = os.path.dirname(os.path.abspath(__file__)),
            keep_alive=False,
        )

    @property
    def payload(self):
        # Survival resamplers only work on training data
        event_col = getattr(self.args, "event_column", None)
        time_col = getattr(self.args, "time_column", None)
        return {
            "metric": self.args.metric,
            "model": self.model,
            "dataset_name": self.args.dataset,
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
            ],
            "event_column": event_col,
            "time_column": time_col,
        }
