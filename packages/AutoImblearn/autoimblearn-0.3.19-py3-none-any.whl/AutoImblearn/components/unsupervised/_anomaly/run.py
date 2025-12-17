"""
Docker client for anomaly detection models.

Supports:
- IsolationForest: Isolation Forest
- OneClassSVM: One-Class SVM
- LOF: Local Outlier Factor
- EllipticEnvelope: Robust covariance estimation
- DBSCAN: Can be used for anomaly detection (noise points)
"""

from AutoImblearn.components.model_client.base_estimator import BaseEstimator


class RunAnomalyDetection(BaseEstimator):
    """
    Docker client for anomaly detection models.

    Args:
        model: Model name (e.g., 'isoforest', 'ocsvm', 'lof')
        data_folder: Path to data folder for volume mounting
    """

    def __init__(self, model="isoforest", data_folder=None):
        if data_folder is None:
            raise ValueError("data_folder cannot be None")

        super().__init__(
            image_name=f"anomaly-api",
            container_name=f"{model}_anomaly_container",
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
            'anomaly_score',   # Anomaly scores
            'precision',       # Precision (if labels available)
            'recall',          # Recall (if labels available)
            'f1',              # F1 score (if labels available)
        ]
