from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

"""
Core User Management Routes

This module provides core user management functionality including retrieval,
creation, deletion, and search operations.

Functions:
    get_all_users: Retrieve all users
    search_users: Search users with flexible criteria
    search_users_by_id: Search users by ID list
    search_users_by_email: Search users by email list
    get_by_id: Retrieve specific user by ID
    search_virtual_user_by_subscriber_instance: Find virtual users
    create_user: Create new user
    delete_user: Delete user
    process_v1_search_users: Process and sanitize v1 search results
"""

from __future__ import annotations

import asyncio

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils import (
    chunk_execution as dmce,
)
from ...utils.convert import is_valid_email
from .exceptions import (
    DeleteUserError,
    SearchUserNotFoundError,
    User_CRUD_Error,
    User_GET_Error,
)

__all__ = [
    "get_all_users",
    "search_users",
    "search_users_by_id",
    "search_users_by_email",
    "get_by_id",
    "search_virtual_user_by_subscriber_instance",
    "create_user",
    "delete_user",
    "process_v1_search_users",
]


def process_v1_search_users(
    v1_user_ls: list[dict],  # list of users from v1_users_search API
) -> list[dict]:  # sanitized list of users.
    """sanitizes the response from v1_users_search API and removes unnecessary attributes"""

    clean_users = []

    for obj in v1_user_ls:
        # dd_user = dd.DictDot(obj_user)

        attributes = obj.pop("attributes")

        clean_users.append(
            {**obj, **{attr["key"]: attr["values"][0] for attr in attributes}}
        )

    return clean_users


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_all_users(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve all users from Domo instance.

    This function returns all users as provided by the Domo API endpoint
    `/api/content/v2/users`. By default, this typically includes active users
    and may exclude deleted users and Domo support accounts. The exact
    filtering behavior (e.g., inclusion of deleted or support users) depends
    on the API's implementation and may change over time. If you require
    information about deleted or support users, consult the Domo API
    documentation or inspect the raw response using `return_raw=True`.
    Args:
        auth: Authentication object
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing all users

    Raises:
        User_GET_Error: If user retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/users"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_users(
    auth: DomoAuth,
    body: dict,
    loop_until_end: bool = True,  # retrieve all available rows
    limit: int = 200,  # maximum rows to return per request.  refers to PAGINATION
    maximum: int = 100,  # equivalent to the LIMIT or TOP clause in SQL, the number of rows to return total
    suppress_no_results_error: bool = False,
    debug_loop: bool = False,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Search users with flexible criteria using the v1 users search API.

    Args:
        auth: Authentication object
        body: Search criteria body for the API request
        loop_until_end: Retrieve all available rows across all pages
        limit: Maximum rows to return per request (pagination)
        maximum: Maximum total rows to return (like SQL LIMIT)
        suppress_no_results_error: Don't raise error if no results found
        return_raw: Return raw API response without processing
        debug_loop: Enable loop debugging

    Returns:
        ResponseGetData object containing search results

    Raises:
        User_GET_Error: If search request fails
        SearchUserNotFoundError: If no users found and suppress_no_results_error is False
    """
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/users/search"

    offset_params = {"offset": "offset", "limit": "limit"}

    def body_fn(skip, limit, body):
        return {**body, "limit": limit, "offset": skip}

    def arr_fn(res: rgd.ResponseGetData):
        return res.response.get("users") if isinstance(res.response, dict) else []

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        maximum=maximum,
        limit=limit,
        offset_params=offset_params,
        offset_params_in_body=True,
        loop_until_end=loop_until_end,
        arr_fn=arr_fn,
        body_fn=body_fn,
        body=body,
        debug_loop=debug_loop,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_GET_Error(res=res)

    if not suppress_no_results_error and len(res.response) == 0:
        raise SearchUserNotFoundError(search_criteria=str(body), res=res)

    res.response = process_v1_search_users(res.response)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_users_by_id(
    auth: DomoAuth,
    user_ids: list[str],  # list of user ids to search
    return_raw: bool = False,
    suppress_no_results_error: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:  # ResponseGetData with user list
    """Search for users by their IDs using the v1 users search API.

    Args:
        user_ids: list of user IDs to search for
        auth: Authentication object
        return_raw: Return raw API response without processing
        suppress_no_results_error: Don't raise error if no results found

    Returns:
        ResponseGetData object containing found users

    Raises:
        User_GET_Error: If search request fails
        SearchUserNotFoundError: If no users found and suppress_no_results_error is False
    """

    user_cn = dmce.chunk_list(user_ids, 1000)

    res_ls = await dmce.gather_with_concurrency(
        n=6,
        *[
            search_users(
                auth=auth,
                body={
                    # "showCount": true,
                    # "count": false,
                    "includeDeleted": False,
                    "includeSupport": False,
                    "filters": [
                        {
                            "field": "id",
                            "filterType": "value",
                            "values": user_ls,
                            "operator": "EQ",
                        }
                    ],
                    "parts": ["DETAILED", "GROUPS", "ROLE"],
                    "attributes": [
                        "id",
                        "displayName",
                        "roleId",
                        "department",
                        "title",
                        "emailAddress",
                        "phoneNumber",
                        "lastActivity",
                    ],
                },
                return_raw=return_raw,
                suppress_no_results_error=suppress_no_results_error,
                context=context,
            )
            for user_ls in user_cn
        ],
    )

    if return_raw:
        return res_ls[-1]

    res = res_ls[-1]

    res.response = [row for ls in [_.response for _ in res_ls] for row in ls]

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_users_by_email(
    user_email_ls: list[
        str
    ],  # list of user emails to search.  Note:  search does not appear to be case sensitive
    auth: DomoAuth,
    return_raw: bool = False,
    suppress_no_results_error: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:  # ResponseGetData with user list
    """Search for users by their email addresses using the v1 users search API.

    Args:
        user_email_ls: list of user email addresses to search for
        auth: Authentication object
        return_raw: Return raw API response without processing
        suppress_no_results_error: Don't raise error if no results found

    Returns:
        ResponseGetData object containing found users

    Raises:
        User_GET_Error: If search request fails
        SearchUserNotFoundError: If no users found and suppress_no_results_error is False

    Note:
        Search does not appear to be case sensitive
    """

    user_cn = dmce.chunk_list(user_email_ls, 1000)

    res_ls = await dmce.gather_with_concurrency(
        n=10,
        *[
            search_users(
                auth=auth,
                body={
                    # "showCount": true,
                    # "count": false,
                    "includeDeleted": False,
                    "includeSupport": False,
                    "limit": 200,
                    "offset": 0,
                    "sort": {"field": "displayName", "order": "ASC"},
                    "filters": [
                        {
                            "filterType": "text",
                            "field": "emailAddress",
                            "text": " ".join(user_ls),
                        }
                    ],
                    "parts": ["DETAILED", "GROUPS", "ROLE"],
                    "attributes": [
                        "id",
                        "displayName",
                        "roleId",
                        "department",
                        "title",
                        "emailAddress",
                        "phoneNumber",
                        "lastActivity",
                    ],
                },
                return_raw=return_raw,
                suppress_no_results_error=suppress_no_results_error,
                context=context,
            )
            for user_ls in user_cn
        ],
    )

    if return_raw:
        return res_ls[-1]

    res = res_ls[-1]

    res.response = [row for ls in [_.response for _ in res_ls] for row in ls]
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def _get_by_id(
    user_id: str,
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
):
    """Internal function to get user by ID using v2 and v3 APIs.

    This function combines data from both v2 and v3 endpoints to provide
    comprehensive user information.
    """
    v2_url = f"https://{auth.domo_instance}.domo.com/api/content/v2/users/{user_id}"

    v3_url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users/{user_id}"

    params = {
        "includeDetails": True,
        "attributes": [
            "id",
            "displayName",
            "roleId",
            "department",
            "title",
            "emailAddress",
            "phoneNumber",
            "lastActivity",
        ],
    }

    res_v2, res_v3 = await asyncio.gather(
        gd.get_data(
            url=v2_url,
            method="GET",
            auth=auth,
            params=params,
            context=context,
        ),
        gd.get_data(
            url=v3_url,
            method="GET",
            auth=auth,
            params=params,
            context=context,
        ),
    )

    if return_raw:
        res_v2.response = {**res_v2.response, **res_v3.response}
        return res_v2

    if res_v2.status == 200 and res_v2.response == "":
        raise SearchUserNotFoundError(
            search_criteria=f"user_id {user_id} not found", res=res_v2
        )

    if not res_v2.is_success:
        raise User_GET_Error(res=res_v2)

    if res_v3.status == 404 and res_v3.response == "Not Found":
        raise SearchUserNotFoundError(
            res=res_v3,
            search_criteria=f"user_id {user_id} not found",
        )

    if (
        not res_v3.status == 404 and not res_v3.response == "Not Found"
    ) and not res_v3.is_success:
        raise User_GET_Error(res=res_v3)

    detail = {
        **(res_v3.response.pop("detail") if isinstance(res_v3.response, dict) else {}),
        # **res_v2.response.pop('detail')
    }

    res_v2.response = {
        **res_v2.response,
        **(res_v3.response if isinstance(res_v3.response, dict) else {}),
        **detail,
    }

    return res_v2


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_by_id(
    user_id: str,
    auth: DomoAuth,
    is_v2: bool = True,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve a specific user by ID.

    Args:
        user_id: The unique identifier for the user
        auth: Authentication object
        return_raw: Return raw API response without processing
        is_v2: If True, use v2 search API, otherwise use combined v2/v3 approach

    Returns:
        ResponseGetData object containing user information

    Raises:
        User_GET_Error: If user retrieval fails
        SearchUserNotFoundError: If user with specified ID doesn't exist
    """

    if not is_v2:
        return await _get_by_id(
            user_id=user_id,
            auth=auth,
            return_raw=return_raw,
            context=context,
        )

    res = await search_users_by_id(
        user_ids=[user_id],
        auth=auth,
        return_raw=return_raw,
        suppress_no_results_error=False,
        context=context,
    )

    if return_raw:
        return res

    res.response = res.response[0]
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_virtual_user_by_subscriber_instance(
    auth: DomoAuth,  # domo auth object
    subscriber_instance_ls: list[str],  # list of subscriber domo instances
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:  # list of virtual domo users
    """Retrieve virtual users for subscriber instances tied to one publisher.

    Args:
        auth: Authentication object for the publisher instance
        subscriber_instance_ls: list of subscriber Domo instance names
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing virtual users

    Raises:
        User_GET_Error: If virtual user retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/proxy_user/domain/"

    body = {
        "domains": [
            f"{subscriber_instance}.domo.com"
            for subscriber_instance in subscriber_instance_ls
        ]
    }

    res = await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_user(
    auth: DomoAuth,
    display_name: str,
    email_address: str,
    role_id: int,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Create a new user in the Domo instance.

    Args:
        auth: Authentication object
        display_name: Display name for the new user
        email_address: Email address for the new user (must be valid)
        role_id: Role ID to assign to the new user
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing created user information

    Raises:
        User_CRUD_Error: If user creation fails
        ValueError: If email address is invalid
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users"

    is_valid_email(email_address)

    body = {
        "displayName": display_name,
        "detail": {"email": email_address},
        "roleId": role_id,
    }

    res = await gd.get_data(
        url=url,
        method="POST",
        body=body,
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        raise User_CRUD_Error(
            operation="create",
            res=res,
            message=f"{res.response} - does this user {email_address} already exist?",
        )

    if not res.is_success:
        raise User_CRUD_Error(operation="create", res=res)

    res.is_success = True
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def delete_user(
    auth: DomoAuth,
    user_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Delete a user from the Domo instance.

    Args:
        auth: Authentication object
        user_id: ID of the user to delete
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object confirming user deletion

    Raises:
        DeleteUserError: If user deletion fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/users/{user_id}"

    if context and context.debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise DeleteUserError(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def toggle_is_enable_user_direct_signon(
    auth: DomoAuth,
    user_ids: list[str],
    is_allow_dso: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Manage direct sign-on permissions for users.

    Args:
        auth: Authentication object
        user_ids: list of user IDs to modify
        is_allow_dso: Whether to allow direct sign-on (default: True)
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object confirming permission changes

    Raises:
        User_CRUD_Error: If direct sign-on permission update fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users/directSignOn"
    params = {"value": is_allow_dso}

    if context and context.debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=user_ids if isinstance(user_ids, list) else [user_ids],
        params=params,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_CRUD_Error(operation="update_direct_signon", res=res)

    return res
