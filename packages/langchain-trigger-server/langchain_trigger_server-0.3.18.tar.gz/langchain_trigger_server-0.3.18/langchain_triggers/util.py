"""Utility functions for trigger handlers."""

import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt


def get_x_service_jwt_token(
    payload: dict[str, Any] | None = None, expiration_seconds: int = 60 * 60
) -> str:
    """Create X-Service-Key JWT token for service-to-service authentication.

    Args:
        payload: Optional payload to include in JWT
        expiration_seconds: Token expiration time in seconds (default 1 hour)

    Returns:
        JWT token string
    """
    exp_datetime = datetime.now(tz=UTC) + timedelta(seconds=expiration_seconds)
    exp = int(exp_datetime.timestamp())

    payload = payload or {}
    payload = {
        "sub": "unspecified",
        "exp": exp,
        **payload,
    }

    secret = os.environ["X_SERVICE_AUTH_JWT_SECRET"]

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )


def create_service_auth_headers(user_id: str, tenant_id: str) -> dict[str, str]:
    """Create authentication headers with X-Service-Key JWT token.

    Args:
        user_id: User ID for the request
        tenant_id: Tenant ID for the request

    Returns:
        Dictionary of authentication headers
    """
    headers = {
        "x-api-key": "",
        "x-auth-scheme": "langsmith-agent",
        "x-user-id": user_id,
        "x-tenant-id": tenant_id,
        "x-service-key": get_x_service_jwt_token(
            payload={
                "tenant_id": tenant_id,
                "user_id": user_id,
            }
        ),
    }

    return headers


def get_langgraph_url(registration: dict[str, Any]) -> str:
    """Get the LangGraph API URL for a given registration
    by comparing the registration's organization ID to the
    LANGCHAIN_ORGANIZATION_ID setting."""
    reg_organization_id = str(registration.get("organization_id"))

    langgraph_api_url = os.getenv("LANGGRAPH_API_URL", "http://localhost:2024")
    langgraph_api_url_public = os.getenv(
        "LANGGRAPH_API_URL_PUBLIC", "http://localhost:2024"
    )
    langchain_organization_id = os.getenv(
        "LANGCHAIN_ORGANIZATION_ID", "f5c798a2-2155-4999-ad27-6d466bd26e1c"
    )

    return (
        langgraph_api_url
        if reg_organization_id == langchain_organization_id
        else langgraph_api_url_public
    )
