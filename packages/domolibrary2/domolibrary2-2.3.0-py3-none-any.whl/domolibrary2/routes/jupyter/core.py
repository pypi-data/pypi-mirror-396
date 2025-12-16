"""
Jupyter Core Functions

This module provides core Jupyter workspace retrieval and management functions.
"""

import urllib

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
    log_call,
)
from .exceptions import Jupyter_GET_Error, JupyterWorkspace_Error

__all__ = [
    "get_jupyter_workspaces",
    "get_jupyter_workspace_by_id",
    "start_jupyter_workspace",
    "parse_instance_service_location_and_prefix",
    "get_workspace_auth_token_params",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_jupyter_workspaces(
    auth: DomoAuth,
    return_raw: bool = False,
    debug_loop: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve all available Jupyter workspaces.

    Args:
        auth: Authentication object containing credentials and instance info
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        debug_loop: Enable detailed loop debugging
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing list of Jupyter workspaces

    Raises:
        Jupyter_GET_Error: If workspace retrieval fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/search/workspaces"

    body = {
        "limit": 50,
        "offset": 0,
        "sortFieldMap": {"CREATED": "DESC"},
        "filters": [],
    }

    def arr_fn(res):
        return res.response["workspaces"]

    offset_params = {"limit": "limit", "offset": "offset"}

    res = await gd.looper(
        url=url,
        method="POST",
        limit=50,
        body=body,
        auth=auth,
        arr_fn=arr_fn,
        offset_params_in_body=True,
        offset_params=offset_params,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Jupyter_GET_Error(
            message="Failed to retrieve Jupyter workspaces", res=res
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
async def get_jupyter_workspace_by_id(
    auth: DomoAuth,
    workspace_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve a specific Jupyter workspace by ID.

    Args:
        auth: Authentication object containing credentials and instance info
        workspace_id: Unique identifier for the workspace to retrieve
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing workspace details

    Raises:
        Jupyter_GET_Error: If workspace retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Jupyter_GET_Error(
            workspace_id=workspace_id,
            message=f"Failed to retrieve workspace {workspace_id}",
            res=res,
        )

    return res


def parse_instance_service_location_and_prefix(
    instance_dict: dict, domo_instance: str
) -> dict:
    """Parse service location and prefix from instance dictionary."""
    url = instance_dict["url"]

    query = urllib.parse.unquote(urllib.parse.urlparse(url).query)
    query = urllib.parse.urlparse(query.split("&")[1].replace("next=", ""))

    return {
        "service_location": query.netloc.replace(domo_instance, "")[1:],
        "service_prefix": query.path,
    }


async def get_workspace_auth_token_params(
    workspace_id: str, auth: DomoAuth, return_raw: bool = False
) -> rgd.ResponseGetData:
    """
    params are needed for authenticating requests inside the workspace environment
    Note: you'll also need a internally generated jupyter_token to authenticate requests
    returns { service_location , service_prefix}
    """
    res = await get_jupyter_workspace_by_id(workspace_id=workspace_id, auth=auth)

    open_instances = res.response.get("instances")

    if return_raw:
        return open_instances

    if not open_instances:
        raise JupyterWorkspace_Error(
            operation="get_auth_token",
            workspace_id=workspace_id,
            message="There are no open instances. Do you need to start the workspace?",
            res=res,
        )

    return parse_instance_service_location_and_prefix(
        open_instances[0], auth.domo_instance
    )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def start_jupyter_workspace(
    auth: DomoAuth,
    workspace_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Start a Jupyter workspace instance.

    Args:
        auth: Authentication object containing credentials and instance info
        workspace_id: Unique identifier for the workspace to start
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing workspace start result

    Raises:
        JupyterWorkspace_Error: If workspace start operation fails
        Jupyter_GET_Error: If workspace retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}/instances"

    try:
        res = await gd.get_data(
            url=url,
            method="POST",
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

    except RuntimeError as e:
        return rgd.ResponseGetData(
            status=500,
            response=f"starting workspace, please wait - {e}",
            is_success=False,
        )

    if res.status == 500 or res.status == 403:
        raise JupyterWorkspace_Error(
            operation="start",
            workspace_id=workspace_id,
            message=f"You may not have access to this workspace {workspace_id}, is it shared with you? Or may already be started",
            res=res,
        )

    if not res.is_success:
        raise JupyterWorkspace_Error(
            operation="start", workspace_id=workspace_id, res=res
        )

    res.response = "workspace started"
    return res
