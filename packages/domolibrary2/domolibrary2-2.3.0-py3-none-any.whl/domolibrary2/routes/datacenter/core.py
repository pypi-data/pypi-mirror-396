from __future__ import annotations

from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

"""
Datacenter Route Core Functions

This module provides core datacenter functions for searching, retrieving lineage,
and sharing resources in Domo.

Enums:
    Datacenter_Enum: Types of datacenter entities
    Dataflow_Type_Filter_Enum: Dataflow type filters
    Datacenter_Filter_Field_Enum: Fields for filtering datacenter searches
    Datacenter_Filter_Field_Certification_Enum: Certification states
    ShareResource_Enum: Resource types that can be shared

Utility Functions:
    generate_search_datacenter_filter: Generate filter for datacenter search
    generate_search_datacenter_filter_search_term: Generate search term filter
    generate_search_datacenter_body: Generate complete search body
    generate_search_datacenter_account_body: Generate account search body

Route Functions:
    search_datacenter: Search across datacenter entities
    get_connectors: Retrieve available connectors
    get_lineage_upstream: Get upstream lineage for an entity
    share_resource: Share a resource with users or groups
"""

from enum import Enum
from typing import TypedDict

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils import enums as dmue
from .exceptions import (
    DatacenterGetError,
    SearchDatacenterNoResultsFoundError,
    ShareResourceError,
)


class Datacenter_Enum(DomoEnumMixin, Enum):
    ACCOUNT = "ACCOUNT"
    CARD = "CARD"
    DATAFLOW = "DATAFLOW"
    DATASET = "DATASET"
    GROUP = "GROUP"
    PAGE = "PAGE"
    USER = "USER"
    CONNECTOR = "CONNECTOR"
    PACKAGE = "PACKAGE"
    DATA_APP = "DATA_APP"
    default = "UNKNOWN"


class Dataflow_Type_Filter_Enum(DomoEnumMixin, Enum):
    ADR = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "ADR",
        "name": "ADR",
        "not": False,
    }

    MYSQL = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "MYSQL",
        "name": "MYSQL",
        "not": False,
    }

    REDSHIFT = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "MYSQL",
        "name": "MYSQL",
        "not": False,
    }

    MAGICV2 = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "MAGIC",
        "name": "Magic ETL v2",
        "not": False,
    }

    MAGIC = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "ETL",
        "name": "Magic ETL",
        "not": False,
    }


class Datacenter_Filter_Field_Enum(DomoEnumMixin, Enum):
    DATAPROVIDER = "dataprovidername_facet"
    CERTIFICATION = "certification.state"


class Datacenter_Filter_Field_Certification_Enum(DomoEnumMixin, Enum):
    CERTIFIED = "CERTIFIED"
    PENDING = "PENDING"
    REQUESTED = "REQUESTED"
    EXPIRED = "EXPIRED"


class ShareResource_Enum(DomoEnumMixin, Enum):
    PAGE = "page"
    CARD = "badge"


class LineageNode(TypedDict):
    type: str
    id: str
    complete: bool
    children: list[LineageNode]
    parents: list[LineageNode]
    descendantCounts: dict[str, int] | None
    ancestorCounts: dict[str, int] | None


def generate_search_datacenter_filter(
    field: str | Datacenter_Filter_Field_Enum,  # use Datacenter_Filter_Field_Enum
    value: str | Enum,
    is_not: bool = False,  # to handle exclusion
) -> dict:
    """Generate a filter object for datacenter search.

    Args:
        field: Field to filter on (string or enum)
        value: Value to filter for (string or enum)
        is_not: Whether to negate the filter

    Returns:
        Dictionary containing filter specification
    """
    field = dmue.normalize_enum(field)
    value = dmue.normalize_enum(value)

    return {
        "filterType": "term",
        "field": field,
        "value": value,
        "not": is_not,
    }


def generate_search_datacenter_filter_search_term(search_term: str) -> dict:
    """Generate a search term filter for datacenter search.

    Args:
        search_term: Text to search for

    Returns:
        Dictionary containing search term filter
    """
    return {"field": "name_sort", "filterType": "wildcard", "query": search_term}


def generate_search_datacenter_body(
    search_text: str | None = None,
    entity_type: (
        str | Datacenter_Enum | list[Datacenter_Enum]
    ) = "DATASET",  # can accept one entity_type or a list of entity_types
    additional_filters_ls: list[dict] | None = None,
    combineResults: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Generate complete body for datacenter search request.

    Args:
        search_text: Optional search text to filter results
        entity_type: Type(s) of entities to search for
        additional_filters_ls: Additional filters to apply
        combineResults: Whether to combine results
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        Dictionary containing complete search body

    Raises:
        ValueError: If entity_type is not a string or Datacenter_Enum
    """
    filters_ls = (
        [generate_search_datacenter_filter_search_term(search_text)]
        if search_text
        else []
    )

    if not isinstance(entity_type, list):
        entity_type = [entity_type]

    entity_type = [dmue.normalize_enum(en) for en in entity_type]

    if not all(isinstance(en, str) for en in entity_type):
        raise ValueError("entity_type must be a string or Datacenter_Enum")

    if additional_filters_ls:
        if not isinstance(additional_filters_ls, list):
            additional_filters_ls = [additional_filters_ls]

        filters_ls += additional_filters_ls

    return {
        "entities": entity_type,
        "filters": filters_ls or [],
        "combineResults": combineResults,
        "query": "*",
        "count": limit,
        "offset": offset,
    }


def generate_search_datacenter_account_body(
    search_str: str, is_exact_match: bool = True
) -> dict:
    """Generate body for datacenter account search.

    Args:
        search_str: String to search for
        is_exact_match: Whether to require exact match

    Returns:
        Dictionary containing account search body
    """
    return {
        "combineResults": False,
        "query": search_str if is_exact_match else f"*{search_str}*",
        "filters": [],
        "facetValuesToInclude": [
            "DATAPROVIDERNAME",
            "OWNED_BY_ID",
            "VALID",
            "USED",
            "LAST_MODIFIED_DATE",
        ],
        "queryProfile": "GLOBAL",
        "entityList": [["account"]],
        "sort": {"fieldSorts": [{"field": "display_name_sort", "sortOrder": "ASC"}]},
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_datacenter(
    auth: DomoAuth,
    maximum: int | None = None,
    body: (
        dict | None
    ) = None,  # either pass a body or generate a body in the function using search_text, entity_type, and additional_filters parameters
    search_text: str | None = None,
    entity_type: str | list = "dataset",  # can accept one value or a list of values
    additional_filters_ls: list | None = None,
    arr_fn: callable | None = None,
    debug_loop: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Search across datacenter entities.

    Args:
        auth: Authentication object
        maximum: Maximum number of results to return
        body: Pre-built search body (optional)
        search_text: Text to search for
        entity_type: Type(s) of entities to search
        additional_filters_ls: Additional filters to apply
        arr_fn: Function to extract array from response
        debug_loop: Enable loop debugging
        return_raw: Return raw response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing search results

    Raises:
        SearchDatacenter_NoResultsFound: If search returns no results
        Datacenter_GET_Error: If search operation fails
    """

    limit = 100  # api enforced limit

    if not body:
        body = generate_search_datacenter_body(
            entity_type=entity_type,
            additional_filters_ls=additional_filters_ls,
            search_text=search_text,
            combineResults=False,
            limit=limit,
        )

    if not arr_fn:

        def arr_fn(res):
            return res.response.get("searchObjects")

    url = f"https://{auth.domo_instance}.domo.com/api/search/v1/query"

    res = await gd.looper(
        auth=auth,
        url=url,
        loop_until_end=True if not maximum else False,
        body=body,
        offset_params_in_body=True,
        offset_params={"offset": "offset", "limit": "count"},
        arr_fn=arr_fn,
        method="POST",
        maximum=maximum,
        limit=limit,
        context=context,
        debug_loop=debug_loop,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    if res.is_success and len(res.response) == 0:
        raise SearchDatacenterNoResultsFoundError(
            res=res, message="no results for query parameters"
        )

    if not res.is_success:
        raise DatacenterGetError(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_connectors(
    auth: DomoAuth,
    search_text: str | None = None,
    additional_filters_ls: list[dict] | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve available connectors from datacenter.

    Args:
        auth: Authentication object
        search_text: Optional text to filter connectors
        additional_filters_ls: Additional filters to apply
        return_raw: Return raw response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing connector list

    Raises:
        SearchDatacenter_NoResultsFound: If no connectors found
        Datacenter_GET_Error: If connector retrieval fails
    """

    additional_filters_ls = additional_filters_ls or []

    body = generate_search_datacenter_body(
        entity_type=Datacenter_Enum.CONNECTOR,
        additional_filters_ls=additional_filters_ls,
        combineResults=True,
    )

    res = await search_datacenter(
        auth=auth,
        body=body,
        return_raw=True,  # Get raw response first to avoid raising errors
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise DatacenterGetError(res=res)

    if search_text:
        s = [
            r
            for r in res.response
            if search_text.lower() in r.get("label", "").lower()
            or search_text.lower() in r.get("title", "").lower()
        ]

        res.response = s

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_lineage_upstream(
    auth: DomoAuth,
    entity_type: str,
    entity_id: str,
    return_raw: bool = False,
    max_depth: int | None = None,
    traverse_up: bool = True,
    traverse_down: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get lineage for a datacenter entity.

    Args:
        auth: Authentication object
        entity_type: Type of entity (e.g., 'dataset', 'dataflow')
        entity_id: ID of the entity
        return_raw: Return raw response without processing
        max_depth: Maximum depth to traverse. Limits how many levels
                  to include. None = unlimited depth.
        traverse_up: If True, traverse upstream (parents/dependencies).
        traverse_down: If True, traverse downstream (children/dependents).
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing lineage data

    Raises:
        Datacenter_GET_Error: If lineage retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/lineage/{entity_type}/{entity_id}"

    params = {
        "traverseUp": "true" if traverse_up else "false",
        "traverseDown": "true" if traverse_down else "false",
    }

    # Add maxDepth parameter if specified
    if max_depth is not None:
        params.update({"maxDepth": str(max_depth)})

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params=params,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise DatacenterGetError(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def share_resource(
    auth: DomoAuth,
    resource_ids: list | str | int,
    resource_type: ShareResource_Enum,
    group_ids: list | str | int | None = None,
    user_ids: list | str | int | None = None,
    message: str | None = None,  # email to user
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Share a page or card with users or groups.

    Args:
        auth: Authentication object
        resource_ids: ID(s) of resources to share
        resource_type: Type of resource (ShareResource_Enum enum)
        group_ids: ID(s) of groups to share with
        user_ids: ID(s) of users to share with
        message: Optional message to include in notification email
        return_raw: Return raw response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object with success message

    Raises:
        ShareResource_Error: If sharing operation fails

    Example body format:
        {
            "resources": [
                {
                    "type": "page",
                    "id": {page_id}
                }
            ],
            "recipients": [
                {
                    "type": "group",
                    "id": "{group_id}"
                }
            ],
            "message": "I thought you might find this page interesting."
        }
    """

    resource_ids = resource_ids if isinstance(resource_ids, list) else [resource_ids]
    if group_ids:
        group_ids = (
            group_ids and group_ids if isinstance(group_ids, list) else [group_ids]
        )

    if user_ids:
        user_ids = user_ids if isinstance(user_ids, list) else [user_ids]

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/share?sendEmail=false"

    recipient_ls = []

    if group_ids:
        for gid in group_ids:
            recipient_ls.append({"type": "group", "id": str(gid)})

    if user_ids:
        for uid in user_ids:
            recipient_ls.append({"type": "user", "id": str(uid)})

    resource_ls = [
        {"type": resource_type.value, "id": str(rid)} for rid in resource_ids
    ]

    body = {
        "resources": resource_ls,
        "recipients": recipient_ls,
        "message": message,
    }

    res = await gd.get_data(
        url,
        method="POST",
        auth=auth,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise ShareResourceError(
            message=res.response,
            domo_instance=auth.domo_instance,
            parent_class=context.parent_class,
            function_name="share_resource",
            res=res,
        )

    if res.is_success:
        res.response = f"{resource_type.value} {','.join([resource['id'] for resource in resource_ls])} successfully shared with {', '.join([recipient['id'] for recipient in recipient_ls])}"

    return res
