"""Admin endpoints for database management."""
import logging
from typing import Dict
from fastapi import APIRouter, HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/migrate")
async def run_migrations() -> Dict[str, str]:
    """
    Run database migrations manually.
    
    Returns:
        Status of migration
    """
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        from alembic.config import Config
        from alembic import command
        
        logger.info("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
        
        return {"status": "success", "message": "Migrations applied successfully"}
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.get("/db-status")
async def db_status() -> Dict:
    """
    Check database status and migration version.
    """
    if not settings.DATABASE_URL:
        return {"configured": False, "status": "not_configured"}
    
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from sqlalchemy import text
        from app.db.database import async_session_maker
        
        async with async_session_maker() as session:
            # Check if alembic_version table exists
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """))
            has_alembic = result.scalar()
            
            if has_alembic:
                # Get current version
                result = await session.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                
                # Get latest migration
                alembic_cfg = Config("alembic.ini")
                script = ScriptDirectory.from_config(alembic_cfg)
                latest = script.get_current_head()
                
                return {
                    "configured": True,
                    "status": "connected",
                    "current_version": version,
                    "latest_version": latest,
                    "up_to_date": version == latest
                }
            else:
                return {
                    "configured": True,
                    "status": "connected",
                    "current_version": None,
                    "message": "No migrations applied yet"
                }
                
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return {
            "configured": True,
            "status": "error",
            "error": str(e)
        }
