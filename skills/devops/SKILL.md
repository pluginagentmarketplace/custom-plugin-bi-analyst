---
name: devops-infrastructure
description: Automate deployment, manage infrastructure, and orchestrate containers with Docker, Kubernetes, and cloud platforms. Use when working on CI/CD, containerization, infrastructure automation, or cloud deployment.
---

# DevOps & Infrastructure Skill

## Quick Start

### Docker Basics
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
# Build and run
docker build -t myapp:1.0 .
docker run -p 3000:3000 myapp:1.0
```

### Docker Compose
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://db:5432/myapp
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:1.0
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
```

### Terraform Infrastructure
```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}

resource "aws_rds_instance" "db" {
  allocated_storage = 20
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  db_name           = "myapp"
  username          = "admin"
  password          = var.db_password
}
```

## CI/CD Pipeline Example

### GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          chmod 600 deploy_key
          ssh -i deploy_key user@prod-server 'cd /app && git pull && npm run deploy'
```

## Monitoring & Observability

### Prometheus Metrics
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'nodejs-app'
    static_configs:
      - targets: ['localhost:9090']
```

### Grafana Dashboard Query
```promql
# CPU usage over time
rate(process_cpu_seconds_total[5m])

# HTTP request rate
rate(http_requests_total[1m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

### ELK Stack Logging
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "ERROR",
  "service": "api",
  "message": "Database connection failed",
  "stack": "Error: connect ECONNREFUSED",
  "userId": "user123",
  "requestId": "req-456"
}
```

## Cloud Platform Comparison

| Platform | Strengths | Services |
|----------|-----------|----------|
| **AWS** | Largest ecosystem | EC2, S3, RDS, Lambda |
| **Azure** | Enterprise integration | VMs, App Service, SQL DB |
| **Google Cloud** | Data & AI tools | Compute Engine, BigQuery |

## Security Best Practices

### Container Security
- [ ] Use minimal base images (Alpine)
- [ ] Scan for vulnerabilities (Trivy, Snyk)
- [ ] Run as non-root user
- [ ] Use secrets management (HashiCorp Vault)
- [ ] Implement RBAC in Kubernetes

### Network Security
- [ ] Use VPCs and security groups
- [ ] Enable encryption in transit (TLS)
- [ ] Implement firewalls
- [ ] Use VPN for private networks
- [ ] Enable DDoS protection

## Linux System Administration
```bash
# System monitoring
top                    # Process monitor
htop                   # Enhanced process monitor
df -h                  # Disk space
free -h                # Memory usage

# Network diagnostics
netstat -tuln          # Open ports
ss -tuln               # Socket statistics
ping -c 4 example.com  # Test connectivity

# User management
useradd -m -s /bin/bash newuser
usermod -aG sudo newuser
passwd newuser

# Package management
apt update && apt upgrade     # Debian/Ubuntu
yum update                    # RedHat/CentOS
```

## Disaster Recovery Planning

### Backup Strategy
- [ ] Regular automated backups
- [ ] Off-site backup copies
- [ ] Test restore procedures
- [ ] Document RTO (Recovery Time Objective)
- [ ] Document RPO (Recovery Point Objective)

### High Availability
```yaml
# Multi-zone deployment
zones:
  - us-east-1a
  - us-east-1b
  - us-east-1c

# Load balancing
load_balancer:
  type: application
  algorithm: round-robin
  health_check: /health
```

## Resources
- [Docker Documentation](https://docs.docker.com)
- [Kubernetes Documentation](https://kubernetes.io/docs)
- [Terraform Registry](https://registry.terraform.io)
- [AWS Best Practices](https://aws.amazon.com/architecture/best-practices/)
