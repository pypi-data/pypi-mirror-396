"""
Jupyter Configuration Functions

This module provides functions for managing Jupyter workspace configuration.
"""

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
from .exceptions import Jupyter_CRUD_Error, SearchJupyterNotFoundError

__all__ = [
    "update_jupyter_workspace_config",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_jupyter_workspace_config(
    auth: DomoAuth,
    workspace_id: str,
    config: dict,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Update the configuration of a Jupyter workspace.

    Args:
        auth: Authentication object containing credentials and instance info
        workspace_id: Unique identifier for the workspace to configure
        config: Configuration dictionary to update the workspace with
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing configuration update result

    Raises:
        Jupyter_CRUD_Error: If workspace configuration update fails
        SearchJupyterNotFoundError: If workspace doesn't exist
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}"

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=config,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"workspace_id: {workspace_id}", res=res
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(
            operation="update_config",
            workspace_id=workspace_id,
            message=f"Error updating workspace configuration for {workspace_id}",
            res=res,
        )

    return res
