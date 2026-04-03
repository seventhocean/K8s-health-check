"""Deployment API routes"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any

from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.get("")
async def list_deployments(
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
    force_refresh: bool = Query(False, description="Force refresh from K8s API"),
) -> Dict[str, Any]:
    """Get all deployments, optionally filtered by namespace"""
    data = await metrics_service.get_deployments(namespace=namespace, force_refresh=force_refresh)
    if not data:
        # Trigger collection if no data
        await metrics_service.collect_all()
        data = await metrics_service.get_deployments(namespace=namespace)
    return data or {"deployments": [], "total": 0}


@router.get("/{namespace}/{deployment_name}")
async def get_deployment(
    namespace: str,
    deployment_name: str,
) -> Dict[str, Any]:
    """Get a specific deployment by namespace and name"""
    data = await metrics_service.get_deployments(namespace=namespace)
    if not data:
        raise HTTPException(status_code=404, detail="No deployments found")

    # Find the specific deployment
    for dep in data.get("deployments", []):
        if dep.get("name") == deployment_name:
            return dep

    raise HTTPException(status_code=404, detail=f"Deployment {deployment_name} not found in namespace {namespace}")


@router.get("/{namespace}/{deployment_name}/status")
async def get_deployment_status(
    namespace: str,
    deployment_name: str,
) -> Dict[str, Any]:
    """Get status for a specific deployment"""
    data = await metrics_service.get_deployments(namespace=namespace)
    if not data:
        raise HTTPException(status_code=404, detail="No deployments found")

    # Find the specific deployment
    for dep in data.get("deployments", []):
        if dep.get("name") == deployment_name:
            return {
                "name": dep.get("name"),
                "namespace": dep.get("namespace"),
                "replicas": dep.get("replicas"),
                "is_ready": dep.get("is_ready"),
                "is_fully_available": dep.get("is_fully_available"),
                "conditions": dep.get("conditions"),
            }

    raise HTTPException(status_code=404, detail=f"Deployment {deployment_name} not found")
