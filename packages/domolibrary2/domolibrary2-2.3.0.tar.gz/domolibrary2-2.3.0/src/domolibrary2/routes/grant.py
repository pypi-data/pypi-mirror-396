from ..auth import DomoAuth
from ..base.exceptions import RouteError
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

__all__ = ["Grant_GET_Error", "get_grants"]


class Grant_GET_Error(RouteError):
    """Raised when grant retrieval operations fail."""

    def __init__(self, message: str | None = None, res=None, **kwargs):
        super().__init__(
            message=message or "Grant retrieval failed",
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
async def get_grants(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/authorities"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise Grant_GET_Error(res=res)

    if len(res.response) == 0:
        raise Grant_GET_Error(
            message=f"{len(res.response)} grants returned",
            res=res,
        )

    return res
