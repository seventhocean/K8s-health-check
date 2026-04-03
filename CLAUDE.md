# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

K8s-health-check is a Kubernetes cluster monitoring system built with Python (FastAPI) backend and Vue 3 frontend. It monitors node-level and K8s resource-level metrics with MySQL for persistence and Redis for caching.

## Architecture

```
Frontend (Vue 3 + TypeScript) → Backend (FastAPI) → K8s API Server
                                      ↓
                              MySQL + Redis
```

**Data Flow:**
```
Collectors (Node/Pod/Deployment) → MetricsService → Redis Cache (TTL: 30s)
                                              ↓
                                          MySQL (persistent storage)
```

**Key Components:**
- `collectors/base.py::BaseCollector` - Abstract base class with `collect()` abstract method
- `services/metrics_service.py::MetricsService` - Orchestrates all collectors and caching
- `services/cache.py::cache` - Redis wrapper with TTL-based caching
- `services/database.py::database` - SQLAlchemy async database connection

**K8s Resources Monitored:**
- Nodes: capacity, allocatable, conditions, kubelet version
- Pods: phase, restart count, QoS class, node assignment
- Deployments: replica status, ready/available counts

**Frontend State Management:**
- Pinia stores in `frontend/src/stores/`
- API client in `frontend/src/api/` using axios
- Vue Router for navigation

**Directory Structure:**
- `backend/app/` - Python backend
  - `collectors/` - Data collectors (Node, Pod, Deployment)
  - `services/` - K8s client, database, cache, metrics service
  - `api/routes/` - REST API endpoints
  - `models/` - SQLAlchemy and Pydantic models
- `frontend/src/` - Vue 3 frontend
  - `api/` - API clients
  - `stores/` - Pinia state management
  - `views/` - Page components (Dashboard, Nodes, Pods, Deployments, Settings)
- `deploy/k8s/` - Kubernetes manifests (namespace, deployments, services, RBAC)
- `deploy/mysql/` - MySQL Dockerfile and init scripts
- `deploy/redis/` - Redis Dockerfile

## Commands

### Development
```bash
make install      # Install dependencies (backend + frontend)
make dev          # Run backend on port 8000
make dev-frontend # Run frontend on port 3000
docker-compose up -d  # Start full stack (MySQL + Redis + Backend + Frontend)
```

### Build & Deploy
```bash
bash build.sh     # Build Docker images (auto-detects buildx, builds linux/amd64)
make deploy       # Deploy to K8s (kubectl apply -f deploy/k8s/manifests.yml)
make undeploy     # Remove K8s resources
make clean        # Remove build artifacts and volumes
```

### Testing
```bash
make test         # Run all tests (pytest)
cd backend && python -m pytest tests/test_foo.py -v  # Run single test file
make lint         # Run linters (ruff for backend, eslint for frontend)
```

### Logs
```bash
make logs         # View all docker-compose logs
make logs-backend # View backend logs only
make logs-frontend# View frontend logs only
```

## Key Configuration

**Environment Variables** (`backend/.env`, copy from `backend/.env.example`):
- `K8S_APISERVER_URL`: K8s API server URL (default: `https://kubernetes.default.svc` for in-cluster)
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- `COLLECTOR_INTERVAL`: Metrics collection interval in seconds (default: 15)

**K8s Access:**
- In-cluster: Via ServiceAccount `k8s-monitor-sa` with ClusterRole for read-only access
- Local dev: Mount `~/.kube/config` or set `KUBECONFIG` environment variable

**Ports:**
- Backend API: 8000 (API docs at `/docs`)
- Frontend: 80 (docker-compose) or 3000 (dev mode)
- MySQL: 3306
- Redis: 6379

**API Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |
| `/api/v1/nodes` | GET | Get node list |
| `/api/v1/nodes/{name}` | GET | Get single node |
| `/api/v1/pods` | GET | Get Pod list |
| `/api/v1/deployments` | GET | Get Deployment list |
| `/api/v1/cluster/summary` | GET | Get cluster overview |
| `/ws/metrics` | WebSocket | Real-time metrics push |

## Extending

**Add new Collector:**
1. Extend `app/collectors/base.py::BaseCollector`
2. Implement `collect()` method returning `Dict[str, Any]`
3. Register in `MetricsService` (`app/services/metrics_service.py`)
4. Add corresponding data models in `app/models/metrics.py`

**Add new API:**
1. Create route file in `app/api/routes/`
2. Import and include router in `app/main.py`

**Add new frontend view:**
1. Create Vue component in `frontend/src/views/`
2. Add route in `frontend/src/router/`
3. Create Pinia store in `frontend/src/stores/` if needed

## Build Notes

- `build.sh` auto-detects buildx; falls back to standard build if unavailable
- Frontend build requires `vue-tsc ^2.0.0` for TypeScript 5.3+ compatibility
- K8s manifests use ServiceAccount with ClusterRole for read-only access to nodes, pods, deployments
- For local K8s access, mount kubeconfig: `~/.kube/config:/root/.kube/config`
