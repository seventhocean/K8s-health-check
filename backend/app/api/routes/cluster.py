"""Cluster API routes"""

from fastapi import APIRouter
from typing import Dict, Any

from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/cluster", tags=["cluster"])


@router.get("/summary")
async def get_cluster_summary() -> Dict[str, Any]:
    """Get cluster-wide summary"""
    summary = await metrics_service.get_cluster_summary()
    if not summary:
        # Trigger collection if no data
        await metrics_service.collect_all()
        summary = await metrics_service.get_cluster_summary()
    return summary or {"message": "No data available"}


@router.get("/namespaces")
async def list_namespaces() -> Dict[str, Any]:
    """Get list of all namespaces with resource counts"""
    pods_data = await metrics_service.get_pods()
    deployments_data = await metrics_service.get_deployments()

    namespaces = {}

    # Aggregate pod counts by namespace
    for pod in pods_data.get("pods", []) if pods_data else []:
        ns = pod.get("namespace", "default")
        if ns not in namespaces:
            namespaces[ns] = {"pods": 0, "deployments": 0}
        namespaces[ns]["pods"] += 1

    # Aggregate deployment counts by namespace
    for dep in deployments_data.get("deployments", []) if deployments_data else []:
        ns = dep.get("namespace", "default")
        if ns not in namespaces:
            namespaces[ns] = {"pods": 0, "deployments": 0}
        namespaces[ns]["deployments"] += 1

    return {
        "namespaces": list(namespaces.keys()),
        "total": len(namespaces),
        "details": namespaces,
    }
