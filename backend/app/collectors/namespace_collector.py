"""Namespace data collector"""

from typing import Any, Dict, List
from app.collectors.base import BaseCollector
from app.services.k8s_client import k8s_client
import logging

logger = logging.getLogger(__name__)


class NamespaceCollector(BaseCollector):
    """Collects namespace information"""

    def __init__(self):
        super().__init__("NamespaceCollector")

    async def collect(self) -> Dict[str, Any]:
        """Collect namespace data"""
        namespaces_data = []
        namespace_list = k8s_client.get_namespaces()

        for ns in namespace_list.items:
            ns_data = self._parse_namespace(ns)
            namespaces_data.append(ns_data)

        return {"namespaces": namespaces_data, "total": len(namespaces_data)}

    def _parse_namespace(self, ns) -> Dict[str, Any]:
        """Parse namespace object into dict"""
        return {
            "name": ns.metadata.name,
            "status": ns.status.phase or "Unknown",
            "created_at": ns.metadata.creation_timestamp,
            "labels": ns.metadata.labels or {},
        }
