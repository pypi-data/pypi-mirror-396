"""
Account Sharing Route Functions

This module provides account sharing and access management functions.

Functions:
    get_account_accesslist: Get account access list
    get_oauth_account_accesslist: Get OAuth account access list
    share_account: Share account with users/groups (v2 API)
    share_oauth_account: Share OAuth account
    share_account_v1: Legacy account sharing (v1 API)
    generate_share_account_v1_payload: Generate v1 API sharing payload
    generate_share_account_v2_payload: Generate v2 API sharing payload
    generate_share_account_payload: Orchestrator function for payload generation

Classes:
    ShareAccount: Abstract base class for sharing enums
    ShareAccount_AccessLevel: v2 API sharing permissions
    ShareAccount_V1_AccessLevel: v1 API sharing permissions (legacy)
"""

from enum import Enum

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.logging import LogDecoratorConfig, ResponseGetDataProcessor, log_call
from .exceptions import AccountSharing_Error


class ShareAccount(DomoEnumMixin):
    """Abstract base class for sharing enums."""


class ShareAccount_V1_AccessLevel(ShareAccount, Enum):
    """Legacy v1 API sharing permissions (users only)."""

    OWNER = "OWNER"
    CAN_EDIT = "WRITE"
    CAN_VIEW = "READ"

    default = "READ"


class ShareAccount_AccessLevel(ShareAccount, Enum):
    """v2 API sharing permissions (users and groups)."""

    OWNER = "OWNER"
    CAN_SHARE = "CAN_SHARE"
    CAN_VIEW = "CAN_VIEW"
    CAN_EDIT = "CAN_EDIT"
    NO_ACCESS = "NONE"

    default = "CAN_VIEW"


# Payload Generation Functions


def generate_share_account_v1_payload(
    user_id: int,
    access_level: ShareAccount_V1_AccessLevel,
) -> dict:
    """Generate v1 API sharing payload for users only.

    V1 API limitations:
    - Only supports sharing with users (no groups)
    - Limited permission set: READ, WRITE, OWNER

    Args:
        user_id: ID of the user to share with
        access_level: Access level (ShareAccount_V1_AccessLevel enum)

    Returns:
        Dictionary payload for v1 share API

    Example:
        >>> payload = generate_share_account_v1_payload(
        ...     user_id=12345,
        ...     access_level=ShareAccount_V1_AccessLevel.CAN_VIEW
        ... )
        >>> # Returns: {"type": "USER", "id": 12345, "permissions": ["READ"]}
    """
    return {"type": "USER", "id": int(user_id), "permissions": [access_level.value]}


def generate_share_account_v2_payload(
    access_level: ShareAccount_AccessLevel,
    user_id: int | None = None,
    group_id: int | None = None,
) -> dict:
    """Generate v2 API sharing payload for users or groups.

    V2 API features:
    - Supports both users and groups
    - Extended permissions: CAN_VIEW, CAN_EDIT, CAN_SHARE, OWNER, NO_ACCESS

    Args:
        access_level: Access level (ShareAccount_AccessLevel enum)
        user_id: ID of the user to share with (mutually exclusive with group_id)
        group_id: ID of the group to share with (mutually exclusive with user_id)

    Returns:
        Dictionary payload for v2 share API

    Raises:
        ValueError: If neither or both user_id and group_id are provided

    Example:
        >>> payload = generate_share_account_v2_payload(
        ...     access_level=ShareAccount_AccessLevel.CAN_VIEW,
        ...     user_id=12345
        ... )
        >>> # Returns: {"type": "USER", "id": "12345", "accessLevel": "CAN_VIEW"}
    """
    if not user_id and not group_id:
        raise ValueError("Must provide either user_id or group_id")

    if user_id and group_id:
        raise ValueError("Cannot provide both user_id and group_id")

    if user_id:
        return {"type": "USER", "id": str(user_id), "accessLevel": access_level.value}

    return {"type": "GROUP", "id": int(group_id), "accessLevel": access_level.value}


def generate_share_account_payload(
    access_level: ShareAccount_AccessLevel | ShareAccount_V1_AccessLevel | str,
    user_id: int | None = None,
    group_id: int | None = None,
    use_v1_api: bool = False,
) -> dict:
    """Orchestrator function to generate appropriate sharing payload.

    This function determines which payload generation function to use based on:
    - The access_level type (v1 or v2 enum)
    - The use_v1_api flag
    - Whether a group_id is provided (forces v2)

    Args:
        access_level: Access level enum or string
        user_id: ID of the user to share with
        group_id: ID of the group to share with (forces v2 API)
        use_v1_api: Force use of v1 API (ignored if group_id provided)

    Returns:
        Dictionary payload for appropriate share API

    Raises:
        ValueError: If group_id provided with v1 access level or use_v1_api=True

    Example:
        >>> # V2 with user
        >>> payload = generate_share_account_payload(
        ...     access_level=ShareAccount_AccessLevel.CAN_VIEW,
        ...     user_id=12345
        ... )

        >>> # V2 with group (auto-detects v2 needed)
        >>> payload = generate_share_account_payload(
        ...     access_level=ShareAccount_AccessLevel.CAN_VIEW,
        ...     group_id=67890
        ... )

        >>> # V1 explicitly
        >>> payload = generate_share_account_payload(
        ...     access_level=ShareAccount_V1_AccessLevel.CAN_VIEW,
        ...     user_id=12345
        ... )
    """
    # Determine if we need v1 or v2
    is_v1_enum = isinstance(access_level, ShareAccount_V1_AccessLevel)

    # Force v2 if group_id provided
    if group_id:
        if is_v1_enum:
            raise ValueError("Cannot share with groups using v1 access levels")
        if use_v1_api:
            raise ValueError("Cannot share with groups using v1 API")

        return generate_share_account_v2_payload(
            access_level=access_level, group_id=group_id
        )

    # Use v1 if explicitly requested or v1 enum provided
    if is_v1_enum or use_v1_api:
        if not user_id:
            raise ValueError("user_id required for v1 API")

        # Convert v2 enum to v1 if needed
        if not is_v1_enum:
            # Map v2 access levels to v1
            v2_to_v1_mapping = {
                "CAN_VIEW": ShareAccount_V1_AccessLevel.CAN_VIEW,
                "CAN_EDIT": ShareAccount_V1_AccessLevel.CAN_EDIT,
                "CAN_SHARE": ShareAccount_V1_AccessLevel.OWNER,
                "OWNER": ShareAccount_V1_AccessLevel.OWNER,
            }

            if isinstance(access_level, str):
                access_level = ShareAccount_AccessLevel.get(access_level)

            access_level = v2_to_v1_mapping.get(
                access_level.value, ShareAccount_V1_AccessLevel.CAN_VIEW
            )

        return generate_share_account_v1_payload(
            user_id=user_id, access_level=access_level
        )

    # Default to v2
    return generate_share_account_v2_payload(access_level=access_level, user_id=user_id)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_account_accesslist(
    auth: DomoAuth,
    account_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get access list for an account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the account to get access list for
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing account access list

    Raises:
        AccountSharing_Error: If access list retrieval fails
    """

    url = (
        f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AccountSharing_Error(
            operation="get access list", account_id=account_id, res=res
        )

    res.response = res.response["list"]

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_oauth_account_accesslist(
    auth: DomoAuth,
    account_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get access list for an OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the OAuth account to get access list for
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing OAuth account access list

    Raises:
        AccountSharing_Error: If OAuth access list retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/templates/{account_id}/share"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AccountSharing_Error(
            operation="get OAuth access list", account_id=account_id, res=res
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def share_account(
    auth: DomoAuth,
    account_id: str,
    share_payload: dict | None = None,
    access_level: (
        ShareAccount_AccessLevel | ShareAccount_V1_AccessLevel | str | None
    ) = None,
    user_id: int | None = None,
    group_id: int | None = None,
    use_v1_api: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Share account with users/groups using v2 API.

    Note: This uses the v2 API which should be deployed to all Domo instances as of DP24.

    Two ways to call this function:
    1. Pass pre-built share_payload (legacy mode)
    2. Pass access_level with user_id or group_id (generates payload automatically)

    Args:
        auth: Authentication object for API requests
        account_id: ID of the account to share
        share_payload: Pre-built sharing payload (optional, overrides other params)
        access_level: Access level enum or string (required if share_payload not provided)
        user_id: ID of user to share with (mutually exclusive with group_id)
        group_id: ID of group to share with (mutually exclusive with user_id)
        use_v1_api: Force v1 API usage (ignored if group_id provided)
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object confirming sharing operation

    Raises:
        ValueError: If neither share_payload nor access_level provided
        Account_AlreadyShared_Error: If account is already shared with target
        Account_Share_Error: If sharing operation fails

    Examples:
        >>> # Using payload generator (new way)
        >>> await share_account(
        ...     auth=auth,
        ...     account_id="123",
        ...     access_level=ShareAccount_AccessLevel.CAN_VIEW,
        ...     user_id=456
        ... )

        >>> # Using pre-built payload (legacy way)
        >>> payload = generate_share_account_v2_payload(
        ...     access_level=ShareAccount_AccessLevel.CAN_VIEW,
        ...     group_id=789
        ... )
        >>> await share_account(
        ...     auth=auth,
        ...     account_id="123",
        ...     share_payload=payload
        ... )
    """

    # Generate payload if not provided
    if not share_payload:
        if not access_level:
            raise ValueError("Must provide either share_payload or access_level")

        share_payload = generate_share_account_payload(
            access_level=access_level,
            user_id=user_id,
            group_id=group_id,
            use_v1_api=use_v1_api,
        )

    # Route to appropriate API endpoint
    if use_v1_api or (
        access_level and isinstance(access_level, ShareAccount_V1_AccessLevel)
    ):
        # Use v1 endpoint
        url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/share"
    else:
        # Use v2 endpoint
        url = f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"

    method = "PUT"

    print(share_payload, type(share_payload))
    res = await gd.get_data(
        auth=auth,
        url=url,
        method=method,
        body=share_payload,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 500 and res.response == "Internal Server Error":
        raise AccountSharing_Error(
            account_id=account_id,
            message=f"{res.response} - User may already have access to account",
            res=res,
            operation=method,
        )

    if not res.is_success:
        raise AccountSharing_Error(account_id=account_id, res=res, operation=method)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def share_oauth_account(
    auth: DomoAuth,
    account_id: str,
    share_payload: dict | None = None,
    access_level: ShareAccount_AccessLevel | str | None = None,
    user_id: int | None = None,
    group_id: int | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Share OAuth account with users/groups.

    Two ways to call this function:
    1. Pass pre-built share_payload (legacy mode)
    2. Pass access_level with user_id or group_id (generates payload automatically)

    Args:
        auth: Authentication object for API requests
        account_id: ID of the OAuth account to share
        share_payload: Pre-built sharing payload (optional, overrides other params)
        access_level: Access level enum or string (required if share_payload not provided)
        user_id: ID of user to share with (mutually exclusive with group_id)
        group_id: ID of group to share with (mutually exclusive with user_id)
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object confirming sharing operation

    Raises:
        ValueError: If neither share_payload nor access_level provided
        Account_Share_Error: If OAuth sharing operation fails

    Examples:
        >>> # Using payload generator
        >>> await share_oauth_account(
        ...     auth=auth,
        ...     account_id="123",
        ...     access_level=ShareAccount_AccessLevel.CAN_VIEW,
        ...     group_id=789
        ... )
    """

    # Generate payload if not provided
    if not share_payload:
        if not access_level:
            raise ValueError("Must provide either share_payload or access_level")

        share_payload = generate_share_account_v2_payload(
            access_level=access_level,
            user_id=user_id,
            group_id=group_id,
        )

    url = f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/templates/share/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=share_payload,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AccountSharing_Error(
            account_id=account_id,
            res=res,
            operation="share OAuth account",
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def share_account_v1(
    auth: DomoAuth,
    account_id: str,
    share_payload: dict | None = None,
    access_level: ShareAccount_V1_AccessLevel | str | None = None,
    user_id: int | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Share account using legacy v1 API (users only).

    Note: V1 API allows sharing with users ONLY. It does not support sharing with groups
    and has a more limited set of share rights (owner or read). See ShareAccount_V1_AccessLevel
    vs ShareAccount_AccessLevel for differences.

    Two ways to call this function:
    1. Pass pre-built share_payload (legacy mode)
    2. Pass access_level with user_id (generates payload automatically)

    Args:
        auth: Authentication object for API requests
        account_id: ID of the account to share
        share_payload: Pre-built sharing payload (optional, overrides other params)
        access_level: Access level enum or string (required if share_payload not provided)
        user_id: ID of user to share with (required if share_payload not provided)
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object confirming sharing operation

    Raises:
        ValueError: If neither share_payload nor (access_level and user_id) provided
        Account_AlreadyShared_Error: If account is already shared with user
        Account_Share_Error: If sharing operation fails

    Examples:
        >>> # Using payload generator
        >>> await share_account_v1(
        ...     auth=auth,
        ...     account_id="123",
        ...     access_level=ShareAccount_V1_AccessLevel.CAN_VIEW,
        ...     user_id=456
        ... )
    """

    # Generate payload if not provided
    if not share_payload:
        if not access_level or not user_id:
            raise ValueError(
                "Must provide either share_payload or (access_level and user_id)"
            )

        share_payload = generate_share_account_v1_payload(
            user_id=user_id,
            access_level=access_level,
        )

    url = (
        f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/share"
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=share_payload,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 500 and res.response == "Internal Server Error":
        raise AccountSharing_Error(
            account_id=account_id,
            message=f"{res.response} - User may already have access to account",
            res=res,
            operation="PUT",
        )

    if not res.is_success:
        raise AccountSharing_Error(
            account_id=account_id,
            res=res,
            operation="PUT",
        )

    return res
