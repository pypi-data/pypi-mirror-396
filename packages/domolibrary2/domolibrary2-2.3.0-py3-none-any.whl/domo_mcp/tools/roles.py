"""
Role Management Tools for Domo MCP Server

Provides tools for managing roles in Domo including listing roles,
viewing role details, and managing role assignments.
"""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp
from domolibrary2.routes import role as role_routes


class DomoRole(BaseModel):
    """Structured output for Domo role data."""

    id: str = Field(description="Role ID")
    name: str = Field(description="Role name")
    description: str | None = Field(default=None, description="Role description")
    is_system_role: bool | None = Field(
        default=None, description="Whether this is a system role"
    )
    user_count: int | None = Field(
        default=None, description="Number of users with this role"
    )


class RoleList(BaseModel):
    """Structured output for list of roles."""

    roles: list[DomoRole] = Field(description="List of Domo roles")
    total_count: int = Field(description="Total number of roles returned")


class RoleGrants(BaseModel):
    """Structured output for role grants/permissions."""

    role_id: str = Field(description="Role ID")
    role_name: str = Field(description="Role name")
    grants: list[str] = Field(description="List of grant/permission names")
    grant_count: int = Field(description="Total number of grants")


class RoleMembership(BaseModel):
    """Structured output for role membership."""

    role_id: str = Field(description="Role ID")
    role_name: str = Field(description="Role name")
    member_ids: list[str] = Field(description="List of member user IDs")
    member_count: int = Field(description="Total number of members")


def _parse_role(data: dict) -> DomoRole:
    """Parse role data from API response."""
    return DomoRole(
        id=str(data.get("id", "")),
        name=data.get("name", ""),
        description=data.get("description"),
        is_system_role=data.get("isSystemRole"),
        user_count=data.get("userCount"),
    )


@mcp.tool()
async def get_roles(
    ctx: Context[ServerSession, DomoContext],
) -> RoleList:
    """List all roles in the Domo instance.

    Returns a list of all roles with their basic information including
    ID, name, description, and whether they are system roles.
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching roles from {auth.domo_instance}")

    try:
        res = await role_routes.get_roles(auth=auth)
        roles_data = res.response or []

        roles = [_parse_role(r) for r in roles_data]

        await ctx.info(f"Found {len(roles)} roles")
        return RoleList(roles=roles, total_count=len(roles))

    except role_routes.RoleNotRetrievedError as e:
        await ctx.error(f"Failed to get roles: {e}")
        raise


@mcp.tool()
async def get_role_by_id(
    role_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> DomoRole:
    """Get details for a specific role.

    Args:
        role_id: The unique identifier of the role
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching role {role_id}")

    try:
        res = await role_routes.get_role_by_id(auth=auth, role_id=role_id)
        return _parse_role(res.response)

    except role_routes.RoleNotRetrievedError as e:
        await ctx.error(f"Failed to get role {role_id}: {e}")
        raise


@mcp.tool()
async def get_role_grants(
    role_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> RoleGrants:
    """Get the list of grants/permissions for a role.

    Args:
        role_id: The ID of the role to get grants for
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching grants for role {role_id}")

    try:
        # Get role info first
        role_res = await role_routes.get_role_by_id(auth=auth, role_id=role_id)
        role_data = role_res.response

        # Get grants
        res = await role_routes.get_role_grants(auth=auth, role_id=role_id)
        grants_data = res.response or []

        grant_names = [g.get("authority", g.get("name", str(g))) for g in grants_data]

        return RoleGrants(
            role_id=role_id,
            role_name=role_data.get("name", ""),
            grants=grant_names,
            grant_count=len(grant_names),
        )

    except role_routes.RoleNotRetrievedError as e:
        await ctx.error(f"Failed to get role grants: {e}")
        raise


@mcp.tool()
async def get_role_membership(
    role_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> RoleMembership:
    """Get the list of users assigned to a role.

    Args:
        role_id: The ID of the role to get members for
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching membership for role {role_id}")

    try:
        # Get role info first
        role_res = await role_routes.get_role_by_id(auth=auth, role_id=role_id)
        role_data = role_res.response

        # Get membership
        res = await role_routes.get_role_membership(auth=auth, role_id=role_id)
        members_data = res.response or []

        member_ids = [str(m.get("id", "")) for m in members_data if m.get("id")]

        return RoleMembership(
            role_id=role_id,
            role_name=role_data.get("name", ""),
            member_ids=member_ids,
            member_count=len(member_ids),
        )

    except role_routes.RoleNotRetrievedError as e:
        await ctx.error(f"Failed to get role membership: {e}")
        raise


@mcp.tool()
async def assign_users_to_role(
    role_id: str,
    user_ids: list[str],
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Assign users to a role.

    Args:
        role_id: The ID of the role to assign users to
        user_ids: List of user IDs to assign to the role
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Assigning {len(user_ids)} users to role {role_id}")

    try:
        await role_routes.role_membership_add_users(
            auth=auth,
            role_id=role_id,
            user_ids=user_ids,
        )

        await ctx.info(f"Assigned users to role {role_id} successfully")
        return f"Successfully assigned {len(user_ids)} users to role {role_id}"

    except role_routes.Role_CRUD_Error as e:
        await ctx.error(f"Failed to assign users to role: {e}")
        raise


@mcp.tool()
async def create_role(
    name: str,
    description: str,
    ctx: Context[ServerSession, DomoContext],
) -> DomoRole:
    """Create a new role in the Domo instance.

    Args:
        name: Name for the new role
        description: Description of the role's purpose
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Creating role: {name}")

    try:
        res = await role_routes.create_role(
            auth=auth,
            name=name,
            description=description,
        )

        await ctx.info(f"Created role: {res.response.get('id')}")
        return _parse_role(res.response)

    except role_routes.Role_CRUD_Error as e:
        await ctx.error(f"Failed to create role: {e}")
        raise
