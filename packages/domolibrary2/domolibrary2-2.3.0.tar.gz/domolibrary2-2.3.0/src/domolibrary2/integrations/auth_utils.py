import os

from dc_logger.client.base import get_global_logger

import domolibrary2.auth as dmda
from domolibrary2.base.exceptions import DomoError
from domolibrary2.client.response import ResponseGetData
from domolibrary2.routes import codeengine as ce_routes
from domolibrary2.utils.logging import log_call

"""
CodeEngine Auth Utility
======================

This module provides a utility function to retrieve Domo authentication credentials from a CodeEngine package.

**How it works:**
1. You must have a CodeEngine package deployed in your Domo instance with a function named `get_account`:

    def get_account(auth_name: str) -> dict:
        return codeengine.get_account(auth_name)

2. Share the necessary accounts with the CodeEngine package so it can access the credentials for the requested `auth_name`.

3. Use `get_auth_from_codeengine` to retrieve credentials for a given account alias (e.g., `sdk_config`, `sdk_data`).

**Typical usage:**

```python
import domolibrary2.auth as dmda
from domolibrary2.integrations.auth_utils import get_auth_from_codeengine

config_auth = dmda.DomoTokenAuth(
    domo_instance="your-instance",
    domo_access_token="your-access-token",
)

target_auth = await get_auth_from_codeengine(
    config_auth=config_auth,
    target_instance="target-instance",
    sudo_package_id="your-package-id",
    sudo_package_version="1.3.1",
    retreival_account_name="sdk_config",
)
# target_auth is a DomoTokenAuth for the requested account
```

**Parameters:**
- `config_auth`: DomoAuth with access to the Domo instance (used to authenticate the API request)
- `target_instance`: The Domo instance for which you want credentials
- `sudo_package_id`: The CodeEngine package ID
- `sudo_package_version`: The version of the CodeEngine package
- `retreival_account_name`: The alias of the account to retrieve (must be shared with the package)
- `function_name`: The CodeEngine function to call (default: "get_account")
- `is_return_access_token`: If True, returns a DomoTokenAuth; if False, returns the raw ResponseGetData

**Returns:**
- DomoTokenAuth for the requested account, or ResponseGetData if `is_return_access_token` is False

**Errors:**
- Raises AssertionError if the returned token is invalid

**See also:**
- CodeEngine package sharing: domolibrary2.routes.codeengine.share_accounts_with_package
- CodeEngine function execution: domolibrary2.routes.codeengine.execute_codeengine_function
"""

logger = get_global_logger()


@log_call(level_name="integration", color="cyan", log_level="info")
async def get_auth_from_env(
    domo_instance_env_var: str = "DOMO_INSTANCE",
    domo_token_env_var: str = "DOMO_ACCESS_TOKEN",
):
    try:
        await logger.info(
            f"Retrieving DomoTokenAuth from environment variables - {domo_instance_env_var}, {domo_token_env_var}",
        )

        auth = dmda.DomoTokenAuth(
            domo_instance=os.environ[domo_instance_env_var],
            domo_access_token=os.environ[domo_token_env_var],
        )
    except KeyError as e:
        message = f"Environment variable not found for Domo auth: {e}"
        await logger.error(message)
        raise KeyError(message)

    try:
        await logger.info(
            f"Validating DomoTokenAuth from environment variables - {domo_instance_env_var}"
        )
        assert await auth.print_is_token()
    except (AssertionError, DomoError) as e:
        message = f"Invalid Domo auth retrieved from environment variables - {e}"
        await logger.error(message)
        raise AssertionError(message)

    return auth


@log_call(level_name="integration", color="cyan", log_level="info")
async def get_auth_from_codeengine(
    config_auth: dmda.DomoAuth,
    sudo_package_id: str,
    sudo_package_version: str,
    retrieval_account_name: str,
    # for returing DomoTokenAuth
    is_return_access_token: bool = True,
    target_instance: str = None,  # required for generating a DomoTokenAuth
    function_name: str = "get_account",  # code engine function name
    debug_api: bool = False,
    return_raw: bool = False,
    **kwargs,
) -> dmda.DomoTokenAuth | ResponseGetData:
    """
    Retrieve account object in clear text using a CodeEngine package.
    optionally converts to DomoTokenAuth.

    Args:
        config_auth: DomoAuth with access to the Domo instance (authenticates the API request)
        target_instance: The Domo instance for which credentials are requested
        sudo_package_id: The CodeEngine package ID
        sudo_package_version: The version of the CodeEngine package
        retreival_account_name: The alias of the account to retrieve (must be shared with the package)
        function_name: The CodeEngine function to call (default: "get_account")
        is_return_access_token: If True, returns a DomoTokenAuth; if False, returns the raw ResponseGetData

    Returns:
        DomoTokenAuth for the requested account, or ResponseGetData if is_return_access_token is False

    Raises:
        AssertionError: If the returned token is invalid
    """

    res = await ce_routes.execute_codeengine_function(
        auth=config_auth,
        package_id=sudo_package_id,
        version=sudo_package_version,
        function_name=function_name,
        input_variables={"auth_name": retrieval_account_name},
        debug_api=debug_api,
        return_raw=return_raw,
        **kwargs,
    )

    if return_raw:
        return res

    if not is_return_access_token:
        await logger.info(
            f"Retrieved auth response for account '{retrieval_account_name}' from Code Engine - returning raw response"
        )
        return res

    await logger.info(
        f"Retrieved auth response for account '{retrieval_account_name}' from Code Engine - generating DomoTokenAuth"
    )
    target_auth = dmda.DomoTokenAuth(
        domo_access_token=res.response["properties"]["domoAccessToken"],
        domo_instance=target_instance,
    )
    try:
        await logger.info(
            f"Validating retrieved DomoTokenAuth - {retrieval_account_name}"
        )
        assert await target_auth.print_is_token()

    except (AssertionError, DomoError) as e:
        message = f"Invalid auth retrieved from CodeEngine for account '{retrieval_account_name}' - {e}"
        await logger.error(message)
        raise AssertionError(message)

    return target_auth
