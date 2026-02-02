"""
Idempotency service for webhook deduplication.

Strategy:
- Redis: Fast check at ingress (<200ms requirement)
- PostgreSQL: Permanent audit log (written by worker)
"""
import logging
from typing import Optional
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)


async def check_and_set(event_id: str, ttl: int = 600) -> bool:
    """
    Check if event has been processed and mark it as processing (atomic).
    
    Implementation:
    - Uses Redis SETNX (SET if Not eXists) for atomic check-and-set
    - TTL protects against memory bloat (10 minutes default)
    - Returns True if event was ALREADY processed (duplicate)
    - Returns False if event is NEW (proceed with processing)
    
    Race Condition Safety:
    Redis SETNX is atomic, so even if two webhooks arrive simultaneously:
    - First webhook: SETNX succeeds → Returns False (proceed)
    - Second webhook: SETNX fails → Returns True (skip)
    
    Args:
        event_id: Unique TikTok event identifier
        ttl: Time-to-live in seconds (default 600 = 10 minutes)
    
    Returns:
        True if event was already processed (DUPLICATE)
        False if event is new (PROCEED)
    
    Example:
        >>> is_duplicate = await check_and_set("evt_123")
        >>> if is_duplicate:
        >>>     return {"status": "ok"}  # Stop processing
        >>> # Otherwise proceed with Celery dispatch
    
    Why 10 Minutes TTL?
    - TikTok typically retries failed webhooks within 5 minutes
    - 10 minutes gives buffer without wasting memory
    - Worker writes permanent log to PostgreSQL IdempotencyLog
    """
    try:
        client = await get_redis_client()
        key = f"idempotency:{event_id}"
        
        # SETNX: SET if Not eXists
        # Returns True if key was SET (new event)
        # Returns False if key already exists (duplicate)
        was_set = await client.set(
            key,
            "processing",
            nx=True,  # Only set if not exists (atomic)
            ex=ttl    # Expire after TTL seconds
        )
        
        if was_set:
            logger.info(f"New event {event_id}, proceeding with processing")
            return False  # New event, proceed
        else:
            logger.warning(f"Duplicate event {event_id}, skipping")
            return True  # Duplicate, skip
            
    except Exception as e:
        logger.error(
            f"Error checking idempotency for {event_id}: {str(e)}",
            exc_info=True
        )
        # Fail open: If Redis is down, allow processing
        # Better to process twice than miss events
        logger.warning("Redis error, allowing event through (fail-open)")
        return False


async def mark_completed(event_id: str, status: str = "success") -> None:
    """
    Update Redis key to mark event as completed.
    
    Optional enhancement: Update the value to track status.
    Not critical since worker writes to PostgreSQL.
    
    Args:
        event_id: Event identifier
        status: Processing status (success, error, etc.)
    """
    try:
        client = await get_redis_client()
        key = f"idempotency:{event_id}"
        
        # Update value to reflect completion status
        await client.set(key, f"completed:{status}", ex=600)
        logger.info(f"Marked event {event_id} as {status}")
        
    except Exception as e:
        logger.error(f"Error marking event complete: {str(e)}", exc_info=True)


async def get_event_status(event_id: str) -> Optional[str]:
    """
    Get current processing status of an event.
    
    Useful for debugging or admin dashboards.
    
    Args:
        event_id: Event identifier
    
    Returns:
        Status string or None if not found
    """
    try:
        client = await get_redis_client()
        key = f"idempotency:{event_id}"
        status = await client.get(key)
        return status
        
    except Exception as e:
        logger.error(f"Error getting event status: {str(e)}", exc_info=True)
        return None
