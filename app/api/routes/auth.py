"""TikTok OAuth authentication endpoints."""
import logging
from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/tiktok/callback")
async def tiktok_oauth_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
) -> Dict:
    """
    TikTok OAuth callback endpoint.
    
    This is where TikTok redirects users after they authorize your app.
    The 'code' parameter is used to exchange for an access token.
    
    Args:
        code: Authorization code from TikTok
        state: CSRF protection state (should match what you sent)
        error: Error code if authorization failed
        error_description: Human-readable error description
    
    Returns:
        JSON response indicating success or failure
    """
    # Handle errors from TikTok
    if error:
        logger.error(f"TikTok OAuth error: {error} - {error_description}")
        raise HTTPException(
            status_code=400, 
            detail=f"OAuth error: {error} - {error_description}"
        )
    
    if not code:
        logger.error("No authorization code received from TikTok")
        raise HTTPException(
            status_code=400, 
            detail="No authorization code received"
        )
    
    logger.info(f"Received TikTok OAuth callback with code (state: {state})")
    
    # In a full implementation, you would:
    # 1. Verify the state matches what you sent (CSRF protection)
    # 2. Exchange the code for an access token
    # 3. Store the tokens securely
    # 4. Redirect user to success page or app
    
    # For now, return success (tokens are already configured in Railway)
    return {
        "status": "success",
        "message": "OAuth callback received successfully",
        "code_received": bool(code),
        "state": state,
        "note": "Your access token is already configured in Railway environment variables"
    }


@router.get("/tiktok/login")
async def tiktok_oauth_login() -> RedirectResponse:
    """
    Initiate TikTok OAuth login flow.
    
    Redirects user to TikTok authorization page.
    """
    # Build TikTok OAuth URL
    # Note: TikTok uses different OAuth endpoints depending on your app type
    # This is for TikTok Login for Business/Developers
    
    oauth_url = "https://www.tiktok.com/auth/authorize/"
    
    params = {
        "client_key": settings.TIKTOK_CLIENT_KEY,
        "redirect_uri": "https://web-production-ec3c.up.railway.app/auth/tiktok/callback",
        "scope": "user.info.basic,video.list,messaging",
        "response_type": "code",
        "state": "philia_thrifts_csrf_token"  # In production, generate random state
    }
    
    # Build query string
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{oauth_url}?{query}"
    
    logger.info(f"Redirecting to TikTok OAuth: {oauth_url}")
    return RedirectResponse(url=full_url)


@router.get("/tiktok/status")
async def tiktok_auth_status() -> Dict:
    """
    Check TikTok authentication status.
    
    Returns current configuration status without exposing secrets.
    """
    return {
        "configured": all([
            settings.TIKTOK_CLIENT_KEY,
            settings.TIKTOK_CLIENT_SECRET,
            settings.TIKTOK_ACCESS_TOKEN
        ]),
        "client_key_set": bool(settings.TIKTOK_CLIENT_KEY),
        "access_token_set": bool(settings.TIKTOK_ACCESS_TOKEN),
        "webhook_configured": bool(settings.TIKTOK_WEBHOOK_SECRET),
        "callback_url": "https://web-production-ec3c.up.railway.app/auth/tiktok/callback"
    }
