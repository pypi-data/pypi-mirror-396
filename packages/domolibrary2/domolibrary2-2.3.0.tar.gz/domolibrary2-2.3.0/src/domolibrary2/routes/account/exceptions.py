"""
Account Route Exception Classes

This module contains all exception classes used by account route functions.

Exception Classes:
    Account_GET_Error: Raised when account retrieval operations fail
    SearchAccountNotFoundError: Raised when account search returns no results
    Account_CRUD_Error: Raised when account create/update/delete operations fail
    AccountSharing_Error: Raised when account sharing operations fail
    Account_Config_Error: Raised when account configuration operations fail
    AccountNoMatchError: Raised when a specific account cannot be found or accessed
    Account_CreateParams_Error: Raised when account creation parameters are invalid
"""

from ...base.exceptions import RouteError


class Account_GET_Error(RouteError):
    """Raised when account retrieval operations fail."""

    def __init__(self, account_id: str | None = None, res=None, **kwargs):
        super().__init__(
            message="Account retrieval failed",
            entity_id=account_id,
            res=res,
            **kwargs,
        )


class SearchAccountNotFoundError(RouteError):
    """Raised when account search operations return no results."""

    def __init__(self, search_criteria: str, res=None, **kwargs):
        message = f"No accounts found matching: {search_criteria}"
        super().__init__(
            message=message,
            res=res,
            additional_context={"search_criteria": search_criteria},
            **kwargs,
        )


class Account_CRUD_Error(RouteError):
    """Raised when account create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str = "CRUD",
        account_id: str | None = None,
        res=None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            message = f"Account {operation} operation failed"
        super().__init__(message=message, entity_id=account_id, res=res, **kwargs)


class AccountSharing_Error(RouteError):
    """Raised when account sharing operations fail."""

    def __init__(
        self,
        operation: str,
        account_id: str | None = None,
        res=None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            message = f"Account sharing {operation} failed"
        super().__init__(message=message, entity_id=account_id, res=res, **kwargs)


class Account_Config_Error(RouteError):
    """Raised when account configuration operations fail."""

    def __init__(
        self,
        account_id: str | None = None,
        res=None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            message = "Account configuration operation failed"
        super().__init__(message=message, entity_id=account_id, res=res, **kwargs)


class AccountNoMatchError(RouteError):
    """Raised when a specific account cannot be found or accessed."""

    def __init__(
        self,
        account_id: str | None = None,
        res=None,
        message: str = "Account not found -- has it been shared with the user?",
        **kwargs,
    ):
        super().__init__(message=message, entity_id=account_id, res=res, **kwargs)


class Account_CreateParams_Error(RouteError):
    """Raised when account creation parameters are invalid."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, **kwargs)
