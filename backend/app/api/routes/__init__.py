"""Routes module"""

from app.api.routes import health, nodes, pods, deployments, cluster, auth, users

__all__ = [
    "health",
    "nodes",
    "pods",
    "deployments",
    "cluster",
    "auth",
    "users",
]
