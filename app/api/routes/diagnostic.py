"""Diagnostic endpoints for troubleshooting webhook issues."""
import logging
from typing import Dict, List
from fastapi import APIRouter, Request
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

# Store recent webhook events for debugging
recent_events: List[Dict] = []


@router.post("/webhook-test")
async def webhook_test(request: Request) -> Dict:
    """
    Test endpoint that captures and logs any webhook request.
    Use this to verify webhooks are reaching your server.
    """
    try:
        raw_body = await request.body()
        headers = dict(request.headers)
        
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "headers": {k: v for k, v in headers.items() if k.lower() not in ['authorization', 'cookie']},
            "body": raw_body.decode('utf-8')[:1000] if raw_body else None,
        }
        
        # Store last 10 events
        recent_events.insert(0, event_data)
        if len(recent_events) > 10:
            recent_events.pop()
        
        logger.info(f"=== WEBHOOK TEST RECEIVED ===")
        logger.info(f"Headers: {event_data['headers']}")
        logger.info(f"Body: {event_data['body']}")
        
        return {
            "status": "received",
            "message": "Webhook test received successfully",
            "event_id": event_data['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error in webhook test: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/recent-events")
async def get_recent_events() -> List[Dict]:
    """Get recent webhook events for debugging."""
    return recent_events


@router.get("/tiktok-config")
async def tiktok_config() -> Dict:
    """Check TikTok configuration (without exposing secrets)."""
    from app.core.config import settings
    
    return {
        "client_key_set": bool(settings.TIKTOK_CLIENT_KEY),
        "client_secret_set": bool(settings.TIKTOK_CLIENT_SECRET),
        "access_token_set": bool(settings.TIKTOK_ACCESS_TOKEN),
        "webhook_secret_set": bool(settings.TIKTOK_WEBHOOK_SECRET),
        "business_id_set": bool(settings.TIKTOK_BUSINESS_ID),
        "webhook_url": "https://web-production-ec3c.up.railway.app/webhook/tiktok",
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health-detailed")
async def health_detailed() -> Dict:
    """Detailed health check with all services."""
    from app.core.config import settings
    from app.db.database import async_session_maker
    
    health_status = {
        "web": "ok",
        "database": "unknown",
        "redis": "unknown",
        "tiktok_configured": settings.is_configured,
    }
    
    # Check database
    try:
        if settings.DATABASE_URL:
            async with async_session_maker() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                health_status["database"] = "connected"
        else:
            health_status["database"] = "not_configured"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    # Check Redis
    try:
        if settings.REDIS_URL:
            from app.core.redis import _get_redis_client
            client = await _get_redis_client()
            if client:
                health_status["redis"] = "connected"
            else:
                health_status["redis"] = "not_connected"
        else:
            health_status["redis"] = "not_configured"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    return health_status
