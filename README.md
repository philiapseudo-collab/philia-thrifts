# Philia Thrifts TikTok Bot

Production-grade, event-driven TikTok DM bot for thrift store sales and customer support.

## Architecture

**Pattern:** Producer-Consumer (Webhook → Queue → Worker)

- **Web Service (FastAPI):** Validates TikTok webhooks, queues events (<200ms response)
- **Worker Service (Celery):** Processes messages, AI routing, database operations
- **Database (PostgreSQL):** Persistent state (users, orders, inventory, conversations)
- **Cache (Redis):** Session management, Celery broker, idempotency tracking

## Tech Stack

- **Python 3.11+** with strict type hints
- **FastAPI** (async web framework)
- **SQLModel** (SQLAlchemy 2.0 + Pydantic)
- **Celery + Redis** (async task queue)
- **OpenAI API** (GPT-4o for intent classification)
- **TikTok Business Messaging API**

## Project Structure

```
philia-thrifts/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── core/
│   │   └── config.py           # Pydantic settings
│   ├── db/
│   │   ├── models.py           # SQLModel database models
│   │   └── database.py         # Async session management
│   ├── api/
│   │   └── routes/
│   │       ├── health.py       # Health check endpoint
│   │       └── webhook.py      # TikTok webhook handler
│   ├── worker/
│   │   ├── celery_app.py       # Celery configuration
│   │   └── tasks.py            # Background tasks
│   └── services/               # TODO: Business logic
├── alembic/                    # Database migrations
├── docker-compose.yml          # Local development
├── Dockerfile                  # Multi-stage build
├── Procfile                    # Railway deployment
├── requirements.txt            # Python dependencies
└── .env.example                # Environment template
```

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - TikTok API keys
# - OpenAI API key
# - Database URL (auto-configured for docker-compose)
```

### 2. Local Development (Docker Compose)

```bash
# Start all services (Postgres, Redis, Web, Worker)
docker-compose up --build

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Database Migrations

```bash
# Generate initial migration
docker-compose exec web alembic revision --autogenerate -m "initial schema"

# Apply migrations
docker-compose exec web alembic upgrade head
```

### 4. Seed Database (Phase 2)

```bash
# Seed inventory with realistic thrift items
docker-compose exec web python scripts/seed_db.py seed

# Expected output:
# ✅ Added: Vintage Nike Windbreaker (VNT-NIKE-WB-001)
# ✅ Added: Carhartt Detroit Jacket - Black (CRH-DET-BLK-002)
# ... (10 items total)

# Test service layer
docker-compose exec web python scripts/test_services.py
```

### 5. Testing the Webhook

```bash
# Health check
curl http://localhost:8000/health

# Test webhook (HMAC validation disabled in local)
curl -X POST http://localhost:8000/webhook/tiktok \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message.received",
    "event_id": "test-123",
    "timestamp": 1234567890,
    "data": {
      "message": {
        "content": "Hello",
        "message_id": "msg-1",
        "from_user_id": "user-1",
        "conversation_id": "conv-1",
        "create_time": 1234567890
      }
    }
  }'
```

## Railway Deployment

### Deploy to Railway

1. **Create Railway Project:**
   ```bash
   railway init
   ```

2. **Add Services:**
   - PostgreSQL (Railway Plugin)
   - Redis (Railway Plugin)
   - Web (from Procfile: `web`)
   - Worker (from Procfile: `worker`)

3. **Set Environment Variables:**
   - Copy all from `.env.example`
   - Railway auto-injects `DATABASE_URL` and `REDIS_URL`

4. **Deploy:**
   ```bash
   railway up
   ```

### Environment Variables (Railway)

Required secrets to configure:
- `TIKTOK_CLIENT_KEY`
- `TIKTOK_CLIENT_SECRET`
- `TIKTOK_ACCESS_TOKEN`
- `TIKTOK_WEBHOOK_SECRET`
- `OPENAI_API_KEY`
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`
- `SENTRY_DSN` (optional)

## Development Workflow

### Type Checking

```bash
mypy app/
```

### Code Formatting

```bash
black app/
```

### Running Tests

```bash
pytest
```

## Database Models (Phase 2 Complete)

- **User:** TikTok users with `tiktok_id` as string PK, `last_interaction_at` for 48h window checks
- **Conversation:** Message history (USER/ASSISTANT/SYSTEM roles)
- **Inventory:** Unique thrift items with `Dict[str, float]` measurements, strict status enums
- **Order:** Customer orders with `total_amount` (Decimal precision)
- **OrderItem:** Junction table linking orders to inventory items
- **IdempotencyLog:** Prevent duplicate webhook processing

### Service Layer (Phase 2 Complete)

**User Service (`app/services/users.py`):**
- `get_or_create_user()`: Upsert pattern with automatic timestamp updates
- `check_window_status()`: 48-hour TikTok messaging window validation

**Inventory Service (`app/services/inventory.py`):**
- `search_available_items()`: ILIKE search on name/description
- `get_item_by_sku()`: Retrieve specific items
- `reserve_item()`: Transactional reservation with SELECT FOR UPDATE (race condition safe)

## Security

- **HMAC Validation:** TikTok webhook signatures (disabled in local)
- **Type Safety:** Pydantic models for all payloads
- **Idempotency:** Event ID tracking in Redis
- **Rate Limiting:** TikTok API compliance

## Next Steps (TODO)

1. **Implement AI Services:**
   - Intent classification (OpenAI)
   - Semantic routing (menu vs. size inquiry)

2. **TikTok API Integration:**
   - Send message endpoint
   - Rate limiting decorator
   - Retry logic with exponential backoff

3. **Business Logic:**
   - Inventory search by size/category
   - Order status lookup
   - 48-hour session window management

4. **Monitoring:**
   - Sentry error tracking
   - Railway logs aggregation
   - Performance metrics

## License

Proprietary - Philia Thrifts
