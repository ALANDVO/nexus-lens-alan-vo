"""OIDC Keycloak SSO authentication tests.

Targeted tests for the /auth callback route, verifying:
- Error parameter handling
- Missing authorization code detection
- State parameter verification
"""

from fastapi.testclient import TestClient
from app.main import create_app


def test_callback_handles_error_param():
    """Callback should return 400 with Keycloak error detail."""
    app = create_app()
    client = TestClient(app, follow_redirects=False)
    resp = client.get("/auth/callback?error=access_denied", follow_redirects=False)
    assert resp.status_code == 400
    assert "Keycloak error: access_denied" in resp.json()["detail"]


def test_callback_requires_code():
    """Callback should return 400 when authorization code is missing."""
    app = create_app()
    client = TestClient(app, follow_redirects=False)
    resp = client.get("/auth/callback?state=test", follow_redirects=False)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Missing authorization code"


def test_callback_validates_state():
    """Callback should return 400 when state parameter doesn't match session."""
    app = create_app()
    client = TestClient(app, follow_redirects=False)
    resp = client.get("/auth/callback?code=test&state=wrongstate", follow_redirects=False)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid state parameter"


def test_login_generates_pkce():
    """Login should redirect to Keycloak with PKCE parameters."""
    app = create_app()
    client = TestClient(app, follow_redirects=False)
    resp = client.get("/auth/login", follow_redirects=False)
    assert resp.status_code == 307
    location = resp.headers["location"]
    assert "response_type=code" in location
    assert "client_id=nexus-lens-frontend" in location
    assert "redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fauth%2Fcallback" in location
    assert "code_challenge" in location
    assert "code_challenge_method=S256" in location
    assert "state=" in location
