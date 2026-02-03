"""
Security utilities for webhook validation and authentication.
"""
import hmac
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def verify_tiktok_signature(
    client_secret: Optional[str],
    signature: Optional[str],
    raw_body: bytes
) -> bool:
    """
    Verify TikTok webhook HMAC signature.
    
    TikTok Security:
    - Uses HMAC-SHA256 with client_secret as key
    - Sends signature in X-TikTok-Signature header
    - Standard hex digest format (no prefix)
    
    Args:
        client_secret: TikTok webhook secret from settings (may be None)
        signature: X-TikTok-Signature header value (may be None)
        raw_body: Raw request body bytes (MUST be original, un-parsed bytes)
    
    Returns:
        True if signature is valid, False otherwise
    
    Security Notes:
    - Uses hmac.compare_digest() to prevent timing attacks
    - Handles missing/malformed signatures gracefully
    - Logs warnings for debugging (but not secrets)
    
    Example:
        >>> body = b'{"event":"message.received","event_id":"123"}'
        >>> secret = "my_webhook_secret"
        >>> sig = "abc123..."  # From X-TikTok-Signature header
        >>> is_valid = verify_tiktok_signature(secret, sig, body)
    """
    # Handle missing secret
    if client_secret is None or client_secret == "":
        logger.warning("TikTok webhook secret not configured")
        return False
    
    # Handle missing signature
    if signature is None or signature == "":
        logger.warning("Missing X-TikTok-Signature header")
        return False
    
    # Handle malformed signature (basic validation)
    if not isinstance(signature, str):
        logger.warning(f"Invalid signature type: {type(signature)}")
        return False
    
    try:
        # Compute expected signature
        # TikTok uses standard HMAC-SHA256 with hex digest
        expected_signature = hmac.new(
            key=client_secret.encode('utf-8'),
            msg=raw_body,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison (prevents timing attacks)
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if not is_valid:
            logger.warning(
                "TikTok signature mismatch. "
                f"Expected length: {len(expected_signature)}, "
                f"Received length: {len(signature)}"
            )
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying TikTok signature: {str(e)}", exc_info=True)
        return False
