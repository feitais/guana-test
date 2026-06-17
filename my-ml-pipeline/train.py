import os
import mlflow

# Point to internal cluster services
os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-service.mlflow.svc.cluster.local:5000"
os.environ["AWS_ACCESS_KEY_ID"] = "mock_aws_access_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "mock_aws_secret_key"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://s3-service.aws-mock.svc.cluster.local:9000"

def main():
    mlflow.set_experiment("ArgoCD_Pipeline_Run")
    with mlflow.start_run():
        print("Running training logic...")
        mlflow.log_param("epochs", 10)
        mlflow.log_metric("loss", 0.02)
        print("Successfully logged to MLflow!")

if __name__ == "__main__":
    main()