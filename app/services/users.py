"""
User service layer for TikTok user management.

Key Features:
- Get or create users (upsert pattern)
- 48-hour messaging window validation (database-based)
- Last interaction tracking
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User

logger = logging.getLogger(__name__)


async def get_or_create_user(
    tiktok_id: str,
    username: Optional[str],
    session: AsyncSession
) -> User:
    """
    Get existing user or create new one (upsert pattern).
    
    Behavior:
    - If user exists: Updates last_interaction_at to now
    - If user doesn't exist: Creates new user record
    
    This ensures every interaction refreshes the 48-hour window.
    
    Args:
        tiktok_id: TikTok OpenID (primary key)
        username: TikTok username (optional, may be None)
        session: Database session
    
    Returns:
        User object (existing or newly created)
    
    Example:
        >>> user = await get_or_create_user("tiktok_123", "john_doe", session)
        >>> print(user.last_interaction_at)  # Just now
    """
    # Try to fetch existing user
    statement = select(User).where(User.tiktok_id == tiktok_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    
    if user:
        # User exists - update interaction timestamp
        user.last_interaction_at = datetime.utcnow()
        
        # Update username if provided and different
        if username and user.username != username:
            user.username = username
        
        session.add(user)
        logger.info(f"Updated user {tiktok_id} interaction timestamp")
    else:
        # User doesn't exist - create new
        user = User(
            tiktok_id=tiktok_id,
            username=username,
            last_interaction_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        session.add(user)
        logger.info(f"Created new user {tiktok_id}")
    
    return user


async def check_window_status(tiktok_id: str, session: AsyncSession) -> bool:
    """
    Check if user is within the 48-hour TikTok messaging window.
    
    TikTok Constraint:
    Bots can only send messages within 48 hours of the user's last message.
    After 48 hours, we can only log (cannot reply).
    
    Implementation:
    - Database-only for MVP (simple, reliable)
    - TODO: Add Redis caching for performance (read Redis → fallback to DB)
    
    Args:
        tiktok_id: TikTok user ID
        session: Database session
    
    Returns:
        True if within 48-hour window, False if expired
    
    Example:
        >>> can_reply = await check_window_status("tiktok_123", session)
        >>> if can_reply:
        >>>     await send_tiktok_message(...)
        >>> else:
        >>>     logger.warning("Window expired, logging only")
    
    TODO: Optimization for Production
    ```python
    # Phase 1: Check Redis cache (fast)
    cached_expiry = await redis.get(f"TIKTOK_WINDOW:{tiktok_id}")
    if cached_expiry:
        return int(time.time()) < int(cached_expiry)
    
    # Phase 2: Fallback to DB, refill cache
    user = await get_user(tiktok_id, session)
    if user:
        expiry_timestamp = user.last_interaction_at + timedelta(hours=48)
        await redis.setex(
            f"TIKTOK_WINDOW:{tiktok_id}",
            timedelta(hours=48),
            int(expiry_timestamp.timestamp())
        )
        return datetime.utcnow() < expiry_timestamp
    ```
    """
    statement = select(User).where(User.tiktok_id == tiktok_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    
    if not user:
        # User doesn't exist - no active window
        logger.warning(f"Window check: User {tiktok_id} not found")
        return False
    
    # Calculate window expiry (48 hours from last interaction)
    window_expiry = user.last_interaction_at + timedelta(hours=48)
    is_within_window = datetime.utcnow() < window_expiry
    
    if is_within_window:
        logger.info(f"User {tiktok_id} within 48h window")
    else:
        hours_expired = (datetime.utcnow() - window_expiry).total_seconds() / 3600
        logger.warning(
            f"User {tiktok_id} window EXPIRED {hours_expired:.1f}h ago"
        )
    
    return is_within_window


async def get_user_by_id(tiktok_id: str, session: AsyncSession) -> Optional[User]:
    """
    Retrieve user by TikTok ID.
    
    Args:
        tiktok_id: TikTok OpenID
        session: Database session
    
    Returns:
        User object or None if not found
    """
    statement = select(User).where(User.tiktok_id == tiktok_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def update_interaction_timestamp(
    tiktok_id: str, 
    session: AsyncSession
) -> bool:
    """
    Update user's last interaction timestamp (refresh 48-hour window).
    
    Use Case:
    When user sends a message, this resets the 48-hour window.
    
    Args:
        tiktok_id: TikTok user ID
        session: Database session
    
    Returns:
        True if updated, False if user not found
    """
    user = await get_user_by_id(tiktok_id, session)
    
    if not user:
        logger.warning(f"Cannot update timestamp: User {tiktok_id} not found")
        return False
    
    user.last_interaction_at = datetime.utcnow()
    session.add(user)
    logger.info(f"Updated interaction timestamp for user {tiktok_id}")
    return True
