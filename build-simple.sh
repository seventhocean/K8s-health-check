#!/bin/bash
set -e

echo "=== K8s Health Check - Build Script (Single Platform) ==="

# Build backend image
echo "Building backend image..."
docker build -t k8s-monitor-backend:latest -t k8s-monitor-backend:$(date +%Y%m%d) ./backend

# Build frontend image
echo "Building frontend image..."
docker build -t k8s-monitor-frontend:latest -t k8s-monitor-frontend:$(date +%Y%m%d) ./frontend

# Build MySQL image (optional, for offline deployment)
echo "Building MySQL image..."
docker build -t k8s-monitor-mysql:latest -f deploy/mysql/Dockerfile .

# Build Redis image (optional, for offline deployment)
echo "Building Redis image..."
docker build -t k8s-monitor-redis:latest -f deploy/redis/Dockerfile .

echo ""
echo "=== Build Complete ==="
echo "Images created:"
echo "  - k8s-monitor-backend:latest"
echo "  - k8s-monitor-frontend:latest"
echo "  - k8s-monitor-mysql:latest (optional)"
echo "  - k8s-monitor-redis:latest (optional)"
echo ""
echo "To run locally with docker-compose:"
echo "  docker-compose up -d"
echo ""
echo "To deploy to K8s:"
echo "  kubectl apply -f deploy/k8s/manifests.yml"
