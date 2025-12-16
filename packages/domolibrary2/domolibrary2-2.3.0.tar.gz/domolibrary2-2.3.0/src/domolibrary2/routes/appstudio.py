from ..auth import DomoAuth
from ..base import exceptions as dmde
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "AppStudio_GET_Error",
    "AppStudio_CRUD_Error",
    "AppStudioSharing_Error",
    "get_appstudio_by_id",
    "get_appstudio_access",
    "get_appstudios_adminsummary",
    "generate_body_add_page_owner_appstudios",
    "generate_body_share_appstudio",
    "add_page_owner",
    "share",
]


class AppStudio_GET_Error(dmde.RouteError):
    """Raised when AppStudio retrieval operations fail."""

    def __init__(
        self,
        appstudio_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message or "AppStudio retrieval failed",
            entity_id=appstudio_id,
            res=res,
            **kwargs,
        )


class AppStudio_CRUD_Error(dmde.RouteError):
    """Raised when AppStudio create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str = "operation",
        appstudio_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"AppStudio {operation} operation failed",
            entity_id=appstudio_id,
            res=res,
            **kwargs,
        )


class AppStudioSharing_Error(dmde.RouteError):
    """Raised when AppStudio sharing operations fail."""

    def __init__(
        self,
        appstudio_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message or "AppStudio sharing operation failed",
            entity_id=appstudio_id,
            res=res,
            **kwargs,
        )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_appstudio_by_id(
    auth: DomoAuth,
    appstudio_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieves an AppStudio page by ID.

    Args:
        auth: Authentication object
        appstudio_id: AppStudio identifier
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        AppStudio_GET_Error: If retrieval fails
    """

    # 9/21/2023 - the domo UI uses /cards to get page info
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/dataapps/{appstudio_id}?authoring=true&includeHiddenViews=true"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppStudio_GET_Error(
            appstudio_id=appstudio_id,
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_appstudio_access(
    auth: DomoAuth,
    appstudio_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieves access list for an AppStudio page.

    Args:
        auth: Authentication object
        appstudio_id: AppStudio identifier
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing users and groups the page is shared with

    Raises:
        AppStudio_GET_Error: If retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/dataapps/{appstudio_id}/access"

    res = await gd.get_data(
        url,
        method="GET",
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppStudio_GET_Error(
            appstudio_id=appstudio_id,
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_appstudios_adminsummary(
    auth: DomoAuth,
    limit: int = 35,
    debug_loop: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieves all AppStudio pages in instance user is able to see.

    Args:
        auth: Authentication object
        limit: Maximum number of items per page
        debug_loop: Enable loop debugging
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing all accessible AppStudio pages

    Raises:
        AppStudio_GET_Error: If retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/dataapps/adminsummary"

    offset_params = {
        "offset": "skip",
        "limit": "limit",
    }

    body = {"orderBy": "title", "ascending": True}

    def arr_fn(res):
        return res.response.get("dataAppAdminSummaries")

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        loop_until_end=True,
        body=body,
        limit=limit,
        context=context,
        debug_loop=debug_loop,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppStudio_GET_Error(res=res)

    return res


def generate_body_add_page_owner_appstudios(
    appstudio_id_ls: list[int],
    group_id_ls: list[int] | None = None,
    user_id_ls: list[int] | None = None,
    note: str = "",
    send_email: bool = False,
) -> dict:
    """Generates request body for adding page owners to AppStudio pages.

    Args:
        appstudio_id_ls: list of AppStudio IDs
        group_id_ls: Optional list of group IDs
        user_id_ls: Optional list of user IDs
        note: Optional note to include
        send_email: Whether to send email notifications

    Returns:
        Dictionary containing the request body
    """
    group_id_ls = group_id_ls or []
    user_id_ls = user_id_ls or []
    owners = []

    for group in group_id_ls:
        owners.append({"id": group, "type": "GROUP"})
    for user in user_id_ls:
        owners.append({"id": user, "type": "USER"})

    body = {
        "entityIds": appstudio_id_ls,
        "owners": owners,
        "note": note,
        "sendEmail": send_email,
    }

    return body


def generate_body_share_appstudio(
    appstudio_ids: list[int],
    group_ids: list[int] | None = None,
    user_ids: list[int] | None = None,
    message: str | None = None,
) -> dict:
    """Generates request body for sharing AppStudio pages.

    Args:
        appstudio_ids: list of AppStudio IDs to share
        group_ids: Optional list of group IDs
        user_ids: Optional list of user IDs
        message: Optional message to include

    Returns:
        Dictionary containing the request body
    """
    group_ids = group_ids or []
    user_ids = user_ids or []

    appstudio_ids = (
        appstudio_ids if isinstance(appstudio_ids, list) else [appstudio_ids]
    )
    if group_ids:
        group_ids = (
            group_ids and group_ids if isinstance(group_ids, list) else [group_ids]
        )

    if user_ids:
        user_ids = user_ids if isinstance(user_ids, list) else [user_ids]

    recipient_ls = []

    if group_ids:
        for gid in group_ids:
            recipient_ls.append({"type": "group", "id": str(gid)})

    if user_ids:
        for uid in user_ids:
            recipient_ls.append({"type": "user", "id": str(uid)})

    body = {
        "dataAppIds": appstudio_ids,
        "recipients": recipient_ls,
        "message": message,
    }

    return body


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def add_page_owner(
    auth: DomoAuth,
    appstudio_id_ls: list[int],
    group_id_ls: list[int] | None = None,
    user_id_ls: list[int] | None = None,
    note: str = "",
    send_email: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Adds page owners to AppStudio pages.

    Args:
        auth: Authentication object
        appstudio_id_ls: list of AppStudio IDs
        group_id_ls: Optional list of group IDs to add as owners
        user_id_ls: Optional list of user IDs to add as owners
        note: Optional note to include with the change
        send_email: Whether to send email notifications
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        AppStudioSharing_Error: If sharing operation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/dataapps/bulk/owners"

    body = generate_body_add_page_owner_appstudios(
        appstudio_id_ls=appstudio_id_ls,
        group_id_ls=group_id_ls,
        user_id_ls=user_id_ls,
        note=note,
        send_email=send_email,
    )

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppStudioSharing_Error(res=res)

    res.response = f"{appstudio_id_ls} appstudios successfully shared with {', '.join([recipient['id'] for recipient in body['owners']])} as owners"

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def share(
    auth: DomoAuth,
    appstudio_ids: list[int],
    group_ids: list[int] | None = None,
    user_ids: list[int] | None = None,
    message: str | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Shares AppStudio pages with users or groups.

    Args:
        auth: Authentication object
        appstudio_ids: list of AppStudio IDs to share
        group_ids: Optional list of group IDs to share with
        user_ids: Optional list of user IDs to share with
        message: Optional message to include in email notification
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        AppStudioSharing_Error: If sharing operation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/dataapps/share?sendEmail=false"

    body = generate_body_share_appstudio(
        appstudio_ids=appstudio_ids,
        group_ids=group_ids,
        user_ids=user_ids,
        message=message,
    )

    res = await gd.get_data(
        url,
        method="POST",
        auth=auth,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppStudioSharing_Error(res=res)

    res.response = f"{appstudio_ids} appstudios successfully shared with {', '.join([recipient['id'] for recipient in body['recipients']])}"

    return res
