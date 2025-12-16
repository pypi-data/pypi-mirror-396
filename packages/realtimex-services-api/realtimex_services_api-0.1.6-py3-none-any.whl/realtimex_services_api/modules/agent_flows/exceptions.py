"""
Agent Flows exception helpers.

Provides helpers to create FastAPI HTTP exceptions with a consistent
error payload structure used across the Agent Flows module.
"""

from typing import Any

from fastapi import HTTPException

_DEFAULT_ERROR_CODES: dict[int, str] = {
    400: "INVALID_INPUT",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "UNPROCESSABLE_ENTITY",
    500: "INTERNAL_ERROR",
}


def agent_flows_http_exception(
    status_code: int,
    *,
    code: str | None = None,
    message: str,
    details: dict[str, Any] | None = None,
) -> HTTPException:
    """
    Create an HTTPException with a structured error payload.

    Args:
        status_code: HTTP status code to return.
        code: Optional machine-friendly error code. Falls back to a default
            mapping based on the status code when omitted.
        message: Human-readable explanation of the error.
        details: Optional structured payload with additional context.
    """
    payload: dict[str, Any] = {
        "code": code or _DEFAULT_ERROR_CODES.get(status_code, "ERROR"),
        "message": message,
    }

    if details:
        payload["details"] = details

    return HTTPException(status_code=status_code, detail=payload)


def extract_error_payload(
    exc: HTTPException,
) -> tuple[str, str, dict[str, Any] | None]:
    """Derive code/message/details tuple from an HTTPException detail payload."""
    detail = exc.detail

    if isinstance(detail, dict):
        code = detail.get("code") or _DEFAULT_ERROR_CODES.get(exc.status_code, "ERROR")
        message = str(detail.get("message", ""))
        details = detail.get("details")
        return code, message, details if isinstance(details, dict) else None

    message = str(detail)
    return (
        _DEFAULT_ERROR_CODES.get(exc.status_code, "ERROR"),
        message,
        None,
    )
