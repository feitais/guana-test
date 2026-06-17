import os
import mlflow
import pandas as pd # If you use pandas, ensure it's in requirements.txt

# AWS/MLflow configuration env vars...
os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-service.mlflow.svc.cluster.local:5000"

def main():
    file_path = "/workspace/dataset.csv"
    
    if os.path.exists(file_path):
        print(f"Success! Found file at {file_path}")
        # Your pipeline processing logic here:
        # df = pd.read_csv(file_path)
    else:
        print(f"Error: File not found at {file_path}")
        return

    mlflow.set_experiment("ArgoCD_Pipeline_Run")
    with mlflow.start_run():
        mlflow.log_param("data_source", "local_s3")
        mlflow.log_metric("data_rows", 1500) 

if __name__ == "__main__":
    main()