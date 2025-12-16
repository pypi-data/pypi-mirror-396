"""
Objectives__Goals Core Routes

Generated from Postman collection. Module: objectives__goals, Submodule: core
"""

import httpx

from ....auth import DomoAuth
from ....client import (
    get_data as gd,
    response as rgd,
)
from ....client.context import RouteContext


@gd.route_function
async def delete_category(
    auth: DomoAuth,
    id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
) -> rgd.ResponseGetData:
    """Delete Category

    DELETE /api/social/v1/objectives/tags/categories/{id}


    Args:
        auth: Authentication object
        session: HTTP client session (optional)
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop for debugging
        parent_class: Name of calling class for debugging
        return_raw: Return raw response without processing
        context: Route context (optional)

    Returns:
        rgd.ResponseGetData object

    Raises:
        httpx.HTTPStatusError: If the request fails
    """
    url = f"https://{auth.domo_instance}.domo.com/api/social/v1/objectives/tags/categories/{id}"

    res = await gd.get_data(auth=auth, url=url, method="DELETE", context=context)

    if return_raw:
        return res

    if not res.is_success:
        raise httpx.HTTPStatusError(
            f"Request failed with status {res.status}",
            request=res.request,
            response=res.response,
        )

    return res


__all__ = [
    "delete_category",
]
