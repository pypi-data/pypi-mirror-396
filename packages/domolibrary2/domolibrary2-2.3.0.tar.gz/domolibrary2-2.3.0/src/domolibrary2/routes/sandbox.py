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

__all__ = [
    "Sandbox_GET_Error",
    "Sandbox_CRUD_Error",
    "get_is_allow_same_instance_promotion_enabled",
    "toggle_allow_same_instance_promotion",
    "get_shared_repos",
    "get_repo_from_id",
]


class Sandbox_GET_Error(RouteError):
    """Raised when sandbox retrieval operations fail."""

    def __init__(
        self,
        repository_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Sandbox retrieval failed",
            entity_id=repository_id,
            res=res,
            **kwargs,
        )


class Sandbox_CRUD_Error(RouteError):
    """Raised when sandbox create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        repository_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Sandbox {operation} operation failed",
            entity_id=repository_id,
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
async def get_is_allow_same_instance_promotion_enabled(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/settings"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_GET_Error(res=res)

    res.response = {
        "name": "allow_same_instance_promotion",
        "is_enabled": res.response["allowSelfPromotion"],
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
async def toggle_allow_same_instance_promotion(
    auth: DomoAuth,
    is_enabled: bool,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Toggle the allow same instance promotion setting.

    Args:
        auth: Authentication object
        is_enabled: Whether to enable same instance promotion
        return_raw: Return raw response without processing
        context: Optional RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        Sandbox_CRUD_Error: If the operation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/settings"

    body = {"allowSelfPromotion": is_enabled}

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_CRUD_Error(operation="toggle same instance promotion", res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_shared_repos(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/search"

    body = {
        "query": {
            "offset": 0,
            "limit": 50,
            "fieldSearchMap": {},
            "sort": "lastCommit",
            "order": "desc",
            "filters": {"userId": None},
            "dateFilters": {},
        },
        "shared": False,
    }

    def arr_fn(res: rgd.ResponseGetData) -> list[dict]:
        return res.response["repositories"]

    offset_params = {"offset": "offset", "limit": "limit"}

    def body_fn(skip, limit, body):
        body["query"].update({"offset": skip, "limit": limit})
        return body

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        body_fn=body_fn,
        body=body,
        loop_until_end=True,
        offset_params=offset_params,
        offset_params_in_body=True,
        return_raw=return_raw,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_repo_from_id(
    auth: DomoAuth,
    repository_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get a sandbox repository by ID.

    Args:
        auth: Authentication object
        repository_id: Repository identifier
        return_raw: Return raw response without processing
        context: Optional RouteContext for request configuration

    Returns:
        ResponseGetData object

    Raises:
        Sandbox_GET_Error: If retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/{repository_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Sandbox_GET_Error(repository_id=repository_id, res=res)

    return res
