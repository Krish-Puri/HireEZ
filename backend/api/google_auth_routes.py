"""
Google OAuth Routes

Handles OAuth flow for Google Calendar API and Meet link generation.
"""

from fastapi import APIRouter, Query
from backend.config import config

router = APIRouter(prefix="/google", tags=["Google"])

SCOPES = "https://www.googleapis.com/auth/calendar.events"


@router.get("/oauth/login")
async def google_oauth_login():
    """Return Google OAuth consent URL for the frontend to display."""
    import urllib.parse
    params = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return {"auth_url": url}


@router.get("/oauth/callback")
async def google_oauth_callback(code: str = Query(...)):
    """Exchange auth code for access token."""
    import httpx
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data)
    if resp.status_code == 200:
        token_data = resp.json()
        return {
            "success": True,
            "access_token": token_data.get("access_token"),
        }
    return {"success": False, "error": resp.text}
