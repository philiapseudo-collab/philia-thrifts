"""
Celery tasks for processing TikTok webhook events.

Integrated with AI Agent, User Service, and Idempotency logging.
"""
import asyncio
import httpx
import json
import logging
from typing import Dict
from datetime import datetime
from app.worker.celery_app import celery_app
from app.db.database import async_session_maker
from app.db.models import IdempotencyLog
from app.clients.tiktok import TikTokClient
from app.services.ai_agent import AIAgent
from app.services.users import get_or_create_user

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.process_message", bind=True, max_retries=3)
def process_message(
    self,
    event_id: str,
    user_id: str,
    text: str,
    raw_payload: str  # JSON string from webhook
) -> Dict[str, str]:
    """
    Process incoming TikTok message with AI agent.
    
    Flow:
        1. Log raw payload (debugging)
        2. Track user (48h window management)
        3. Run AI conversation
        4. Save IdempotencyLog (audit trail)
    
    Args:
        self: Celery task instance (bind=True)
        event_id: TikTok event identifier
        user_id: TikTok user OpenID
        text: Message content
        raw_payload: Complete webhook payload as JSON string
    
    Returns:
        Status dictionary for Celery result backend
    """
    # Check if database is configured
    if async_session_maker is None:
        logger.error("Cannot process message: Database not configured")
        return {"status": "error", "reason": "database_not_configured"}
    
    logger.info(f"Processing event {event_id} from user {user_id}")
    
    # Run async processing logic
    try:
        result = asyncio.run(_async_process_message(event_id, user_id, text, raw_payload))
        return result
    except Exception as e:
        logger.error(f"Failed to process event {event_id}: {str(e)}", exc_info=True)
        # Retry on transient errors
        raise self.retry(exc=e, countdown=5)


async def _async_process_message(
    event_id: str,
    user_id: str,
    text: str,
    raw_payload: str
) -> Dict[str, str]:
    """
    Async message processing logic.
    
    Separated from sync Celery task for clean async/await usage.
    """
    # Step 1: Log raw payload for debugging
    logger.info("="*60)
    logger.info(f"RAW WEBHOOK PAYLOAD (event {event_id}):")
    logger.info("-"*60)
    try:
        payload_dict = json.loads(raw_payload)
        logger.info(json.dumps(payload_dict, indent=2))
    except json.JSONDecodeError:
        logger.info(raw_payload)
    logger.info("="*60)
    
    # Step 2: Initialize async database session with transaction
    async with async_session_maker() as session:
        async with session.begin():  # Auto-commit on success
            
            # Step 3: User Management (Track 48h window)
            try:
                user = await get_or_create_user(
                    tiktok_id=user_id,
                    username=None,  # Can extract from payload later
                    session=session
                )
                logger.info(
                    f"User {user.tiktok_id} tracked "
                    f"(last interaction: {user.last_interaction_at})"
                )
            except Exception as e:
                logger.error(f"Failed to track user: {str(e)}", exc_info=True)
                # Continue processing despite user error
            
            # Step 4: Log message details
            logger.info(f"Processing message from {user_id}: '{text[:100]}'")
            
            # Step 5: AI Agent Logic
            try:
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    # Initialize TikTok client
                    tiktok = TikTokClient(http_client)
                    
                    # Initialize AI agent
                    agent = AIAgent(tiktok)
                    
                    # Handle conversation (AI → OpenAI → Inventory → TikTok)
                    await agent.handle_conversation(user_id, text, session)
                    
                    logger.info("✅ AI conversation completed successfully")
            
            except Exception as e:
                logger.error(f"AI agent error: {str(e)}", exc_info=True)
                # Continue to idempotency log even if AI fails
            
            # Step 6: Audit Log (Idempotency)
            try:
                idempotency_log = IdempotencyLog(
                    event_id=event_id,
                    processed_at=datetime.utcnow(),
                    status="success"
                )
                session.add(idempotency_log)
                logger.info(f"Saved IdempotencyLog for event {event_id}")
            except Exception as e:
                logger.error(f"Failed to save IdempotencyLog: {str(e)}", exc_info=True)
                # Continue even if logging fails
    
    logger.info(f"✅ Successfully processed event {event_id}")
    return {"status": "success", "event_id": event_id, "user_id": user_id}
