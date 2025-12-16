"""CodeEngine Upload Route Functions.

This module provides route functions for uploading Python code to CodeEngine packages.

Functions:
    upload_package_version: Upload Python code to a CodeEngine package

Example:
    >>> from domolibrary2.routes.codeengine import upload_package_version
    >>> result = await upload_package_version(
    ...     auth=auth,
    ...     package_id="517ca12c-3459-4e66-b0bb-40f000720a84",
    ...     code="def hello(name: str) -> str: return f'Hello {name}'"
    ... )
"""

from __future__ import annotations

from ...auth import DomoAuth
from ...base.exceptions import DomoError
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
from .exceptions import CodeEngine_CRUD_Error

__all__ = [
    "upload_package_version",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def upload_package_version(
    auth: DomoAuth,
    package_id: str,
    code: str,
    is_new_version: bool = False,
    metadata: dict | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Upload Python code to a CodeEngine package.

    This route function validates inputs, builds a manifest from the Python code,
    and deploys it to the specified CodeEngine package.

    Args:
        auth: Authentication object with valid Domo credentials
        package_id: ID of the CodeEngine package to update
        code: Python source code string to deploy
        is_new_version: If True, create a new version. If False (default),
            update the current version.
        metadata: Optional metadata overrides including:
            - runtime: Runtime version (default: "PYTHON_3_13")
            - accountsMapping: List of account mapping dicts
            - name: Package name override
            - description: Package description
            - handler_name: Name of the handler function
        return_raw: Return raw response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData containing:
            - package_id: The package ID
            - version: The version that was created/updated
            - status: "created" or "updated"
            - manifest: The generated manifest

    Raises:
        CodeEngine_CRUD_Error: If validation fails or deployment fails

    Example:
        >>> from domolibrary2.auth import DomoTokenAuth
        >>> auth = DomoTokenAuth(
        ...     domo_instance="mycompany",
        ...     domo_access_token="your-token"
        ... )
        >>> code = '''
        ... def process_data(items: list, limit: int = 10) -> dict:
        ...     \"\"\"Process items and return summary.\"\"\"
        ...     return {"count": len(items[:limit])}
        ... '''
        >>> result = await upload_package_version(
        ...     auth=auth,
        ...     package_id="517ca12c-3459-4e66-b0bb-40f000720a84",
        ...     code=code,
        ...     is_new_version=False
        ... )

    Note:
        - Default runtime is Python 3.13 ("PYTHON_3_13")
        - Multi-file packages are not supported; code must be a single string
        - The first top-level function in the code is used as the handler unless
          handler_name is specified in metadata
    """

    # Validate inputs
    if not package_id:
        raise CodeEngine_CRUD_Error(
            operation="upload",
            message="package_id is required",
        )

    if not code or not code.strip():
        raise CodeEngine_CRUD_Error(
            operation="upload",
            entity_id=package_id,
            message="code is required and cannot be empty",
        )

    # Import here to avoid circular imports
    from ...classes.DomoCodeEngine.CodeEngine import DomoCodeEngine_Package

    # Get package instance and deploy
    package = await DomoCodeEngine_Package.get_by_id(
        auth=auth,
        package_id=package_id,
        context=context,
    )

    try:
        result = await package.deploy_version(
            code=code,
            is_new_version=is_new_version,
            metadata=metadata,
            context=context,
        )

        # Build response
        res = rgd.ResponseGetData(
            status=200,
            response=result,
            is_success=True,
        )

        return res

    except DomoError as e:
        # Wrap non-CodeEngine errors
        if not isinstance(e, CodeEngine_CRUD_Error):
            raise CodeEngine_CRUD_Error(
                operation="upload",
                entity_id=package_id,
                message=str(e),
            ) from e
        raise
