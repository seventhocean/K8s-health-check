"""Node metrics collector"""

from typing import Any, Dict, List
from app.collectors.base import BaseCollector
from app.services.k8s_client import k8s_client
import logging

logger = logging.getLogger(__name__)


class NodeCollector(BaseCollector):
    """Collects node-level metrics"""

    def __init__(self):
        super().__init__("NodeCollector")

    async def collect(self) -> Dict[str, Any]:
        """Collect node metrics"""
        nodes_data = []
        node_list = k8s_client.get_nodes()

        for node in node_list.items:
            node_metrics = self._parse_node(node)
            nodes_data.append(node_metrics)

        return {"nodes": nodes_data, "total": len(nodes_data)}

    def _parse_node(self, node) -> Dict[str, Any]:
        """Parse node object into metrics dict"""
        status = node.status
        capacity = status.capacity
        allocatable = status.allocatable

        # Calculate resource usage
        cpu_capacity = self._parse_cpu(capacity.get("cpu", "0"))
        cpu_allocatable = self._parse_cpu(allocatable.get("cpu", "0"))

        memory_capacity = self._parse_memory(capacity.get("memory", "0"))
        memory_allocatable = self._parse_memory(allocatable.get("memory", "0"))

        pod_capacity = int(capacity.get("pods", "0"))
        pod_allocatable = int(allocatable.get("pods", "0"))

        # Get conditions
        conditions = {}
        for condition in status.conditions:
            conditions[condition.type] = {
                "status": condition.status,
                "reason": condition.reason,
                "message": condition.message,
                "last_transition": condition.last_transition_time,
            }

        return {
            "name": node.metadata.name,
            "labels": node.metadata.labels or {},
            "created_at": node.metadata.creation_timestamp,
            "kubelet_version": status.node_info.kubelet_version,
            "os_image": status.node_info.os_image,
            "container_runtime": status.node_info.container_runtime_version,
            "conditions": conditions,
            "capacity": {
                "cpu": cpu_capacity,
                "memory_bytes": memory_capacity,
                "pods": pod_capacity,
            },
            "allocatable": {
                "cpu": cpu_allocatable,
                "memory_bytes": memory_allocatable,
                "pods": pod_allocatable,
            },
            "addresses": self._get_addresses(status.addresses),
            "is_ready": self._is_node_ready(conditions),
        }

    def _is_node_ready(self, conditions: Dict) -> bool:
        """Check if node is in Ready state"""
        ready_condition = conditions.get("Ready", {})
        return ready_condition.get("status") == "True"

    def _get_addresses(self, addresses: List) -> Dict[str, str]:
        """Get node addresses"""
        result = {}
        for addr in addresses:
            result[addr.type] = addr.address
        return result

    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to millicores"""
        if cpu_str.endswith("m"):
            return float(cpu_str[:-1])
        return float(cpu_str) * 1000

    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory string to bytes"""
        units = {
            "Ki": 1024,
            "Mi": 1024**2,
            "Gi": 1024**3,
            "Ti": 1024**4,
            "K": 1000,
            "M": 1000**2,
            "G": 1000**3,
            "T": 1000**4,
        }
        for unit, multiplier in units.items():
            if memory_str.endswith(unit):
                return int(float(memory_str[:-len(unit)]) * multiplier)
        try:
            return int(memory_str)
        except ValueError:
            return 0
