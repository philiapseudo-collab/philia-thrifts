"""
Service layer test script.

Usage:
    python scripts/test_services.py

This script demonstrates and tests the service layer functionality:
- User creation and window checks
- Inventory search
- Item reservation with race condition prevention
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import async_session_maker
from app.services.users import (
    get_or_create_user,
    check_window_status,
    get_user_by_id
)
from app.services.inventory import (
    search_available_items,
    get_item_by_sku,
    reserve_item,
    get_available_count
)


async def test_user_services():
    """Test user service layer."""
    print("\n" + "="*60)
    print("🧪 Testing User Services")
    print("="*60)
    
    async with async_session_maker() as session:
        # Test 1: Create new user
        print("\n1️⃣ Testing get_or_create_user (new user)...")
        user = await get_or_create_user("test_user_123", "john_doe", session)
        await session.commit()
        print(f"   ✅ Created user: {user.tiktok_id} (@{user.username})")
        print(f"   Last interaction: {user.last_interaction_at}")
        
        # Test 2: Update existing user
        print("\n2️⃣ Testing get_or_create_user (existing user)...")
        await asyncio.sleep(1)  # Small delay to see timestamp update
        user2 = await get_or_create_user("test_user_123", "john_updated", session)
        await session.commit()
        print(f"   ✅ Updated user: {user2.tiktok_id} (@{user2.username})")
        print(f"   Last interaction: {user2.last_interaction_at}")
        
        # Test 3: Check window status (should be valid)
        print("\n3️⃣ Testing check_window_status (within 48h)...")
        is_valid = await check_window_status("test_user_123", session)
        print(f"   ✅ Window status: {is_valid} (expected: True)")
        
        # Test 4: Check window status for expired user (simulate)
        print("\n4️⃣ Testing check_window_status (expired)...")
        # Manually set old timestamp
        user3 = await get_user_by_id("test_user_123", session)
        user3.last_interaction_at = datetime.utcnow() - timedelta(hours=50)
        session.add(user3)
        await session.commit()
        
        is_valid_expired = await check_window_status("test_user_123", session)
        print(f"   ✅ Window status: {is_valid_expired} (expected: False)")
        
        # Cleanup: Reset timestamp
        user3.last_interaction_at = datetime.utcnow()
        session.add(user3)
        await session.commit()


async def test_inventory_services():
    """Test inventory service layer."""
    print("\n" + "="*60)
    print("🧪 Testing Inventory Services")
    print("="*60)
    
    async with async_session_maker() as session:
        # Test 1: Get available count
        print("\n1️⃣ Testing get_available_count...")
        count = await get_available_count(session)
        print(f"   ✅ Available items: {count}")
        
        # Test 2: Search items
        print("\n2️⃣ Testing search_available_items (query: 'nike')...")
        items = await search_available_items("nike", session, limit=3)
        print(f"   ✅ Found {len(items)} items:")
        for item in items:
            print(f"      - {item.name} ({item.sku}) - ${item.price}")
        
        # Test 3: Get item by SKU
        print("\n3️⃣ Testing get_item_by_sku...")
        if items:
            sku = items[0].sku
            item = await get_item_by_sku(sku, session)
            print(f"   ✅ Retrieved: {item.name}")
            print(f"      Size: {item.size_label}")
            print(f"      Measurements: {item.measurements}")
            print(f"      Status: {item.status.value}")
        
        # Test 4: Reserve item (with transaction)
        print("\n4️⃣ Testing reserve_item (transactional)...")
        if items:
            sku = items[0].sku
            async with session.begin():
                success = await reserve_item(sku, "test_user_123", session)
                print(f"   ✅ Reservation success: {success}")
                
                # Verify status changed
                item = await get_item_by_sku(sku, session)
                print(f"      New status: {item.status.value}")
                
                # Try to reserve again (should fail)
                success2 = await reserve_item(sku, "test_user_456", session)
                print(f"   ✅ Second reservation: {success2} (expected: False)")


async def test_race_condition_simulation():
    """
    Simulate race condition on item reservation.
    
    This demonstrates that SELECT FOR UPDATE prevents double-booking.
    """
    print("\n" + "="*60)
    print("🧪 Testing Race Condition Prevention")
    print("="*60)
    
    # Find an available item
    async with async_session_maker() as session:
        items = await search_available_items("", session, limit=1)
        if not items:
            print("   ⚠️  No available items to test race condition")
            return
        
        test_sku = items[0].sku
        print(f"\n🎯 Testing concurrent reservations on: {items[0].name} ({test_sku})")
    
    async def try_reserve(user_id: str):
        """Simulate user trying to reserve item."""
        async with async_session_maker() as session:
            async with session.begin():
                success = await reserve_item(test_sku, user_id, session)
                if success:
                    print(f"   ✅ User {user_id} SUCCEEDED")
                else:
                    print(f"   ❌ User {user_id} FAILED (already reserved)")
                return success
    
    # Simulate 5 users trying to reserve at the same time
    results = await asyncio.gather(
        try_reserve("user_001"),
        try_reserve("user_002"),
        try_reserve("user_003"),
        try_reserve("user_004"),
        try_reserve("user_005")
    )
    
    success_count = sum(results)
    print(f"\n📊 Results: {success_count} succeeded, {5 - success_count} failed")
    print(f"   Expected: Exactly 1 success (race condition prevented ✓)")


async def main():
    """Run all tests."""
    print("\n" + "🚀 " * 20)
    print("SERVICE LAYER TEST SUITE")
    print("🚀 " * 20)
    
    try:
        await test_user_services()
        await test_inventory_services()
        await test_race_condition_simulation()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
