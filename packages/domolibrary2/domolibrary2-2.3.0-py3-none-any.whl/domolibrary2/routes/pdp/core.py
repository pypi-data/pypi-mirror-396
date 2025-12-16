"""
PDP Core Route Functions

This module provides functions for retrieving PDP policies and utility functions
for working with PDP policy data.

Functions:
    get_pdp_policies: Retrieve all PDP policies for a dataset
    search_pdp_policies_by_name: Search for specific PDP policies by name
    generate_policy_parameter_simple: Utility function for creating policy parameters
    generate_policy_body: Utility function for creating policy request bodies
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
from .exceptions import PDP_GET_Error, SearchPDPNotFoundError

__all__ = [
    "get_pdp_policies",
    "search_pdp_policies_by_name",
    "generate_policy_parameter_simple",
    "generate_policy_body",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_pdp_policies(
    auth: DomoAuth,
    dataset_id: str,
    include_all_rows: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve all PDP policies for a specific dataset.

    Fetches a list of all PDP (Personalized Data Permissions) policies associated
    with the specified dataset. Includes policy filters, associations, and open
    policy settings when include_all_rows is True.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        include_all_rows: Include policy associations, filters, and open policy (default: True)
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing list of PDP policies

    Raises:
        PDP_GET_Error: If PDP policy retrieval fails or API returns an error

    Example:
        >>> policies_response = await get_pdp_policies(auth, "abc123")
        >>> for policy in policies_response.response:
        ...     print(f"Policy: {policy['name']}, ID: {policy['filterGroupId']}")
    """
    url = f"http://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/"

    if include_all_rows:
        url += "?options=load_associations,load_filters,include_open_policy"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
        is_follow_redirects=True,
    )

    if return_raw:
        return res

    if not res.is_success or (
        isinstance(res.response, list) and len(res.response) == 0
    ):
        raise PDP_GET_Error(
            dataset_id=dataset_id,
            res=res,
            message=f"Failed to retrieve PDP policies for dataset {dataset_id}",
        )

    return res


def search_pdp_policies_by_name(
    search_name: str,
    result_list: list[dict],
    is_exact_match: bool = True,
    is_suppress_errors: bool = False,
) -> dict | list[dict | bool]:
    """
    Search for PDP policies by name within a list of policies.

    Searches through a list of PDP policies to find those matching the specified
    name. Can perform exact or partial matching.

    Args:
        search_name: Name or partial name to search for
        result_list: list of policy dictionaries from get_pdp_policies response
        is_exact_match: If True, search for exact name match; if False, partial match
        is_suppress_errors: If True, return False instead of raising error when not found

    Returns:
        Single policy dict (exact match), list of policy dicts (partial match),
        or False if no matches and is_suppress_errors is True

    Raises:
        SearchPDPNotFoundError: If no policies match the search criteria (unless is_suppress_errors is True)

    Example:
        >>> policies = await get_pdp_policies(auth, "abc123")
        >>> policy = search_pdp_policies_by_name("Sales Policy", policies.response)
        >>> print(f"Found policy: {policy['filterGroupId']}")
    """
    if is_exact_match:
        policy_search = next(
            (policy for policy in result_list if policy["name"] == search_name), None
        )
    else:
        policy_search = [
            policy
            for policy in result_list
            if search_name.lower() in policy["name"].lower()
        ]

    if not policy_search and not is_suppress_errors:
        raise SearchPDPNotFoundError(
            search_criteria=f"name: {search_name}",
        )

    return policy_search or False


def generate_policy_parameter_simple(
    column_name: str,
    type: str = "COLUMN",
    column_values_ls: list[str] | None = None,
    operator: str = "EQUALS",
    ignore_case: bool = True,
) -> dict:
    """
    Generate a simple policy parameter for PDP policy creation.

    Creates a parameter dictionary that defines a filter condition for a PDP policy.
    Parameters specify which column values users can see.

    Args:
        column_name: Name of the column to filter on
        type: Parameter type (default: "COLUMN")
        column_values_ls: list of column values to filter, or single value
        operator: Comparison operator (default: "EQUALS")
        ignore_case: Whether to ignore case when comparing values (default: True)

    Returns:
        Dictionary representing a policy parameter

    Example:
        >>> param = generate_policy_parameter_simple(
        ...     column_name="Region",
        ...     column_values_ls=["West", "East"]
        ... )
        >>> print(param)
        {'type': 'COLUMN', 'name': 'Region', 'values': ['West', 'East'], ...}
    """
    if not isinstance(column_values_ls, list):
        column_values_ls = [column_values_ls] if column_values_ls is not None else []

    return {
        "type": type,
        "name": column_name,
        "values": column_values_ls,
        "operator": operator,
        "ignoreCase": ignore_case,
    }


def generate_policy_body(
    policy_name: str,
    dataset_id: str,
    parameters_ls: list[dict],
    policy_id: str | None = None,
    user_ids: list[str] | None = None,
    group_ids: list[str] | None = None,
    virtual_user_ids: list[str] | None = None,
) -> dict:
    """
    Generate a policy body for PDP policy creation or update.

    Creates a complete request body for creating or updating a PDP policy,
    including filter parameters and user/group assignments.

    Args:
        policy_name: Name for the policy
        dataset_id: Unique identifier for the dataset
        parameters_ls: list of parameter dicts (from generate_policy_parameter_simple)
        policy_id: Policy ID (only for updates, omit for new policies)
        user_ids: list of user IDs to assign the policy to
        group_ids: list of group IDs to assign the policy to
        virtual_user_ids: list of virtual user IDs to assign the policy to

    Returns:
        Dictionary representing complete policy request body

    Example:
        >>> params = [generate_policy_parameter_simple("Region", column_values_ls=["West"])]
        >>> body = generate_policy_body(
        ...     policy_name="West Region Access",
        ...     dataset_id="abc123",
        ...     parameters_ls=params,
        ...     user_ids=["12345"]
        ... )
        >>> # Use body in create_policy or update_policy
    """
    if not user_ids:
        user_ids = []

    if not group_ids:
        group_ids = []

    if not virtual_user_ids:
        virtual_user_ids = []

    if not isinstance(parameters_ls, list):
        parameters_ls = [parameters_ls]

    body = {
        "name": policy_name,
        "dataSourceId": dataset_id,
        "userIds": user_ids,
        "virtualUserIds": virtual_user_ids,
        "groupIds": group_ids,
        "dataSourcePermissions": False,
        "parameters": parameters_ls,
    }

    if policy_id:
        body.update({"filterGroupId": policy_id})

    return body
