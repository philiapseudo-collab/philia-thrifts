"""Test endpoints for simulating TikTok messages."""
import logging
import json
from typing import Dict
from fastapi import APIRouter, HTTPException
from app.worker.tasks import process_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/test", tags=["test"])


@router.post("/simulate-message")
async def simulate_message(user_id: str = "test_user_123", text: str = "Hi, do you have Nike shoes?") -> Dict:
    """
    Simulate a TikTok message to test the full flow without TikTok.
    
    Args:
        user_id: Simulated user ID
        text: Message text
    
    Returns:
        Status of the test
    """
    try:
        logger.info(f"=== TEST: Simulating message from {user_id}: '{text}' ===")
        
        # Create a test event
        event_id = f"test_{user_id}_{hash(text)}"
        
        # Dispatch to Celery worker
        process_message.delay(
            event_id=event_id,
            user_id=user_id,
            text=text,
            raw_payload=json.dumps({
                "event": "message.received",
                "event_id": event_id,
                "sender_id": user_id,
                "message": {"content": text}
            })
        )
        
        logger.info(f"Test message dispatched: {event_id}")
        
        return {
            "status": "dispatched",
            "event_id": event_id,
            "user_id": user_id,
            "message": text,
            "note": "Check worker logs to see if AI responds"
        }
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.get("/check-worker")
async def check_worker() -> Dict:
    """Check if Celery worker is running and connected."""
    try:
        from app.worker.celery_app import celery_app
        
        # Check broker connection
        with celery_app.connection() as conn:
            conn.connect()
            broker_ok = conn.connected
        
        return {
            "celery_app": "initialized",
            "broker_connected": broker_ok,
            "tasks_registered": list(celery_app.tasks.keys())
        }
        
    except Exception as e:
        return {
            "celery_app": "error",
            "error": str(e)
        }
