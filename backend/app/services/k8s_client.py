"""Kubernetes client wrapper"""

import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class K8sClient:
    """Kubernetes API client wrapper"""

    _instance: Optional["K8sClient"] = None
    _initialized: bool = False

    def __new__(cls) -> "K8sClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._init_client()
            self._initialized = True

    def _init_client(self) -> None:
        """Initialize Kubernetes client"""
        self._ready = False
        try:
            # Try in-cluster config first
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
            self._ready = True
        except config.ConfigException:
            # Fall back to kubeconfig
            try:
                config.load_kube_config()
                logger.info("Loaded kubeconfig")
                self._ready = True
            except config.ConfigException as e:
                logger.error(f"Failed to load Kubernetes config: {e}")
                logger.warning("K8s client not initialized - running without K8s access")
                self.core_v1 = None
                self.apps_v1 = None
                self.batch_v1 = None
                self.custom_metrics = None
                return

        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
        self.custom_metrics = None  # Can be initialized if metrics-server is available
        logger.info("K8s client initialized successfully")

    def get_nodes(self):
        """Get all nodes"""
        try:
            return self.core_v1.list_node()
        except ApiException as e:
            logger.error(f"Failed to list nodes: {e}")
            raise

    def get_node(self, name: str):
        """Get node by name"""
        try:
            return self.core_v1.read_node(name)
        except ApiException as e:
            logger.error(f"Failed to get node {name}: {e}")
            raise

    def get_pods(self, namespace: Optional[str] = None):
        """Get pods, optionally filtered by namespace"""
        try:
            if namespace:
                return self.core_v1.list_namespaced_pod(namespace)
            return self.core_v1.list_pod_for_all_namespaces()
        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            raise

    def get_deployments(self, namespace: Optional[str] = None):
        """Get deployments, optionally filtered by namespace"""
        try:
            if namespace:
                return self.apps_v1.list_namespaced_deployment(namespace)
            return self.apps_v1.list_deployment_for_all_namespaces()
        except ApiException as e:
            logger.error(f"Failed to list deployments: {e}")
            raise

    def get_namespaces(self):
        """Get all namespaces"""
        try:
            return self.core_v1.list_namespace()
        except ApiException as e:
            logger.error(f"Failed to list namespaces: {e}")
            raise

    def get_services(self, namespace: Optional[str] = None):
        """Get services, optionally filtered by namespace"""
        try:
            if namespace:
                return self.core_v1.list_namespaced_service(namespace)
            return self.core_v1.list_service_for_all_namespaces()
        except ApiException as e:
            logger.error(f"Failed to list services: {e}")
            raise

    def get_events(self, namespace: str, limit: int = 100):
        """Get recent events in a namespace"""
        try:
            return self.core_v1.list_namespaced_event(
                namespace, limit=limit
            )
        except ApiException as e:
            logger.error(f"Failed to list events in {namespace}: {e}")
            raise


# Global instance
k8s_client = K8sClient()
