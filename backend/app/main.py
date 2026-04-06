"""FastAPI application entry point"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.database import database
from app.services.cache import cache
from app.services.metrics_service import metrics_service
from app.api.routes import health, nodes, pods, deployments, cluster, auth, users
from app.api.websocket import websocket_metrics, metrics_updater

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting up...")

    # Initialize database
    await database.connect()
    await database.create_all()

    # Initialize cache
    await cache.connect()

    # Initial metrics collection
    logger.info("Running initial metrics collection...")
    await metrics_service.collect_all()

    # Start background metrics updater
    updater_task = asyncio.create_task(metrics_updater())

    logger.info(f"{settings.APP_NAME} started on {settings.HOST}:{settings.PORT}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    updater_task.cancel()
    await cache.disconnect()
    await database.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Kubernetes cluster health check and monitoring system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api/v1 prefix
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(nodes.router, prefix="/api/v1")
app.include_router(pods.router, prefix="/api/v1")
app.include_router(deployments.router, prefix="/api/v1")
app.include_router(cluster.router, prefix="/api/v1")

# WebSocket endpoint
@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_metrics(websocket)


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
    }
