from __future__ import annotations

from enum import Enum

from ..auth import DomoAuth
from ..base import exceptions as de
from ..base.base import DomoEnumMixin
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext
from ..utils import enums as dmue
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "Cards_API_Exception",
    "CardSearch_NotFoundError",
    "get_card_by_id",
    "get_kpi_definition",
    "Card_OptionalParts_Enum",
    "get_card_metadata",
    "generate_body_search_cards_only_apps_filter",
    "generate_body_search_cards_admin_summary",
    "search_cards_admin_summary",
]


class Cards_API_Exception(de.RouteError):  # noqa: N801
    def __init__(self, res: rgd.ResponseGetData, message: str | None = None):
        # Extract authentication errors more prominently
        if res and res.status == 401:
            message = (
                message
                or "Authentication failed - Invalid credentials or expired token"
            )
        super().__init__(res=res, message=message)


class CardSearch_NotFoundError(de.RouteError):  # noqa: N801
    def __init__(
        self,
        card_id: str,
        domo_instance: str,
        function_name: str,
        status: int,
        parent_class: str | None = None,
        message: str | None = None,
    ):
        super().__init__(
            status=status,
            message=message or f"card {card_id} not found",
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )


class Card_OptionalParts_Enum(DomoEnumMixin, Enum):  # noqa: N801
    CERTIFICATION = "certification"
    DATASOURCES = "datasources"
    DOMOAPP = "domoapp"
    DRILLPATH = "drillPath"
    MASONDATA = "masonData"
    METADATA = "metadata"
    OWNERS = "owners"
    PROBLEMS = "problems"
    PROPERTIES = "properties"


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_card_by_id(
    card_id: str,
    auth: DomoAuth,
    optional_parts: (
        list[Card_OptionalParts_Enum] | str
    ) = "certification,datasources,drillPath,owners,properties,domoapp",
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
):
    """Retrieve a card by ID with optional parts.

    Args:
        card_id: The card ID to retrieve
        auth: Authentication object
        optional_parts: List of Card_OptionalParts_Enum values (preferred) or comma-separated string
            (for backward compatibility). Defaults to "certification,datasources,drillPath,owners,properties,domoapp"

            **Note:** Enum values are preferred over strings for type safety and better IDE support.
        return_raw: Return raw API response
        context: Optional RouteContext for request configuration

    Returns:
        ResponseGetData object containing card data
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/cards/"

    parts_str = dmue.normalize_optional_parts(optional_parts)
    params = {"parts": parts_str, "urns": card_id}

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params=params,
        context=context,
    )

    if not res.is_success:
        raise Cards_API_Exception(res=res)

    if return_raw:
        return res

    res.response = res.response[0]

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_kpi_definition(
    auth: DomoAuth,
    card_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/cards/kpi/definition"

    body = {"urn": card_id}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if not res.is_success and res.response == "Not Found":
        raise CardSearch_NotFoundError(
            card_id=card_id,
            status=res.status,
            domo_instance=auth.domo_instance,
            function_name="get_kpi_definition",
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
async def get_card_metadata(
    auth: DomoAuth,
    card_id: str,
    optional_parts: (
        list[Card_OptionalParts_Enum] | str
    ) = "metadata,certification,datasources,owners,problems,domoapp",
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve card metadata with optional parts.

    Args:
        auth: Authentication object
        card_id: The card ID to retrieve metadata for
        optional_parts: List of Card_OptionalParts_Enum values (preferred) or comma-separated string
            (for backward compatibility). Defaults to "metadata,certification,datasources,owners,problems,domoapp"

            **Note:** Enum values are preferred over strings for type safety and better IDE support.
        context: Optional RouteContext for request configuration

    Returns:
        ResponseGetData object containing card metadata
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/cards"

    parts_str = dmue.normalize_optional_parts(optional_parts)
    params = {"urns": card_id, "parts": parts_str}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        params=params,
        context=context,
    )

    if not res.is_success:
        raise Cards_API_Exception(res=res)

    if res.is_success and len(res.response) == 0:
        raise CardSearch_NotFoundError(
            card_id=card_id,
            status=res.status,
            domo_instance=auth.domo_instance,
            parent_class=context.parent_class,
            function_name="get_card_metadata",
        )

    res.response = res.response[0]

    return res


def generate_body_search_cards_only_apps_filter() -> dict:
    return {
        "includeCardTypeClause": True,
        "cardTypes": ["domoapp", "mason", "custom"],
        "ascending": True,
        "orderBy": "cardTitle",
    }


def generate_body_search_cards_admin_summary(
    page_ids: list[str] | None = None,
    #  searchPages: bool = True,
    card_search_text: str | None = None,
    page_search_text: str | None = None,
) -> dict:
    body = {"ascending": True, "orderBy": "cardTitle"}

    if card_search_text:
        body.update(
            {"cardTitleSearchText": card_search_text, "includeCardTitleClause": True}
        )

    if page_search_text:
        body.update(
            {
                "pageTitleSearchText": page_search_text,
                "includePageTitleClause": True,
                "notOnPage": False,
            }
        )

    if page_ids:
        body.update({"pageIds": page_ids})

    return body


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_cards_admin_summary(
    auth: DomoAuth,
    body: dict,
    maximum: int | None = None,
    optional_parts: (
        list[Card_OptionalParts_Enum] | str
    ) = "certification,datasources,drillPath,owners,properties,domoapp",
    debug_loop: bool = False,
    wait_sleep: int = 3,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Search cards admin summary with optional parts.

    Args:
        auth: Authentication object
        body: Search body dictionary
        maximum: Maximum number of results to return
        optional_parts: List of Card_OptionalParts_Enum values (preferred) or comma-separated string
            (for backward compatibility). Defaults to "certification,datasources,drillPath,owners,properties,domoapp"

            **Note:** Enum values are preferred over strings for type safety and better IDE support.
        debug_loop: Enable loop debugging
        wait_sleep: Sleep time between requests
        return_raw: Return raw API response
        context: Optional RouteContext for request configuration

    Returns:
        ResponseGetData object containing card admin summaries
    """

    limit = 100
    offset = 0
    loop_until_end = False if maximum else True

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/cards/adminsummary"

    parts_str = dmue.normalize_optional_parts(optional_parts)
    params = {"parts": parts_str}

    offset_params = {
        "offset": "skip",
        "limit": "limit",
    }

    def arr_fn(res):
        return res.response.get("cardAdminSummaries", [])

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        offset_params_in_body=False,
        limit=limit,
        skip=offset,
        body=body,
        maximum=maximum,
        fixed_params=params,
        debug_loop=debug_loop,
        loop_until_end=loop_until_end,
        wait_sleep=wait_sleep,
        context=context,
    )

    if not res.is_success:
        raise Cards_API_Exception(res=res)

    return res
