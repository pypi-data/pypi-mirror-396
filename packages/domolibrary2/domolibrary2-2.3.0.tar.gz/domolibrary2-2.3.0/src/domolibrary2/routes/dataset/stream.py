from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "Stream_GET_Error",
    "Stream_CRUD_Error",
    "get_streams",
    "get_stream_by_id",
    "update_stream",
    "create_stream",
    "execute_stream",
]


from ...auth import DomoAuth
from ...base.exceptions import RouteError
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext

__all__ = [
    "Stream_GET_Error",
    "Stream_CRUD_Error",
    "get_streams",
    "get_stream_by_id",
    "update_stream",
    "create_stream",
    "execute_stream",
]


class Stream_GET_Error(RouteError):
    """Raised when stream retrieval operations fail."""

    def __init__(
        self,
        stream_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Stream retrieval failed",
            entity_id=stream_id,
            res=res,
            **kwargs,
        )


class Stream_CRUD_Error(RouteError):
    """Raised when stream create, update, delete, or execute operations fail."""

    def __init__(
        self,
        operation: str,
        stream_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Stream {operation} operation failed",
            entity_id=stream_id,
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
async def get_streams(
    auth: DomoAuth,
    loop_until_end: bool = True,
    debug_loop: bool = False,
    return_raw: bool = False,
    skip: int = 0,
    maximum: int = 1000,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    streams do not appear to be recycled, not recommended for use as will return a virtually limitless number of streams
    instead use get_stream_by_id
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/"

    def arr_fn(res):
        return res.response

    res = await gd.looper(
        auth=auth,
        url=url,
        offset_params={"limit": "limit", "offset": "offet"},
        arr_fn=arr_fn,
        loop_until_end=loop_until_end,
        method="GET",
        offset_params_in_body=False,
        limit=500,
        skip=skip,
        maximum=maximum,
        debug_loop=debug_loop,
        context=context,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_stream_by_id(
    auth: DomoAuth,
    stream_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get a stream by its ID.

    Args:
        auth: Authentication object
        stream_id: Unique stream identifier
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        Stream_GET_Error: If retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_GET_Error(stream_id=stream_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_stream(
    auth: DomoAuth,
    stream_id: str,
    body: dict,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Update a stream configuration.

    Args:
        auth: Authentication object
        stream_id: Unique stream identifier
        body: Stream configuration data
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        Stream_CRUD_Error: If update operation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body,
        method="PUT",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_CRUD_Error(operation="update", stream_id=stream_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_stream(
    auth: DomoAuth,
    body: dict,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Create a new stream.

    Args:
        auth: Authentication object
        body: Stream configuration data
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        Stream_CRUD_Error: If create operation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=body,
        method="POST",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_CRUD_Error(operation="create", res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def execute_stream(
    auth: DomoAuth,
    stream_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Execute a stream to run data import.

    Args:
        auth: Authentication object
        stream_id: Unique stream identifier
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        Stream_CRUD_Error: If execute operation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}/executions"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Stream_CRUD_Error(operation="execute", stream_id=stream_id, res=res)

    return res
