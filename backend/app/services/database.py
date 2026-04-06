"""Database connection and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, List, Type
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# Define Base here to avoid circular imports
class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# List of models to be imported for table creation
MODELS: List[Type[Base]] = []


class Database:
    """Database connection manager"""

    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    async def connect(self) -> None:
        """Initialize database connection"""
        # Build MySQL connection URL for async
        database_url = (
            f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        )

        self.engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )

        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        logger.info("Database connected")

    async def disconnect(self) -> None:
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
        logger.info("Database disconnected")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.async_session_maker() as session:
            yield session

    async def create_all_tables(self) -> None:
        """Create all tables (useful for initialization)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created")


# Global instance
database = Database()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes"""
    async for session in database.get_session():
        yield session
