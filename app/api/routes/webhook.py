"""
TikTok webhook endpoint with HMAC signature validation.
Producer layer: Validates and queues events in <200ms.

Phase 3: Ingestion & Async Dispatch
- Signature validation using app.core.security
- Idempotency check via Redis (fast path)
- Celery dispatch with flexible payload extraction
"""
import logging
import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.security import verify_tiktok_signature
from app.services.idempotency import check_and_set
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])


# ============================================================================
# Pydantic Models for TikTok Webhook Payload
# ============================================================================

class TikTokWebhookPayload(BaseModel):
    """
    Flexible TikTok webhook event structure.
    
    TikTok's API structure varies by version and event type.
    This model captures common fields and allows flexible extraction.
    
    Strategy:
    - Capture standard fields (event, event_id, timestamp)
    - Store everything else in data/entry for flexible parsing
    - Worker logs raw payload for schema debugging
    """
    # Standard fields
    event: Optional[str] = None
    event_id: Optional[str] = None
    timestamp: Optional[int] = None
    
    # Flexible containers (TikTok uses different structures)
    data: Optional[Dict[str, Any]] = None
    entry: Optional[list] = None  # Meta/TikTok Business API pattern
    
    @property
    def sender_id(self) -> str:
        """
        Extract sender ID from various possible structures.
        
        Handles:
        - Flat structure: data.sender_id
        - Nested: data.message.from_user_id
        - Entry pattern: entry[0].changes[0].value.sender
        
        Falls back to "unknown" for worker to handle.
        """
        # Try flat data structure
        if self.data:
            if "sender_id" in self.data:
                return self.data["sender_id"]
            
            # Try nested message structure
            if "message" in self.data:
                msg = self.data["message"]
                if isinstance(msg, dict) and "from_user_id" in msg:
                    return msg["from_user_id"]
        
        # Try entry pattern (Meta-style)
        if self.entry and len(self.entry) > 0:
            # Structure: entry[0].changes[0].value.sender
            try:
                first_entry = self.entry[0]
                if "changes" in first_entry and len(first_entry["changes"]) > 0:
                    change = first_entry["changes"][0]
                    if "value" in change and "sender" in change["value"]:
                        return change["value"]["sender"]
            except (KeyError, IndexError, TypeError):
                pass
        
        logger.warning("Could not extract sender_id from payload")
        return "unknown"
    
    @property
    def message_text(self) -> str:
        """
        Extract message text from various possible structures.
        
        Falls back to empty string for worker to handle.
        """
        # Try nested message structure
        if self.data and "message" in self.data:
            msg = self.data["message"]
            if isinstance(msg, dict):
                # Try different text field names
                for field in ["content", "text", "body"]:
                    if field in msg:
                        return msg[field]
        
        # Try entry pattern
        if self.entry and len(self.entry) > 0:
            try:
                first_entry = self.entry[0]
                if "changes" in first_entry and len(first_entry["changes"]) > 0:
                    change = first_entry["changes"][0]
                    if "value" in change and "text" in change["value"]:
                        return change["value"]["text"]
            except (KeyError, IndexError, TypeError):
                pass
        
        logger.warning("Could not extract message text from payload")
        return ""


# ============================================================================
# Webhook Verification (GET) - Required for TikTok webhook registration
# ============================================================================

@router.get("/tiktok")
async def tiktok_webhook_verify(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
) -> str:
    """
    TikTok webhook verification endpoint.
    
    TikTok sends a GET request with hub.mode=subscribe and hub.challenge
    to verify the webhook URL. We must echo back the challenge.
    
    Args:
        hub_mode: Should be "subscribe"
        hub_verify_token: Should match our configured token
        hub_challenge: The challenge string to echo back
    
    Returns:
        The hub_challenge string (required for verification)
    """
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    # Verify the mode is subscribe
    if hub_mode != "subscribe":
        logger.error(f"Invalid hub.mode: {hub_mode}")
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    # In production, verify the hub_verify_token matches your secret
    # For now, we accept any token (TikTok uses different verification methods)
    
    if not hub_challenge:
        logger.error("Missing hub.challenge")
        raise HTTPException(status_code=400, detail="Missing challenge")
    
    logger.info(f"Webhook verified! Echoing challenge: {hub_challenge}")
    return hub_challenge


# ============================================================================
# Webhook Endpoint (POST) - Receives TikTok events
# ============================================================================

@router.post("/tiktok")
async def tiktok_webhook(
    request: Request,
    x_tiktok_signature: str = Header(None, alias="X-TikTok-Signature")
) -> Dict[str, str]:
    """
    TikTok webhook endpoint with idempotency and signature validation.
    
    Phase 3 Flow:
        1. Read raw body (await request.body())
        2. Verify HMAC signature → 401 if invalid
        3. Parse JSON payload
        4. Check Redis idempotency → 200 if duplicate (stop retries)
        5. Dispatch to Celery worker
        6. Return 200 OK in <200ms
    
    Security:
        - HMAC-SHA256 signature validation (production)
        - Disabled in local for testing convenience
        - Constant-time comparison prevents timing attacks
    
    Performance:
        - Redis check adds <10ms (in-memory)
        - Celery dispatch is non-blocking
        - Total response time <200ms (TikTok requirement)
    """
    # Check if Redis/Celery are configured
    if not settings.REDIS_URL:
        logger.error("Webhook received but Redis not configured")
        raise HTTPException(status_code=503, detail="Service not fully configured")
    
    # Step 1: Read raw body for HMAC validation
    raw_body = await request.body()
    
    # Step 2: Verify HMAC signature
    if not settings.is_local:
        # Production: Strict validation
        if not verify_tiktok_signature(
            settings.TIKTOK_WEBHOOK_SECRET,
            x_tiktok_signature,
            raw_body
        ):
            logger.error("TikTok signature validation failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        # Local: Log but allow
        logger.info("Local environment: Skipping HMAC validation")
    
    # Step 3: Parse JSON payload
    try:
        payload_dict = await request.json()
        payload = TikTokWebhookPayload(**payload_dict)
    except Exception as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload format")
    
    # Extract event_id (required for idempotency)
    event_id = payload.event_id or f"unknown_{payload.timestamp}"
    
    # Step 4: Check idempotency (Redis fast path)
    try:
        is_duplicate = await check_and_set(event_id, ttl=600)
        if is_duplicate:
            logger.info(f"Duplicate event {event_id}, returning 200 OK")
            return {"status": "ok", "event_id": event_id, "duplicate": True}
    except Exception as e:
        # If Redis fails, log and proceed (fail-open)
        logger.error(f"Idempotency check failed: {str(e)}")
    
    # Step 5: Extract user_id and text (with flexible parsing)
    user_id = payload.sender_id
    text = payload.message_text
    
    # Step 6: Dispatch to Celery worker (non-blocking)
    try:
        # Pass raw payload as JSON string for worker debugging
        raw_payload_json = json.dumps(payload_dict)
        
        # Import here to avoid circular imports
        from app.worker.tasks import process_message
        
        process_message.delay(
            event_id=event_id,
            user_id=user_id,
            text=text,
            raw_payload=raw_payload_json
        )
        
        logger.info(f"Dispatched event {event_id} to worker (user: {user_id})")
    except Exception as e:
        logger.error(f"Failed to dispatch to Celery: {str(e)}")
        # Still return 200 OK to prevent TikTok retries
    
    # Step 7: Return 200 OK (fast response)
    return {"status": "ok", "event_id": event_id}
