from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

"""
CodeEngine Core Route Functions

This module provides core functions for managing Domo CodeEngine packages including
retrieval and testing operations.

Functions:
    get_packages: Retrieve all codeengine packages
    get_codeengine_package_by_id: Retrieve a specific package by ID
    get_package_versions: Retrieve all versions of a package
    get_codeengine_package_by_id_and_version: Retrieve a specific package version
    test_package_is_released: Test if a package version is released
    test_package_is_identical: Test if package code is identical to existing

Enums:
    CodeEngine_Package_Parts: Enum for package parts parameter values
"""

from __future__ import annotations

from enum import Enum

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from .exceptions import (
    CodeEngine_FunctionCallError,
    CodeEngine_GET_Error,
)

__all__ = [
    "CodeEngine_Package_Parts",
    "get_packages",
    "get_codeengine_package_by_id",
    "get_current_package_version",
    "get_package_versions",
    "get_codeengine_package_by_id_and_version",
    "test_package_is_released",
    "test_package_is_identical",
    "execute_codeengine_function",
]


class CodeEngine_Package_Parts(DomoEnumMixin, Enum):
    """Enum for package parts parameter values."""

    VERSIONS = "versions"
    FUNCTIONS = "functions"
    CODE = "code"


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_packages(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve all codeengine packages.

    Args:
        auth: Authentication object
        context: Route context (optional)
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package list

    Raises:
        CodeEngine_GET_Error: If package retrieval fails
    """
    url = f"http://{auth.domo_instance}.domo.com/api/codeengine/v2/packages"

    res = await gd.get_data(
        url=url,
        auth=auth,
        method="get",
        context=context,
        is_follow_redirects=True,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_GET_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_codeengine_package_by_id(
    auth: DomoAuth,
    package_id: str,
    params: dict | None = None,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific codeengine package by ID.

    Args:
        auth: Authentication object
        package_id: Package identifier
        params: Query parameters (optional, defaults to {"parts": "versions"})
        context: Route context (optional)
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package data

    Raises:
        CodeEngine_FunctionCallError: If package_id is not provided
        CodeEngine_GET_Error: If package retrieval fails
    """
    if not package_id:
        raise CodeEngine_FunctionCallError(
            message="Package ID must be provided.",
            auth=auth,
        )

    url = (
        f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}"
    )

    params = params or {"parts": "versions, name"}

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
        raise CodeEngine_GET_Error(entity_id=package_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_current_package_version(
    auth: DomoAuth,
    package_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> str:
    """
    Get the current version of a CodeEngine package.

    Convenience function that retrieves the package metadata and extracts
    the current version string from the versions array.

    Args:
        auth: Authentication object
        package_id: Package identifier
        context: Route context (optional)

    Returns:
        str: Current package version (e.g., "1.0.0")

    Raises:
        CodeEngine_GET_Error: If package retrieval fails or version not found

    Example:
        >>> version = await get_current_package_version(
        ...     auth=auth,
        ...     package_id="b368d630-7ca5-4b8a-b4ec-f130cf312dc1"
        ... )
        >>> print(f"Current version: {version}")
        Current version: 1.2.3
    """
    res = await get_codeengine_package_by_id(
        auth=auth,
        package_id=package_id,
        params={"parts": "versions"},
        context=context,
        return_raw=False,
    )

    # Extract version from response
    versions = res.response.get("versions", [])
    if not versions:
        raise CodeEngine_GET_Error(
            entity_id=package_id,
            res=res,
            message="No versions found for package",
        )

    # Return the last version (current version)
    current_version = versions[-1].get("version")
    if not current_version:
        raise CodeEngine_GET_Error(
            entity_id=package_id,
            res=res,
            message="Version string not found in package metadata",
        )

    res.response = current_version

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_package_versions(
    auth: DomoAuth,
    package_id: str,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve all versions of a codeengine package.

    Each package can have one or many versions.

    Args:
        auth: Authentication object
        package_id: Package identifier
        context: Route context (optional)
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package versions

    Raises:
        CodeEngine_FunctionCallError: If package_id is not provided
        CodeEngine_GET_Error: If version retrieval fails
    """
    if not package_id:
        raise CodeEngine_FunctionCallError(
            message="Package ID must be provided.",
            auth=auth,
        )

    url = f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}/versions/"

    params = {"parts": "functions,code"}

    res = await gd.get_data(
        url=url,
        method="get",
        auth=auth,
        params=params,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_GET_Error(entity_id=package_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_codeengine_package_by_id_and_version(
    auth: DomoAuth,
    package_id: str,
    version: str,
    params: dict | None = None,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieve a specific codeengine package by ID and version.

    Args:
        auth: Authentication object
        package_id: Package identifier
        version: Package version
        params: Query parameters (optional, defaults to {"parts": "functions,code"})
        context: Route context (optional)
        return_raw: Return raw response without processing

    Returns:
        ResponseGetData object containing package version data

    Raises:
        CodeEngine_FunctionCallError: If package_id or version is not provided
        CodeEngine_GET_Error: If package retrieval fails
    """
    if not package_id or not version:
        raise CodeEngine_FunctionCallError(
            message=f"Package ID {package_id or 'not provided'} and version {version or 'not provided'} must be provided.",
            auth=auth,
        )

    url = f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}/versions/{version}"

    params = params or {"parts": "functions,code,name"}

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
        raise CodeEngine_GET_Error(entity_id=f"{package_id}/v{version}", res=res)

    return res


async def test_package_is_released(
    package_id: str,
    version: str,
    auth: DomoAuth,
    existing_package: dict | None = None,
    params: dict | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> bool:
    """
    Test if a package version is already released.

    Args:
        package_id: Package identifier
        version: Package version
        auth: Authentication object
        existing_package: Pre-fetched package data (optional)
        params: Query parameters (optional)
        context: Route context (optional)
        **context_kwargs: Additional context parameters

    Returns:
        True if the package is already released, False otherwise
    """
    existing_package = (
        existing_package
        or (
            await get_codeengine_package_by_id_and_version(
                auth=auth,
                package_id=package_id,
                version=version,
                params=params,
                context=context,
            )
        ).response
    )

    return existing_package.get("released", False)


async def test_package_is_identical(
    package_id: str,
    version: str,
    auth: DomoAuth,
    existing_package: dict | None = None,
    new_package: dict | None = None,
    new_code: str | None = None,
    params: dict | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> bool:
    """
    Test if the code in a new package matches the existing package.

    Args:
        package_id: Package identifier
        version: Package version
        auth: Authentication object
        existing_package: Pre-fetched existing package data (optional)
        new_package: New package data to compare (optional)
        new_code: New code to compare (optional)
        params: Query parameters (optional)
        context: Route context (optional)
        **context_kwargs: Additional context parameters

    Returns:
        True if the package code is identical, False otherwise
    """
    existing_package = (
        existing_package
        or (
            await get_codeengine_package_by_id(
                auth=auth,
                package_id=package_id,
                params=params,
                context=context,
            )
        ).response
    )

    new_code = new_code or (new_package.get("code") if new_package else None)

    return existing_package.get("code") == new_code


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def execute_codeengine_function(
    auth: DomoAuth,
    package_id: str,
    version: str,
    function_name: str,
    input_variables: dict,
    is_get_logs: bool = True,
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/codeengine/v2/packages/{package_id}/versions/{version}/functions/{function_name}"

    res = await gd.get_data(
        method="POST",
        url=url,
        auth=auth,
        body={"inputVariables": input_variables, "settings": {"getLogs": is_get_logs}},
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise CodeEngine_GET_Error(
            entity_id=f"{package_id}/v{version}/function/{function_name}", res=res
        )

    print("\n\n")
    print("Function Execution Response:")
    print(f"Status: {res.status}")
    print(f"Response type: {type(res.response)}")
    print(f"Response: {res.response}")
    print(f"Response repr: {repr(res.response)}")

    # Handle empty or non-dict responses
    if not res.response or not isinstance(res.response, dict):
        raise CodeEngine_FunctionCallError(
            message=f"Function execution returned invalid response: {res.response!r}",
            auth=auth,
            res=res,
        )

    if not res.response.get("status") == "SUCCESS":
        raise CodeEngine_FunctionCallError(
            message=f"Function execution failed with status {res.response.get('status')}",
            auth=auth,
            res=res,
        )

    response = res.response.pop("result")

    metadata = res.response

    res.response = {**response, "_metadata": metadata}

    return res
