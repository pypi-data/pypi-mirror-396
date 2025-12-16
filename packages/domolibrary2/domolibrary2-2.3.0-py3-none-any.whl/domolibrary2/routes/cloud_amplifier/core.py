from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

"""
Cloud Amplifier Core Functions

This module contains core functions for managing Cloud Amplifier integrations.
"""

from typing import Any

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from .exceptions import (
    CloudAmplifier_CRUD_Error,
    CloudAmplifier_GET_Error,
    SearchCloudAmplifierNotFoundError,
)
from .utils import ENGINES, create_integration_body

__all__ = [
    "get_integrations",
    "get_integration_by_id",
    "get_integration_permissions",
    "get_integration_warehouses",
    "create_integration",
    "update_integration",
    "update_integration_warehouses",
    "delete_integration",
    "convert_federated_to_cloud_amplifier",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_integrations(
    auth: DomoAuth,
    integration_engine: ENGINES | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve a list of all Cloud Amplifier integrations.

    Fetches all integrations associated with the current Domo instance,
    optionally filtered by engine type (SNOWFLAKE, BIGQUERY).

    Args:
        auth: Authentication object containing instance and credentials
        integration_engine: Optional filter by engine type (SNOWFLAKE or BIGQUERY)
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing list of integrations

    Raises:
        CloudAmplifier_GET_Error: If integration retrieval fails

    Example:
        >>> integrations_response = await get_integrations(auth)
        >>> for integration in integrations_response.response:
        ...     print(f"Integration: {integration['id']}")
    """

    api_type = "data"
    params = None

    if integration_engine:  # Change to query if engine is provided to filter by engine
        api_type = "query"
        params = {"deviceEngine": integration_engine}

    url = f"https://{auth.domo_instance}.domo.com/api/{api_type}/v1/byos/accounts"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        params=params,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_integration_by_id(
    auth: DomoAuth,
    integration_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific Cloud Amplifier integration by ID.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Unique identifier for the integration
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing integration details

    Raises:
        CloudAmplifier_GET_Error: If integration retrieval fails
        SearchCloudAmplifierNotFoundError: If integration doesn't exist

    Example:
        >>> integration = await get_integration_by_id(auth, "12345")
        >>> print(integration.response)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/accounts/{integration_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if res.status == 404:
        raise SearchCloudAmplifierNotFoundError(
            search_criteria=f"Integration ID: {integration_id}",
            res=res,
        )

    if not res.is_success:
        raise CloudAmplifier_GET_Error(entity_id=integration_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_integration_permissions(
    auth: DomoAuth,
    user_id: str | None = None,
    integration_ids: list[str] | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve permissions for Cloud Amplifier integrations.

    Lists permissions for specified integrations and/or user.

    Args:
        auth: Authentication object containing instance and credentials
        user_id: Optional user ID to filter permissions
        integration_ids: Optional list of integration IDs to check permissions for
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing permissions information

    Raises:
        CloudAmplifier_GET_Error: If permissions retrieval fails

    Example:
        >>> permissions = await get_integration_permissions(auth, user_id="123")
        >>> print(permissions.response)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/accounts/permissions/list"

    body = {}

    if user_id:
        body.update({"userId": user_id})

    if integration_ids:
        body.update({"integrationIds": integration_ids})

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
        raise CloudAmplifier_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_integration_warehouses(
    auth: DomoAuth,
    integration_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    list available compute warehouses for a Cloud Amplifier integration.

    User must have permission to view the integration.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Integration ID to list warehouses for
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing list of warehouses

    Raises:
        CloudAmplifier_GET_Error: If warehouse retrieval fails or user lacks permission

    Example:
        >>> warehouses = await get_integration_warehouses(auth, "integration-123")
        >>> for warehouse in warehouses.response:
        ...     print(warehouse['name'])
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/warehouses/{integration_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if return_raw:
        return res

    if res.status == 403:
        raise CloudAmplifier_GET_Error(
            entity_id=integration_id,
            res=res,
            message=f"User may not have permission to view the warehouses - {integration_id}",
        )

    if not res.is_success:
        raise CloudAmplifier_GET_Error(entity_id=integration_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_integration(
    auth: DomoAuth,
    engine: ENGINES,
    friendly_name: str,
    service_account_id: str,
    auth_method: str,
    description: str = "",
    admin_auth_method: str | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Create a new Cloud Amplifier integration.

    Args:
        auth: Authentication object containing instance and credentials
        engine: Cloud platform engine (SNOWFLAKE or BIGQUERY)
        friendly_name: Display name for the integration
        service_account_id: Service account ID to use for authentication
        auth_method: Authentication method
        description: Optional description for the integration (default: "")
        admin_auth_method: Admin authentication method (defaults to auth_method)
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing created integration details

    Raises:
        CloudAmplifier_CRUD_Error: If integration creation fails

    Example:
        >>> result = await create_integration(
        ...     auth,
        ...     engine="SNOWFLAKE",
        ...     friendly_name="My Snowflake Integration",
        ...     service_account_id="account-123",
        ...     auth_method="OAUTH"
        ... )
        >>> print(result.response)
    """

    if admin_auth_method is None:
        admin_auth_method = auth_method

    body = create_integration_body(
        engine=engine,
        friendly_name=friendly_name,
        service_account_id=service_account_id,
        auth_method=auth_method,
        admin_auth_method=admin_auth_method,
        description=description,
    )

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/accounts"

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
        raise CloudAmplifier_CRUD_Error(
            operation="create",
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
async def update_integration(
    auth: DomoAuth,
    integration_id: str,
    update_body: dict[str, Any],
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Update a Cloud Amplifier integration.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Integration ID to update
        update_body: Dictionary containing fields to update
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing update result

    Raises:
        CloudAmplifier_CRUD_Error: If integration update fails

    Example:
        >>> update_body = {"properties": {"friendlyName": {"value": "New Name"}}}
        >>> result = await update_integration(auth, "integration-123", update_body)
        >>> print(result.response)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/accounts/{integration_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=update_body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_CRUD_Error(
            operation="update",
            entity_id=integration_id,
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
async def update_integration_warehouses(
    auth: DomoAuth,
    integration_id: str,
    warehouses: list[dict[str, Any]],
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Update the compute warehouses for a Cloud Amplifier integration.

    Expects a list of warehouse dicts as returned by the GET warehouses endpoint.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Integration ID to update warehouses for
        warehouses: list of warehouse configuration dictionaries
        session: Optional HTTP client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to omit in debug output
        parent_class: Name of calling class for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing update result

    Raises:
        CloudAmplifier_CRUD_Error: If warehouse update fails

    Example:
        >>> warehouses = [{"name": "COMPUTE_WH", "size": "LARGE"}]
        >>> result = await update_integration_warehouses(
        ...     auth, "integration-123", warehouses
        ... )
        >>> print(result.response)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/byos/warehouses/{integration_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=warehouses,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_CRUD_Error(
            operation="update warehouses",
            entity_id=integration_id,
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
async def delete_integration(
    auth: DomoAuth,
    integration_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Delete a Cloud Amplifier integration.

    Args:
        auth: Authentication object containing instance and credentials
        integration_id: Integration ID to delete
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing deletion confirmation

    Raises:
        CloudAmplifier_CRUD_Error: If integration deletion fails

    Example:
        >>> result = await delete_integration(auth, "integration-123")
        >>> print(result.response)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/byos/accounts/{integration_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_CRUD_Error(
            operation="delete",
            entity_id=integration_id,
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
async def convert_federated_to_cloud_amplifier(
    auth: DomoAuth,
    federated_dataset_id: str,
    cloud_amplifier_integration_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Convert a federated dataset to use a Cloud Amplifier integration.

    Args:
        auth: Authentication object containing instance and credentials
        federated_dataset_id: Dataset ID of the federated dataset to convert
        cloud_amplifier_integration_id: Integration ID to convert to
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing conversion result

    Raises:
        CloudAmplifier_CRUD_Error: If conversion operation fails

    Example:
        >>> result = await convert_federated_to_cloud_amplifier(
        ...     auth, "dataset-123", "integration-456"
        ... )
        >>> print(result.response)
    """

    url = (
        f"https://{auth.domo_instance}.domo.com/api/query/migration/federated/to/amplifier/"
        f"{federated_dataset_id}/integrations/{cloud_amplifier_integration_id}"
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body={},
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CloudAmplifier_CRUD_Error(
            operation="convert",
            entity_id=federated_dataset_id,
            res=res,
        )

    return res
