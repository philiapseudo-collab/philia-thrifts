"""
Database engine and session management.
Async SQLAlchemy setup for FastAPI.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.core.config import settings

# Engine is None if DATABASE_URL is not configured
engine: Optional[AsyncEngine] = None
async_session_maker = None

if settings.DATABASE_URL:
    # Create async engine only if DATABASE_URL is configured
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.LOG_LEVEL == "DEBUG",  # Log SQL in debug mode
        future=True,
    )

    # Async session factory
    async_session_maker = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    Usage: session: AsyncSession = Depends(get_session)
    
    Raises:
        RuntimeError: If database is not configured
    """
    if async_session_maker is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL environment variable.")
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    NOTE: In production, use Alembic migrations instead.
    """
    if engine is None:
        raise RuntimeError("Cannot initialize database: DATABASE_URL not configured")
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
