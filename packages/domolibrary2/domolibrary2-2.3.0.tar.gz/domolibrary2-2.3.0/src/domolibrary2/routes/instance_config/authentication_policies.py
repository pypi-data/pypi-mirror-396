"""Authentication policy configuration routes for Domo instance settings."""

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    ResponseGetDataProcessor,
    log_call,
)
from .exceptions import Config_CRUD_Error, Config_GET_Error

__all__ = [
    "GetPasswordReuseHistoryError",
    "get_password_reuse_history",
    "set_password_reuse_history",
    "toggle_password_reuse_history",
]


class GetPasswordReuseHistoryError(Config_GET_Error):
    """Raised when retrieving password reuse history policy fails."""

    def __init__(self, res: rgd.ResponseGetData, message: str = ""):
        super().__init__(res=res, message=message)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_password_reuse_history(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get the password reuse history policy setting.

    This determines how many previous passwords are remembered and cannot be reused.

    Args:
        auth: DomoAuth authentication object
        return_raw: If True, return raw ResponseGetData object

    Returns:
        ResponseGetData with the password reuse history value (int) in response field,
        or raw ResponseGetData if return_raw=True

    Raises:
        GetPasswordReuseHistoryError: If the API call fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/domo.policy.password_reuse_history"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GetPasswordReuseHistoryError(res=res)

    # Parse the value from the response
    if isinstance(res.response, dict) and "value" in res.response:
        try:
            res.response = int(res.response["value"])
        except (ValueError, TypeError):
            res.response = res.response["value"]

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def set_password_reuse_history(
    auth: DomoAuth,
    history_count: int,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Set the password reuse history policy setting.

    This determines how many previous passwords are remembered and cannot be reused.
    Setting history_count to 0 disables password reuse history checking entirely.

    Args:
        auth: DomoAuth authentication object
        history_count: Number of previous passwords to remember (0-10).
                      Set to 0 to disable password reuse history checking.
        return_raw: If True, return raw ResponseGetData object

    Returns:
        ResponseGetData with the updated password reuse history value in response field

    Raises:
        Config_CRUD_Error: If the API call fails

    Example:
        # Disable password reuse history
        await set_password_reuse_history(auth=auth, history_count=0)

        # Remember last 5 passwords
        await set_password_reuse_history(auth=auth, history_count=5)
    """
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/domo.policy.password_reuse_history"

    body = {
        "name": "domo.policy.password_reuse_history",
        "value": str(history_count),
    }

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

    # Return the updated value
    return await get_password_reuse_history(
        auth=auth,
        context=context,
    )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def toggle_password_reuse_history(
    auth: DomoAuth,
    is_enable_history: bool,
    history_count: int = 10,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Enable or disable password reuse history checking.

    When enabled, the specified number of previous passwords are remembered and
    cannot be reused. When disabled, users can reuse any previous password.

    Args:
        auth: DomoAuth authentication object
        is_enable_history: If True, enable history checking with history_count.
                          If False, disable history checking (sets to 0).
        history_count: Number of previous passwords to remember when enabling (default: 10).
                      Ignored when is_enable_history=False.
        return_raw: If True, return raw ResponseGetData object

    Returns:
        ResponseGetData with the updated password reuse history value

    Raises:
        Config_CRUD_Error: If the API call fails

    Example:
        # Disable password reuse history checking
        await toggle_password_reuse_history(auth=auth, is_enable_history=False)

        # Enable with default (remember last 10 passwords)
        await toggle_password_reuse_history(auth=auth, is_enable_history=True)

        # Enable with custom count (remember last 5 passwords)
        await toggle_password_reuse_history(auth=auth, is_enable_history=True, history_count=5)
    """

    count = history_count if is_enable_history else 0
    return await set_password_reuse_history(
        auth=auth,
        history_count=count,
        return_raw=return_raw,
        context=context,
    )
