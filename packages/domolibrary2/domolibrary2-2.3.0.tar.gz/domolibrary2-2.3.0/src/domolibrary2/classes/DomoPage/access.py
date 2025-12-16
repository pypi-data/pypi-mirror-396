"""Page access control and sharing operations."""

__all__ = ["test_page_access", "get_accesslist", "share"]


import httpx

from ...auth import DomoAuth
from ...client.context import RouteContext
from ...client.response import ResponseGetData
from ...routes import (
    datacenter as datacenter_routes,
    page as page_routes,
)
from ...utils import chunk_execution as dmce
from .. import DomoUser as dmu
from .exceptions import Page_NoAccess


async def test_page_access(
    self,
    suppress_no_access_error: bool = False,
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_num_stacks_to_drop: int = 2,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    """Test if the authenticated user has access to the page.

    This method calls the page access test API endpoint which returns the page owners.
    If the user doesn't have access, it raises a Page_NoAccess exception unless suppressed.

    Args:
        suppress_no_access_error: If True, suppresses the Page_NoAccess exception when
            user doesn't have access. Defaults to False.
        debug_api: Enable detailed API request/response logging. Defaults to False.
        return_raw: Return raw ResponseGetData without processing. Defaults to False.
        session: Optional httpx client session for connection reuse.
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output. Defaults to 2.
        context: Optional RouteContext for API call configuration
        **context_kwargs: Additional context parameters

    Returns:
        ResponseGetData object containing page access information and owner list.

    Raises:
        Page_NoAccess: If user doesn't have access and suppress_no_access_error is False.
    """
    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    res = await page_routes.get_page_access_test(
        auth=self.auth,
        page_id=self.id,
        context=context,
    )

    if return_raw:
        return res

    try:
        page_access = res.response.get("pageAccess")

        if not page_access:
            raise Page_NoAccess(
                page_id=self.id,
                page_title=self.title,
                domo_instance=self.auth.domo_instance,
                function_name="test_page_access",
                parent_class=self.__class__.__name__,
            )

    except Page_NoAccess as e:
        print(e)

        if not suppress_no_access_error:
            raise e

    return res


async def get_accesslist(
    self,
    auth: DomoAuth | None = None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    debug_num_stacks_to_drop: int = 2,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData | dict[str, int | list]:
    """Retrieve the access list for the page showing users and groups with access.

    This method fetches the comprehensive access list for a page, including:
    - Users with explicit share permissions
    - Groups with access permissions
    - User ownership information (direct or through group membership)
    - Group ownership information

    Args:
        auth: Authentication object. If not provided, uses self.auth.
        return_raw: Return raw ResponseGetData without processing. Defaults to False.
        debug_api: Enable detailed API request/response logging. Defaults to False.
        session: Optional httpx client session for connection reuse.
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output. Defaults to 2.
        context: Optional RouteContext for API call configuration
        **context_kwargs: Additional context parameters

    Returns:
        If return_raw is True:
            ResponseGetData object containing raw access list data.
        If return_raw is False:
            Dictionary containing:
                - explicit_shared_user_count (int): Number of users with explicit shares
                - total_user_count (int): Total number of users with access
                - domo_users (list[DomoUser]): list of users with access, enriched with:
                    - custom_attributes['is_explicit_share']: True if directly shared
                    - custom_attributes['group_membership']: list of groups user belongs to
                    - custom_attributes['is_owner']: True if user is an owner
                - domo_groups (list[DomoGroup]): list of groups with access, enriched with:
                    - custom_attributes['is_owner']: True if group is an owner

    Raises:
        PageSharing_Error: If access list retrieval fails (raised by route function).
        SearchPageNotFoundError: If page with specified ID doesn't exist (raised by route function).
    """
    auth = auth or self.auth

    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    res = await page_routes.get_page_access_list(
        auth=auth,
        is_expand_users=True,
        page_id=self.id,
        context=context,
    )

    if return_raw:
        return res

    from ..DomoGroup import core as dmg

    s = {
        "explicit_shared_user_count": res.response.get("explicitSharedUserCount"),
        "total_user_count": res.response.get("totalUserCount"),
    }

    user_ls = res.response.get("users", None)
    domo_users = []

    if user_ls and isinstance(user_ls, list) and len(user_ls) > 0:
        domo_users_manager = dmu.DomoUsers(auth=auth)
        domo_users = await domo_users_manager.search_by_id(
            user_ids=[user.get("id") for user in user_ls],
            only_allow_one=False,
            suppress_no_results_error=True,
        )

    group_ls = res.response.get("groups", None)
    domo_groups = []
    if group_ls and isinstance(group_ls, list) and len(group_ls) > 0:
        domo_groups = await dmce.gather_with_concurrency(
            n=60,
            *[
                dmg.DomoGroup.get_by_id(
                    group_id=group.get("id"),
                    auth=auth,
                    context=context,
                )
                for group in group_ls
            ],
        )

    res = await self.test_page_access(suppress_no_access_error=True, context=context)
    owner_ls = res.response["owners"]  # from test_page_access

    for domo_user in domo_users:
        # isExplicitShare is set by the get_access_list API response
        domo_user.custom_attributes["is_explicit_share"] = next(
            obj["isExplicitShare"]
            for obj in user_ls
            if int(obj.get("id")) == int(domo_user.id)
        )

        # group membership is determined by get_access_list API response
        domo_user.custom_attributes["group_membership"] = [
            domo_group
            for group_obj in group_ls
            for domo_group in domo_groups
            if int(domo_user.id) in [int(obj["id"]) for obj in group_obj.get("users")]
            and domo_group.id == group_obj["id"]
        ]

        # isOwner determined by test_access API response and group membership
        domo_user.custom_attributes["is_owner"] = False

        # test ownership as a user
        match_owner = next(
            (
                owner_obj
                for owner_obj in owner_ls
                if int(owner_obj["id"]) == int(domo_user.id)
                and owner_obj["type"] == "USER"
            ),
            None,
        )

        match_group = next(
            (
                owner_obj
                for owner_obj in owner_ls
                if int(owner_obj["id"])
                in [
                    int(domo_group.id)
                    for domo_group in domo_user.custom_attributes["group_membership"]
                ]
                and owner_obj["type"] == "GROUP"
            ),
            None,
        )

        if match_owner or match_group:
            domo_user.custom_attributes["is_owner"] = True

    # group ownership is confirmed test_access API
    for domo_group in domo_groups:
        match_owner = next(
            (
                owner_obj
                for owner_obj in owner_ls
                if int(owner_obj["id"]) == int(domo_group.id)
                and owner_obj["type"] == "GROUP"
            ),
            None,
        )

        domo_group.custom_attributes["is_owner"] = True if match_owner else False

    return {
        **s,
        "domo_users": domo_users,
        "domo_groups": domo_groups,
    }


async def share(
    self,
    auth: DomoAuth | None = None,
    domo_users: list | object | None = None,
    domo_groups: list | object | None = None,
    message: str | None = None,
    debug_api: bool = False,
    session: httpx.AsyncClient | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> ResponseGetData:
    """Share the page with specified users and/or groups.

    This method shares the page with one or more users and/or groups. It uses the
    datacenter share_resource route function to perform the sharing operation.

    Args:
        auth: Authentication object. If not provided, uses self.auth.
        domo_users: DomoUser object(s) to share page with. Can be a single DomoUser
            or a list of DomoUser objects. Defaults to None.
        domo_groups: DomoGroup object(s) to share page with. Can be a single DomoGroup
            or a list of DomoGroup objects. Defaults to None.
        message: Optional message to include in the automated email notification.
        debug_api: Enable detailed API request/response logging. Defaults to False.
        session: Optional httpx client session for connection reuse.
        context: Optional RouteContext for API call configuration
        **context_kwargs: Additional context parameters

    Returns:
        ResponseGetData object containing the sharing operation result.

    Raises:
        Exception: Various exceptions may be raised by the datacenter share_resource
            route function if the sharing operation fails.
    """
    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    if domo_groups:
        domo_groups = domo_groups if isinstance(domo_groups, list) else [domo_groups]
    if domo_users:
        domo_users = domo_users if isinstance(domo_users, list) else [domo_users]

    res = await datacenter_routes.share_resource(
        auth=auth or self.auth,
        resource_ids=[self.id],
        resource_type=datacenter_routes.ShareResource_Enum.PAGE,
        group_ids=[group.id for group in domo_groups] if domo_groups else None,
        user_ids=[user.id for user in domo_users] if domo_users else None,
        message=message,
        context=context,
    )

    return res
