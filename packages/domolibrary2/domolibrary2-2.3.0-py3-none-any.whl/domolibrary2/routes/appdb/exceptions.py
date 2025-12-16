"""
AppDb Exception Classes

This module contains all exception classes used by AppDb route functions.

Exception Classes:
    AppDb_GET_Error: Raised when AppDb retrieval operations fail
    SearchAppDbNotFoundError: Raised when AppDb search returns no results
    AppDb_CRUD_Error: Raised when AppDb create/update/delete operations fail
"""

from ...base.exceptions import RouteError

__all__ = [
    "AppDb_GET_Error",
    "SearchAppDbNotFoundError",
    "AppDb_CRUD_Error",
]


class AppDb_GET_Error(RouteError):
    """Raised when AppDb retrieval operations fail."""

    def __init__(
        self,
        appdb_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "AppDb retrieval failed",
            entity_id=appdb_id,
            res=res,
            **kwargs,
        )


class SearchAppDbNotFoundError(RouteError):
    """Raised when AppDb search operations return no results."""

    def __init__(
        self,
        search_criteria: str,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"No AppDb items found matching: {search_criteria}",
            res=res,
            **kwargs,
        )


class AppDb_CRUD_Error(RouteError):
    """Raised when AppDb create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        appdb_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"AppDb {operation} operation failed",
            entity_id=appdb_id,
            res=res,
            **kwargs,
        )
