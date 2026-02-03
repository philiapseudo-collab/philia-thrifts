"""
Redis utilities for session management and idempotency.
"""
import json
from typing import Optional, Any
from datetime import timedelta
from app.core.config import settings

# Redis client (async)
redis_client = None

# Flag to track if Redis is available
_redis_available = False


async def _get_redis_client():
    """
    Internal: Get or create Redis client.
    Lazy initialization pattern.
    """
    global redis_client, _redis_available
    
    if not settings.REDIS_URL:
        return None
    
    if redis_client is None:
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            _redis_available = True
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to connect to Redis: {e}")
            _redis_available = False
            return None
    
    return redis_client


async def check_idempotency(event_id: str) -> bool:
    """
    Check if event has already been processed.
    
    Args:
        event_id: TikTok webhook event ID
    
    Returns:
        True if event was already processed
    """
    client = await _get_redis_client()
    if client is None:
        return False  # Fail open if Redis not available
    
    key = f"idempotency:{event_id}"
    return await client.exists(key) > 0


async def mark_event_processed(event_id: str, ttl_hours: int = 72) -> None:
    """
    Mark event as processed (idempotency lock).
    
    Args:
        event_id: TikTok webhook event ID
        ttl_hours: Time to keep record (default 72h)
    """
    client = await _get_redis_client()
    if client is None:
        return
    
    key = f"idempotency:{event_id}"
    await client.setex(key, timedelta(hours=ttl_hours), "processed")


async def get_session_window(user_id: str) -> Optional[int]:
    """
    Get TikTok 48-hour messaging window expiry timestamp.
    
    Args:
        user_id: TikTok user OpenID
    
    Returns:
        Unix timestamp when window expires, or None if expired
    """
    client = await _get_redis_client()
    if client is None:
        return None
    
    key = f"TIKTOK_WINDOW:{user_id}"
    timestamp = await client.get(key)
    return int(timestamp) if timestamp else None


async def update_session_window(user_id: str, expiry_timestamp: int) -> None:
    """
    Update TikTok 48-hour messaging window.
    
    Args:
        user_id: TikTok user OpenID
        expiry_timestamp: Unix timestamp (48 hours from last user message)
    """
    client = await _get_redis_client()
    if client is None:
        return
    
    key = f"TIKTOK_WINDOW:{user_id}"
    await client.setex(key, timedelta(hours=48), str(expiry_timestamp))


async def set_cache(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    """
    Set cache value with TTL.
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl_seconds: Time to live in seconds
    """
    client = await _get_redis_client()
    if client is None:
        return
    
    serialized = json.dumps(value)
    await client.setex(key, timedelta(seconds=ttl_seconds), serialized)


async def get_cache(key: str) -> Optional[Any]:
    """
    Get cached value.
    
    Args:
        key: Cache key
    
    Returns:
        Cached value (JSON deserialized) or None
    """
    client = await _get_redis_client()
    if client is None:
        return None
    
    value = await client.get(key)
    return json.loads(value) if value else None
