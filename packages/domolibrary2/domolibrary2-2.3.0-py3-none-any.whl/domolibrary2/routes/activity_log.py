from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

"""routes for interacting with the activity log"""

from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext

__all__ = [
    "ActivityLog_GET_Error",
    "get_activity_log_object_types",
    "search_activity_log",
]


class ActivityLog_GET_Error(RouteError):
    """Raised when activity log retrieval operations fail."""

    def __init__(self, message: str | None = None, res=None, **kwargs):
        super().__init__(
            message=message or "Activity log retrieval failed",
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
async def get_activity_log_object_types(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """retrieves a list of valid objectTypes that can be used to search the activity_log API"""

    url = f"https://{auth.domo_instance}.domo.com/api/audit/v1/user-audits/objectTypes"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        context=context,
    )

    if not res.is_success:
        raise ActivityLog_GET_Error(
            message="Failed to get activity log object types", res=res
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
async def search_activity_log(
    auth: DomoAuth,
    start_time: int,  # epoch time in milliseconds
    end_time: int,  # epoch time in milliseconds
    maximum: int | None = None,
    object_type: str | None = None,
    debug_loop: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """loops over activity log api to retrieve audit logs"""

    url = f"https://{auth.domo_instance}.domo.com/api/audit/v1/user-audits"

    if object_type and object_type != "ACTIVITY_LOG":
        url = f"{url}/objectTypes/{object_type}"

    fixed_params = {"end": end_time, "start": start_time}

    offset_params = {
        "offset": "offset",
        "limit": "limit",
    }

    def arr_fn(res) -> list[dict]:
        return res.response

    res = await gd.looper(
        auth=auth,
        method="GET",
        url=url,
        arr_fn=arr_fn,
        fixed_params=fixed_params,
        offset_params=offset_params,
        maximum=maximum,
        limit=1000,
        debug_loop=debug_loop,
        context=context,
    )

    if not res.is_success:
        raise ActivityLog_GET_Error(res=res)

    return res
