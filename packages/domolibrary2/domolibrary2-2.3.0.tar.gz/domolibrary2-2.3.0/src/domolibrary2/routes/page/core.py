"""
Page Core Functions

This module provides core page retrieval and definition functions.

Functions:
    get_pages_adminsummary: Retrieve all pages visible to the user
    get_page_by_id: Retrieve a specific page by ID
    get_page_definition: Retrieve detailed page definition
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
from .exceptions import Page_GET_Error, SearchPageNotFoundError

__all__ = [
    "get_pages_adminsummary",
    "get_page_by_id",
    "get_page_definition",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_pages_adminsummary(
    auth: DomoAuth,
    search_title: str | None = None,
    page_parent_id: str | None = None,
    body: dict | None = None,
    limit: int = 35,
    debug_loop: bool = False,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve all pages in instance that user is able to see.

    Args:
        auth: Authentication object containing credentials and instance info
        search_title: Optional title search filter
        page_parent_id: Optional parent page ID filter
        body: Optional custom request body
        limit: Maximum number of results per request (default: 35)
        debug_loop: Enable loop debugging output
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing pages information

    Raises:
        Page_GET_Error: If page retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/pages/adminsummary"

    offset_params = {
        "offset": "skip",
        "limit": "limit",
    }

    body = body or {"orderBy": "pageTitle", "ascending": True}

    if search_title:
        body.update(
            {"includePageTitleClause": True, "pageTitleSearchText": search_title}
        )

    if page_parent_id:
        body.update(
            {"includeParentPageIdsClause": True, "parentPageIds": [page_parent_id]}
        )

    def arr_fn(res) -> list[dict]:
        return res.response.get("pageAdminSummaries")

    # Build/merge RouteContext via decorator; use it for looper call
    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        loop_until_end=True,
        body=body,
        limit=limit,
        debug_loop=debug_loop,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Page_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_page_by_id(
    auth: DomoAuth,
    page_id: str,
    include_layout: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve a specific page by ID.

    Args:
        auth: Authentication object containing credentials and instance info
        page_id: Unique identifier for the page
        include_layout: Include page layout information in response
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing page information

    Raises:
        Page_GET_Error: If page retrieval fails
        SearchPageNotFoundError: If page with specified ID doesn't exist
    """

    # 9/21/2023 - the domo UI uses /cards to get page info
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/stacks/{page_id}/cards"

    if include_layout:
        url += "?includeV4PageLayouts=true"

    # Use RouteContext for logging, caching, and session configuration
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchPageNotFoundError(
                search_criteria=f"page_id: {page_id}",
                res=res,
            )
        raise Page_GET_Error(page_id=page_id, res=res)

    if not isinstance(res.response, dict) or not res.response.get("id", None):
        raise Page_GET_Error(
            page_id=page_id,
            message="Invalid page response format",
            res=res,
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
async def get_page_definition(
    auth: DomoAuth,
    page_id: int | str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve detailed page definition including metadata and layout.

    Args:
        auth: Authentication object containing credentials and instance info
        page_id: Unique identifier for the page
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing detailed page information

    Raises:
        Page_GET_Error: If page definition retrieval fails
        SearchPageNotFoundError: If page with specified ID doesn't exist
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/stacks/{page_id}/cards"

    params = {
        "includeV4PageLayouts": "true",
        "parts": "metadata,datasources,library,drillPathURNs,certification,owners,dateInfo,subscriptions,slicers",
    }

    res = await gd.get_data(
        url,
        method="GET",
        auth=auth,
        params=params,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchPageNotFoundError(
                search_criteria=f"page_id: {page_id}",
                res=res,
            )
        raise Page_GET_Error(page_id=str(page_id), res=res)

    if not isinstance(res.response, dict) or not res.response.get("id", None):
        raise Page_GET_Error(
            page_id=str(page_id),
            message="Invalid page definition response format",
            res=res,
        )

    return res
