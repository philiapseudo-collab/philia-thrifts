"""
Inventory service layer for thrift item management.

Key Features:
- Search available items with ILIKE queries
- Reserve items with transactional locking (prevents race conditions)
- Retrieve items by SKU
"""
import logging
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Inventory, InventoryStatus

logger = logging.getLogger(__name__)


async def get_item_by_sku(sku: str, session: AsyncSession) -> Optional[Inventory]:
    """
    Retrieve inventory item by SKU.
    
    Args:
        sku: Unique item identifier
        session: Database session (explicit parameter for Celery compatibility)
    
    Returns:
        Inventory item or None if not found
    """
    statement = select(Inventory).where(Inventory.sku == sku)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def search_available_items(
    query: str, 
    session: AsyncSession,
    limit: int = 5
) -> List[Inventory]:
    """
    Search available thrift items by name or description.
    
    Search Strategy:
    - Only AVAILABLE items (status filter)
    - Case-insensitive partial match (ILIKE)
    - Searches both name AND description
    - Ordered by newest first
    
    Args:
        query: Search term (e.g., "nike", "jacket")
        session: Database session
        limit: Maximum results to return (default 5)
    
    Returns:
        List of matching inventory items
    
    Example:
        >>> items = await search_available_items("vintage nike", session)
        >>> # Returns items like "Vintage Nike Windbreaker"
    """
    search_pattern = f"%{query}%"
    
    statement = (
        select(Inventory)
        .where(Inventory.status == InventoryStatus.AVAILABLE)
        .where(
            or_(
                Inventory.name.ilike(search_pattern),
                Inventory.description.ilike(search_pattern)
            )
        )
        .order_by(Inventory.created_at.desc())
        .limit(limit)
    )
    
    result = await session.execute(statement)
    return list(result.scalars().all())


async def reserve_item(
    sku: str, 
    user_id: str, 
    session: AsyncSession
) -> bool:
    """
    Reserve an inventory item for a user with transactional locking.
    
    Critical Implementation:
    - Uses SELECT ... FOR UPDATE to prevent race conditions
    - If two users try to reserve simultaneously, only one succeeds
    - Atomic check-and-set operation
    
    Args:
        sku: Item SKU to reserve
        user_id: TikTok user ID (for logging/audit trail)
        session: Database session (must be in a transaction)
    
    Returns:
        True if reservation succeeded, False if item unavailable
    
    Transaction Safety:
    The caller MUST wrap this in a transaction:
    ```python
    async with session.begin():
        success = await reserve_item(sku, user_id, session)
        if success:
            await session.commit()
    ```
    
    Race Condition Prevention:
    without FOR UPDATE:
        User A: SELECT (status=AVAILABLE) ✓
        User B: SELECT (status=AVAILABLE) ✓
        User A: UPDATE to RESERVED ✓
        User B: UPDATE to RESERVED ✓  <- DOUBLE RESERVATION!
    
    with FOR UPDATE:
        User A: SELECT FOR UPDATE (locks row) ✓
        User B: SELECT FOR UPDATE (waits...)
        User A: UPDATE to RESERVED ✓
        User A: COMMIT (releases lock)
        User B: SELECT sees RESERVED ✗
        User B: Returns False
    """
    try:
        # Lock the row for update (prevents concurrent modifications)
        statement = (
            select(Inventory)
            .where(Inventory.sku == sku)
            .with_for_update()  # Critical: Row-level lock
        )
        
        result = await session.execute(statement)
        item = result.scalar_one_or_none()
        
        if item is None:
            logger.warning(f"Reserve failed: Item {sku} not found")
            return False
        
        if item.status != InventoryStatus.AVAILABLE:
            logger.info(f"Reserve failed: Item {sku} is {item.status.value}")
            return False
        
        # Update status to RESERVED
        item.status = InventoryStatus.RESERVED
        session.add(item)
        
        logger.info(f"Reserved item {sku} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error reserving item {sku}: {str(e)}", exc_info=True)
        return False


async def get_available_count(session: AsyncSession) -> int:
    """
    Get count of available inventory items.
    
    Useful for:
    - Dashboard metrics
    - "We have X items available" messages
    
    Args:
        session: Database session
    
    Returns:
        Number of AVAILABLE items
    """
    from sqlalchemy import func
    
    statement = (
        select(func.count(Inventory.id))
        .where(Inventory.status == InventoryStatus.AVAILABLE)
    )
    
    result = await session.execute(statement)
    return result.scalar_one()
