"""
BeastMode Route Functions

This module provides functions for managing Domo BeastModes (calculated fields)
including search, retrieval, locking operations, and finding BeastModes associated
with cards, datasets, and pages.

Functions:
    search_beastmodes: Search for BeastModes with filters
    lock_beastmode: Lock or unlock a BeastMode
    get_beastmode_by_id: Retrieve a specific BeastMode by ID
    get_card_beastmodes: Get BeastModes associated with a card
    get_dataset_beastmodes: Get BeastModes associated with a dataset
    get_page_beastmodes: Get BeastModes associated with a page
    generate_beastmode_body: Utility function for building search request body

Exception Classes:
    BeastMode_GET_Error: Raised when BeastMode retrieval fails
    BeastMode_CRUD_Error: Raised when BeastMode create/update/delete operations fail
    SearchBeastModeNotFoundError: Raised when BeastMode search returns no results
"""

from enum import Enum

from ..auth import DomoAuth
from ..base.base import DomoEnumMixin
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext
from ..utils import chunk_execution as dmce
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "BeastMode_GET_Error",
    "BeastMode_CRUD_Error",
    "SearchBeastModeNotFoundError",
    "Search_BeastModeLink",
    "generate_beastmode_body",
    "search_beastmodes",
    "lock_beastmode",
    "get_beastmode_by_id",
    "get_card_beastmodes",
    "get_dataset_beastmodes",
    "get_page_beastmodes",
    # Legacy export for backward compatibility
    "BeastModes_API_Error",
]


class BeastMode_GET_Error(RouteError):
    """
    Raised when BeastMode retrieval operations fail.

    This exception is used for failures during GET operations on BeastModes,
    including API errors and unexpected response formats.
    """

    def __init__(
        self,
        entity_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            if entity_id:
                message = f"Failed to retrieve BeastMode {entity_id}"
            else:
                message = "Failed to retrieve BeastModes"

        super().__init__(message=message, entity_id=entity_id, res=res, **kwargs)


class BeastMode_CRUD_Error(RouteError):
    """
    Raised when BeastMode create, update, or delete operations fail.

    This exception is used for failures during lock/unlock operations
    or other modification operations on BeastModes.
    """

    def __init__(
        self,
        operation: str,
        entity_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            if entity_id:
                message = f"BeastMode {operation} failed for BeastMode {entity_id}"
            else:
                message = f"BeastMode {operation} operation failed"

        super().__init__(
            message=message,
            entity_id=entity_id,
            res=res,
            additional_context={"operation": operation},
            **kwargs,
        )


class SearchBeastModeNotFoundError(RouteError):
    """
    Raised when BeastMode search operations return no results.

    This exception is used when searching for specific BeastModes that
    don't exist or when search criteria match no BeastModes.
    """

    def __init__(
        self,
        search_criteria: str,
        res: rgd.ResponseGetData | None = None,
        **kwargs,
    ):
        message = f"No BeastModes found matching: {search_criteria}"
        super().__init__(
            message=message,
            res=res,
            additional_context={"search_criteria": search_criteria},
            **kwargs,
        )


# Legacy alias for backward compatibility
BeastModes_API_Error = BeastMode_GET_Error


class Search_BeastModeLink(DomoEnumMixin, Enum):
    CARD = "CARD"
    DATASOURCE = "DATA_SOURCE"


def generate_beastmode_body(
    name: str | None = None,
    filters: list[dict] | None = None,
    is_unlocked: bool | None = None,
    is_not_variable: bool | None = None,
    link: Search_BeastModeLink = None,
):
    filters = filters or []

    body = {}
    if name:
        body.update({"name": name})

    return {
        "name": "",
        "filters": [{"field": "notvariable"}, *filters],
        "sort": {"field": "name", "ascending": True},
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_beastmodes(
    auth: DomoAuth,
    filters: list[dict] | None = None,
    debug_loop: bool = False,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Search for BeastModes with optional filters.

    Searches for BeastModes (calculated fields) in the Domo instance using
    optional filter criteria. Returns a paginated list of matching BeastModes.

    Args:
        auth: Authentication object containing instance and credentials
        filters: Optional list of filter dictionaries to apply to the search
        debug_loop: Enable detailed loop iteration logging
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing list of BeastModes

    Raises:
        BeastMode_GET_Error: If search operation fails

    Example:
        >>> beastmodes_res = await search_beastmodes(auth)
        >>> for bm in beastmodes_res.response:
        ...     print(f"BeastMode: {bm['name']}, ID: {bm['id']}")
    """

    offset_params = {
        "offset": "offset",
        "limit": "limit",
    }
    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/functions/search"

    body = generate_beastmode_body(filters)

    def arr_fn(res) -> list[dict]:
        return res.response["results"]

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        body=body,
        offset_params_in_body=True,
        offset_params=offset_params,
        loop_until_end=True,
        debug_loop=debug_loop,
        return_raw=return_raw,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise BeastMode_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def lock_beastmode(
    auth: DomoAuth,
    beastmode_id: str,
    is_locked: bool,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Lock or unlock a BeastMode.

    Sets the lock status of a BeastMode to prevent or allow modifications.
    Locked BeastModes cannot be edited or deleted.

    Args:
        auth: Authentication object containing instance and credentials
        beastmode_id: Unique identifier for the BeastMode
        is_locked: True to lock the BeastMode, False to unlock it
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing the updated BeastMode data

    Raises:
        BeastMode_CRUD_Error: If lock/unlock operation fails

    Example:
        >>> result = await lock_beastmode(auth, "beastmode-123", is_locked=True)
        >>> print(f"BeastMode locked: {result.is_success}")
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/functions/template/{beastmode_id}"

    body = {"locked": is_locked}

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        operation = "lock" if is_locked else "unlock"
        raise BeastMode_CRUD_Error(
            operation=operation,
            entity_id=str(beastmode_id),
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
async def get_beastmode_by_id(
    auth: DomoAuth,
    beastmode_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific BeastMode by its ID.

    Fetches details for a single BeastMode identified by its unique ID.
    Returns information about the BeastMode including its formula, name,
    and associated resources.

    Args:
        auth: Authentication object containing instance and credentials
        beastmode_id: Unique identifier for the BeastMode to retrieve
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing the specific BeastMode data

    Raises:
        BeastMode_GET_Error: If BeastMode retrieval fails
    SearchBeastModeNotFoundError: If no BeastMode with the specified ID exists

    Example:
        >>> beastmode_res = await get_beastmode_by_id(auth, "beastmode-123")
        >>> bm_data = beastmode_res.response
        >>> print(f"BeastMode: {bm_data['name']}")
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/functions/template/{beastmode_id}"

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
            raise SearchBeastModeNotFoundError(
                search_criteria=f"ID: {beastmode_id}",
                res=res,
            )
        else:
            raise BeastMode_GET_Error(
                entity_id=str(beastmode_id),
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
async def get_card_beastmodes(
    auth: DomoAuth,
    card_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> list[dict]:
    """
    Get BeastModes associated with a specific card.

    Retrieves all BeastModes that are linked to the specified card.
    This function searches all BeastModes and filters for those with
    links to the given card ID.

    Args:
        auth: Authentication object containing instance and credentials
        card_id: Unique identifier for the card
        return_raw: Return raw API response without filtering
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        list of BeastMode dictionaries containing id, name, locked status,
        legacyId, status, and links

    Example:
        >>> card_beastmodes = await get_card_beastmodes(auth, "card-123")
        >>> for bm in card_beastmodes:
        ...     print(f"BeastMode: {bm['name']}")
    """

    res = await search_beastmodes(
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    all_bms = res.response

    filter_bms = [
        bm
        for bm in all_bms
        if any(
            [
                True
                for link in bm["links"]
                if link["resource"]["type"] == "CARD"
                and link["resource"]["id"] == card_id
            ]
        )
    ]

    return [
        {
            "id": bm["id"],
            "name": bm["name"],
            "locked": bm["locked"],
            "legacyId": bm["legacyId"],
            "status": bm["status"],
            "links": bm["links"],
        }
        for bm in filter_bms
    ]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataset_beastmodes(
    dataset_id: str,
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    # ✅ Correct: Accept context from wrapper and pass it through
    # ❌ DO NOT call RouteContext.build_context() here - the wrapper handles it!
    all_bms = (
        await search_beastmodes(
            auth=auth,
            context=context,
            **context_kwargs,
        )
    ).response

    filter_bms = [
        bm
        for bm in all_bms
        if any(
            [
                True
                for link in bm["links"]
                if link["resource"]["type"] == "DATA_SOURCE"
                and link["resource"]["id"] == dataset_id
            ],
        )
    ]

    if return_raw:
        return filter_bms

    return [
        {
            "id": bm["id"],
            "name": bm["name"],
            "locked": bm["locked"],
            "legacyId": bm["legacyId"],
            "status": bm["status"],
            "links": bm["links"],
        }
        for bm in filter_bms
    ]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_page_beastmodes(
    page_id: str,
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    # ✅ Correct: Accept context from wrapper and pass it through
    # ❌ DO NOT call RouteContext.build_context() here - the wrapper handles it!
    from . import page as page_routes

    page_definition = (
        await page_routes.get_page_definition(
            page_id=page_id, auth=auth, context=context, **context_kwargs
        )
    ).response

    card_ids = [card["id"] for card in page_definition["cards"]]

    # the gather_with_concurrency returns a list (cards in the page) of lists (bms in the card).  use list comprehension to make one big list
    page_card_bms = await dmce.gather_with_concurrency(
        *[
            get_card_beastmodes(card_id=card_id, auth=auth, context=context)
            for card_id in card_ids
        ],
        n=5,
    )
    page_card_bms = [
        bm for card_bms in page_card_bms for bm in card_bms
    ]  # flattens list

    bms = []
    for bm in page_card_bms:
        if bm["id"] in [f["id"] for f in bms]:
            bms.append(bm)

    return bms
