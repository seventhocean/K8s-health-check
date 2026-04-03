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

**Directory Structure:**
- `backend/app/` - Python backend
  - `collectors/` - Data collectors (Node, Pod, Deployment)
  - `services/` - K8s client, database, cache, metrics service
  - `api/routes/` - REST API endpoints
- `frontend/src/` - Vue 3 frontend
  - `api/` - API clients
  - `stores/` - Pinia state management
  - `views/` - Page components

## Commands

### Development
```bash
make install      # Install dependencies
make dev          # Run backend (port 8000)
make dev-frontend # Run frontend (port 3000)
docker-compose up -d  # Start full stack
```

### Build & Deploy
```bash
make build    # Build Docker images
make deploy   # Deploy to K8s (kubectl apply)
```

### Testing
```bash
make test   # Run tests
make lint   # Run linters
```

## Key Configuration

- **Environment**: `backend/.env` (copy from `.env.example`)
- **K8s Access**: In-cluster via ServiceAccount or local kubeconfig
- **Database**: MySQL on port 3306, Redis on port 6379
- **Collector Interval**: Default 15 seconds (configurable via `COLLECTOR_INTERVAL`)

## Extending

**Add new Collector:**
1. Extend `app/collectors/base.py::BaseCollector`
2. Implement `collect()` method
3. Register in `services/metrics_service.py`

**Add new API:**
1. Create route file in `app/api/routes/`
2. Import and include in `app/main.py`
