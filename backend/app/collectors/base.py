"""Base Collector class"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base class for all collectors"""

    def __init__(self, name: str):
        self.name = name
        self.last_collect_time: datetime = None
        self.collect_count: int = 0

    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """
        Collect metrics data.
        Returns a dictionary with collected metrics.
        """
        pass

    async def run(self) -> Dict[str, Any]:
        """Execute collection and update metadata"""
        try:
            data = await self.collect()
            self.last_collect_time = datetime.utcnow()
            self.collect_count += 1
            logger.debug(f"{self.name} collected data at {self.last_collect_time}")
            return data
        except Exception as e:
            logger.error(f"{self.name} collection failed: {e}")
            raise

    def get_status(self) -> Dict[str, Any]:
        """Get collector status"""
        return {
            "name": self.name,
            "last_collect_time": self.last_collect_time.isoformat() if self.last_collect_time else None,
            "collect_count": self.collect_count,
        }
