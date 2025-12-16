"""
Shared dependencies for the Agent Flows module.

Contains utilities for extracting authentication context such as the KC user id
from incoming requests.
"""

import base64
import json
from typing import Any, TypedDict

from fastapi import Header

from .exceptions import agent_flows_http_exception


class AuthContext(TypedDict):
    """Authentication context extracted from the Authorization header."""

    token: str
    kc_user_id: str


def _extract_bearer_token(authorization: str | None) -> str:
    """Extract the Bearer token from an Authorization header."""
    if not authorization:
        raise agent_flows_http_exception(
            status_code=401, message="Authorization header is required"
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise agent_flows_http_exception(
            status_code=401,
            message="Authorization header must use the Bearer schema",
        )

    token = parts[1].strip()
    if not token:
        raise agent_flows_http_exception(
            status_code=401, message="Bearer token is missing"
        )

    return token


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    """Decode a JWT payload without signature verification."""
    try:
        segments = token.split(".")
        if len(segments) < 2:
            raise ValueError("Token must contain header and payload segments")

        payload_segment = segments[1]
        padding = "=" * (-len(payload_segment) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_segment + padding)
        payload = json.loads(decoded_bytes)
    except (ValueError, json.JSONDecodeError) as exc:
        raise agent_flows_http_exception(
            status_code=401, message="Invalid access token"
        ) from exc

    if not isinstance(payload, dict):
        raise agent_flows_http_exception(
            status_code=401, message="Invalid access token payload"
        )

    return payload


async def get_auth_context(
    authorization: str = Header(..., description="Bearer access token"),
) -> AuthContext:
    """
    Resolve authentication context from Authorization header.

    Extracts the raw token and Keycloak user identifier (KC user ID).
    """
    token = _extract_bearer_token(authorization)
    payload = _decode_jwt_payload(token)

    kc_user_id = str(payload.get("sub") or payload.get("user_id") or "").strip()
    if not kc_user_id:
        raise agent_flows_http_exception(
            status_code=401,
            message="Unable to determine user identity from access token",
        )

    return {"token": token, "kc_user_id": kc_user_id}
