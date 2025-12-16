"""
Account Configuration Route Functions

This module provides account configuration management functions for both regular and OAuth accounts.

Functions:
    get_account_config: Retrieve account configuration
    get_oauth_account_config: Retrieve OAuth account configuration
    update_account_config: Update account configuration
    update_oauth_account_config: Update OAuth account configuration
"""

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.logging import LogDecoratorConfig, ResponseGetDataProcessor, log_call
from .core import get_account_by_id
from .exceptions import Account_Config_Error, AccountNoMatchError
from .oauth import get_oauth_account_by_id


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_account_config(
    auth: DomoAuth,
    account_id: int | str,
    data_provider_type: str | None = None,
    is_unmask: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve configuration for a specific account.

    Args:
        auth: Authentication object for API requests
        account_id: The ID of the account to get config for
        data_provider_type: Type of data provider (auto-detected if not provided)
        is_unmask: Whether to unmask encrypted values in config
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing account configuration

    Raises:
        AccountNoMatchError: If account is not found or not accessible
        Account_Config_Error: If account configuration retrieval fails
    """

    if not data_provider_type:
        # Reuse the same RouteContext for the metadata lookup
        res = await get_account_by_id(
            auth=auth,
            account_id=account_id,
            is_unmask=is_unmask,
            context=context,
            return_raw=True,
        )
        data_provider_type = res.response["dataProviderType"]

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
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
        raise Account_Config_Error(account_id=str(account_id), res=res)

    res.response.update(
        {
            "_search_metadata": {
                "account_id": account_id,
                "data_provider_type": data_provider_type,
            }
        }
    )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_oauth_account_config(
    auth: DomoAuth,
    account_id: int | str,
    data_provider_type: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Retrieve configuration for a specific OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: The ID of the OAuth account to get config for
        data_provider_type: Type of data provider for the OAuth account
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object containing OAuth account configuration

    Raises:
        AccountNoMatchError: If OAuth account is not found or not accessible
        Account_Config_Error: If OAuth account configuration retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/template/{account_id}?unmask=true"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        timeout=20,  # occasionally this API has a long response time
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success and (
        res.response == "Forbidden" or res.response == "Not Found"
    ):
        raise AccountNoMatchError(account_id=str(account_id), res=res)

    if not res.is_success:
        raise Account_Config_Error(account_id=str(account_id), res=res)

    res.response.update(
        {
            "_search_metadata": {
                "account_id": account_id,
                "data_provider_type": data_provider_type,
            }
        }
    )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def update_account_config(
    auth: DomoAuth,
    account_id: int | str,
    config_body: dict,
    data_provider_type: str | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Update configuration for an account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the account to update config for
        config_body: New configuration data
        data_provider_type: Type of data provider (auto-detected if not provided)
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object confirming config update

    Raises:
        Account_Config_Error: If account configuration update fails
    """

    # get the data_provider_type, which is necessary for updating the config setting
    if not data_provider_type:
        res = await get_account_by_id(
            auth=auth,
            account_id=account_id,
            is_unmask=False,
            context=context,
            return_raw=True,
        )
        data_provider_type = res.response.get("dataProviderType")

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=config_body,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        raise Account_Config_Error(
            account_id=str(account_id),
            res=res,
            message=f"Error updating config | use debug_api = True - {res.response}",
        )

    if not res.is_success:
        raise Account_Config_Error(account_id=str(account_id), res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def update_oauth_account_config(
    auth: DomoAuth,
    account_id: int | str,
    config_body: dict,
    data_provider_type: str | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Update configuration for an OAuth account.

    Args:
        auth: Authentication object for API requests
        account_id: ID of the OAuth account to update config for
        config_body: New configuration data
        data_provider_type: Type of data provider (auto-detected if not provided)
        return_raw: Return raw response without processing
        context: RouteContext for request configuration

    Returns:
        ResponseGetData object confirming config update

    Raises:
        Account_Config_Error: If OAuth account configuration update fails
    """

    # get the data_provider_type, which is necessary for updating the config setting
    if not data_provider_type:
        res = await get_oauth_account_by_id(
            auth=auth,
            account_id=account_id,
            context=context,
            return_raw=True,
        )
        data_provider_type = res.response.get("dataProviderType")

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/template/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=config_body,
        context=context,
    )

    if return_raw:
        return res

    if res.status == 400 and res.response == "Bad Request":
        raise Account_Config_Error(
            account_id=str(account_id),
            res=res,
            message=f"Error updating OAuth config | use debug_api = True - {res.response}",
        )

    if not res.is_success:
        raise Account_Config_Error(account_id=str(account_id), res=res)

    return res
