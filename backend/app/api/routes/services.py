"""Service API routes"""

from fastapi import APIRouter
from typing import Any, Dict, Optional

from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
async def list_services(
    namespace: Optional[str] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """Get list of all services, optionally filtered by namespace"""
    return await metrics_service.get_services(
        namespace=namespace, force_refresh=force_refresh
    ) or {"services": [], "total": 0}


@router.get("/{namespace}/{name}")
async def get_service(namespace: str, name: str) -> Dict[str, Any]:
    """Get single service detail"""
    data = await metrics_service.get_services()
    if not data:
        return {"error": "No service data available"}
    for svc in data.get("services", []):
        if svc.get("namespace") == namespace and svc.get("name") == name:
            return svc
    return {"error": f"Service '{namespace}/{name}' not found"}
