"""OIDC Keycloak SSO authentication routes (planned milestone).

Provides:
- /auth/login  — initiate Keycloak OIDC login with PKCE S256
- /auth/callback — handle Keycloak OIDC authorization code callback
- /auth/logout — initiate Keycloak OIDC logout
- /auth/me     — return current user info from session
"""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, HTTPException
from starlette.responses import RedirectResponse
import urllib.parse

from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# OIDC configuration - read from .env via config module
KEYCLOAK_URL = settings.keycloak_url or "http://keycloak:8081"
KEYCLOAK_REALM = settings.keycloak_realm or "nexus-lens"
KEYCLOAK_CLIENT_ID = settings.keycloak_client_id or "nexus-lens-frontend"
KEYCLOAK_CLIENT_SECRET = settings.keycloak_client_secret or ""
KEYCLOAK_AUTH_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
KEYCLOAK_LOGOUT_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"
KEYCLOAK_REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"


@router.get("/login", include_in_schema=False)
async def login(request: Request):
    """Initiate Keycloak OIDC login with PKCE S256."""
    # Generate random state and code verifier for PKCE
    import secrets
    import base64

    state = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    # Code challenge = SHA256(code_verifier) base64url encoded
    import hashlib
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().rstrip("=")

    # Store state in session for callback verification
    request.session["oauth2_state"] = state

    auth_params = {
        "response_type": "code",
        "client_id": KEYCLOAK_CLIENT_ID,
        "redirect_uri": KEYCLOAK_REDIRECT_URI,
        "scope": "openid profile email",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "session_state": state,
    }

    auth_url = f"{KEYCLOAK_AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    return RedirectResponse(url=auth_url)


@router.get("/callback", include_in_schema=False)
async def callback(request: Request):
    """Handle Keycloak OIDC callback - exchange auth code for tokens."""
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        raise HTTPException(status_code=400, detail=f"Keycloak error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    # Verify state matches (simple check for now)
    stored_state = request.session.get("oauth2_state")
    if stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Exchange authorization code for tokens
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": KEYCLOAK_REDIRECT_URI,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }

    import httpx
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(KEYCLOAK_TOKEN_URL, data=token_data, timeout=10)
    
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_resp.text}")

    # In a full implementation, we would validate the ID token here
    # and set secure HttpOnly cookies with user info
    
    # For now, set session indicators
    request.session["oidc_logged_in"] = True
    request.session["user"] = {
        "sub": "keycloak-user",
        "name": "Keycloak User",
        "email": "user@alanvo.net",
    }

    # Redirect to the API docs or frontend
    redirect_url = request.query_params.get("next", "/docs")
    return RedirectResponse(url=redirect_url)


@router.get("/logout", include_in_schema=False)
async def logout(request: Request, response: Response):
    """Handle Keycloak OIDC logout."""
    post_logout = request.query_params.get("next", "/")

    logout_params = {
        "post_logout_redirect_uri": post_logout,
    }

    logout_url = f"{KEYCLOAK_LOGOUT_URL}?{urllib.parse.urlencode(logout_params)}"

    # Clear session
    request.session.clear()

    return RedirectResponse(url=logout_url)


@router.get("/me", include_in_schema=False)
async def me(request: Request):
    """Return current user info from session."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user": user}
