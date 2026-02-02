"""Health check and system status endpoints."""
import logging
from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_session

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """
    Health check endpoint with database connectivity test.
    
    Returns:
        Status dictionary with service health
    """
    try:
        # Test database connection
        result = await session.execute(text("SELECT 1"))
        db_status = "connected" if result else "disconnected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "error"
    
    return {
        "status": "ok",
        "db": db_status,
        "service": "philia-thrifts-bot"
    }
