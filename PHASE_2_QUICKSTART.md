# Phase 2: Quick Start Guide

## 🚀 Testing Your Phase 2 Implementation

Follow these steps to verify everything works:

### Step 1: Start Services
```bash
# If not already running
docker-compose up -d
```

### Step 2: Generate Migration
```bash
# Generate migration from updated models
docker-compose exec web alembic revision --autogenerate -m "phase 2: data layer complete"

# You should see output like:
# INFO  [alembic.runtime.migration] Generating migration...
# Generating /app/alembic/versions/xxxxx_phase_2_data_layer_complete.py
```

### Step 3: Apply Migration
```bash
docker-compose exec web alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade -> xxxxx, phase 2: data layer complete
```

### Step 4: Seed Database
```bash
docker-compose exec web python scripts/seed_db.py seed

# Expected output:
# 🌱 Starting database seed...
# ✅ Added: Vintage Nike Windbreaker (VNT-NIKE-WB-001)
# ✅ Added: Carhartt Detroit Jacket - Black (CRH-DET-BLK-002)
# ✅ Added: Levi's 501 Original Fit Jeans (LEV-501-W32L30-003)
# ... (10 items total)
# ✨ Seed completed! Added: 10 items
```

### Step 5: Test Service Layer
```bash
docker-compose exec web python scripts/test_services.py

# Expected output:
# 🚀🚀🚀... SERVICE LAYER TEST SUITE 🚀🚀🚀...
#
# 🧪 Testing User Services
# 1️⃣ Testing get_or_create_user (new user)...
#    ✅ Created user: test_user_123 (@john_doe)
# 2️⃣ Testing get_or_create_user (existing user)...
#    ✅ Updated user: test_user_123 (@john_updated)
# 3️⃣ Testing check_window_status (within 48h)...
#    ✅ Window status: True (expected: True)
# 4️⃣ Testing check_window_status (expired)...
#    ✅ Window status: False (expected: False)
#
# 🧪 Testing Inventory Services
# 1️⃣ Testing get_available_count...
#    ✅ Available items: 8
# 2️⃣ Testing search_available_items (query: 'nike')...
#    ✅ Found 1 items:
#       - Vintage Nike Windbreaker (VNT-NIKE-WB-001) - $45.00
# 3️⃣ Testing get_item_by_sku...
#    ✅ Retrieved: Vintage Nike Windbreaker
#       Size: L
#       Measurements: {'pit_to_pit': 24.5, 'length': 28.0, 'sleeve_length': 25.5}
#       Status: AVAILABLE
# 4️⃣ Testing reserve_item (transactional)...
#    ✅ Reservation success: True
#       New status: RESERVED
#    ✅ Second reservation: False (expected: False)
#
# 🧪 Testing Race Condition Prevention
# 🎯 Testing concurrent reservations on: Carhartt Detroit Jacket - Black (CRH-DET-BLK-002)
#    ✅ User user_001 SUCCEEDED
#    ❌ User user_002 FAILED (already reserved)
#    ❌ User user_003 FAILED (already reserved)
#    ❌ User user_004 FAILED (already reserved)
#    ❌ User user_005 FAILED (already reserved)
#
# 📊 Results: 1 succeeded, 4 failed
#    Expected: Exactly 1 success (race condition prevented ✓)
#
# ✅ All tests completed!
```

---

## 🔍 Verify Database Contents

### Connect to Database
```bash
# Option 1: psql (if you have PostgreSQL client)
docker-compose exec postgres psql -U postgres -d philia_thrifts

# Option 2: Use your IDE's database tool (DataGrip, VS Code, etc.)
# Connection: postgresql://postgres:postgres@localhost:5432/philia_thrifts
```

### Check Tables
```sql
-- View all tables
\dt

-- Expected output:
--  public | alembic_version    | table | postgres
--  public | conversations      | table | postgres
--  public | idempotency_logs   | table | postgres
--  public | inventory          | table | postgres
--  public | order_items        | table | postgres
--  public | orders             | table | postgres
--  public | users              | table | postgres

-- View inventory items
SELECT sku, name, price, status FROM inventory;

-- Expected: 10 thrift items (8 AVAILABLE, 1 RESERVED, 1 SOLD)

-- View users created by test script
SELECT tiktok_id, username, last_interaction_at FROM users;

-- Expected: test_user_123
```

---

## 📝 Manual Testing Examples

### Test User Service (Python REPL)
```bash
docker-compose exec web python

>>> from app.db.database import async_session_maker
>>> from app.services.users import get_or_create_user, check_window_status
>>> import asyncio
>>>
>>> async def test():
...     async with async_session_maker() as session:
...         user = await get_or_create_user("manual_test_001", "alice", session)
...         await session.commit()
...         print(f"Created: {user.tiktok_id}")
...         
...         can_reply = await check_window_status("manual_test_001", session)
...         print(f"Can reply: {can_reply}")
>>>
>>> asyncio.run(test())
Created: manual_test_001
Can reply: True
```

### Test Inventory Service (Python REPL)
```python
>>> from app.services.inventory import search_available_items, reserve_item
>>>
>>> async def test_search():
...     async with async_session_maker() as session:
...         items = await search_available_items("vintage", session)
...         for item in items:
...             print(f"{item.name} - ${item.price}")
>>>
>>> asyncio.run(test_search())
Vintage Nike Windbreaker - $45.00
Vintage Chambray Work Shirt - $42.00
```

---

## ⚠️ Troubleshooting

### Issue: Migration Error "Target database is not up to date"
```bash
# Check current migration status
docker-compose exec web alembic current

# View migration history
docker-compose exec web alembic history

# If stuck, you can:
# 1. Stamp current version
docker-compose exec web alembic stamp head

# 2. Or reset (DANGER: deletes data)
docker-compose down -v  # Remove volumes
docker-compose up -d    # Recreate
```

### Issue: Seed Script Error "Already Exists"
```bash
# This is normal on re-runs (idempotent)
# To clear and re-seed:
docker-compose exec web python scripts/seed_db.py clear
# Type: DELETE ALL
docker-compose exec web python scripts/seed_db.py seed
```

### Issue: Test Script Fails
```bash
# Check logs
docker-compose logs web

# Check database connection
docker-compose exec web python -c "from app.db.database import async_session_maker; import asyncio; asyncio.run(async_session_maker().__anext__())"

# If connection fails, ensure Postgres is healthy
docker-compose ps
docker-compose logs postgres
```

---

## ✅ Success Criteria

You've successfully completed Phase 2 if:

- ✅ Migration generated without errors
- ✅ 7 tables created (users, inventory, orders, order_items, conversations, idempotency_logs, alembic_version)
- ✅ Seed script adds 10 items
- ✅ Test script shows all tests passing
- ✅ Race condition test shows exactly 1 success
- ✅ Can manually query database and see data

---

## 🎯 Next: Phase 3 Planning

Once Phase 2 is verified, we can move to:

**Phase 3: TikTok API Integration**
- Send message endpoint
- Rate limiting
- Webhook → Worker → Reply flow

Let me know when you've tested Phase 2 and we'll proceed! 🚀
