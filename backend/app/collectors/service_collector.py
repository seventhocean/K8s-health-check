"""Service data collector"""

from typing import Any, Dict, List
from app.collectors.base import BaseCollector
from app.services.k8s_client import k8s_client
import logging

logger = logging.getLogger(__name__)


class ServiceCollector(BaseCollector):
    """Collects service information"""

    def __init__(self):
        super().__init__("ServiceCollector")

    async def collect(self) -> Dict[str, Any]:
        """Collect service data"""
        services_data = []
        service_list = k8s_client.get_services()

        for svc in service_list.items:
            svc_data = self._parse_service(svc)
            services_data.append(svc_data)

        return {"services": services_data, "total": len(services_data)}

    def _parse_service(self, svc) -> Dict[str, Any]:
        """Parse service object into dict"""
        spec = svc.spec or {}

        # Parse ports
        ports = []
        if spec.ports:
            for p in spec.ports:
                ports.append({
                    "name": p.name or "",
                    "port": p.port,
                    "target_port": str(p.target_port) if p.target_port else "",
                    "protocol": p.protocol or "TCP",
                })

        return {
            "name": svc.metadata.name,
            "namespace": svc.metadata.namespace or "default",
            "type": spec.type or "ClusterIP",
            "cluster_ip": spec.cluster_ip or "",
            "external_ip": self._get_external_ip(spec),
            "ports": ports,
            "selector": svc.spec.selector or {},
            "created_at": svc.metadata.creation_timestamp,
            "labels": svc.metadata.labels or {},
        }

    def _get_external_ip(self, spec) -> str:
        """Get external IP from service spec"""
        external_ips = getattr(spec, 'external_i_ps', None)
        if external_ips:
            return ", ".join(external_ips)
        lb_ip = getattr(spec, 'load_balancer_ip', None)
        if lb_ip:
            return lb_ip
        return ""
