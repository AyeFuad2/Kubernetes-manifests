# Setup Guide: Deploy Flask Application to Amazon EKS

This guide provides step-by-step instructions to deploy the Flask application to your Amazon EKS cluster.

## Prerequisites

Before starting, ensure you have:

- ✅ AWS Account with active EKS cluster
- ✅ `kubectl` installed and configured ([Install kubectl](https://kubernetes.io/docs/tasks/tools/))
- ✅ `aws` CLI installed and configured ([Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- ✅ Docker installed (for building images) ([Install Docker](https://docs.docker.com/get-docker/))
- ✅ ECR repository created for storing images
- ✅ Container image built and pushed to ECR

## Step 1: Configure kubectl Access to EKS

Update your kubeconfig to connect to your EKS cluster:

```bash
# Replace region, cluster-name, and role-arn with your values
aws eks update-kubeconfig \
  --region us-east-1 \
  --name my-eks-cluster

# Verify connection
kubectl get nodes
```

You should see your worker nodes listed.

## Step 2: Create ECR Repository (if not already created)

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name nextwork-flask-backend \
  --region us-east-1

# Get the repository URI
aws ecr describe-repositories \
  --repository-names nextwork-flask-backend \
  --query 'repositories[0].repositoryUri' \
  --output text
```

Save the repository URI for the next step.

## Step 3: Build and Push Docker Image to ECR

### Authenticate Docker with ECR

```bash
# Get authorization token and authenticate Docker
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### Build Docker Image

```bash
# Navigate to your application directory
cd /path/to/flask-app

# Build Docker image
docker build -t nextwork-flask-backend:latest .
```

### Tag and Push to ECR

```bash
# Tag the image with ECR URI
docker tag nextwork-flask-backend:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:latest
```

## Step 4: Update Deployment Manifest

Replace the placeholder in `flask-deployment.yaml`:

```bash
# Replace with your actual ECR image URI
sed -i 's|<YOUR_ECR_IMAGE_URI>|<account-id>.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:latest|g' \
  flask-deployment.yaml

# Verify the change
grep "image:" flask-deployment.yaml
```

## Step 5: Deploy to EKS

### Apply Deployment

```bash
# Create the deployment
kubectl apply -f flask-deployment.yaml

# Check deployment status
kubectl rollout status deployment/nextwork-flask-backend
```

### Apply Service

```bash
# Create the service
kubectl apply -f flask-service.yaml

# Verify service is created
kubectl get service nextwork-flask-backend
```

## Step 6: Verify Deployment

### Check Deployment Status

```bash
# Get deployment details
kubectl get deployment nextwork-flask-backend

# Get pod information
kubectl get pods -l app=nextwork-flask-backend

# View detailed pod information
kubectl describe pods -l app=nextwork-flask-backend
```

### Check Service Status

```bash
# Get service details
kubectl get service nextwork-flask-backend

# Get service endpoints
kubectl get endpoints nextwork-flask-backend
```

## Step 7: Access Your Application

### Get the NodePort

```bash
# Get service details and note the NodePort
kubectl get service nextwork-flask-backend

# Extract NodePort (usually in format 8080:xxxxx/TCP)
# The xxxxx value is your NodePort
```

### Find a Worker Node's Public IP

```bash
# Get worker node information
kubectl get nodes -o wide

# Get a specific node's external IP
kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}'
```

### Access the Application

```bash
# Using the NodePort and node IP
curl http://<node-public-ip>:<nodeport>

# Example:
# curl http://52.12.34.56:30080
```

## Step 8: View Logs

```bash
# View logs from all pods
kubectl logs -l app=nextwork-flask-backend --tail=50

# View logs from a specific pod
kubectl logs <pod-name>

# Stream logs in real-time
kubectl logs <pod-name> -f

# View logs from previous pod instance (if it crashed)
kubectl logs <pod-name> --previous
```

## Step 9: Scale the Application

```bash
# Scale to 5 replicas
kubectl scale deployment nextwork-flask-backend --replicas=5

# View updated deployment
kubectl get deployment nextwork-flask-backend

# View all pods
kubectl get pods -l app=nextwork-flask-backend
```

## Step 10: Update Application

### Deploy New Version

```bash
# Build and push new Docker image
docker build -t nextwork-flask-backend:v2 .
docker tag nextwork-flask-backend:v2 \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:v2
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:v2

# Update deployment with new image
kubectl set image deployment/nextwork-flask-backend \
  nextwork-flask-backend=<account-id>.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:v2 \
  --record

# Check rollout status
kubectl rollout status deployment/nextwork-flask-backend
```

### Rollback if Needed

```bash
# View rollout history
kubectl rollout history deployment/nextwork-flask-backend

# Rollback to previous version
kubectl rollout undo deployment/nextwork-flask-backend

# Rollback to specific revision
kubectl rollout undo deployment/nextwork-flask-backend --to-revision=1
```

## Step 11: Clean Up Resources

### Delete Service

```bash
kubectl delete service nextwork-flask-backend
```

### Delete Deployment

```bash
kubectl delete deployment nextwork-flask-backend
```

### Or Delete All at Once

```bash
kubectl delete -f flask-deployment.yaml -f flask-service.yaml
```

### Delete ECR Repository (Optional)

```bash
# Warning: This deletes all images in the repository
aws ecr delete-repository \
  --repository-name nextwork-flask-backend \
  --force \
  --region us-east-1
```

## Verification Checklist

After deployment, verify:

- [ ] kubectl is connected to EKS cluster
- [ ] Docker image is built and pushed to ECR
- [ ] Deployment manifest has correct ECR image URI
- [ ] 3 pods are running (`kubectl get pods`)
- [ ] Service is created and has NodePort assigned
- [ ] Application is accessible via NodePort
- [ ] Logs show application is running correctly
- [ ] Health checks (liveness & readiness probes) are passing

## Common Issues & Solutions

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>
```

### Image Pull Errors

Ensure:
- ECR image URI is correct
- IAM permissions allow pulling from ECR
- Docker credentials are configured

### Service Not Accessible

```bash
# Check if service has endpoints
kubectl get endpoints nextwork-flask-backend

# Verify security groups allow traffic on NodePort
```

## Next Steps

- Monitor your application with CloudWatch
- Set up auto-scaling based on metrics
- Implement CI/CD pipeline for automated deployments
- Add ingress controller for advanced routing
- Set up monitoring and alerting

---

For more help, see [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
