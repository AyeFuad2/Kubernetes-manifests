<img src="https://cdn.prod.website-files.com/677c400686e724409a5a7409/6790ad949cf622dc8dcd9fe4_nextwork-logo-leather.svg" alt="NextWork" width="300" />

# Kubernetes Manifests: Deploy Flask Application to Amazon EKS

**Project:** AWS Compute - EKS3  
**Author:** Fuad Aye  
**Email:** fuadaye@gmail.com  
**Repository:** [kubernetes-manifests](https://github.com/AyeFuad2/kubernetes-manifests)

---

## 📋 Overview

This project demonstrates how to deploy a containerized Flask backend application to Amazon EKS (Elastic Kubernetes Service) using Kubernetes manifests. You'll learn to create and configure Deployment and Service manifests that automate application deployment, scaling, and networking within a Kubernetes cluster.

### What You'll Learn

- **Docker Containerization** - Package applications into container images
- **Amazon ECR** - Store and manage container images securely
- **Amazon EKS** - Deploy containers on a managed Kubernetes cluster
- **Kubernetes Deployments** - Define how applications run and scale
- **Kubernetes Services** - Expose applications and manage networking

### Real-World Workflow

```
Code → Docker Image → ECR Repository → Kubernetes Deployment → Kubernetes Service → EKS Cluster
```

---

## 🚀 Quick Start

### Prerequisites

- AWS Account with EKS cluster running
- `kubectl` configured to access your EKS cluster
- Docker installed (for building images)
- AWS CLI configured
- Container image pushed to Amazon ECR

### Deployment Steps

1. **Update the image URI** in `flask-deployment.yaml`:
   ```bash
   sed -i 's|<YOUR_ECR_IMAGE_URI>|<your-actual-ecr-uri>|g' flask-deployment.yaml
   ```

2. **Apply the Deployment manifest**:
   ```bash
   kubectl apply -f flask-deployment.yaml
   ```

3. **Apply the Service manifest**:
   ```bash
   kubectl apply -f flask-service.yaml
   ```

4. **Verify deployment**:
   ```bash
   kubectl get deployments
   kubectl get pods
   kubectl get services
   ```

5. **Access your application**:
   ```bash
   kubectl get svc nextwork-flask-backend
   # Note the NodePort (usually 3xxxx) and use: http://<node-ip>:<nodeport>
   ```

---

## 📁 Project Structure

```
kubernetes-manifests/
├── README.md                    # This file
├── flask-deployment.yaml        # Kubernetes Deployment manifest
├── flask-service.yaml           # Kubernetes Service manifest
└── docs/
    ├── SETUP_GUIDE.md          # Detailed setup instructions
    └── TROUBLESHOOTING.md      # Common issues and solutions
```

---

## 📖 Manifest Files Explained

### Deployment Manifest (`flask-deployment.yaml`)

A **Kubernetes Deployment** defines how your application runs and scales within the cluster.

**Key components:**
- **replicas: 3** - Maintains 3 identical pod instances
- **image** - Container image URI from Amazon ECR
- **containerPort: 8080** - Port your Flask app listens on
- **Automatic scaling** - If a pod crashes, Kubernetes replaces it automatically
- **Rolling updates** - Deploy new versions with zero downtime

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nextwork-flask-backend
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nextwork-flask-backend
  template:
    metadata:
      labels:
        app: nextwork-flask-backend
    spec:
      containers:
        - name: nextwork-flask-backend
          image: <YOUR_ECR_IMAGE_URI>
          ports:
            - containerPort: 8080
```

### Service Manifest (`flask-service.yaml`)

A **Kubernetes Service** provides a stable network endpoint for accessing your pods.

**Key components:**
- **type: NodePort** - Exposes the service outside the cluster
- **port: 8080** - External port for accessing the service
- **targetPort: 8080** - Internal port where pods listen
- **selector** - Routes traffic to pods with matching labels
- **Stable endpoint** - Pod IP changes are handled automatically

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nextwork-flask-backend
spec:
  selector:
    app: nextwork-flask-backend
  type: NodePort
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
```

---

## 🔧 Configuration Guide

### Update Container Image

Replace `<YOUR_ECR_IMAGE_URI>` with your actual ECR image URI:

```bash
# Example ECR URI format:
# 123456789012.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:latest

kubectl set image deployment/nextwork-flask-backend \
  nextwork-flask-backend=<YOUR_ECR_IMAGE_URI> \
  --record
```

### Scale Application

Increase or decrease replicas:

```bash
# Scale to 5 replicas
kubectl scale deployment nextwork-flask-backend --replicas=5

# Check status
kubectl get deployment nextwork-flask-backend
```

### View Logs

Monitor application logs:

```bash
# View logs from all pods
kubectl logs -l app=nextwork-flask-backend --tail=100

# Stream logs from a specific pod
kubectl logs <pod-name> -f
```

### Delete Resources

Clean up when done:

```bash
# Delete service
kubectl delete service nextwork-flask-backend

# Delete deployment
kubectl delete deployment nextwork-flask-backend

# Delete all resources in one command
kubectl delete -f flask-deployment.yaml -f flask-service.yaml
```

---

## 📊 Common kubectl Commands

| Command | Purpose |
|---------|---------|
| `kubectl get deployments` | List all deployments |
| `kubectl get pods` | List all pods |
| `kubectl get services` | List all services |
| `kubectl describe deployment nextwork-flask-backend` | View deployment details |
| `kubectl rollout status deployment/nextwork-flask-backend` | Check deployment progress |
| `kubectl rollout history deployment/nextwork-flask-backend` | View deployment history |
| `kubectl rollout undo deployment/nextwork-flask-backend` | Rollback to previous version |

---

## 🎯 Project Highlights

### What Makes This Project Important

1. **Cloud-Native Development** - Learn modern application deployment patterns
2. **Infrastructure as Code** - Define infrastructure using version-controlled YAML files
3. **Scalability** - Automatic pod scaling and management
4. **Reliability** - Self-healing deployments with automatic restart
5. **Real-World Practice** - Experience used in production environments

### Time to Complete

Approximately **1–2 hours**, including:
- Setting up Amazon EKS cluster
- Building and pushing Docker image to ECR
- Creating and configuring manifests
- Deploying and testing the application

---

## 🐛 Troubleshooting

### Pods Not Running

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events

# View pod logs
kubectl logs <pod-name>
```

### Service Not Accessible

```bash
# Verify service exists
kubectl get service nextwork-flask-backend

# Check endpoints
kubectl get endpoints nextwork-flask-backend

# Test connectivity
kubectl exec -it <pod-name> -- curl localhost:8080
```

### Image Pull Errors

```bash
# Verify image URI is correct
kubectl describe pod <pod-name> | grep -i image

# Check ECR access
aws ecr describe-repositories --repository-names nextwork-flask-backend
```

For more troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📚 AWS & Kubernetes Resources

- [Amazon EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Amazon ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [Kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

## 📝 License

This project is part of the NextWork AWS Compute series and is provided for educational purposes.

---

## ✨ Project Workflow Summary

This project successfully demonstrates the complete cloud-native deployment workflow:

1. ✅ Containerize Flask application with Docker
2. ✅ Store image in Amazon ECR
3. ✅ Define Deployment manifest with 3 replicas
4. ✅ Create Service manifest for external access
5. ✅ Deploy to Amazon EKS cluster
6. ✅ Verify and test application

By understanding these components and how they work together, you're now equipped to deploy and manage containerized applications in production Kubernetes environments!

---

**Happy Kubernetes deploying! 🚀**
