# src/anypoint_sdk/auth.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from ._http import HttpClient


@dataclass(frozen=True)
class TokenAuth:
    """Holds a bearer token and produces the HTTP auth header."""

    token: str

    def as_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[str] = None
    scope: Optional[str] = None


def get_token_with_client_credentials(
    http: HttpClient,
    client_id: str,
    client_secret: str,
) -> TokenResponse:
    """
    Exchange client credentials for an Anypoint access token.
    Docs: https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token
    """

    payload: dict[str, Any] = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    r = http.post_json("/accounts/api/v2/oauth2/token", json_body=payload)
    data = r.json() or {}
    token = data.get("access_token")
    if not token:
        raise ValueError("Token response missing access_token")
    return TokenResponse(
        access_token=token,
        token_type=data.get("token_type", "bearer"),
        expires_in=data.get("expires_in"),
        scope=data.get("scope"),
    )
