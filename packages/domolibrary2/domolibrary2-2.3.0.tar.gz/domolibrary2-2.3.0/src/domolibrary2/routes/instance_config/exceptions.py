"""
Instance Config Route Exception Classes

This module contains all exception classes used by instance config route functions.

Exception Classes:
    ApiClient_GET_Error: Raised when API client retrieval operations fail
    ApiClient_CRUD_Error: Raised when API client create/update/delete operations fail
    ApiClient_RevokeError: Raised when API client revocation operations fail
    SearchApiClientNotFoundError: Raised when API client search operations return no results
"""

from ...base.exceptions import RouteError
from ...client import response as rgd

__all__ = [
    "ApiClient_GET_Error",
    "ApiClient_CRUD_Error",
    "ApiClient_RevokeError",
    "SearchApiClientNotFoundError",
]


class Config_GET_Error(RouteError):
    def __init__(self, res: rgd.ResponseGetData, message: str | None = None):
        super().__init__(res=res, message=message)


class Config_CRUD_Error(RouteError):
    def __init__(self, res: rgd.ResponseGetData, message: str | None = None):
        super().__init__(res=res, message=message)


class ApiClient_GET_Error(RouteError):
    """
    Raised when API client retrieval operations fail.

    This exception is used for failures during GET operations on API clients,
    including API errors and unexpected response formats.
    """

    def __init__(
        self,
        entity_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            if entity_id:
                message = f"Failed to retrieve API client {entity_id}"
            else:
                message = "Failed to retrieve API clients"

        super().__init__(message=message, entity_id=entity_id, res=res, **kwargs)


class ApiClient_CRUD_Error(RouteError):
    """
    Raised when API client create, update, or delete operations fail.

    This exception is used for failures during API client creation, modification,
    or deletion operations.
    """

    def __init__(
        self,
        operation: str = "operation",
        entity_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            if entity_id:
                message = f"API client {operation} failed for client {entity_id}"
            else:
                message = f"API client {operation} operation failed"

        super().__init__(
            message=message,
            entity_id=entity_id,
            res=res,
            additional_context={"operation": operation},
            **kwargs,
        )


class ApiClient_RevokeError(RouteError):
    """
    Raised when API client revocation operations fail.

    This is a specialized CRUD error specifically for revocation operations.
    It provides additional context for revocation-specific failures.
    """

    def __init__(
        self,
        client_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            if client_id:
                message = f"Error revoking API client {client_id}"
            else:
                message = "Error revoking API client"

        super().__init__(
            message=message,
            entity_id=client_id,
            res=res,
            **kwargs,
        )


class SearchApiClientNotFoundError(RouteError):
    """
    Raised when API client search operations return no results.

    This exception is used when searching for API clients by name or other
    criteria yields no matching results.
    """

    def __init__(
        self,
        search_criteria: str,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            message = f"No API client found matching: {search_criteria}"

        super().__init__(
            message=message,
            res=res,
            additional_context={"search_criteria": search_criteria},
            **kwargs,
        )
