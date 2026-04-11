"""Metrics service - orchestrates collection and storage"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.collectors.node_collector import NodeCollector
from app.collectors.pod_collector import PodCollector
from app.collectors.deployment_collector import DeploymentCollector
from app.collectors.namespace_collector import NamespaceCollector
from app.collectors.service_collector import ServiceCollector
from app.services.cache import cache
from app.services.database import database
from app.models.metrics import (
    NodeMetrics,
    PodMetrics,
    DeploymentMetrics,
    ClusterSummary,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

logger = logging.getLogger(__name__)


class MetricsService:
    """Service for collecting and storing metrics"""

    def __init__(self):
        self.node_collector = NodeCollector()
        self.pod_collector = PodCollector()
        self.deployment_collector = DeploymentCollector()
        self.namespace_collector = NamespaceCollector()
        self.service_collector = ServiceCollector()

    async def collect_all(self) -> Dict[str, Any]:
        """Collect all metrics and store in cache"""
        results = {}

        # Collect node metrics
        node_data = await self.node_collector.run()
        results["nodes"] = node_data
        await cache.set(cache.nodes_key(), node_data)

        # Cache individual nodes
        for node in node_data.get("nodes", []):
            await cache.set(cache.node_key(node["name"]), node)

        # Collect pod metrics
        pod_data = await self.pod_collector.run()
        results["pods"] = pod_data
        await cache.set(cache.pods_key(), pod_data)

        # Collect deployment metrics
        deployment_data = await self.deployment_collector.run()
        results["deployments"] = deployment_data
        await cache.set(cache.deployments_key(), deployment_data)

        # Collect namespace metrics
        namespace_data = await self.namespace_collector.run()
        results["namespaces"] = namespace_data
        await cache.set(cache.namespaces_key(), namespace_data)

        # Collect service metrics
        service_data = await self.service_collector.run()
        results["services"] = service_data
        await cache.set(cache.services_key(), service_data)

        # Create and cache cluster summary
        summary = self._create_summary(results)
        results["summary"] = summary
        await cache.set(cache.cluster_summary_key(), summary)

        logger.debug("All metrics collected and cached")
        return results

    async def get_cluster_summary(self) -> Optional[Dict[str, Any]]:
        """Get cluster summary from cache"""
        return await cache.get(cache.cluster_summary_key())

    async def get_nodes(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Get node metrics"""
        if force_refresh:
            await cache.delete(cache.nodes_key())
        return await cache.get(cache.nodes_key())

    async def get_node(self, name: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Get single node metrics"""
        if force_refresh:
            await cache.delete(cache.node_key(name))
            # Trigger collection
            await self.collect_all()
        return await cache.get(cache.node_key(name))

    async def get_pods(
        self, namespace: Optional[str] = None, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get pod metrics"""
        if force_refresh:
            await cache.delete(cache.pods_key(namespace))
            await self.collect_all()
        data = await cache.get(cache.pods_key())
        if not data:
            return None
        if namespace:
            # Filter by namespace
            filtered = [
                p for p in data.get("pods", []) if p.get("namespace") == namespace
            ]
            return {"pods": filtered, "total": len(filtered)}
        return data

    async def get_deployments(
        self, namespace: Optional[str] = None, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get deployment metrics"""
        if force_refresh:
            await cache.delete(cache.deployments_key(namespace))
            await self.collect_all()
        data = await cache.get(cache.deployments_key())
        if not data:
            return None
        if namespace:
            # Filter by namespace
            filtered = [
                d for d in data.get("deployments", []) if d.get("namespace") == namespace
            ]
            return {"deployments": filtered, "total": len(filtered)}
        return data

    async def get_namespaces(
        self, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get namespace data"""
        if force_refresh:
            await cache.delete(cache.namespaces_key())
            await self.collect_all()
        return await cache.get(cache.namespaces_key())

    async def get_services(
        self, namespace: Optional[str] = None, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get service data"""
        if force_refresh:
            await cache.delete(cache.services_key())
            await self.collect_all()
        data = await cache.get(cache.services_key())
        if not data:
            return None
        if namespace:
            filtered = [
                s for s in data.get("services", []) if s.get("namespace") == namespace
            ]
            return {"services": filtered, "total": len(filtered)}
        return data

    def _create_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create cluster summary from collected metrics"""
        nodes = metrics.get("nodes", {})
        pods = metrics.get("pods", {})
        deployments = metrics.get("deployments", {})

        # Node summary
        node_list = nodes.get("nodes", [])
        ready_nodes = sum(1 for n in node_list if n.get("is_ready"))

        # Pod summary
        pod_list = pods.get("pods", [])
        pod_phases = {}
        for pod in pod_list:
            phase = pod.get("phase", "Unknown")
            pod_phases[phase] = pod_phases.get(phase, 0) + 1

        # Deployment summary
        deployment_list = deployments.get("deployments", [])
        ready_deployments = sum(1 for d in deployment_list if d.get("is_ready"))

        # Resource totals - Capacity and Allocatable
        total_cpu_capacity = sum(n.get("capacity", {}).get("cpu", 0) for n in node_list)
        total_cpu_allocatable = sum(n.get("allocatable", {}).get("cpu", 0) for n in node_list)
        total_memory_capacity = sum(n.get("capacity", {}).get("memory_bytes", 0) for n in node_list)
        total_memory_allocatable = sum(n.get("allocatable", {}).get("memory_bytes", 0) for n in node_list)

        # Calculate total requested resources from all pods
        total_cpu_requested = 0
        total_memory_requested = 0
        for pod in pod_list:
            resources = pod.get("resources", {})
            requests = resources.get("requests", {})
            total_cpu_requested += requests.get("cpu", 0)
            total_memory_requested += requests.get("memory", 0)

        # Available = Allocatable - Requested
        total_cpu_available = max(0, total_cpu_allocatable - total_cpu_requested)
        total_memory_available = max(0, total_memory_allocatable - total_memory_requested)

        return {
            "collected_at": datetime.utcnow().isoformat(),
            "nodes": {
                "total": nodes.get("total", 0),
                "ready": ready_nodes,
                "not_ready": nodes.get("total", 0) - ready_nodes,
            },
            "pods": {
                "total": pods.get("total", 0),
                "by_phase": pod_phases,
            },
            "deployments": {
                "total": deployments.get("total", 0),
                "ready": ready_deployments,
                "not_ready": deployments.get("total", 0) - ready_deployments,
            },
            "resources": {
                "total_cpu_capacity_millicores": total_cpu_capacity,
                "total_cpu_allocatable_millicores": total_cpu_allocatable,
                "total_cpu_requested_millicores": total_cpu_requested,
                "total_cpu_available_millicores": total_cpu_available,
                "total_memory_capacity_bytes": total_memory_capacity,
                "total_memory_allocatable_bytes": total_memory_allocatable,
                "total_memory_requested_bytes": total_memory_requested,
                "total_memory_available_bytes": total_memory_available,
            },
        }


# Global instance
metrics_service = MetricsService()
