"""
Core Account Route Functions

This module provides core account retrieval functions for both regular and OAuth accounts.

Functions:
    get_available_data_providers: Retrieve available data providers
    get_accounts: Retrieve all accounts user has access to
    get_account_by_id: Retrieve specific account by ID
"""

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.logging import LogDecoratorConfig, ResponseGetDataProcessor, log_call
from .exceptions import Account_GET_Error, AccountNoMatchError


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_available_data_providers(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve available data providers from Domo.

    Args:
        auth: Authentication object
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing available data providers

    Raises:
        Account_GET_Error: If data provider retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers"

    res = await gd.get_data(auth=auth, url=url, method="GET", context=context)

    if return_raw:
        return res

    if not res.is_success:
        raise Account_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_accounts(
    auth: DomoAuth,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve a list of all accounts the user has read access to.

    Note: Users with "Manage all accounts" permission will retrieve all account objects.

    Args:
        auth: Authentication object for API requests
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing account list

    Raises:
        Account_GET_Error: If account retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    res = await gd.get_data(auth=auth, url=url, method="GET", context=context)

    if return_raw:
        return res

    if not res.is_success:
        raise Account_GET_Error(res=res)
    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_account_by_id(
    auth: DomoAuth,
    account_id: int | str,
    is_unmask: bool = False,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve metadata about a specific account.

    Args:
        auth: Authentication object for API requests
        account_id: The ID of the account to retrieve
        is_unmask: Whether to unmask encrypted values in response
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing account metadata

    Raises:
        AccountNoMatchError: If account is not found or not accessible
        Account_GET_Error: If account retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        timeout=20,  # occasionally this API has a long response time
        params={"unmask": is_unmask},
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success and (
        res.response == "Forbidden" or res.response == "Not Found"
    ):
        raise AccountNoMatchError(account_id=str(account_id), res=res)

    if not res.is_success:
        raise Account_GET_Error(entity_id=str(account_id), res=res)

    return res
