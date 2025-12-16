"""
Page Exception Classes

This module contains all exception classes for page operations.
"""

from ...base.exceptions import RouteError
from ...client import response as rgd

__all__ = [
    "Page_GET_Error",
    "SearchPageNotFoundError",
    "Page_CRUD_Error",
    "PageSharing_Error",
]


class Page_GET_Error(RouteError):
    """Raised when page retrieval operations fail."""

    def __init__(
        self,
        page_id: str | None = None,
        message: str | None = None,
        res: rgd.ResponseGetData | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Page retrieval failed",
            entity_id=page_id,
            res=res,
            **kwargs,
        )


class SearchPageNotFoundError(RouteError):
    """Raised when page search operations return no results."""

    def __init__(
        self,
        message: str | None = None,
        search_criteria: str | None = None,
        res: rgd.ResponseGetData | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"No pages found matching: {search_criteria}",
            res=res,
            additional_context={"search_criteria": search_criteria},
            **kwargs,
        )


class Page_CRUD_Error(RouteError):
    """Raised when page create, update, or delete operations fail."""

    def __init__(
        self,
        message: str | None = None,
        operation: str | None = None,
        page_id: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Page {operation} operation failed",
            entity_id=page_id,
            res=res,
            **kwargs,
        )


class PageSharing_Error(RouteError):
    """Raised when page sharing operations fail."""

    def __init__(
        self,
        message: str | None = None,
        operation: str | None = None,
        page_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Page sharing {operation} failed",
            entity_id=page_id,
            res=res,
            **kwargs,
        )
