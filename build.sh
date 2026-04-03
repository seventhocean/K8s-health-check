#!/bin/bash
set -e

echo "=== K8s Health Check - Build Script ==="

# 检查是否安装了 buildx
if ! docker buildx version &> /dev/null; then
    echo "Installing docker buildx..."
    docker run --rm --privileged tonistiigi/binfmt --install all
fi

# 创建或使用现有 builder
docker buildx create --use --name k8s-builder 2>/dev/null || docker buildx use k8s-builder
docker buildx inspect --bootstrap > /dev/null 2>&1

# Build backend image
echo "Building backend image..."
docker buildx build --platform linux/amd64,linux/arm64 \
    -t k8s-monitor-backend:latest \
    -t k8s-monitor-backend:$(date +%Y%m%d) \
    -f backend/Dockerfile \
    --load \
    ./backend

# Build frontend image
echo "Building frontend image..."
docker buildx build --platform linux/amd64,linux/arm64 \
    -t k8s-monitor-frontend:latest \
    -t k8s-monitor-frontend:$(date +%Y%m%d) \
    -f frontend/Dockerfile \
    --load \
    ./frontend

# Build MySQL image (optional, for offline deployment)
echo "Building MySQL image..."
docker buildx build --platform linux/amd64,linux/arm64 \
    -t k8s-monitor-mysql:latest \
    -f deploy/mysql/Dockerfile \
    --load \
    .

# Build Redis image (optional, for offline deployment)
echo "Building Redis image..."
docker buildx build --platform linux/amd64,linux/arm64 \
    -t k8s-monitor-redis:latest \
    -f deploy/redis/Dockerfile \
    --load \
    .

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
echo ""
echo "To push images to registry for offline deployment:"
echo "  docker tag k8s-monitor-backend:latest <registry>/k8s-monitor-backend:latest"
echo "  docker tag k8s-monitor-frontend:latest <registry>/k8s-monitor-frontend:latest"
echo "  docker tag k8s-monitor-mysql:latest <registry>/k8s-monitor-mysql:latest"
echo "  docker tag k8s-monitor-redis:latest <registry>/k8s-monitor-redis:latest"
echo "  docker push <registry>/k8s-monitor-backend:latest"
echo "  docker push <registry>/k8s-monitor-frontend:latest"
echo "  docker push <registry>/k8s-monitor-mysql:latest"
echo "  docker push <registry>/k8s-monitor-redis:latest"
