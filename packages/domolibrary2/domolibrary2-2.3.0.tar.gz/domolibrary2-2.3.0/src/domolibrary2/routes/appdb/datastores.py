from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

"""
AppDb Datastore Functions

This module provides functions for managing Domo AppDb datastores including
retrieval and creation operations.

Functions:
    get_datastores: Retrieve all datastores
    get_datastore_by_id: Retrieve a specific datastore by ID
    get_collections_from_datastore: Get collections from a specific datastore
    create_datastore: Create a new datastore
"""

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from .exceptions import AppDb_CRUD_Error, AppDb_GET_Error, SearchAppDbNotFoundError

__all__ = [
    "get_datastores",
    "get_datastore_by_id",
    "get_collections_from_datastore",
    "create_datastore",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_datastores(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve all datastores.

    Args:
        auth: Authentication object containing credentials and instance info
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing datastores information

    Raises:
        AppDb_GET_Error: If datastores retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_datastore_by_id(
    auth: DomoAuth,
    datastore_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve a specific datastore by ID.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_id: Unique identifier for the datastore
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing datastore information

    Raises:
        AppDb_GET_Error: If datastore retrieval fails
        SearchAppDbNotFoundError: If datastore with specified ID doesn't exist
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/{datastore_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchAppDbNotFoundError(
                search_criteria=f"datastore_id: {datastore_id}",
                res=res,
            )
        raise AppDb_GET_Error(appdb_id=datastore_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_collections_from_datastore(
    auth: DomoAuth,
    datastore_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get collections from a specific datastore.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_id: Unique identifier for the datastore
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing collections information

    Raises:
        AppDb_GET_Error: If collections retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/{datastore_id}/collections"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_GET_Error(appdb_id=datastore_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_datastore(
    auth: DomoAuth,
    datastore_name: str | None = None,  # in UI shows up as appName
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Create a new datastore.

    Args:
        auth: Authentication object containing credentials and instance info
        datastore_name: Name for the new datastore (shows as appName in UI)
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing created datastore information

    Raises:
        AppDb_CRUD_Error: If datastore creation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/"

    body = {"name": datastore_name}

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
        raise AppDb_CRUD_Error(operation="create", res=res)

    return res
