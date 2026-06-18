import os
import ray
import pandas as pd
import mlflow
from sklearn.linear_model import LogisticRegression

# 1. Connect to the local Ray cluster context automatically
if not ray.is_initialized():
    ray.init()

print("🚀 Ray Cluster Connected successfully!")

# 2. Configure MLflow tracking to point to our in-cluster service
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow-service.mlflow.svc.cluster.local:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Distributed_KubeRay_Setup")

# 3. Configure storage paths (S3 mock via MinIO)
# The Ray workers will use these environment variables to stream data
S3_ENDPOINT = os.environ.get("MLFLOW_S3_ENDPOINT_URL", "http://s3-service.mlflow.svc.cluster.local:9000")

storage_options = {
    "key": "mock_aws_access_key",
    "secret": "mock_aws_secret_key",
    "client_kwargs": {"endpoint_url": S3_ENDPOINT}
}

@ray.remote
def train_shard(shard_id, s3_path, options):
    """Distributed worker task that runs in parallel across the Ray cluster"""
    print(f"🤖 Worker computing data shard #{shard_id}...")
    # Read the dataset file straight from our mock S3 bucket
    df = pd.read_csv(s3_path, storage_options=options)
    
    X = df[['feature']]
    y = df['label']
    
    model = LogisticRegression()
    model.fit(X, y)
    
    return float(model.score(X, y))

with mlflow.start_run():
    print("📊 Initializing parallel training runs across Ray workers...")
    s3_data_url = "s3://mlflow-bucket/dataset.csv"
    
    # Fire off parallel jobs across our worker nodes
    futures = [train_shard.remote(i, s3_data_url, storage_options) for i in range(2)]
    accuracies = ray.get(futures)
    
    mean_accuracy = sum(accuracies) / len(accuracies)
    
    # Log everything straight to MLflow
    mlflow.log_param("data_source", s3_data_url)
    mlflow.log_metric("mean_accuracy", mean_accuracy)
    
    print(f"✅ Training completed! Mean Accuracy: {mean_accuracy}")
    print("📈 Metrics pushed successfully to the MLflow Dashboard.")