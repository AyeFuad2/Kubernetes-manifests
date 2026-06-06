# Random Joke Generator API

A production-ready Flask REST API that generates random jokes using the JokeAPI external service. This application demonstrates containerization, deployment to Kubernetes, and API integration best practices.

**Repository:** [kubernetes-manifests - joke-generator branch](https://github.com/AyeFuad2/kubernetes-manifests/tree/joke-generator)

---

## 🎭 Overview

This project demonstrates building a cloud-native microservice that:
- Integrates with external APIs (JokeAPI)
- Handles errors gracefully with proper HTTP status codes
- Runs in Docker containers
- Deploys to Kubernetes with proper health checks
- Includes comprehensive unit tests
- Follows production-ready best practices

### Key Features

✅ **REST API Endpoints** - Clean, well-documented API endpoints  
✅ **External API Integration** - Seamless JokeAPI integration  
✅ **Filtering Capabilities** - Filter jokes by category and type  
✅ **Error Handling** - Comprehensive error handling and logging  
✅ **Docker Support** - Containerized with Docker and gunicorn  
✅ **Kubernetes Ready** - Includes deployment and service manifests  
✅ **Health Checks** - Liveness and readiness probes  
✅ **Unit Tests** - 20+ comprehensive test cases  
✅ **Scalable** - Runs 3 replicas with rolling updates  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerization)
- kubectl (for Kubernetes deployment)
- AWS EKS cluster with ECR (for production deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/AyeFuad2/kubernetes-manifests.git
   cd kubernetes-manifests
   git checkout joke-generator
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Test the API**
   ```bash
   # Get a random joke
   curl http://localhost:5000/api/joke
   
   # Get a programming joke
   curl http://localhost:5000/api/joke?category=Programming
   
   # Get a two-part joke
   curl http://localhost:5000/api/joke?type=twopart
   ```

### Run Unit Tests

```bash
python -m pytest test_app.py -v

# Or with unittest
python -m unittest discover
```

---

## 📚 API Endpoints

### Health Check
```
GET /
```
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Joke Generator API",
  "version": "1.0.0"
}
```

### Get Random Joke
```
GET /api/joke
```
Fetches a random joke with optional filters.

**Query Parameters:**
- `category` (optional): General, Programming, Knock-Knock, or Any (default: Any)
- `type` (optional): single, twopart, or any (default: any)

**Example:**
```bash
curl "http://localhost:5000/api/joke?category=Programming&type=single"
```

**Response (Single):**
```json
{
  "joke": "Why do programmers prefer dark mode? Because light attracts bugs!",
  "type": "single",
  "category": "Programming",
  "fetched_at": "2026-06-06T18:50:00.123456"
}
```

**Response (Two-Part):**
```json
{
  "setup": "Why do Java developers wear glasses?",
  "delivery": "Because they don't C#",
  "joke": "Why do Java developers wear glasses? Because they don't C#",
  "type": "twopart",
  "category": "Programming",
  "fetched_at": "2026-06-06T18:50:00.123456"
}
```

### Get Completely Random Joke
```
GET /api/joke/random
```
Gets a completely random joke (any category, any type).

### Get Supported Categories
```
GET /api/joke/categories
```
Returns list of supported joke categories.

**Response:**
```json
{
  "categories": ["General", "Programming", "Knock-Knock"]
}
```

### Get Supported Types
```
GET /api/joke/types
```
Returns list of supported joke types.

**Response:**
```json
{
  "types": ["single", "twopart"]
}
```

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t joke-generator:latest .

# Run the container locally
docker run -p 5000:5000 joke-generator:latest

# Test the container
curl http://localhost:5000/api/joke
```

### Push to Amazon ECR

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create repository (if not exists)
aws ecr create-repository \
  --repository-name joke-generator \
  --region us-east-1

# Tag image for ECR
docker tag joke-generator:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/joke-generator:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/joke-generator:latest
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- EKS cluster running
- kubectl configured
- Image pushed to ECR

### Update Manifests

Replace `<YOUR_ECR_IMAGE_URI>` in `k8s-deployment.yaml`:

```bash
sed -i 's|<YOUR_ECR_IMAGE_URI>|<account-id>.dkr.ecr.us-east-1.amazonaws.com/joke-generator:latest|g' \
  k8s-deployment.yaml
```

### Deploy to EKS

```bash
# Create deployment
kubectl apply -f k8s-deployment.yaml

# Create service
kubectl apply -f k8s-service.yaml

# Check status
kubectl get deployments
kubectl get pods -l app=joke-generator
kubectl get services

# View logs
kubectl logs -l app=joke-generator -f

# Port forward for testing
kubectl port-forward svc/joke-generator 5000:5000

# Test
curl http://localhost:5000/api/joke
```

### Scale the Application

```bash
# Scale to 5 replicas
kubectl scale deployment joke-generator --replicas=5

# Check status
kubectl get deployment joke-generator
```

### Cleanup

```bash
# Delete service and deployment
kubectl delete -f k8s-service.yaml
kubectl delete -f k8s-deployment.yaml

# Or delete all at once
kubectl delete service joke-generator
kubectl delete deployment joke-generator
```

---

## 📋 Project Structure

```
joke-generator/
├── app.py                    # Flask application
├── test_app.py              # Unit tests
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── k8s-deployment.yaml     # Kubernetes Deployment manifest
├── k8s-service.yaml        # Kubernetes Service manifest
└── README-JOKE-GENERATOR.md # This file
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests with verbose output
python -m pytest test_app.py -v

# Run specific test class
python -m pytest test_app.py::JokeGeneratorTestCase -v

# Run with coverage
pip install coverage
coverage run -m pytest test_app.py
coverage report
```

### Test Coverage

The test suite includes 20+ test cases covering:
- Health check and error handling
- Category and type validation
- Response formatting
- API endpoints with various filters
- Error scenarios and edge cases
- Mock JokeAPI responses

---

## 🏗️ Application Architecture

### Code Structure

**app.py** - Main Flask application
- `JokeAPIError` - Custom exception class
- `get_supported_categories()` - Cached category list
- `validate_category()` - Category validation
- `validate_type()` - Type validation
- `fetch_joke_from_api()` - External API integration
- `format_joke_response()` - Response formatting
- Route handlers for all endpoints

### Error Handling

The application handles multiple error scenarios:
- Invalid category/type parameters (400)
- API timeout/connection errors (503)
- Internal server errors (500)
- Not found errors (404)

### Logging

Comprehensive logging for:
- API requests
- External API calls
- Errors and exceptions
- Performance tracking

---

## 📊 Performance

- **Response Time**: < 500ms average
- **Throughput**: 4 gunicorn workers
- **Memory**: 256Mi requests, 512Mi limits
- **CPU**: 250m requests, 500m limits
- **Replicas**: 3 for high availability

---

## 🔄 CI/CD Integration

### Local Testing Before Deployment

```bash
# Run tests
python -m pytest test_app.py

# Build Docker image
docker build -t joke-generator:latest .

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/joke-generator:latest

# Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml
```

---

## 🛠️ Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>

# Check events
kubectl get events
```

### Image Pull Errors

```bash
# Verify image URI is correct
kubectl describe pod <pod-name> | grep Image

# Check ECR credentials
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints joke-generator

# Port forward to test
kubectl port-forward svc/joke-generator 5000:5000

# Test from local machine
curl http://localhost:5000/api/joke
```

---

## 📚 External Resources

- **JokeAPI Documentation**: https://jokeapi.dev/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Docker Documentation**: https://docs.docker.com/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **AWS EKS Guide**: https://docs.aws.amazon.com/eks/

---

## 🎓 Learning Outcomes

By exploring this project, you'll learn:
- ✅ REST API design with Flask
- ✅ External API integration and error handling
- ✅ Docker containerization best practices
- ✅ Kubernetes deployment manifests
- ✅ Health checks and probes
- ✅ Unit testing and mocking
- ✅ Production-ready code structure
- ✅ Cloud-native application design

---

## 📝 License

This project is part of the NextWork AWS Compute series and is provided for educational purposes.

---

## 🤝 Contributing

Feel free to fork this repository, make improvements, and submit pull requests!

---

**Happy deploying! 🚀**

Built with ❤️ for cloud-native development.
