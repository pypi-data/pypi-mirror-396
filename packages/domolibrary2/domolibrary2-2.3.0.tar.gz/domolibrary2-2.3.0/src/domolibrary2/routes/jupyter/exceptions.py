"""
Jupyter Exception Classes

This module contains all exception classes for Jupyter workspace operations.
"""

from ...base.exceptions import RouteError

__all__ = [
    "Jupyter_GET_Error",
    "SearchJupyterNotFoundError",
    "Jupyter_CRUD_Error",
    "JupyterWorkspace_Error",
]


class Jupyter_GET_Error(RouteError):
    """Raised when Jupyter workspace retrieval operations fail."""

    def __init__(
        self,
        workspace_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            entity_id=workspace_id,
            res=res,
            **kwargs,
        )


class SearchJupyterNotFoundError(RouteError):
    """Raised when Jupyter workspace search operations return no results."""

    def __init__(
        self,
        search_criteria: str,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message
            or f"Jupyter search returned no results for: {search_criteria}",
            entity_id=search_criteria,
            res=res,
            **kwargs,
        )


class Jupyter_CRUD_Error(RouteError):
    """Raised when Jupyter workspace create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        workspace_id: str | None = None,
        content_path: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        entity_id = workspace_id or content_path
        super().__init__(
            message=message or f"Jupyter {operation} operation failed",
            entity_id=entity_id,
            res=res,
            **kwargs,
        )


class JupyterWorkspace_Error(RouteError):
    """Raised when Jupyter workspace operations fail."""

    def __init__(
        self,
        operation: str,
        workspace_id: str,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Jupyter workspace {operation} operation failed",
            entity_id=workspace_id,
            res=res,
            **kwargs,
        )


# Backward compatibility aliases
JupyterAPI_Error = Jupyter_GET_Error
JupyterAPI_WorkspaceStarted = JupyterWorkspace_Error
