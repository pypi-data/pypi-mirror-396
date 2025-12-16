from ...auth import DomoAuth
from ...base.exceptions import RouteError
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    ResponseGetDataProcessor,
    log_call,
)

__all__ = [
    "InstanceSwitcher_GET_Error",
    "InstanceSwitcher_CRUD_Error",
    "get_instance_switcher_mapping",
    "set_instance_switcher_mapping",
]


class InstanceSwitcher_GET_Error(RouteError):
    """Raised when instance switcher mapping retrieval operations fail."""

    def __init__(
        self,
        entity_id: str | None = None,
        res=None,
        message: str | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Instance switcher mapping retrieval failed",
            entity_id=entity_id,
            res=res,
            **kwargs,
        )


class InstanceSwitcher_CRUD_Error(RouteError):
    """Raised when instance switcher mapping create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        entity_id: str | None = None,
        res=None,
        message: str | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message
            or f"Instance switcher mapping {operation} operation failed",
            entity_id=entity_id,
            res=res,
            additional_context={"operation": operation},
            **kwargs,
        )


# gets existing instance switcher mapping, response = list[dict]
@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_instance_switcher_mapping(
    auth: DomoAuth,
    return_raw: bool = False,
    timeout: int = 20,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve instance switcher mapping configuration.

    Gets the existing instance switcher mappings which define how users are
    routed to different Domo instances based on user attributes.

    Args:
        auth: Authentication object containing instance and credentials
        return_raw: Return raw API response without processing
        timeout: Request timeout in seconds (default: 20)

    Returns:
        ResponseGetData object containing list of instance switcher mappings

    Raises:
        InstanceSwitcher_GET_Error: If retrieval operation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/everywhere/admin/userattributeinstances"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        timeout=timeout,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise InstanceSwitcher_GET_Error(
            message=f"failed to retrieve instance switcher mapping - {res.response}",
            res=res,
        )

    return res


# update the instance switcher mappings
@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def set_instance_switcher_mapping(
    auth: DomoAuth,
    mapping_payloads: list[dict],
    return_raw: bool = False,
    timeout: int = 60,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Update instance switcher mapping configuration.

    Sets or updates the instance switcher mappings which define how users are
    routed to different Domo instances based on user attributes.

    Args:
        auth: Authentication object containing instance and credentials
        mapping_payloads: list of mapping configurations, each with format:
            {'userAttribute': 'attribute_name', 'instance': 'instance.domo.com'}
        return_raw: Return raw API response without processing
        timeout: Request timeout in seconds (default: 60)

    Returns:
        ResponseGetData object with success message

    Raises:
        InstanceSwitcher_CRUD_Error: If update operation fails

    Example:
        >>> mapping_payloads = [
        ...     {'userAttribute': 'test1', 'instance': 'test.domo.com'},
        ...     {'userAttribute': 'test2', 'instance': 'prod.domo.com'}
        ... ]
        >>> await set_instance_switcher_mapping(auth, mapping_payloads)
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/everywhere/admin/userattributeinstances"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=mapping_payloads,
        timeout=timeout,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise InstanceSwitcher_CRUD_Error(
            operation="update",
            message=f"failed to update instance switcher mappings - {res.response}",
            res=res,
        )

    res.response = "success: updated instance switcher mappings"
    return res
