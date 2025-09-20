# Financial Health API

A Flask-based REST API for managing financial health tips, containerized with Docker and deployable on Kubernetes.

## 🚀 Features

- **Flask REST API** with SQLAlchemy database integration
- **Docker containerization** for consistent deployments
- **Kubernetes deployment** with auto-scaling capabilities
- **Health checks** and monitoring endpoints
- **Terraform infrastructure** for cloud deployment
- **Production-ready** with proper error handling and logging

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check and API information |
| `GET` | `/tips` | Retrieve all financial tips |
| `POST` | `/tips` | Add a new financial tip |

### Example Responses

**GET /** 
```json
{
  "message": "Hello from Dockerized Flask App!",
  "status": "running",
  "available_endpoints": ["/tips"]
}
```

**GET /tips**
```json
{
  "tips": [
    "Create a budget and stick to it",
    "Build an emergency fund"
  ]
}
```

**POST /tips**
```json
// Request body
{
  "tip": "Invest in low-cost index funds"
}

// Response
{
  "message": "Tip added!"
}
```

## 🐳 Docker Usage

### Build the Docker Image
```bash
docker build -t financial-health-api .
```

### Run the Container
```bash
# Run on port 8080 (recommended to avoid macOS port conflicts)
docker run -p 8080:5001 financial-health-api

# Access the API
curl http://localhost:8080
```

### Docker Commands
```bash
# View running containers
docker ps

# Check container logs
docker logs <container-id>

# Stop container
docker stop <container-id>
```

## ☸️ Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (minikube, EKS, GKE, AKS)
- kubectl configured

### Deploy to Kubernetes
```bash
# Deploy the application (5 replicas for high availability)
kubectl apply -f k8s-deployment.yaml

# Deploy the service (multiple options available)
kubectl apply -f k8s-service.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
```

### Scaling
```bash
# Scale to 8 pods
kubectl scale deployment financial-health-api --replicas=8

# Auto-scale based on CPU usage
kubectl autoscale deployment financial-health-api --cpu-percent=70 --min=3 --max=10
```

### Service Options

#### 1. LoadBalancer (Cloud Environments)
- **Best for:** AWS EKS, Google GKE, Azure AKS
- **Access:** External IP provided by cloud provider
- **Port:** 80

#### 2. NodePort (Local/Testing)
- **Best for:** Minikube, local clusters
- **Access:** `http://<node-ip>:30080`
- **Port:** 30080

#### 3. Ingress (Production with Custom Domain)
- **Best for:** Production with custom domains
- **Requires:** Ingress controller (nginx, traefik)
- **Access:** `http://financial-health-api.local`

## 🏗️ Infrastructure as Code

The project includes Terraform configuration for cloud deployment:

- `main.tf` - Main infrastructure configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values

## 📁 Project Structure

```
financial-health-api/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── k8s-deployment.yaml   # Kubernetes deployment (5 replicas)
├── k8s-service.yaml      # Kubernetes service options
├── main.tf              # Terraform main configuration
├── variables.tf         # Terraform variables
├── outputs.tf           # Terraform outputs
├── instance/            # SQLite database directory
│   └── tips.db         # SQLite database file
└── README.md           # This file
```

## 🛠️ Development Setup

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:5001
```

### Environment Variables
- `FLASK_ENV`: Set to `production` for production deployments
- Database is automatically created using SQLite

## 🔍 Monitoring and Health Checks

### Health Endpoints
- **Liveness Probe:** `GET /` - Checks if application is running
- **Readiness Probe:** `GET /` - Checks if application is ready to serve traffic

### Kubernetes Health Checks
- **Initial Delay:** 30 seconds for liveness, 5 seconds for readiness
- **Check Interval:** 10 seconds for liveness, 5 seconds for readiness

## 🚀 Deployment Examples

### Quick Start with Docker
```bash
# Clone the repository
git clone <repository-url>
cd financial-health-api

# Build and run
docker build -t financial-health-api .
docker run -p 8080:5001 financial-health-api

# Test the API
curl http://localhost:8080
curl -X POST http://localhost:8080/tips \
  -H "Content-Type: application/json" \
  -d '{"tip": "Save 20% of your income"}'
```

### Production Kubernetes Deployment
```bash
# Deploy to production cluster
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml

# Get external IP
kubectl get service financial-health-api-service

# Monitor deployment
kubectl get pods -l app=financial-health-api -w
```

## 📊 Resource Requirements

### Kubernetes Resources
- **Memory:** 128Mi request, 256Mi limit per pod
- **CPU:** 100m request, 200m limit per pod
- **Replicas:** 5 pods for high availability
- **Total Resources:** ~640Mi memory, 1000m CPU (across all pods)

## 🔧 Troubleshooting

### Common Issues

**Port 5000 already in use (macOS)**
- Solution: Use port 8080 instead: `docker run -p 8080:5001 financial-health-api`

**Docker daemon not running**
- Solution: Start Docker Desktop application

**Kubernetes pods not starting**
- Check: `kubectl describe pod <pod-name>`
- Verify: Image is available and resource limits

**Database connection issues**
- SQLite database is created automatically in the `instance/` directory
- Ensure write permissions for the container

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏷️ Version History

- **v1.0.0** - Initial release with Docker and Kubernetes support
- **v1.1.0** - Added 5-replica scaling and comprehensive service options
- **v1.2.0** - Enhanced monitoring, health checks, and documentation
