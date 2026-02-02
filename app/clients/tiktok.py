"""
TikTok Business Messaging API client (Simplified for MVP).
"""
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class TikTokClient:
    """
    Simplified TikTok client for message sending.
    
    Features:
    - Graceful failure on auth errors (401/403)
    - Retry on rate limits (429) and server errors (5xx)
    - Clean error logging
    """
    
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.url = settings.TIKTOK_MESSAGING_API_BASE_URL
        self.access_token = settings.TIKTOK_ACCESS_TOKEN
        self.business_id = settings.TIKTOK_BUSINESS_ID 

    async def send_message(self, recipient_id: str, text: str):
        """
        Sends a text message to a TikTok user.
        
        Args:
            recipient_id: TikTok user OpenID
            text: Message content
        
        Returns:
            Response JSON on success, None on graceful failure
        
        Raises:
            HTTPStatusError: On 429 or 5xx (triggers Celery retry)
        """
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }

        payload = {
            "business_id": self.business_id,
            "recipient_id": recipient_id,
            "message_type": "text",
            "content": {"text": text}
        }

        try:
            response = await self.client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"✅ Message sent to {recipient_id}: {response.status_code}")
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code in [401, 403]:
                # Auth errors - graceful fail (don't crash worker)
                logger.critical(f"TikTok Auth Error: {e.response.text}")
                return None
                
            elif e.response.status_code == 429 or e.response.status_code >= 500:
                # Rate limit or server error - retry
                logger.warning(f"TikTok Temporary Error: {e.response.status_code}")
                raise e  # Trigger Celery retry
                
            else:
                # Other client errors - log and fail gracefully
                logger.error(f"TikTok Client Error: {e.response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Unknown TikTok error: {e}")
            raise
