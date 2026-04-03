#!/bin/bash
set -e

echo "=== K8s Health Check - Build Script ==="

# Build backend image
echo "Building backend image..."
docker build -t k8s-monitor-backend:latest ./backend

# Build frontend image
echo "Building frontend image..."
docker build -t k8s-monitor-frontend:latest ./frontend

echo ""
echo "=== Build Complete ==="
echo "Images created:"
echo "  - k8s-monitor-backend:latest"
echo "  - k8s-monitor-frontend:latest"
echo ""
echo "To run locally with docker-compose:"
echo "  docker-compose up -d"
echo ""
echo "To deploy to K8s:"
echo "  kubectl apply -f deploy/k8s/manifests.yml"
