"""
Domo Authentication Context for MCP Server

Provides lifespan management for DomoAuth instances, ensuring proper
initialization and cleanup of authentication resources.
"""

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

from domolibrary2.auth import DomoTokenAuth


@dataclass
class DomoContext:
    """Context containing Domo authentication for MCP tools.

    Attributes:
        auth: The DomoTokenAuth instance for API calls
        domo_instance: The Domo instance name
    """

    auth: DomoTokenAuth
    domo_instance: str


class DomoAuthError(Exception):
    """Raised when Domo authentication fails or is misconfigured."""

    pass


def get_auth_from_env() -> DomoTokenAuth:
    """Create DomoTokenAuth from environment variables.

    Environment Variables:
        DOMO_INSTANCE: The Domo instance name (required)
        DOMO_ACCESS_TOKEN: The Domo access token (required)

    Returns:
        DomoTokenAuth: Configured authentication instance

    Raises:
        DomoAuthError: If required environment variables are missing
    """
    domo_instance = os.environ.get("DOMO_INSTANCE")
    domo_access_token = os.environ.get("DOMO_ACCESS_TOKEN")

    if not domo_instance:
        raise DomoAuthError(
            "DOMO_INSTANCE environment variable is required. "
            "Set it to your Domo instance name (e.g., 'mycompany')."
        )

    if not domo_access_token:
        raise DomoAuthError(
            "DOMO_ACCESS_TOKEN environment variable is required. "
            "Generate an access token from Admin > Access Tokens in Domo."
        )

    return DomoTokenAuth(
        domo_instance=domo_instance,
        domo_access_token=domo_access_token,
    )


@asynccontextmanager
async def domo_lifespan(server):
    """Async context manager for Domo authentication lifespan.

    This is used by FastMCP to manage authentication during server lifecycle.
    Authentication is initialized on startup and can be cleaned up on shutdown.

    Args:
        server: The FastMCP server instance

    Yields:
        DomoContext: Context with authenticated Domo client

    Raises:
        DomoAuthError: If authentication setup fails
    """
    auth = get_auth_from_env()

    try:
        yield DomoContext(
            auth=auth,
            domo_instance=auth.domo_instance,
        )
    finally:
        # DomoTokenAuth doesn't maintain persistent connections that need cleanup.
        # If httpx sessions were opened by tools, they are managed per-request.
        pass
