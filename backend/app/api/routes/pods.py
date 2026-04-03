"""Pod API routes"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List

from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/pods", tags=["pods"])


@router.get("")
async def list_pods(
    namespace: Optional[str] = Query(None, description="Filter by namespace"),
    force_refresh: bool = Query(False, description="Force refresh from K8s API"),
) -> Dict[str, Any]:
    """Get all pods, optionally filtered by namespace"""
    data = await metrics_service.get_pods(namespace=namespace, force_refresh=force_refresh)
    if not data:
        # Trigger collection if no data
        await metrics_service.collect_all()
        data = await metrics_service.get_pods(namespace=namespace)
    return data or {"pods": [], "total": 0}


@router.get("/{namespace}/{pod_name}")
async def get_pod(
    namespace: str,
    pod_name: str,
) -> Dict[str, Any]:
    """Get a specific pod by namespace and name"""
    data = await metrics_service.get_pods(namespace=namespace)
    if not data:
        raise HTTPException(status_code=404, detail="No pods found")

    # Find the specific pod
    for pod in data.get("pods", []):
        if pod.get("name") == pod_name:
            return pod

    raise HTTPException(status_code=404, detail=f"Pod {pod_name} not found in namespace {namespace}")


@router.get("/namespace/{namespace}/status")
async def get_namespace_pod_status(
    namespace: str,
) -> Dict[str, Any]:
    """Get pod status summary for a namespace"""
    data = await metrics_service.get_pods(namespace=namespace)
    if not data:
        return {"namespace": namespace, "total": 0, "by_phase": {}}

    # Calculate status summary
    by_phase = {}
    for pod in data.get("pods", []):
        phase = pod.get("phase", "Unknown")
        by_phase[phase] = by_phase.get(phase, 0) + 1

    return {
        "namespace": namespace,
        "total": data.get("total", 0),
        "by_phase": by_phase,
    }
