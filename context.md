# Project Context: Philia Thrifts TikTok Automation Bot

## 1. High-Level Objective
Build a production-grade, event-driven TikTok DM bot for "Philia Thrifts" (a clothing/shoe resale business). The bot acts as a first-line SDR (Sales Development Representative) and Customer Support agent. It handles inquiries about sizing, availability, and order status within TikTok's strict API constraints.

## 2. The Tech Stack (Railway Deployment)
* **Infrastructure:** Railway (Dockerized).
* **Language:** Python 3.11+.
* **Web Framework:** FastAPI (Async) for high-concurrency webhook ingestion.
* **Asynchronous Processing:** Celery + Redis (Broker).
* **Database:** PostgreSQL (Persistent State) + Redis (Session/Window Management).
* **ORM:** SQLAlchemy (Async) or Prisma Client Python.
* **AI/LLM:** OpenAI API (GPT-4o) via `openai` SDK.
* **External API:** TikTok Business Messaging API (v1).

## 3. Architecture & Data Flow
**Pattern:** Producer-Consumer (Webhook -> Queue -> Worker).

1.  **Ingress (Web Service):**
    * Endpoint: `POST /webhook/tiktok`
    * Responsibility: Validate HMAC signature (`X-TikTok-Signature`), push payload to Redis, return `200 OK` <200ms.
    * **NO business logic** in this layer.

2.  **Processing (Worker Service):**
    * Responsibility: Fetch context, decide intent (AI or Regex), execute database calls, send reply via TikTok API.
    * **Session Management:** Check `TIKTOK_WINDOW:{user_id}` in Redis. If expired (48h), logging only.

3.  **Egress:**
    * Strict adherence to TikTok rate limits.
    * Retry logic (Exponential Backoff) for failed API calls.

## 4. Business Domain: Philia Thrifts
* **Inventory Model:** Unique SKUs (Thrift). If an item is reserved/sold, it is unavailable immediately.
* **Sizing Logic:** Bot must distinguish between "Tag Size" and "Measurements" (e.g., "It says L but fits like an M").
* **Interaction Style:** Helpful, trendy but professional.
* **UX Pattern:** "Hybrid Menu".
    * Visual: Numbered Text List (1. Status, 2. New Drops, 3. Human).
    * Logic: AI Semantic Router (Accepts "1" OR "Where is my order?").

## 5. Coding Standards (Senior Engineer Level)
* **Type Safety:** Strict Python type hints (`typing.List`, `typing.Optional`, Pydantic models).
* **Config:** `pydantic-settings` for `.env` management.
* **Error Handling:** Never crash the worker. Catch all exceptions, log to stdout (for Railway logs), and degrade gracefully.
* **Structure:** Modular usage.
    * `/app/core` (Config, Security)
    * `/app/api` (Routes)
    * `/app/worker` (Celery tasks)
    * `/app/services` (Business Logic/LLM)
    * `/app/db` (Models/CRUD)

## 6. Critical API Constraints
* **Idempotency:** Track `event_id` in Redis to prevent processing duplicate webhooks.
* **Window:** 48-hour hard limit on replying.
* **Media:** Text and static images only. No button payloads.