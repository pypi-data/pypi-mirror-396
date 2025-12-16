"""
Access Token Management Tools for Domo MCP Server

Provides tools for managing access tokens in Domo including listing, generating,
and revoking tokens for API authentication.
"""

import datetime as dt

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp
from domolibrary2.routes import access_token as token_routes


class AccessToken(BaseModel):
    """Structured output for Domo access token data."""

    id: int = Field(description="Access token ID")
    name: str = Field(description="Token name")
    owner_id: str = Field(description="Owner user ID")
    owner_name: str | None = Field(default=None, description="Owner display name")
    expires: str | None = Field(default=None, description="Expiration date/time")
    is_expired: bool | None = Field(
        default=None, description="Whether token is expired"
    )


class AccessTokenList(BaseModel):
    """Structured output for list of access tokens."""

    tokens: list[AccessToken] = Field(description="List of access tokens")
    total_count: int = Field(description="Total number of tokens returned")
    expired_count: int = Field(
        default=0, description="Number of expired tokens in the list"
    )


class GeneratedToken(BaseModel):
    """Structured output for a newly generated access token."""

    id: int = Field(description="Access token ID")
    name: str = Field(description="Token name")
    token: str = Field(description="The actual token value (store securely!)")
    owner_id: str = Field(description="Owner user ID")
    expires: str | None = Field(default=None, description="Expiration date/time")


def _parse_token(data: dict) -> AccessToken:
    """Parse access token data from API response."""
    expires = data.get("expires")
    is_expired = None

    if expires:
        now = dt.datetime.now(dt.UTC)
        if isinstance(expires, dt.datetime):
            # Ensure timezone-aware comparison
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=dt.UTC)
            is_expired = expires < now
            expires = expires.isoformat()
        elif isinstance(expires, int | float):
            # Unix timestamps are typically UTC
            expires_dt = dt.datetime.fromtimestamp(expires / 1000, tz=dt.UTC)
            is_expired = expires_dt < now
            expires = expires_dt.isoformat()

    owner = data.get("owner", {}) or {}

    return AccessToken(
        id=data.get("id", 0),
        name=data.get("name", ""),
        owner_id=str(owner.get("id", data.get("ownerId", ""))),
        owner_name=owner.get("name") or owner.get("displayName"),
        expires=expires,
        is_expired=is_expired,
    )


@mcp.tool()
async def get_access_tokens(
    ctx: Context[ServerSession, DomoContext],
    include_expired: bool = Field(
        default=True, description="Whether to include expired tokens"
    ),
) -> AccessTokenList:
    """List all access tokens in the Domo instance.

    Returns a list of all access tokens with their metadata including
    name, owner, expiration date, and whether they are expired.

    Args:
        include_expired: Whether to include expired tokens (default: True)
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching access tokens from {auth.domo_instance}")

    try:
        res = await token_routes.get_access_tokens(auth=auth)
        tokens_data = res.response or []

        tokens = [_parse_token(t) for t in tokens_data]

        # Count expired tokens
        expired_count = sum(1 for t in tokens if t.is_expired)

        # Filter out expired if requested
        if not include_expired:
            tokens = [t for t in tokens if not t.is_expired]

        await ctx.info(f"Found {len(tokens)} tokens ({expired_count} expired)")
        return AccessTokenList(
            tokens=tokens,
            total_count=len(tokens),
            expired_count=expired_count,
        )

    except token_routes.AccessToken_GET_Error as e:
        await ctx.error(f"Failed to get access tokens: {e}")
        raise


@mcp.tool()
async def get_expired_access_tokens(
    ctx: Context[ServerSession, DomoContext],
) -> AccessTokenList:
    """Get only expired access tokens.

    Returns a list of access tokens that have passed their expiration date.
    Useful for identifying tokens that need to be revoked or renewed.
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching expired access tokens from {auth.domo_instance}")

    try:
        res = await token_routes.get_access_tokens(auth=auth)
        tokens_data = res.response or []

        tokens = [_parse_token(t) for t in tokens_data]

        # Filter to only expired tokens
        expired_tokens = [t for t in tokens if t.is_expired]

        await ctx.info(f"Found {len(expired_tokens)} expired tokens")
        return AccessTokenList(
            tokens=expired_tokens,
            total_count=len(expired_tokens),
            expired_count=len(expired_tokens),
        )

    except token_routes.AccessToken_GET_Error as e:
        await ctx.error(f"Failed to get access tokens: {e}")
        raise


@mcp.tool()
async def generate_access_token(
    token_name: str,
    user_id: str,
    ctx: Context[ServerSession, DomoContext],
    duration_days: int = Field(
        default=90, description="Number of days until token expires"
    ),
) -> GeneratedToken:
    """Generate a new access token for a user.

    Creates a new access token with the specified name and expiration period.
    The token can be used for API authentication.

    IMPORTANT: The token value is only returned once - store it securely!

    Args:
        token_name: Descriptive name for the new access token
        user_id: User ID who will own the token
        duration_days: Number of days until token expires (default: 90)
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Generating access token '{token_name}' for user {user_id}")

    try:
        res = await token_routes.generate_access_token(
            auth=auth,
            token_name=token_name,
            user_id=user_id,
            duration_in_days=duration_days,
        )
        token_data = res.response

        expires = token_data.get("expires")
        if isinstance(expires, int | float):
            expires = dt.datetime.fromtimestamp(expires / 1000).isoformat()

        await ctx.info(f"Generated access token ID: {token_data.get('id')}")
        return GeneratedToken(
            id=token_data.get("id", 0),
            name=token_data.get("name", token_name),
            token=token_data.get("token", ""),
            owner_id=str(user_id),
            expires=expires,
        )

    except token_routes.AccessToken_CRUD_Error as e:
        await ctx.error(f"Failed to generate access token: {e}")
        raise


@mcp.tool()
async def revoke_access_token(
    access_token_id: int,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Revoke an existing access token.

    Permanently revokes an access token, making it immediately unusable.
    This action cannot be undone.

    Args:
        access_token_id: The ID of the access token to revoke
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Revoking access token {access_token_id}")

    try:
        await token_routes.revoke_access_token(
            auth=auth, access_token_id=access_token_id
        )
        await ctx.info(f"Revoked access token {access_token_id}")
        return f"Successfully revoked access token {access_token_id}"

    except token_routes.AccessToken_CRUD_Error as e:
        await ctx.error(f"Failed to revoke access token: {e}")
        raise


@mcp.tool()
async def revoke_expired_tokens(
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Revoke all expired access tokens.

    Finds and revokes all access tokens that have passed their expiration date.
    Returns a summary of the revocation results.
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info("Finding and revoking expired access tokens")

    try:
        # Get all tokens
        res = await token_routes.get_access_tokens(auth=auth)
        tokens_data = res.response or []

        tokens = [_parse_token(t) for t in tokens_data]
        expired_tokens = [t for t in tokens if t.is_expired]

        if not expired_tokens:
            await ctx.info("No expired tokens found")
            return "No expired tokens found to revoke"

        revoked_count = 0
        failed_count = 0

        for token in expired_tokens:
            try:
                await token_routes.revoke_access_token(
                    auth=auth, access_token_id=token.id
                )
                revoked_count += 1
                await ctx.info(f"Revoked expired token: {token.name} (ID: {token.id})")
            except token_routes.AccessToken_CRUD_Error:
                failed_count += 1
                await ctx.warning(
                    f"Failed to revoke token: {token.name} (ID: {token.id})"
                )

        result = f"Revoked {revoked_count} expired tokens"
        if failed_count > 0:
            result += f" ({failed_count} failed)"

        await ctx.info(result)
        return result

    except token_routes.AccessToken_GET_Error as e:
        await ctx.error(f"Failed to get access tokens: {e}")
        raise
