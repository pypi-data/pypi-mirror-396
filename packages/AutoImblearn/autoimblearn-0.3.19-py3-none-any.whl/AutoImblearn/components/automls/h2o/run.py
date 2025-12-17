import os
from AutoImblearn.components.model_client.base_estimator import BaseEstimator


class RunH2O(BaseEstimator):
    """
    H2O AutoML client using Docker containerization.

    Follows the standardized BaseEstimator pattern with automatic
    Docker lifecycle management, dynamic port allocation, and container pooling support.
    """

    def __init__(self, data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name="h2o-api",
            container_name="h2o_container",
            container_port=8080,  # Internal port, external will be dynamic
            volume_mounts={
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
            },
            dockerfile_dir=os.path.dirname(os.path.abspath(__file__)),
        )

    @property
    def payload(self):
        """
        Create payload for H2O AutoML training.

        Returns:
            dict: Payload containing metric, dataset info, and file paths
        """
        return {
            "metric": self.args.metric,
            "model": "h2o",  # Identifier for AutoML system
            "dataset_name": self.args.dataset,
            "dataset": [
                f"{self.args.dataset}/X_train_{self.container_name}.csv",
                f"{self.args.dataset}/y_train_{self.container_name}.csv",
                f"{self.args.dataset}/X_test_{self.container_name}.csv",
                f"{self.args.dataset}/y_test_{self.container_name}.csv"
            ],
            "params": None,
        }
