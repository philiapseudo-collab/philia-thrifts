#!/usr/bin/env python3
"""
Database migration runner for Railway deployment.
Run this script on startup to apply pending migrations.
"""
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_migrations():
    """Run Alembic migrations programmatically."""
    try:
        from alembic.config import Config
        from alembic import command
        from app.core.config import settings
        
        if not settings.DATABASE_URL:
            logger.error("DATABASE_URL not configured, skipping migrations")
            return False
        
        logger.info("Running database migrations...")
        
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Upgrade to latest version
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Migrations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(run_migrations())
    sys.exit(0 if success else 1)
