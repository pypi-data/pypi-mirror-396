# gate/ext/google_oauth.py

"""Client for the hosted Revert auth service.

This module intentionally avoids handling Google OAuth client secrets locally.
Instead, it delegates OAuth to the hosted service running at AUTH_SERVICE_BASE.
"""

import os
import requests

AUTH_SERVICE_BASE = os.getenv("AUTH_SERVICE_BASE", "https://auth.revertly.app")
AUTH_STATE = os.getenv("AUTH_STATE", "gateway-local")


def _auth_service_url(path: str) -> str:
    return f"{AUTH_SERVICE_BASE.rstrip('/')}{path}"


def get_auth_url() -> str:
    """Return a Google OAuth URL from the hosted auth service for this gateway."""
    resp = requests.get(
        _auth_service_url("/oauth/google/url"),
        params={"state": AUTH_STATE},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    url = data.get("auth_url")
    if not url:
        raise RuntimeError("Auth service did not return auth_url")
    return url


def _fetch_access_token() -> str:
    """Fetch a valid Google access token for this gateway from the auth service."""
    resp = requests.post(
        _auth_service_url("/oauth/google/access_token"),
        params={"state": AUTH_STATE},
        timeout=10,
    )

    # The auth service returns HTTP 400 when the gateway is not authorized or
    # when tokens are invalid/expired.
    if resp.status_code == 400:
        raise RuntimeError(resp.text or "No valid Google access token; authorize first")

    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Auth service did not return access_token")
    return token


def load_tokens():
    """Backwards-compatible helper used by the gateway to check auth status.

    Returns a minimal dict containing an access_token if one can be fetched,
    or None otherwise.
    """
    try:
        token = _fetch_access_token()
        return {"access_token": token}
    except Exception:
        return None


def get_auth_headers() -> dict:
    """Return Authorization headers for Google APIs using the auth service."""
    token = _fetch_access_token()
    return {"Authorization": f"Bearer {token}"}
