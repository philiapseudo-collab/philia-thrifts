"""Health check and system status endpoints."""
import logging
from typing import Dict, Any
from fastapi import APIRouter
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Status dictionary with service health
    """
    health_status = {
        "status": "ok",
        "service": "philia-thrifts-bot",
        "configured": settings.is_configured,
    }
    
    # Only check database if configured
    if settings.DATABASE_URL:
        try:
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy import text
            from app.db.database import async_session_maker
            
            async with async_session_maker() as session:
                result = await session.execute(text("SELECT 1"))
                db_status = "connected" if result else "disconnected"
                health_status["db"] = db_status
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            health_status["db"] = "error"
            health_status["db_error"] = str(e)
    else:
        health_status["db"] = "not_configured"
    
    return health_status


@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check - verifies all required services are available.
    Used by Railway/Kubernetes for pod readiness.
    """
    if not settings.is_configured:
        return {
            "status": "not_ready",
            "reason": "configuration_incomplete",
            "configured": "false"
        }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        from app.db.database import async_session_maker
        
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "status": "not_ready",
            "reason": "database_unavailable",
            "error": str(e)
        }
    
    return {
        "status": "ready",
        "service": "philia-thrifts-bot"
    }
