NAMESPACE_MLFLOW = mlflow
NAMESPACE_ARGOCD = argocd
NAMESPACE_KUBERAY = kuberay

.PHONY: up down status deploy-infra deploy-kuberay sync-argocd setup-s3 port-forward-mlflow port-forward-argocd

up:
	-colima start --cpu 4 --memory 16
	minikube start --driver=docker --cpus=4 --memory=8192 --disk-size=40g
	minikube addons enable ingress

down:
	-minikube stop
	-colima stop

status:
	-minikube status
	-kubectl get pods -n $(NAMESPACE_MLFLOW)
	-kubectl get pods -n $(NAMESPACE_ARGOCD)

deploy-infra:
	-kubectl create namespace $(NAMESPACE_ARGOCD)
	-kubectl create namespace $(NAMESPACE_MLFLOW)
	kubectl apply --server-side -n $(NAMESPACE_ARGOCD) -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
	kubectl apply -f infra-setup.yaml

deploy-kuberay:
	-kubectl create namespace $(NAMESPACE_KUBERAY)
	kubectl create -k "github.com/ray-project/kuberay/ray-operator/config/default?ref=v1.1.0&timeout=90s"	
sync-argocd:
	kubectl apply -f argocd-app.yaml

setup-s3:
	@echo "Ensuring dataset.csv exists locally..."
	@echo "id,feature,label" > dataset.csv
	@echo "1,0.5,1" >> dataset.csv
	@echo "2,1.2,0" >> dataset.csv
	@echo "Spinning up temporary network bridge to local MinIO endpoint..."
	kubectl port-forward svc/s3-service -n $(NAMESPACE_MLFLOW) 9000:9000 > /dev/null 2>&1 & \
	PID=$$!; \
	sleep 3; \
	echo "Creating s3://mlflow-bucket..."; \
	AWS_ACCESS_KEY_ID=mock_aws_access_key AWS_SECRET_ACCESS_KEY=mock_aws_secret_key aws --endpoint-url http://localhost:9000 s3 mb s3://mlflow-bucket --region us-east-1 || true; \
	echo "Uploading dataset.csv to mock cloud workspace..."; \
	AWS_ACCESS_KEY_ID=mock_aws_access_key AWS_SECRET_ACCESS_KEY=mock_aws_secret_key aws --endpoint-url http://localhost:9000 s3 cp dataset.csv s3://mlflow-bucket/dataset.csv --region us-east-1; \
	kill $$PID 2>/dev/null || true
	@echo "S3 Mock Storage configuration sequence complete!"
port-forward-mlflow:
	kubectl port-forward svc/mlflow-service -n $(NAMESPACE_MLFLOW) 5000:5000

port-forward-argocd:
	@echo "ArgoCD Authentication Config Profile:"
	@echo "Username: admin"
	@echo "Password: admin"
	@echo "Opening tunnel to ArgoCD Engine. Open http://localhost:8080 in your browser..."
	kubectl port-forward svc/argocd-server -n $(NAMESPACE_ARGOCD) 8080:443
