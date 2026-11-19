# Flask Full-Stack + MongoDB + Docker + Kubernetes

A learning project with two separate Flask applications and MongoDB.

## Architecture

- Frontend Flask: port 5000; serves HTML and calls the backend.
- Backend Flask API: port 5001; provides user CRUD endpoints.
- MongoDB: port 27017; stores users.
- Docker Compose: runs all three services locally.
- Kubernetes: deploys frontend, backend and MongoDB into namespace `flask-app`.

## Requirements

- Python 3.10+ for local development (Docker uses Python 3.12)
- Docker Desktop / Docker Engine with Compose
- kubectl
- Minikube

## A. Run locally without Docker

Terminal 1 - MongoDB (Docker):
```bash
docker run -d --name mongodb-local \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=change-this-local-password \
  -v mongo_local_data:/data/db mongo:8
```p

Terminal 2 - backend:
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
$env:MONGO_URI="mongodb://admin:prashant@143143@localhost:27017/mydatabase?authSource=admin"
python app.py
```
On Linux/macOS, set the variable with:
`export MONGO_URI='mongodb://admin:change-this-local-password@localhost:27017/mydatabase?authSource=admin'`

Terminal 3 - frontend:
```bash
cd frontend
python -m venv .venv
# Activate the environment, then:
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## B. Run with Docker Compose

Copy `.env.example` to `.env` and change the example passwords/secrets.
```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```

Open:
- Frontend: http://localhost:5000
- Backend: http://localhost:5001
- Backend users API: http://localhost:5001/users

Stop:
```bash
docker compose down
```
Data remains in the named volume. `docker compose down -v` deletes the database volume.

## C. Deploy to Minikube

Run from the project root. Ensure Minikube is running:
```bash
minikube start --driver=docker
kubectl get nodes
```

Build images inside Minikube's image store:
```bash
minikube image build -t flask-backend:v1 ./backend
minikube image build -t flask-frontend:v1 ./frontend
```

IMPORTANT: Before applying manifests, edit `k8s/mongodb-secret.yaml` and replace the learning password. Also replace the demo `FLASK_SECRET_KEY` in `k8s/frontend-deployment.yaml` with a strong random value (preferably move it into its own Kubernetes Secret).

Apply resources in dependency order:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb-secret.yaml
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/mongodb-service.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

Or, after the namespace exists, apply all remaining manifests:
```bash
kubectl apply -f k8s/
```

Check:
```bash
kubectl get all -n flask-app
kubectl get pvc -n flask-app
kubectl get pods -n flask-app -w
kubectl describe pods -n flask-app
kubectl logs deployment/backend -n flask-app
```

Open frontend:
```bash
minikube service frontend -n flask-app
```
If needed, use a tunnel/port-forward:
```bash
kubectl port-forward -n flask-app service/frontend 5000:5000
```
Then open http://localhost:5000

Backend port-forward for API testing:
```bash
kubectl port-forward -n flask-app service/backend 5001:5001
```
Then test http://localhost:5001/health and http://localhost:5001/users.

PowerShell create-user test:
```powershell
Invoke-RestMethod -Uri http://localhost:5001/users -Method POST -ContentType "application/json" -Body '{"name":"Prashant","email":"prashant@example.com"}'
Invoke-RestMethod http://localhost:5001/users
```

## D. Useful Kubernetes commands

```bash
kubectl get pods -n flask-app
kubectl get deployments -n flask-app
kubectl get svc -n flask-app
kubectl get pvc -n flask-app
kubectl get events -n flask-app --sort-by=.metadata.creationTimestamp
kubectl scale deployment/backend --replicas=3 -n flask-app
kubectl rollout status deployment/backend -n flask-app
kubectl rollout history deployment/backend -n flask-app
kubectl rollout restart deployment/backend -n flask-app
kubectl rollout undo deployment/backend -n flask-app
kubectl exec -it deployment/backend -n flask-app -- sh
kubectl delete -f k8s/
```

## Notes / learning-project limitations

- MongoDB is a single-replica Deployment with a PVC. This is suitable for learning, not highly available production database hosting.
- Kubernetes Secret values in this demo are examples. Kubernetes Secrets are not automatically encrypted in etcd; configure encryption at rest and RBAC for real deployments.
- The MongoDB root account is used for simplicity. Production applications should use a least-privilege database user.
- The Compose and Kubernetes passwords are configured separately. If you change one, update the corresponding connection settings.
- `depends_on` in Compose controls startup ordering; MongoDB healthcheck is used to wait for database readiness. Kubernetes readiness probes govern service traffic.
