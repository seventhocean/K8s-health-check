"""Node API routes"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any

from app.services.metrics_service import metrics_service
from app.services.cache import cache

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("")
async def list_nodes(
    force_refresh: bool = Query(False, description="Force refresh from K8s API"),
) -> Dict[str, Any]:
    """Get all nodes"""
    data = await metrics_service.get_nodes(force_refresh=force_refresh)
    if not data:
        # Trigger collection if no data
        await metrics_service.collect_all()
        data = await metrics_service.get_nodes()
    return data or {"nodes": [], "total": 0}


@router.get("/{node_name}")
async def get_node(
    node_name: str,
    force_refresh: bool = Query(False, description="Force refresh from K8s API"),
) -> Dict[str, Any]:
    """Get a specific node by name"""
    data = await metrics_service.get_node(node_name, force_refresh=force_refresh)
    if not data:
        raise HTTPException(status_code=404, detail=f"Node {node_name} not found")
    return data


@router.get("/{node_name}/metrics")
async def get_node_metrics(
    node_name: str,
) -> Dict[str, Any]:
    """Get metrics for a specific node"""
    data = await metrics_service.get_node(node_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Node {node_name} not found")

    # Extract key metrics
    return {
        "name": data.get("name"),
        "is_ready": data.get("is_ready"),
        "capacity": data.get("capacity"),
        "allocatable": data.get("allocatable"),
        "conditions": data.get("conditions"),
        "kubelet_version": data.get("kubelet_version"),
        "os_image": data.get("os_image"),
    }
