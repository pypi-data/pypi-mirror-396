"""
PDP CRUD Route Functions

This module provides functions for creating, updating, and deleting PDP policies.

Functions:
    create_policy: Create a new PDP policy
    update_policy: Update an existing PDP policy
    delete_policy: Delete a PDP policy
    toggle_pdp: Enable or disable PDP for a dataset
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
from .core import get_pdp_policies, search_pdp_policies_by_name
from .exceptions import PDP_CRUD_Error

__all__ = [
    "create_policy",
    "update_policy",
    "delete_policy",
    "toggle_pdp",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_policy(
    auth: DomoAuth,
    dataset_id: str,
    body: dict,
    override_same_name: bool = False,
    is_suppress_errors: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Create a new PDP policy for a dataset.

    Creates a new Personalized Data Permissions policy with the specified
    parameters and assignments. Can check for duplicate policy names before
    creating.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        body: Policy request body (from generate_policy_body)
        override_same_name: If True, allow creating policy with duplicate name
        is_suppress_errors: If True, return existing policy instead of error for duplicates
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing created policy information

    Raises:
        PDP_CRUD_Error: If policy creation fails or duplicate name exists

    Example:
        >>> params = [generate_policy_parameter_simple("Region", column_values_ls=["West"])]
        >>> body = generate_policy_body(
        ...     policy_name="West Region Access",
        ...     dataset_id="abc123",
        ...     parameters_ls=params
        ... )
        >>> response = await create_policy(auth, "abc123", body)
        >>> policy_id = response.response.get("filterGroupId")
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups"

    if not override_same_name:
        existing_policies = await get_pdp_policies(
            auth=auth,
            dataset_id=dataset_id,
            context=context,
        )

        policy_exists = search_pdp_policies_by_name(
            search_name=body.get("name"),
            result_list=existing_policies.response,
            is_exact_match=True,
            is_suppress_errors=True,
        )

        if policy_exists:
            if not is_suppress_errors:
                raise PDP_CRUD_Error(
                    operation="create",
                    dataset_id=dataset_id,
                    res=existing_policies,
                    message='Policy name already exists. Avoid creating PDP policies with the same name. To override, set "override_same_name=True"',
                )

            return existing_policies

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise PDP_CRUD_Error(
            operation="create",
            dataset_id=dataset_id,
            res=res,
            message=f"Failed to create policy - {res.response}",
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
async def update_policy(
    auth: DomoAuth,
    dataset_id: str,
    policy_id: str,
    body: dict,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Update an existing PDP policy.

    Modifies an existing Personalized Data Permissions policy with new
    parameters, assignments, or name.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        policy_id: Unique identifier for the policy to update
        body: Policy request body (from generate_policy_body)
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing updated policy information

    Raises:
        PDP_CRUD_Error: If policy update fails

    Example:
        >>> params = [generate_policy_parameter_simple("Region", column_values_ls=["West", "East"])]
        >>> body = generate_policy_body(
        ...     policy_name="Updated Policy Name",
        ...     dataset_id="abc123",
        ...     parameters_ls=params,
        ...     policy_id="policy123"
        ... )
        >>> response = await update_policy(auth, "abc123", "policy123", body)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/{policy_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise PDP_CRUD_Error(
            operation="update",
            dataset_id=dataset_id,
            policy_id=policy_id,
            res=res,
            message=f"Failed to update policy {policy_id} - {res.response}",
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
async def delete_policy(
    auth: DomoAuth,
    dataset_id: str,
    policy_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Delete a PDP policy.

    Permanently removes a Personalized Data Permissions policy from a dataset.
    This action cannot be undone.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        policy_id: Unique identifier for the policy to delete
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        PDP_CRUD_Error: If policy deletion fails

    Example:
        >>> response = await delete_policy(auth, "abc123", "policy123")
        >>> print(f"Policy deleted: {response.response}")
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/{policy_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise PDP_CRUD_Error(
            operation="delete",
            dataset_id=dataset_id,
            policy_id=policy_id,
            res=res,
            message=f"Failed to delete policy {policy_id} - {res.response}",
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
async def toggle_pdp(
    auth: DomoAuth,
    dataset_id: str,
    is_enable: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Enable or disable PDP for a dataset.

    Toggles Personalized Data Permissions on or off for the specified dataset.
    When disabled, all users can see all data in the dataset.

    Args:
        auth: Authentication object containing instance and credentials
        dataset_id: Unique identifier for the dataset
        is_enable: If True, enable PDP; if False, disable PDP (default: True)
        return_raw: Return raw API response without processing
        context: Optional RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object with confirmation message

    Raises:
        PDP_CRUD_Error: If toggle operation fails

    Example:
        >>> # Enable PDP for a dataset
        >>> response = await toggle_pdp(auth, "abc123", is_enable=True)
        >>> # Disable PDP for a dataset
        >>> response = await toggle_pdp(auth, "abc123", is_enable=False)
    """
    url = (
        f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}"
    )

    body = {
        "enabled": is_enable,
        "external": False,  # not sure what this parameter does
    }

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        action = "enable" if is_enable else "disable"
        raise PDP_CRUD_Error(
            operation=f"toggle ({action})",
            dataset_id=dataset_id,
            res=res,
            message=f"Failed to {action} PDP for dataset {dataset_id} - {res.response}",
        )

    return res
