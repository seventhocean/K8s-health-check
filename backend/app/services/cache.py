"""Redis cache client"""

import redis.asyncio as redis
from typing import Any, Optional
import json
import logging
from datetime import timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class CacheClient:
    """Redis cache client wrapper"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        try:
            await self.client.ping()
            logger.info("Redis connected")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.client:
            await self.client.close()
        logger.info("Redis disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed for {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache"""
        try:
            serialized = json.dumps(value)
            ttl = ttl or settings.REDIS_CACHE_TTL
            return await self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Cache set failed for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return await self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Cache delete failed for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists check failed for {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Clear all keys matching pattern"""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys) > 0
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern failed for {pattern}: {e}")
            return False

    # Cache keys helpers
    @staticmethod
    def node_key(node_name: str) -> str:
        return f"node:{node_name}"

    @staticmethod
    def nodes_key() -> str:
        return "nodes:all"

    @staticmethod
    def pods_key(namespace: Optional[str] = None) -> str:
        if namespace:
            return f"pods:{namespace}"
        return "pods:all"

    @staticmethod
    def deployments_key(namespace: Optional[str] = None) -> str:
        if namespace:
            return f"deployments:{namespace}"
        return "deployments:all"

    @staticmethod
    def cluster_summary_key() -> str:
        return "cluster:summary"


# Global instance
cache = CacheClient()
