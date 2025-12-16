"""
PDP Exception Classes

This module contains all exception classes used by PDP route functions.

Exception Classes:
    PDP_GET_Error: Raised when PDP policy retrieval operations fail
    SearchPDPNotFoundError: Raised when PDP search returns no results
    PDP_CRUD_Error: Raised when PDP create/update/delete operations fail
    PDPNotRetrievedError: Legacy error class (use PDP_GET_Error instead)
    SearchPDP_Error: Legacy error class (use SearchPDPNotFoundError instead)
    CreatePolicy_Error: Legacy error class (use PDP_CRUD_Error instead)
"""

from ...base.exceptions import RouteError
from ...client import response as rgd

__all__ = [
    "PDP_GET_Error",
    "SearchPDPNotFoundError",
    "PDP_CRUD_Error",
    # Legacy exports for backward compatibility
    "PDPNotRetrievedError",
    "SearchPDP_Error",
    "CreatePolicy_Error",
]


class PDP_GET_Error(RouteError):
    """
    Raised when PDP policy retrieval operations fail.

    This exception is used for failures during GET operations on PDP policies,
    including API errors and unexpected response formats.
    """

    def __init__(
        self,
        dataset_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            if dataset_id:
                message = f"Failed to retrieve PDP policies for dataset {dataset_id}"
            else:
                message = "Failed to retrieve PDP policies"

        super().__init__(message=message, entity_id=dataset_id, res=res, **kwargs)


class SearchPDPNotFoundError(RouteError):
    """
    Raised when PDP policy search operations return no results.

    This exception is used when searching for specific PDP policies that
    don't exist or when search criteria match no policies.
    """

    def __init__(
        self,
        search_criteria: str,
        res: rgd.ResponseGetData | None = None,
        **kwargs,
    ):
        message = f"No PDP policies found matching: {search_criteria}"
        super().__init__(
            message=message,
            res=res,
            **kwargs,
        )


class PDP_CRUD_Error(RouteError):
    """
    Raised when PDP policy create, update, or delete operations fail.

    This exception is used for failures during policy creation, modification,
    or deletion operations.
    """

    def __init__(
        self,
        operation: str,
        dataset_id: str | None = None,
        policy_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            if policy_id:
                message = f"PDP policy {operation} failed for policy {policy_id}"
            elif dataset_id:
                message = f"PDP policy {operation} failed for dataset {dataset_id}"
            else:
                message = f"PDP policy {operation} operation failed"

        super().__init__(
            message=message,
            entity_id=policy_id or dataset_id,
            res=res,
            **kwargs,
        )


# Legacy error classes for backward compatibility
class PDPNotRetrievedError(PDP_GET_Error):
    """Legacy error class - use PDP_GET_Error instead."""

    def __init__(
        self,
        domo_instance=None,
        function_name=None,
        status=None,
        message=None,
        pdp_id=None,
    ):
        super().__init__(
            dataset_id=pdp_id,
            message=message,
            res=None,
        )


class SearchPDP_Error(SearchPDPNotFoundError):
    """Legacy error class - use SearchPDPNotFoundError instead."""

    def __init__(
        self, status=None, message=None, domo_instance=None, function_name=None
    ):
        # Extract search criteria from message if available
        search_criteria = message or "unknown"
        super().__init__(search_criteria=search_criteria, res=None)


class CreatePolicy_Error(PDP_CRUD_Error):
    """Legacy error class - use PDP_CRUD_Error instead."""

    def __init__(
        self, res: rgd.ResponseGetData | None = None, message: str | None = None
    ):
        super().__init__(operation="create", message=message, res=res)
