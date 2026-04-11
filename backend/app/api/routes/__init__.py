"""Routes module"""

from app.api.routes import health, nodes, pods, deployments, cluster, auth, users, namespaces, services

__all__ = [
    "health",
    "nodes",
    "pods",
    "deployments",
    "cluster",
    "auth",
    "users",
    "namespaces",
    "services",
]
