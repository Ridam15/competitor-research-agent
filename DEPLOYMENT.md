# Competitor Research Agent - Deployment Scripts

## Docker Deployment

### Quick Start
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd competitor-research-agent

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 3. Build and run
docker-compose up --build
```

### Production Deployment
```bash
# Build optimized production image
docker build -t competitor-research-agent:prod -f Dockerfile.prod .

# Run with resource limits
docker run -d \
  --name cra-production \
  --memory=1g \
  --cpus=0.5 \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -v $(pwd)/reports:/app/reports \
  competitor-research-agent:prod
```

### Docker Commands Reference
```bash
# Build image
docker build -t competitor-research-agent .

# Run interactive analysis
docker run -it --rm \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -v $(pwd)/reports:/app/reports \
  competitor-research-agent \
  python main.py "competitors to Tesla"

# Run enhanced CLI
docker run -it --rm \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -v $(pwd)/reports:/app/reports \
  competitor-research-agent \
  python src/cli/enhanced_cli.py --interactive

# System status check
docker run --rm \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  competitor-research-agent \
  python src/cli/enhanced_cli.py --status

# Run test suite
docker run --rm \
  competitor-research-agent \
  python run_tests.py quick
```

## Cloud Deployment

### AWS ECS Deployment
```bash
# 1. Build and tag for ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
docker tag competitor-research-agent:latest <account>.dkr.ecr.us-west-2.amazonaws.com/competitor-research-agent:latest
docker push <account>.dkr.ecr.us-west-2.amazonaws.com/competitor-research-agent:latest

# 2. Create ECS task definition (see aws-ecs-task-definition.json)
# 3. Deploy to ECS cluster
```

### Google Cloud Run Deployment
```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/competitor-research-agent

# 2. Deploy to Cloud Run
gcloud run deploy competitor-research-agent \
  --image gcr.io/PROJECT-ID/competitor-research-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

### Azure Container Instances
```bash
# 1. Create resource group
az group create --name cra-resources --location eastus

# 2. Deploy container
az container create \
  --resource-group cra-resources \
  --name competitor-research-agent \
  --image competitor-research-agent:latest \
  --cpu 1 \
  --memory 1 \
  --environment-variables GEMINI_API_KEY=${GEMINI_API_KEY} \
  --restart-policy Never
```

## Kubernetes Deployment

### Basic Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: competitor-research-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cra
  template:
    metadata:
      labels:
        app: cra
    spec:
      containers:
      - name: cra
        image: competitor-research-agent:latest
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: cra-secrets
              key: gemini-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: cra-service
spec:
  selector:
    app: cra
  ports:
  - port: 80
    targetPort: 8000
```

### Deploy to Kubernetes
```bash
# Create secrets
kubectl create secret generic cra-secrets \
  --from-literal=gemini-api-key=${GEMINI_API_KEY}

# Deploy application
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods
kubectl logs -f deployment/competitor-research-agent
```

## Monitoring and Logging

### Prometheus Metrics
```yaml
# Add to docker-compose.yml for monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Centralized Logging with ELK Stack
```yaml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Environment-Specific Configurations

### Development
```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up

# Enable debug mode
docker run -it --rm \
  -e LOG_LEVEL=DEBUG \
  -e ENABLE_PERFORMANCE_MONITORING=true \
  competitor-research-agent \
  python src/cli/enhanced_cli.py --verbose
```

### Staging
```bash
# Staging environment with limited resources
docker-compose -f docker-compose.staging.yml up
```

### Production
```bash
# Production with all monitoring enabled
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8000/health
```

## Scaling and Performance

### Horizontal Scaling with Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml cra-stack

# Scale service
docker service scale cra-stack_competitor-research-agent=5
```

### Load Balancing
```yaml
# nginx.conf for load balancing
upstream cra_backend {
    server cra-instance-1:8000;
    server cra-instance-2:8000;
    server cra-instance-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://cra_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### Data Backup
```bash
# Backup reports and cache
docker run --rm -v cra_reports:/backup/reports \
  -v cra_cache:/backup/cache \
  busybox tar czf /backup/cra-backup-$(date +%Y%m%d).tar.gz /backup/reports /backup/cache

# Restore from backup
docker run --rm -v cra_reports:/restore/reports \
  -v cra_cache:/restore/cache \
  -v $(pwd)/backup:/backup \
  busybox tar xzf /backup/cra-backup-YYYYMMDD.tar.gz -C /restore/
```

## Troubleshooting

### Common Deployment Issues
```bash
# Check container logs
docker logs -f competitor-research-agent

# Debug container
docker exec -it competitor-research-agent /bin/bash

# Test API connectivity
docker run --rm competitor-research-agent \
  python -c "from src.utils.config import validate_configuration; print(validate_configuration())"

# Memory usage check
docker stats competitor-research-agent

# Disk usage
docker exec competitor-research-agent df -h
```

### Performance Optimization
```bash
# Enable caching
docker run -d \
  -e ENABLE_CACHING=true \
  -e CACHE_TTL_HOURS=48 \
  -v cra_cache:/app/cache \
  competitor-research-agent

# Resource monitoring
docker run --rm \
  competitor-research-agent \
  python src/cli/enhanced_cli.py --performance
```
