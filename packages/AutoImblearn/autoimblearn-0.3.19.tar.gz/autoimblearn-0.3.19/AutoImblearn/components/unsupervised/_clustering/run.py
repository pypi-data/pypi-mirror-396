"""
Docker client for clustering models.

Supports:
- KMeans: Classic centroid-based clustering
- DBSCAN: Density-based clustering
- AgglomerativeClustering: Hierarchical clustering
- GaussianMixture: Probabilistic clustering
- MeanShift: Mode-seeking clustering
- SpectralClustering: Graph-based clustering
"""

from AutoImblearn.components.model_client.base_estimator import BaseEstimator


class RunClusteringModel(BaseEstimator):
    """
    Docker client for clustering models.

    Args:
        model: Model name (e.g., 'kmeans', 'dbscan', 'hierarchical', 'gmm')
        data_folder: Path to data folder for volume mounting
    """

    def __init__(self, model="kmeans", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"clustering-api",
            container_name=f"{model}_clustering_container",
            volume_mounts={
                "/tmp": {
                    'bind': '/tmp',
                    'mode': 'rw'
                },
                data_folder: {
                    'bind': '/data',
                    'mode': 'rw'
                },
            },
            api_base_url="http://localhost",
            port_bindings={5000: None}  # Random host port
        )

        self.model_name = model
        self.supported_metrics = [
            'silhouette',      # Silhouette score
            'calinski',        # Calinski-Harabasz index
            'davies_bouldin',  # Davies-Bouldin index
            'inertia',         # Within-cluster sum of squares (KMeans)
        ]

# TODO write payload