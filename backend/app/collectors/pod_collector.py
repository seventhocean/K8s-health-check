"""Pod metrics collector"""

from typing import Any, Dict, List
from app.collectors.base import BaseCollector
from app.services.k8s_client import k8s_client
import logging

logger = logging.getLogger(__name__)


class PodCollector(BaseCollector):
    """Collects pod-level metrics"""

    def __init__(self):
        super().__init__("PodCollector")

    async def collect(self) -> Dict[str, Any]:
        """Collect pod metrics"""
        pods_data = []
        pod_list = k8s_client.get_pods()

        for pod in pod_list.items:
            pod_metrics = self._parse_pod(pod)
            pods_data.append(pod_metrics)

        # Group by namespace
        by_namespace = self._group_by_namespace(pods_data)

        return {
            "pods": pods_data,
            "total": len(pods_data),
            "by_namespace": by_namespace,
        }

    def _parse_pod(self, pod) -> Dict[str, Any]:
        """Parse pod object into metrics dict"""
        status = pod.status
        spec = pod.spec
        metadata = pod.metadata

        # Container statuses
        container_statuses = []
        if status.container_statuses:
            for cs in status.container_statuses:
                container_statuses.append({
                    "name": cs.name,
                    "ready": cs.ready,
                    "restart_count": cs.restart_count,
                    "image": cs.image,
                    "started": cs.started,
                    "state": self._get_container_state(cs.state),
                    "reason": cs.state.waiting.reason if cs.state.waiting else (cs.state.terminated.reason if cs.state.terminated else None),
                })

        # Resource requests and limits
        resources = self._parse_resources(spec.containers)

        # Get pod phase and conditions
        phase = status.phase

        # Determine actual pod status (handles Terminating, CrashLoopBackOff, etc.)
        actual_status = self._get_pod_actual_status(phase, metadata.deletion_timestamp, container_statuses)

        conditions = {c.type: c.status for c in status.conditions}

        return {
            "name": metadata.name,
            "namespace": metadata.namespace,
            "labels": metadata.labels or {},
            "annotations": metadata.annotations or {},
            "phase": actual_status,  # Use actual status instead of raw phase
            "qos_class": status.qos_class,
            "priority": spec.priority or 0,
            "priority_class_name": spec.priority_class_name,
            "node_name": spec.node_name,
            "host_ip": status.host_ip,
            "pod_ip": status.pod_ip,
            "service_account": spec.service_account_name,
            "conditions": conditions,
            "containers": {
                "count": len(spec.containers),
                "ready": sum(1 for cs in container_statuses if cs.get("ready")),
                "statuses": container_statuses,
            },
            "resources": resources,
            "created_at": metadata.creation_timestamp,
            "start_time": status.start_time,
            "reason": status.reason,
            "message": status.message,
        }

    def _get_pod_actual_status(self, phase: str, deletion_timestamp, container_statuses: List[Dict]) -> str:
        """Determine actual pod status considering termination and crash loops"""
        # Check if pod is terminating
        if deletion_timestamp:
            return "Terminating"

        # Check container states for crash loops
        for cs in container_statuses:
            reason = cs.get("reason")
            state = cs.get("state")
            if reason == "CrashLoopBackOff":
                return "CrashLoopBackOff"
            if reason == "OOMKilled":
                return "OOMKilled"
            if state == "waiting" and reason in ["ContainerCreating", "ImagePullBackOff", "ErrImagePull"]:
                return reason

        return phase

    def _get_container_state(self, state) -> Dict[str, Any]:
        """Get container state as dict"""
        if state.waiting:
            return {"state": "waiting", "reason": state.waiting.reason}
        elif state.running:
            return {"state": "running", "started_at": state.running.started_at}
        elif state.terminated:
            return {
                "state": "terminated",
                "reason": state.terminated.reason,
                "exit_code": state.terminated.exit_code,
            }
        return {"state": "unknown"}

    def _parse_resources(self, containers) -> Dict[str, Any]:
        """Parse container resources"""
        total_requests = {"cpu": 0, "memory": 0}
        total_limits = {"cpu": 0, "memory": 0}

        for container in containers:
            resources = container.resources
            if resources:
                if resources.requests:
                    total_requests["cpu"] += self._parse_cpu(resources.requests.get("cpu", "0"))
                    total_requests["memory"] += self._parse_memory(resources.requests.get("memory", "0"))
                if resources.limits:
                    total_limits["cpu"] += self._parse_cpu(resources.limits.get("cpu", "0"))
                    total_limits["memory"] += self._parse_memory(resources.limits.get("memory", "0"))

        return {
            "requests": total_requests,
            "limits": total_limits,
        }

    def _group_by_namespace(self, pods: List[Dict]) -> Dict[str, Dict]:
        """Group pods by namespace"""
        result = {}
        for pod in pods:
            ns = pod["namespace"]
            if ns not in result:
                result[ns] = {"count": 0, "phases": {}}
            result[ns]["count"] += 1
            phase = pod["phase"]
            result[ns]["phases"][phase] = result[ns]["phases"].get(phase, 0) + 1
        return result

    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to millicores"""
        if cpu_str.endswith("m"):
            return float(cpu_str[:-1])
        try:
            return float(cpu_str) * 1000
        except ValueError:
            return 0

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
