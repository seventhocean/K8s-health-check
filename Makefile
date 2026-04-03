.PHONY: help dev build deploy clean install lint test

# Default target
help:
	@echo "K8s Health Check - Makefile Commands"
	@echo ""
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run backend in development mode"
	@echo "  build       - Build Docker images"
	@echo "  up          - Start docker-compose"
	@echo "  down        - Stop docker-compose"
	@echo "  deploy      - Deploy to K8s cluster"
	@echo "  clean       - Remove build artifacts"
	@echo "  lint        - Run linters"
	@echo "  test        - Run tests"

# Install dependencies
install:
	cd backend && uv pip install -e .
	cd frontend && npm install

# Run backend in development mode
dev:
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend in development mode
dev-frontend:
	cd frontend && npm run dev

# Build Docker images
build:
	docker build -t k8s-monitor-backend:latest ./backend
	docker build -t k8s-monitor-frontend:latest ./frontend

# Start docker-compose
up:
	docker-compose up -d

# Stop docker-compose
down:
	docker-compose down

# Deploy to K8s
deploy:
	kubectl apply -f deploy/k8s/manifests.yml

# Delete K8s resources
undeploy:
	kubectl delete -f deploy/k8s/manifests.yml

# Clean build artifacts
clean:
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/*.egg-info
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	docker-compose down -v

# Run linters
lint:
	cd backend && python -m ruff check app/
	cd frontend && npm run lint

# Run tests
test:
	cd backend && python -m pytest

# View logs
logs:
	docker-compose logs -f

# View backend logs
logs-backend:
	docker-compose logs -f backend

# View frontend logs
logs-frontend:
	docker-compose logs -f frontend
