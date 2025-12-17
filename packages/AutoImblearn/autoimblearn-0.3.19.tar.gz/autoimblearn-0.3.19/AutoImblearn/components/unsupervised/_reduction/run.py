"""
Docker client for dimensionality reduction models.

Supports:
- PCA: Principal Component Analysis
- t-SNE: t-Distributed Stochastic Neighbor Embedding
- UMAP: Uniform Manifold Approximation and Projection
- TruncatedSVD: Singular Value Decomposition
- ICA: Independent Component Analysis
- NMF: Non-negative Matrix Factorization
"""

from AutoImblearn.components.model_client.base_estimator import BaseEstimator


class RunDimensionalityReduction(BaseEstimator):
    """
    Docker client for dimensionality reduction models.

    Args:
        model: Model name (e.g., 'pca', 'tsne', 'umap')
        data_folder: Path to data folder for volume mounting
    """

    def __init__(self, model="pca", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"reduction-api",
            container_name=f"{model}_reduction_container",
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
            'reconstruction',  # Reconstruction error
            'explained_var',   # Explained variance ratio (PCA, TruncatedSVD)
            'kl_divergence',   # KL divergence (t-SNE)
        ]
