"""
User Management Tools for Domo MCP Server

Provides tools for managing users in Domo including listing, searching,
creating, updating, and deleting users.
"""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp
from domolibrary2.routes import (
    role as role_routes,
    user as user_routes,
)


class DomoUser(BaseModel):
    """Structured output for Domo user data."""

    id: str = Field(description="User ID")
    display_name: str = Field(description="User display name")
    email: str = Field(description="User email address")
    role_name: str | None = Field(default=None, description="User role name")
    role_id: int | None = Field(default=None, description="User role ID")
    department: str | None = Field(default=None, description="User department")
    title: str | None = Field(default=None, description="User job title")


class UserList(BaseModel):
    """Structured output for list of users."""

    users: list[DomoUser] = Field(description="List of Domo users")
    total_count: int = Field(description="Total number of users returned")


def _parse_user(user_data: dict) -> DomoUser:
    """Parse user data from API response to DomoUser model."""
    role = user_data.get("role") or user_data.get("roleId") or {}
    return DomoUser(
        id=str(user_data.get("id", "")),
        display_name=user_data.get("displayName", ""),
        email=user_data.get("emailAddress", user_data.get("email", "")),
        role_name=role.get("name") if isinstance(role, dict) else None,
        role_id=role.get("id") if isinstance(role, dict) else role,
        department=user_data.get("department"),
        title=user_data.get("title"),
    )


@mcp.tool()
async def get_users(
    ctx: Context[ServerSession, DomoContext],
    limit: int = Field(default=500, description="Maximum number of users to return"),
) -> UserList:
    """List all users in the Domo instance.

    Returns a list of all users with their basic information including
    ID, display name, email, role, department, and title.
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching users from {auth.domo_instance}")

    try:
        res = await user_routes.get_all_users(auth=auth)
        users_data = res.response or []

        # Apply limit
        users_data = users_data[:limit]

        users = [_parse_user(u) for u in users_data]

        await ctx.info(f"Found {len(users)} users")
        return UserList(users=users, total_count=len(users))

    except user_routes.User_GET_Error as e:
        await ctx.error(f"Failed to get users: {e}")
        raise


@mcp.tool()
async def get_user_by_id(
    user_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> DomoUser:
    """Get a specific Domo user by their ID.

    Args:
        user_id: The unique identifier of the user to retrieve
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching user {user_id}")

    try:
        res = await user_routes.get_by_id(auth=auth, user_id=user_id)
        user_data = res.response

        return _parse_user(user_data)

    except user_routes.User_GET_Error as e:
        await ctx.error(f"Failed to get user {user_id}: {e}")
        raise


@mcp.tool()
async def search_users_by_email(
    email: str,
    ctx: Context[ServerSession, DomoContext],
) -> UserList:
    """Search for Domo users by email address.

    Args:
        email: Email address or partial email to search for
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Searching users with email: {email}")

    try:
        res = await user_routes.search_users_by_email(auth=auth, user_email_ls=[email])
        users_data = res.response or []

        users = [_parse_user(u) for u in users_data]

        await ctx.info(f"Found {len(users)} users matching '{email}'")
        return UserList(users=users, total_count=len(users))

    except user_routes.SearchUserNotFoundError:
        await ctx.info(f"No users found matching '{email}'")
        return UserList(users=[], total_count=0)


@mcp.tool()
async def create_user(
    email: str,
    display_name: str,
    role_id: int,
    ctx: Context[ServerSession, DomoContext],
) -> DomoUser:
    """Create a new user in Domo.

    Args:
        email: Email address for the new user
        display_name: Display name for the new user
        role_id: Role ID to assign to the user
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Creating user: {email}")

    try:
        res = await user_routes.create_user(
            auth=auth,
            email_address=email,
            display_name=display_name,
            role_id=role_id,
        )
        user_data = res.response

        await ctx.info(f"Created user: {user_data.get('id')}")
        return _parse_user(user_data)

    except user_routes.User_CRUD_Error as e:
        await ctx.error(f"Failed to create user: {e}")
        raise


@mcp.tool()
async def delete_user(
    user_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Delete a user from Domo (soft delete - user can be restored).

    This performs a soft delete where the user is marked as deleted but can be
    restored. Use this for standard user removal operations.

    Args:
        user_id: The ID of the user to delete
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Deleting user: {user_id}")

    try:
        await user_routes.delete_user(auth=auth, user_id=user_id)
        await ctx.info(f"Deleted user: {user_id}")
        return f"Successfully deleted user {user_id}"

    except user_routes.DeleteUserError as e:
        await ctx.error(f"Failed to delete user: {e}")
        raise


@mcp.tool()
async def update_user_properties(
    user_id: str,
    ctx: Context[ServerSession, DomoContext],
    display_name: str | None = Field(
        default=None, description="New display name for the user"
    ),
    email: str | None = Field(
        default=None, description="New email address for the user"
    ),
    title: str | None = Field(default=None, description="New job title for the user"),
    department: str | None = Field(
        default=None, description="New department for the user"
    ),
    phone_number: str | None = Field(
        default=None, description="New phone number for the user"
    ),
) -> str:
    """Update user properties in Domo.

    Updates one or more properties for a user. Only provided fields will be updated.

    Args:
        user_id: The ID of the user to update
        display_name: New display name for the user
        email: New email address for the user
        title: New job title for the user
        department: New department for the user
        phone_number: New phone number for the user
    """
    auth = ctx.request_context.lifespan_context.auth

    # Build list of properties to update
    properties = []

    if display_name is not None:
        properties.append(
            user_routes.UserProperty(
                user_routes.UserProperty_Type.display_name, display_name
            )
        )
    if email is not None:
        properties.append(
            user_routes.UserProperty(user_routes.UserProperty_Type.email_address, email)
        )
    if title is not None:
        properties.append(
            user_routes.UserProperty(user_routes.UserProperty_Type.title, title)
        )
    if department is not None:
        properties.append(
            user_routes.UserProperty(
                user_routes.UserProperty_Type.department, department
            )
        )
    if phone_number is not None:
        properties.append(
            user_routes.UserProperty(
                user_routes.UserProperty_Type.phone_number, phone_number
            )
        )

    if not properties:
        return "No properties provided to update"

    await ctx.info(f"Updating {len(properties)} properties for user {user_id}")

    try:
        await user_routes.update_user(
            auth=auth,
            user_id=user_id,
            user_property_ls=properties,
        )

        property_names = [p.property_type.name for p in properties]
        await ctx.info(f"Updated user {user_id}: {', '.join(property_names)}")
        return f"Successfully updated user {user_id}: {', '.join(property_names)}"

    except user_routes.User_CRUD_Error as e:
        await ctx.error(f"Failed to update user properties: {e}")
        raise


@mcp.tool()
async def change_user_role(
    user_id: str,
    new_role_id: int,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Change a user's role.

    Assigns a new role to the specified user.

    Args:
        user_id: The ID of the user to update
        new_role_id: The ID of the new role to assign
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Changing role for user {user_id} to role {new_role_id}")

    try:
        # Update the role using the user properties API
        properties = [
            user_routes.UserProperty(user_routes.UserProperty_Type.role_id, new_role_id)
        ]

        await user_routes.update_user(
            auth=auth,
            user_id=user_id,
            user_property_ls=properties,
        )

        await ctx.info(f"Changed user {user_id} to role {new_role_id}")
        return f"Successfully changed user {user_id} to role {new_role_id}"

    except user_routes.User_CRUD_Error as e:
        await ctx.error(f"Failed to change user role: {e}")
        raise


@mcp.tool()
async def set_user_landing_page(
    user_id: str,
    page_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Set a user's default landing page.

    Sets the page that will be shown when the user logs into Domo.

    Args:
        user_id: The ID of the user to update
        page_id: The ID of the page to set as landing page
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Setting landing page for user {user_id} to page {page_id}")

    try:
        await user_routes.set_user_landing_page(
            auth=auth,
            user_id=user_id,
            page_id=page_id,
        )

        await ctx.info(f"Set landing page for user {user_id}")
        return f"Successfully set landing page for user {user_id} to page {page_id}"

    except user_routes.User_CRUD_Error as e:
        await ctx.error(f"Failed to set landing page: {e}")
        raise


@mcp.tool()
async def reset_user_password(
    user_id: str,
    new_password: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Reset a user's password.

    Sets a new password for the specified user. The password should meet
    Domo's password requirements.

    Args:
        user_id: The ID of the user whose password to reset
        new_password: The new password to set
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Resetting password for user {user_id}")

    try:
        await user_routes.reset_password(
            auth=auth,
            user_id=user_id,
            new_password=new_password,
        )

        await ctx.info(f"Reset password for user {user_id}")
        return f"Successfully reset password for user {user_id}"

    except user_routes.ResetPasswordPasswordUsedError:
        await ctx.warning(f"Password was previously used for user {user_id}")
        return f"Failed: Password has been used previously for user {user_id}"

    except user_routes.User_CRUD_Error as e:
        await ctx.error(f"Failed to reset password: {e}")
        raise


@mcp.tool()
async def request_password_reset_email(
    email: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Request a password reset email for a user.

    Sends a password reset email to the specified email address.

    Args:
        email: The email address of the user requesting password reset
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Requesting password reset for {email}")

    try:
        await user_routes.request_password_reset(
            domo_instance=auth.domo_instance,
            email=email,
        )

        await ctx.info(f"Password reset email sent to {email}")
        return f"Password reset email sent to {email}"

    except user_routes.User_CRUD_Error as e:
        await ctx.error(f"Failed to request password reset: {e}")
        raise


@mcp.tool()
async def set_user_direct_signon(
    user_ids: list[str],
    ctx: Context[ServerSession, DomoContext],
    allow_direct_signon: bool = Field(
        default=True, description="Whether to allow direct sign-on"
    ),
) -> str:
    """Enable or disable direct sign-on for users.

    Controls whether users can sign in directly to Domo or must use SSO.

    Args:
        user_ids: List of user IDs to update
        allow_direct_signon: Whether to allow direct sign-on (default: True)
    """
    auth = ctx.request_context.lifespan_context.auth
    action = "Enabling" if allow_direct_signon else "Disabling"
    await ctx.info(f"{action} direct sign-on for {len(user_ids)} users")

    try:
        await user_routes.user_is_allowed_direct_signon(
            auth=auth,
            user_ids=user_ids,
            is_allow_dso=allow_direct_signon,
        )

        status = "enabled" if allow_direct_signon else "disabled"
        await ctx.info(f"Direct sign-on {status} for {len(user_ids)} users")
        return f"Successfully {status} direct sign-on for {len(user_ids)} users"

    except user_routes.User_CRUD_Error as e:
        await ctx.error(f"Failed to update direct sign-on: {e}")
        raise


@mcp.tool()
async def bulk_change_user_roles(
    user_ids: list[str],
    new_role_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Change roles for multiple users at once.

    Assigns a new role to all specified users. This is more efficient than
    changing roles individually for bulk operations.

    Args:
        user_ids: List of user IDs to update
        new_role_id: The ID of the new role to assign to all users
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Changing {len(user_ids)} users to role {new_role_id}")

    try:
        await role_routes.role_membership_add_users(
            auth=auth,
            role_id=new_role_id,
            user_ids=user_ids,
        )

        await ctx.info(f"Changed {len(user_ids)} users to role {new_role_id}")
        return f"Successfully changed {len(user_ids)} users to role {new_role_id}"

    except role_routes.Role_CRUD_Error as e:
        await ctx.error(f"Failed to change user roles: {e}")
        raise
