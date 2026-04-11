"""Namespace API routes"""

from fastapi import APIRouter
from typing import Any, Dict, Optional

from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/namespaces", tags=["namespaces"])


@router.get("")
async def list_namespaces(
    namespace: Optional[str] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """Get list of all namespaces"""
    if namespace:
        # Filter specific namespace
        data = await metrics_service.get_namespaces(force_refresh=force_refresh)
        if not data:
            return {"namespaces": [], "total": 0}
        filtered = [
            ns for ns in data.get("namespaces", []) if ns.get("name") == namespace
        ]
        return {"namespaces": filtered, "total": len(filtered)}
    return await metrics_service.get_namespaces(force_refresh=force_refresh) or {
        "namespaces": [],
        "total": 0,
    }


@router.get("/{name}")
async def get_namespace(name: str) -> Dict[str, Any]:
    """Get single namespace detail"""
    data = await metrics_service.get_namespaces()
    if not data:
        return {"error": "No namespace data available"}
    for ns in data.get("namespaces", []):
        if ns.get("name") == name:
            return ns
    return {"error": f"Namespace '{name}' not found"}
