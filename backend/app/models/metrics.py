"""Database models"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class NodeMetrics(Base):
    """Node metrics storage"""
    __tablename__ = "node_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_name = Column(String(255), nullable=False, index=True)
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Capacity
    cpu_capacity = Column(Float)
    cpu_allocatable = Column(Float)
    memory_capacity = Column(Float)
    memory_allocatable = Column(Float)
    pod_capacity = Column(Integer)
    pod_allocatable = Column(Integer)

    # Status
    is_ready = Column(Integer)
    kubelet_version = Column(String(255))
    os_image = Column(String(255))
    container_runtime = Column(String(255))

    # Addresses
    internal_ip = Column(String(64))
    external_ip = Column(String(64))

    # Raw data
    conditions = Column(JSON)
    labels = Column(JSON)

    __table_args__ = (
        Index("idx_node_time", "node_name", "collected_at"),
    )


class PodMetrics(Base):
    """Pod metrics storage"""
    __tablename__ = "pod_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pod_name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False, index=True)
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Status
    phase = Column(String(64))
    qos_class = Column(String(64))
    node_name = Column(String(255))
    host_ip = Column(String(64))
    pod_ip = Column(String(64))
    service_account = Column(String(255))

    # Container info
    container_count = Column(Integer)
    container_ready_count = Column(Integer)

    # Resources
    cpu_request = Column(Float)
    cpu_limit = Column(Float)
    memory_request = Column(Float)
    memory_limit = Column(Float)

    # Metadata
    labels = Column(JSON)
    container_statuses = Column(JSON)

    __table_args__ = (
        Index("idx_pod_namespace_time", "namespace", "pod_name", "collected_at"),
    )


class DeploymentMetrics(Base):
    """Deployment metrics storage"""
    __tablename__ = "deployment_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False, index=True)
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Replica status
    desired_replicas = Column(Integer)
    ready_replicas = Column(Integer)
    available_replicas = Column(Integer)
    unavailable_replicas = Column(Integer)
    updated_replicas = Column(Integer)

    # Strategy
    strategy_type = Column(String(64))

    # Status flags
    is_ready = Column(Integer)
    is_fully_available = Column(Integer)

    # Metadata
    labels = Column(JSON)
    selector = Column(JSON)
    conditions = Column(JSON)

    __table_args__ = (
        Index("idx_deployment_namespace_time", "namespace", "deployment_name", "collected_at"),
    )


class ClusterSummary(Base):
    """Cluster summary snapshots"""
    __tablename__ = "cluster_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Node stats
    total_nodes = Column(Integer)
    ready_nodes = Column(Integer)
    not_ready_nodes = Column(Integer)

    # Pod stats
    total_pods = Column(Integer)
    running_pods = Column(Integer)
    pending_pods = Column(Integer)
    failed_pods = Column(Integer)

    # Deployment stats
    total_deployments = Column(Integer)
    ready_deployments = Column(Integer)

    # Resource totals
    total_cpu_capacity = Column(Float)
    total_cpu_allocatable = Column(Float)
    total_memory_capacity = Column(Float)
    total_memory_allocatable = Column(Float)

    # Summary snapshot
    summary_data = Column(JSON)
