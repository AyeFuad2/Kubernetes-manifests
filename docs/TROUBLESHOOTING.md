# Troubleshooting Guide

Common issues and solutions for deploying Flask applications to Amazon EKS.

## Pod Issues

### Pods Stuck in Pending State

**Symptoms:** `kubectl get pods` shows `Pending` status

**Common Causes:**
- Insufficient cluster resources
- Node pool issues
- Resource constraints

**Solutions:**

```bash
# Check pod details
kubectl describe pod <pod-name>

# Check cluster resources
kubectl top nodes
kubectl top pods

# Check node status
kubectl get nodes

# If nodes are NotReady, check node logs
kubectl describe node <node-name>
```

### Pods Crashing (CrashLoopBackOff)

**Symptoms:** `kubectl get pods` shows `CrashLoopBackOff` status

**Common Causes:**
- Application errors
- Missing environment variables
- Incorrect container image
- Port conflicts

**Solutions:**

```bash
# View pod logs
kubectl logs <pod-name>

# View previous logs (if pod restarted)
kubectl logs <pod-name> --previous

# Check pod events
kubectl describe pod <pod-name>

# Verify container is listening on correct port
kubectl exec -it <pod-name> -- netstat -tuln
```

### Pods in ImagePullBackOff

**Symptoms:** `kubectl get pods` shows `ImagePullBackOff` status

**Common Causes:**
- Incorrect image URI
- Image doesn't exist in ECR
- IAM permissions issue
- Authentication failure

**Solutions:**

```bash
# Verify image URI in deployment
kubectl get deployment -o yaml | grep image:

# Check if image exists in ECR
aws ecr describe-images \
  --repository-name nextwork-flask-backend \
  --region us-east-1

# Verify ECR authentication
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Check pod events for detailed error
kubectl describe pod <pod-name> | grep -A 5 Events
```

### Pods in Init:0/1 or Waiting State

**Symptoms:** Pod shows `Init` or `Waiting` status

**Common Causes:**
- Readiness probe failing
- Init container not completing
- Dependency not available

**Solutions:**

```bash
# Check detailed pod status
kubectl describe pod <pod-name>

# Check readiness probe
kubectl get pod <pod-name> -o jsonpath='{.status.conditions[?(@.type=="Ready")]}'

# View logs
kubectl logs <pod-name> -c <container-name>
```

## Deployment Issues

### Deployment Not Rolling Out

**Symptoms:** `kubectl rollout status` shows timeout

**Solutions:**

```bash
# Check deployment status
kubectl describe deployment nextwork-flask-backend

# Check pod status
kubectl get pods -l app=nextwork-flask-backend

# Check events
kubectl get events --sort-by='.lastTimestamp' | tail -20

# Manually check pod logs for errors
kubectl logs -l app=nextwork-flask-backend --tail=50
```

### Rolling Back After Failed Deployment

```bash
# View deployment history
kubectl rollout history deployment/nextwork-flask-backend

# Rollback to previous version
kubectl rollout undo deployment/nextwork-flask-backend

# Rollback to specific revision
kubectl rollout undo deployment/nextwork-flask-backend --to-revision=2

# Verify rollback
kubectl rollout status deployment/nextwork-flask-backend
```

## Service Issues

### Service Not Accessible

**Symptoms:** Cannot reach application via NodePort

**Solutions:**

```bash
# Verify service exists and has endpoints
kubectl get service nextwork-flask-backend
kubectl get endpoints nextwork-flask-backend

# If no endpoints, check if pods are running
kubectl get pods -l app=nextwork-flask-backend

# Verify service ports
kubectl describe service nextwork-flask-backend

# Test connectivity from pod
kubectl exec -it <pod-name> -- curl localhost:8080
```

### NodePort Not Accessible from Outside

**Symptoms:** Service is accessible from cluster but not externally

**Common Causes:**
- Security group not allowing traffic
- Wrong NodePort
- Node not accessible

**Solutions:**

```bash
# Get service details
kubectl get service nextwork-flask-backend -o yaml

# Get worker node external IP
kubectl get nodes -o wide

# Verify security group allows NodePort
# In AWS Console: EC2 > Security Groups > Check inbound rules

# Check if node is accessible
ping <node-public-ip>

# Test port on node
curl http://<node-public-ip>:30080
```

### Endpoints Not Showing

**Symptoms:** `kubectl get endpoints` shows `<none>`

**Solutions:**

```bash
# Verify pods have correct labels
kubectl get pods --show-labels

# Check selector in service
kubectl get service nextwork-flask-backend -o yaml | grep -A 2 selector

# Verify labels match
# Labels on pods should match service selector

# Fix by updating deployment labels
kubectl set selector deployment nextwork-flask-backend \
  app=nextwork-flask-backend --overwrite
```

## Resource Issues

### Out of Memory (OOM) Errors

**Symptoms:** Pods killed with OOMKilled message

**Solutions:**

```bash
# Check resource usage
kubectl top pods

# Increase memory limits in deployment
# Edit flask-deployment.yaml and increase:
# resources.limits.memory

# Reapply deployment
kubectl apply -f flask-deployment.yaml

# Monitor memory usage
kubectl top pods --containers
```

### CPU Throttling

**Symptoms:** Application running slowly

**Solutions:**

```bash
# Check CPU requests/limits
kubectl describe deployment nextwork-flask-backend | grep -A 5 Limits

# Monitor CPU usage
kubectl top pods

# Increase CPU limits if needed
kubectl set resources deployment nextwork-flask-backend \
  --limits=cpu=1000m \
  --requests=cpu=500m
```

## Logging and Debugging

### View Logs

```bash
# Last 50 lines
kubectl logs <pod-name> --tail=50

# Stream logs in real-time
kubectl logs <pod-name> -f

# All pods for an app
kubectl logs -l app=nextwork-flask-backend --tail=100

# Previous pod instance logs
kubectl logs <pod-name> --previous

# Logs from specific container
kubectl logs <pod-name> -c <container-name>

# With timestamps
kubectl logs <pod-name> --timestamps=true
```

### Execute Commands in Pod

```bash
# Interactive shell
kubectl exec -it <pod-name> -- /bin/bash

# Run single command
kubectl exec <pod-name> -- curl localhost:8080

# Check environment variables
kubectl exec <pod-name> -- env

# Check file system
kubectl exec <pod-name> -- ls -la /app
```

### Inspect Pod Details

```bash
# Full YAML definition
kubectl get pod <pod-name> -o yaml

# JSON format
kubectl get pod <pod-name> -o json

# Custom columns
kubectl get pods -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.phase,\
RESTARTS:.status.containerStatuses[0].restartCount,\
NODE:.spec.nodeName
```

## Network Issues

### Pod-to-Pod Communication Issues

```bash
# Test DNS resolution
kubectl exec <pod-name> -- nslookup kubernetes.default

# Test connectivity between pods
kubectl exec <pod-name> -- ping <other-pod-ip>

# Check network policies
kubectl get networkpolicies

# View iptables rules
kubectl exec <pod-name> -- iptables -L
```

### Slow Network

```bash
# Check network bandwidth
kubectl exec <pod-name> -- iperf3 -c <other-pod-ip>

# Monitor network traffic
kubectl exec <pod-name> -- tc qdisc show

# Check MTU settings
kubectl exec <pod-name> -- ip link show
```

## ECR Integration Issues

### ECR Authentication Failures

```bash
# Re-authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Check IAM policy for EKS nodes
# Policy should include:
# ecr:GetAuthorizationToken
# ecr:BatchGetImage
# ecr:GetDownloadUrlForLayer
```

### Image Not Found in ECR

```bash
# List images in repository
aws ecr describe-images \
  --repository-name nextwork-flask-backend \
  --region us-east-1

# Check image tags
aws ecr list-images \
  --repository-name nextwork-flask-backend \
  --region us-east-1

# Push missing image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/nextwork-flask-backend:latest
```

## Performance Issues

### Slow Application Response

```bash
# Check application logs
kubectl logs <pod-name> --tail=100

# Check resource constraints
kubectl top pods <pod-name>

# Verify CPU/memory are not maxed out
kubectl describe pod <pod-name> | grep -A 10 "Limits\|Requests"

# Check for errors in logs
kubectl logs <pod-name> | grep -i error
```

### High Latency

```bash
# Test network latency between pods
kubectl exec <pod-name> -- ping <service-name>

# Check DNS resolution time
kubectl exec <pod-name> -- time nslookup nextwork-flask-backend

# Monitor network metrics
kubectl top nodes
```

## Getting Help

### Collect Diagnostic Information

```bash
# Export cluster info
kubectl cluster-info dump --output-directory=./cluster-dump

# Export pod details
kubectl describe pod <pod-name> > pod-details.txt

# Export logs
kubectl logs <pod-name> > pod-logs.txt

# Export events
kubectl get events > cluster-events.txt
```

### Useful Commands

```bash
# Check cluster health
kubectl get componentstatuses

# View all resources
kubectl get all

# Check recent events
kubectl get events --sort-by='.lastTimestamp'

# View resource quotas
kubectl describe resourcequota

# Check persistent volumes
kubectl get pv
```

### Common Commands Reference

| Issue | Command |
|-------|---------|
| Pod won't start | `kubectl describe pod <name>` |
| Check logs | `kubectl logs <pod-name>` |
| Exec into pod | `kubectl exec -it <pod-name> -- bash` |
| Scale deployment | `kubectl scale deployment <name> --replicas=5` |
| View events | `kubectl get events --sort-by='.lastTimestamp'` |
| Check resources | `kubectl top pods` |
| Rollback deployment | `kubectl rollout undo deployment/<name>` |
| Port forward | `kubectl port-forward <pod-name> 8080:8080` |

---

For more information, visit:
- [Kubernetes Troubleshooting](https://kubernetes.io/docs/tasks/debug-application-cluster/)
- [Amazon EKS Troubleshooting](https://docs.aws.amazon.com/eks/latest/userguide/troubleshooting.html)
