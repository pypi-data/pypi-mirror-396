"""
Group Management Tools for Domo MCP Server

Provides tools for managing groups in Domo including listing, searching,
creating, and managing group membership.
"""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp
from domolibrary2.routes import group as group_routes


class DomoGroup(BaseModel):
    """Structured output for Domo group data."""

    id: str = Field(description="Group ID")
    name: str = Field(description="Group name")
    description: str | None = Field(default=None, description="Group description")
    member_count: int | None = Field(
        default=None, description="Number of members in the group"
    )
    group_type: str | None = Field(default=None, description="Type of group")


class GroupList(BaseModel):
    """Structured output for list of groups."""

    groups: list[DomoGroup] = Field(description="List of Domo groups")
    total_count: int = Field(description="Total number of groups returned")


class GroupMembership(BaseModel):
    """Structured output for group membership."""

    group_id: str = Field(description="Group ID")
    group_name: str = Field(description="Group name")
    member_ids: list[str] = Field(description="List of member user IDs")
    member_count: int = Field(description="Total number of members")


def _parse_group(data: dict) -> DomoGroup:
    """Parse group data from API response."""
    return DomoGroup(
        id=str(data.get("id", "")),
        name=data.get("name", ""),
        description=data.get("description"),
        member_count=data.get("memberCount") or data.get("userCount"),
        group_type=data.get("type"),
    )


@mcp.tool()
async def get_groups(
    ctx: Context[ServerSession, DomoContext],
    limit: int = Field(default=500, description="Maximum number of groups to return"),
) -> GroupList:
    """List all groups in the Domo instance.

    Returns a list of all groups with their basic information including
    ID, name, description, and member count.
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching groups from {auth.domo_instance}")

    try:
        res = await group_routes.get_all_groups(auth=auth)
        groups_data = res.response or []

        # Apply limit
        groups_data = groups_data[:limit]

        groups = [_parse_group(g) for g in groups_data]

        await ctx.info(f"Found {len(groups)} groups")
        return GroupList(groups=groups, total_count=len(groups))

    except group_routes.Group_GET_Error as e:
        await ctx.error(f"Failed to get groups: {e}")
        raise


@mcp.tool()
async def get_group_by_id(
    group_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> DomoGroup:
    """Get a specific group by its ID.

    Args:
        group_id: The unique identifier of the group
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching group {group_id}")

    try:
        res = await group_routes.get_group_by_id(auth=auth, group_id=group_id)
        return _parse_group(res.response)

    except group_routes.Group_GET_Error as e:
        await ctx.error(f"Failed to get group {group_id}: {e}")
        raise


@mcp.tool()
async def search_groups(
    search_name: str,
    ctx: Context[ServerSession, DomoContext],
    exact_match: bool = Field(
        default=False, description="Whether to require exact name match"
    ),
) -> GroupList:
    """Search for groups by name.

    Args:
        search_name: Group name or partial name to search for
        exact_match: Whether to require exact name match (default: False)
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Searching groups with name: {search_name}")

    try:
        res = await group_routes.search_groups_by_name(
            auth=auth,
            search_name=search_name,
            is_exact_match=exact_match,
        )
        groups_data = res.response or []

        groups = [_parse_group(g) for g in groups_data]

        await ctx.info(f"Found {len(groups)} groups matching '{search_name}'")
        return GroupList(groups=groups, total_count=len(groups))

    except group_routes.SearchGroups_Error:
        await ctx.info(f"No groups found matching '{search_name}'")
        return GroupList(groups=[], total_count=0)


@mcp.tool()
async def get_group_membership(
    group_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> GroupMembership:
    """Get the list of members in a group.

    Args:
        group_id: The ID of the group to get members for
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching membership for group {group_id}")

    try:
        # Get group info first
        group_res = await group_routes.get_group_by_id(auth=auth, group_id=group_id)
        group_data = group_res.response

        # Get membership
        res = await group_routes.get_group_membership(auth=auth, group_id=group_id)
        members_data = res.response or []

        member_ids = [str(m.get("id", "")) for m in members_data if m.get("id")]

        return GroupMembership(
            group_id=group_id,
            group_name=group_data.get("name", ""),
            member_ids=member_ids,
            member_count=len(member_ids),
        )

    except group_routes.Group_GET_Error as e:
        await ctx.error(f"Failed to get group membership: {e}")
        raise


@mcp.tool()
async def create_group(
    name: str,
    ctx: Context[ServerSession, DomoContext],
    description: str = Field(default="", description="Group description"),
) -> DomoGroup:
    """Create a new group in Domo.

    Args:
        name: Name for the new group
        description: Optional description for the group
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Creating group: {name}")

    try:
        res = await group_routes.create_group(
            auth=auth,
            group_name=name,
            description=description,
        )
        group_data = res.response

        await ctx.info(f"Created group: {group_data.get('id')}")
        return _parse_group(group_data)

    except group_routes.Group_CRUD_Error as e:
        await ctx.error(f"Failed to create group: {e}")
        raise


@mcp.tool()
async def update_group_membership(
    group_id: str,
    add_user_ids: list[str],
    ctx: Context[ServerSession, DomoContext],
    remove_user_ids: list[str] = Field(
        default=[], description="User IDs to remove from group"
    ),
) -> str:
    """Update group membership by adding or removing users.

    Args:
        group_id: The ID of the group to update
        add_user_ids: List of user IDs to add to the group
        remove_user_ids: List of user IDs to remove from the group
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(
        f"Updating membership for group {group_id}: "
        f"adding {len(add_user_ids)}, removing {len(remove_user_ids)}"
    )

    try:
        if add_user_ids:
            await group_routes.update_group_members(
                auth=auth,
                group_id=group_id,
                member_ids=add_user_ids,
                is_remove=False,
            )

        if remove_user_ids:
            await group_routes.update_group_members(
                auth=auth,
                group_id=group_id,
                member_ids=remove_user_ids,
                is_remove=True,
            )

        await ctx.info(f"Updated group {group_id} membership successfully")
        return (
            f"Successfully updated group {group_id}: "
            f"added {len(add_user_ids)} users, removed {len(remove_user_ids)} users"
        )

    except group_routes.Group_CRUD_Error as e:
        await ctx.error(f"Failed to update group membership: {e}")
        raise
