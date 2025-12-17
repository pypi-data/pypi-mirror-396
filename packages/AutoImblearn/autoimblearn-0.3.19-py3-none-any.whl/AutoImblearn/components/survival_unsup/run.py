from AutoImblearn.components.model_client.base_estimator import BaseEstimator
import os


class RunSurvivalUnsupervised(BaseEstimator):
    """
    Docker client for survival unsupervised learning models.

    Args:
        model: Model name (e.g., 'survival_tree', 'survival_kmeans')
        data_folder: Path to data folder for volume mounting
    """

    def __init__(self, model="survival_tree", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")
        self.model = model

        super().__init__(
            image_name=f"survival-unsupervised-api",
            container_name=f"{model}_survival_unsupervised_container",
            container_port=8080,
            volume_mounts={
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
                "/var/run/docker.sock": "/var/run/docker.sock",
            },
            dockerfile_dir = os.path.dirname(os.path.abspath(__file__)),
        )

    @property
    def payload(self):
        # TODO write payload
        pass

        #     self.model_name = model
        # self.supported_metrics = [
        #     'log_rank',        # Log-rank statistic for cluster separation
        #     'c_index',         # Within-cluster C-index
        #     'silhouette',      # Silhouette score adapted for survival
        # ]
