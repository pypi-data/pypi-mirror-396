from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.convert import convert_string_to_bool
from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    ResponseGetDataProcessor,
    log_call,
)
from .exceptions import Config_CRUD_Error, Config_GET_Error

__all__ = [
    "ToggleConfig_CRUD_Error",
    "get_is_invite_social_users_enabled",
    "toggle_is_invite_social_users_enabled",
    "get_is_user_invite_notifications_enabled",
    "toggle_is_user_invite_enabled",
    "get_is_weekly_digest_enabled",
    "toggle_is_weekly_digest_enabled",
    "get_is_left_nav_enabled_v1",
    "get_is_left_nav_enabled",
    "toggle_is_left_nav_enabled_v1",
    "toggle_is_left_nav_enabled",
]


class ToggleConfig_CRUD_Error(Config_CRUD_Error):
    def __init__(self, res: rgd.ResponseGetData, message: str | None = None):
        super().__init__(res=res, message=message)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_is_invite_social_users_enabled(
    auth: DomoAuth,
    customer_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    # must pass the customer as the short form API endpoint (without customer_id) does not support a GET request
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v3/customers/features/free-invite"

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/customers/{customer_id}/features/free-invite"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Config_GET_Error(
            res=res,
        )

    res.response = {"name": "free-invite", "is_enabled": res.response["enabled"]}

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def toggle_is_invite_social_users_enabled(
    auth: DomoAuth,
    customer_id: str,
    is_enabled: bool,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Toggle whether social users can be invited to the instance.

    Args:
        auth: Authentication object
        customer_id: Customer ID for the instance
        is_enabled: True to enable social user invites, False to disable
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData with the updated configuration
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/customers/{customer_id}/features/free-invite"

    body = {"enabled": is_enabled}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise ToggleConfig_CRUD_Error(
            res=res,
            message=f"Failed to toggle social user invites to {is_enabled}",
        )

    res.response = {"name": "free-invite", "is_enabled": is_enabled}

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_is_user_invite_notifications_enabled(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/user.invite.email.enabled"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Config_GET_Error(res=res)

    res.response = {
        "name": "user.invite.email.enabled",
        "is_enabled": (
            convert_string_to_bool(res.response.get("value", False))
            if isinstance(res.response, dict)
            else False
        ),
    }

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def toggle_is_user_invite_enabled(
    auth: DomoAuth,
    is_enabled: bool,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Admin > Company Settings > Notifications
    """

    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/user.invite.email.enabled"

    body = {"value": is_enabled}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if not res.is_success:
        raise ToggleConfig_CRUD_Error(res=res, message=str(res.response))

    if return_raw:
        return res

    return await get_is_user_invite_notifications_enabled(
        auth=auth,
        context=context,
    )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_is_weekly_digest_enabled(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/come-back-to-domo-all-users"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if res.status == 404 and res.response == "Not Found":
        raise Config_CRUD_Error(res=res)

    if not res.is_success:
        raise Config_CRUD_Error(res=res)

    res.response = {
        "is_enabled": convert_string_to_bool(res.response["value"]),
        "feature": "come-back-to-domo-all-users",
    }

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def toggle_is_weekly_digest_enabled(
    auth: DomoAuth,
    is_enabled: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/come-back-to-domo-all-users"

    body = {"name": "come-back-to-domo-all-users", "value": is_enabled}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Config_CRUD_Error(res=res)

    return await get_is_weekly_digest_enabled(
        auth=auth,
        context=context,
    )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_is_left_nav_enabled_v1(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """
    2025-09-15 -- deprecated
    """

    url = f"https://{auth.domo_instance}.domo.com/api/nav/v1/leftnav/customer"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Config_GET_Error(res=res)

    res.response = {
        "is_enabled": res.response or False,
        "feature": "use-left-nav",
    }

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_is_left_nav_enabled(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """
    2025-09-15 current version of leftnav enabled
    """

    url = f"https://{auth.domo_instance}.domo.com/api/nav/v1/leftnav/enabled"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Config_GET_Error(res=res)

    res.response = {
        "is_enabled": res.response or False,
        "feature": "use-left-nav",
    }

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def toggle_is_left_nav_enabled_v1(
    auth: DomoAuth,
    is_use_left_nav: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """
    2025-09-15 -- deprecated
    """

    url = f"https://{auth.domo_instance}.domo.com/api/nav/v1/leftnav/customer"

    params = {"use-left-nav": is_use_left_nav}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        params=params,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise ToggleConfig_CRUD_Error(res=res)

    res.response = {
        "is_enabled": res.response,
        "feature": "use-left-nav",
    }

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def toggle_is_left_nav_enabled(
    auth: DomoAuth,
    is_use_left_nav: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """
    2025-09-15 -- switched to new leftnav API
    """

    url = f"https://{auth.domo_instance}.domo.com/api/nav/v1/leftnav/customer-settings"

    if is_use_left_nav:
        body = {"enabled": "CUSTOMER"}
    else:
        body = {"enabled": "NONE"}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise ToggleConfig_CRUD_Error(res=res)

    res.response = {
        "is_enabled": res.response,
        "feature": "use-left-nav",
    }

    return res
