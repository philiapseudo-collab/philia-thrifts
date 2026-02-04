"""
FastAPI application entrypoint.
Production-grade TikTok DM bot for Philia Thrifts.
"""
import logging
import subprocess
import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Start Celery worker in background thread
def start_celery_worker():
    """Start Celery worker as a background process."""
    import time
    time.sleep(5)  # Wait for app to start
    subprocess.run([
        "celery", "-A", "app.worker.celery_app", 
        "worker", "--loglevel=info", "--concurrency=2"
    ])

# Start Celery in background
threading.Thread(target=start_celery_worker, daemon=True).start()

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Application Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and shutdown lifecycle.
    
    Startup:
        - Initialize database tables (dev only - use Alembic in prod)
        - Log configuration
    
    Shutdown:
        - Graceful cleanup
    """
    logger.info("🚀 Starting Philia Thrifts TikTok Bot")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Configured: {settings.is_configured}")
    
    # Run database migrations
    if settings.DATABASE_URL:
        logger.info("Running database migrations...")
        try:
            import subprocess
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Database migrations completed successfully")
            if result.stdout:
                logger.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Database migration failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            # Don't crash on migration failure
        except Exception as e:
            logger.error(f"Database migration failed: {e}", exc_info=True)
            # Don't crash on migration failure - tables might already exist
    else:
        logger.warning("DATABASE_URL not configured, skipping database migrations")
    
    # Initialize Sentry (if configured)
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                traces_sample_rate=1.0 if settings.is_local else 0.1,
            )
            logger.info("Sentry monitoring initialized")
        except ImportError:
            logger.warning("Sentry SDK not installed")
    
    yield
    
    logger.info("👋 Shutting down Philia Thrifts TikTok Bot")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Philia Thrifts TikTok Bot",
    description="Event-driven TikTok DM bot for thrift store sales and support",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_local else None,  # Disable in production
    redoc_url="/redoc" if settings.is_local else None,
)

# CORS middleware (configure based on your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_local else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.routes import health, webhook, admin, seed, auth, seed_button, seed_direct, diagnostic

app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(admin.router)
app.include_router(seed.router)
app.include_router(auth.router)
app.include_router(seed_button.router)
app.include_router(seed_direct.router)
app.include_router(diagnostic.router)


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Philia Thrifts TikTok Bot",
        "version": "1.0.0",
        "status": "operational",
        "configured": settings.is_configured,
        "docs": "/docs" if settings.is_local else "disabled",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_local,
        log_level=settings.LOG_LEVEL.lower(),
    )
