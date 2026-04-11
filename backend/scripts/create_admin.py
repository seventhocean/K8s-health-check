"""Script to create default admin user"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.auth import User
import bcrypt


async def create_default_user():
    """Create default admin user if not exists"""

    # Build database URL
    database_url = (
        f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    )

    engine = create_async_engine(database_url)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

    async with async_session_maker() as session:
        # Check if admin user exists
        result = await session.execute(select(User).where(User.username == "admin"))
        admin_user = result.scalar_one_or_none()

        if admin_user:
            print("Admin user already exists.")
            return

        # Create admin user with strong password
        # Password must: 8+ chars, uppercase, lowercase, digit, special char
        hashed_password = bcrypt.hashpw(
            "Admin@123".encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")
        new_user = User(
            username="admin",
            email="admin@example.com",
            phone="",
            role="admin",
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(new_user)
        await session.commit()

        print("=" * 50)
        print("Default admin user created successfully!")
        print("=" * 50)
        print("Username: admin")
        print("Password: Admin@123")
        print("=" * 50)
        print("Please change the password after first login!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(create_default_user())
