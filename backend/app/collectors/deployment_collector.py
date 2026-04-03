"""Deployment metrics collector"""

from typing import Any, Dict, List
from app.collectors.base import BaseCollector
from app.services.k8s_client import k8s_client
import logging

logger = logging.getLogger(__name__)


class DeploymentCollector(BaseCollector):
    """Collects deployment-level metrics"""

    def __init__(self):
        super().__init__("DeploymentCollector")

    async def collect(self) -> Dict[str, Any]:
        """Collect deployment metrics"""
        deployments_data = []
        deployment_list = k8s_client.get_deployments()

        for deployment in deployment_list.items:
            deployment_metrics = self._parse_deployment(deployment)
            deployments_data.append(deployment_metrics)

        # Group by namespace
        by_namespace = self._group_by_namespace(deployments_data)

        return {
            "deployments": deployments_data,
            "total": len(deployments_data),
            "by_namespace": by_namespace,
        }

    def _parse_deployment(self, deployment) -> Dict[str, Any]:
        """Parse deployment object into metrics dict"""
        spec = deployment.spec
        status = deployment.status
        metadata = deployment.metadata

        # Calculate replica status
        desired = spec.replicas or 0
        ready = status.ready_replicas or 0
        available = status.available_replicas or 0
        unavailable = status.unavailable_replicas or 0
        updated = status.updated_replicas or 0

        # Strategy info
        strategy = spec.strategy.type if spec.strategy else "RollingUpdate"
        rolling_update = None
        if spec.strategy and spec.strategy.rolling_update:
            rolling_update = {
                "max_surge": str(spec.strategy.rolling_update.max_surge),
                "max_unavailable": str(spec.strategy.rolling_update.max_unavailable),
            }

        # Conditions
        conditions = []
        if status.conditions:
            for condition in status.conditions:
                conditions.append({
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message,
                })

        return {
            "name": metadata.name,
            "namespace": metadata.namespace,
            "labels": metadata.labels or {},
            "annotations": metadata.annotations or {},
            "created_at": metadata.creation_timestamp,
            "replicas": {
                "desired": desired,
                "ready": ready,
                "available": available,
                "unavailable": unavailable,
                "updated": updated,
            },
            "strategy": {
                "type": strategy,
                "rolling_update": rolling_update,
            },
            "selector": spec.selector.match_labels if spec.selector else {},
            "template_labels": spec.template.metadata.labels if spec.template.metadata else {},
            "conditions": conditions,
            "is_ready": ready == desired,
            "is_fully_available": available == desired,
        }

    def _group_by_namespace(self, deployments: List[Dict]) -> Dict[str, Dict]:
        """Group deployments by namespace"""
        result = {}
        for dep in deployments:
            ns = dep["namespace"]
            if ns not in result:
                result[ns] = {"count": 0, "ready": 0, "not_ready": 0}
            result[ns]["count"] += 1
            if dep["is_ready"]:
                result[ns]["ready"] += 1
            else:
                result[ns]["not_ready"] += 1
        return result
