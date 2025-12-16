"""
Page/Dashboard Tools for Domo MCP Server

Provides tools for managing pages and dashboards in Domo including
listing, viewing details, and managing access.
"""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp
from domolibrary2.routes import page as page_routes


class DomoPage(BaseModel):
    """Structured output for Domo page/dashboard data."""

    id: str = Field(description="Page ID")
    name: str = Field(description="Page name")
    description: str | None = Field(default=None, description="Page description")
    owner_id: str | None = Field(default=None, description="Owner user ID")
    parent_page_id: str | None = Field(
        default=None, description="Parent page ID if nested"
    )
    card_count: int | None = Field(
        default=None, description="Number of cards on the page"
    )
    is_locked: bool | None = Field(default=None, description="Whether page is locked")


class PageList(BaseModel):
    """Structured output for list of pages."""

    pages: list[DomoPage] = Field(description="List of Domo pages")
    total_count: int = Field(description="Total number of pages returned")


class PageAccess(BaseModel):
    """Structured output for page access information."""

    page_id: str = Field(description="Page ID")
    page_name: str = Field(description="Page name")
    user_ids: list[str] = Field(description="List of user IDs with access")
    group_ids: list[str] = Field(description="List of group IDs with access")
    total_users: int = Field(description="Total users with access")
    total_groups: int = Field(description="Total groups with access")


def _parse_page(data: dict) -> DomoPage:
    """Parse page data from API response."""
    return DomoPage(
        id=str(data.get("id", "")),
        name=data.get("name", data.get("title", "")),
        description=data.get("description"),
        owner_id=str(data.get("ownerId", "")) if data.get("ownerId") else None,
        parent_page_id=(
            str(data.get("parentPageId", "")) if data.get("parentPageId") else None
        ),
        card_count=data.get("cardCount"),
        is_locked=data.get("locked"),
    )


@mcp.tool()
async def get_pages(
    ctx: Context[ServerSession, DomoContext],
    limit: int = Field(default=500, description="Maximum number of pages to return"),
) -> PageList:
    """List all pages/dashboards in the Domo instance.

    Returns a list of all pages visible to the authenticated user with their
    basic information including ID, name, owner, and card count.
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching pages from {auth.domo_instance}")

    try:
        res = await page_routes.get_pages_adminsummary(auth=auth)
        pages_data = res.response or []

        # Apply limit
        pages_data = pages_data[:limit]

        pages = [_parse_page(p) for p in pages_data]

        await ctx.info(f"Found {len(pages)} pages")
        return PageList(pages=pages, total_count=len(pages))

    except page_routes.Page_GET_Error as e:
        await ctx.error(f"Failed to get pages: {e}")
        raise


@mcp.tool()
async def get_page_by_id(
    page_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> DomoPage:
    """Get details for a specific page/dashboard.

    Args:
        page_id: The unique identifier of the page
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching page {page_id}")

    try:
        res = await page_routes.get_page_by_id(auth=auth, page_id=page_id)
        return _parse_page(res.response)

    except page_routes.Page_GET_Error as e:
        await ctx.error(f"Failed to get page {page_id}: {e}")
        raise


@mcp.tool()
async def get_page_access(
    page_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> PageAccess:
    """Get the access list for a page showing which users and groups have access.

    Args:
        page_id: The ID of the page to get access for
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching access list for page {page_id}")

    try:
        # Get page info first
        page_res = await page_routes.get_page_by_id(auth=auth, page_id=page_id)
        page_data = page_res.response

        # Get access list
        res = await page_routes.get_page_access_list(auth=auth, page_id=page_id)
        access_data = res.response or {}

        users = access_data.get("users", [])
        groups = access_data.get("groups", [])

        user_ids = [str(u.get("id", "")) for u in users if u.get("id")]
        group_ids = [str(g.get("id", "")) for g in groups if g.get("id")]

        return PageAccess(
            page_id=page_id,
            page_name=page_data.get("name", page_data.get("title", "")),
            user_ids=user_ids,
            group_ids=group_ids,
            total_users=len(user_ids),
            total_groups=len(group_ids),
        )

    except page_routes.Page_GET_Error as e:
        await ctx.error(f"Failed to get page access: {e}")
        raise


@mcp.tool()
async def add_page_owners(
    page_ids: list[str],
    user_ids: list[str],
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Add owners to one or more pages.

    Args:
        page_ids: List of page IDs to add owners to
        user_ids: List of user IDs to add as owners
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Adding {len(user_ids)} owners to {len(page_ids)} pages")

    try:
        await page_routes.add_page_owner(
            auth=auth,
            page_ids=page_ids,
            owner_ids=user_ids,
        )

        await ctx.info("Added page owners successfully")
        return f"Successfully added {len(user_ids)} owners to {len(page_ids)} pages"

    except page_routes.Page_CRUD_Error as e:
        await ctx.error(f"Failed to add page owners: {e}")
        raise
