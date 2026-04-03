#!/bin/bash
set -e

echo "=== K8s Health Check - Build Script ==="

# 检查是否安装了 buildx
if docker buildx version &> /dev/null; then
    USE_BUILDX=true
    echo "使用 docker buildx 构建多平台镜像"

    # 创建或使用现有 builder
    docker buildx create --use --name k8s-builder 2>/dev/null || docker buildx use k8s-builder
    docker buildx inspect --bootstrap > /dev/null 2>&1

    BUILD_CMD="docker buildx build --platform linux/amd64,linux/arm64 --load"
else
    USE_BUILDX=false
    echo "未检测到 buildx，使用传统 build 构建当前平台镜像"
    echo "如需多平台支持，请安装 buildx: https://docs.docker.com/go/buildx/"
    echo ""

    BUILD_CMD="docker build"
fi

# Build backend image
echo "Building backend image..."
$BUILD_CMD -t k8s-monitor-backend:latest -t k8s-monitor-backend:$(date +%Y%m%d) ./backend

# Build frontend image
echo "Building frontend image..."
$BUILD_CMD -t k8s-monitor-frontend:latest -t k8s-monitor-frontend:$(date +%Y%m%d) ./frontend

# Build MySQL image (optional, for offline deployment)
echo "Building MySQL image..."
$BUILD_CMD -t k8s-monitor-mysql:latest -f deploy/mysql/Dockerfile .

# Build Redis image (optional, for offline deployment)
echo "Building Redis image..."
$BUILD_CMD -t k8s-monitor-redis:latest -f deploy/redis/Dockerfile .

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
