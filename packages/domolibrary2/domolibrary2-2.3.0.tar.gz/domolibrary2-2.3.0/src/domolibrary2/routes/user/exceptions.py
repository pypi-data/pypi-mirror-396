"""
User Route Exception Classes

This module contains all exception classes used by user route functions.

Exception Classes:
    User_GET_Error: Raised when user retrieval operations fail
    User_CRUD_Error: Raised when user create/update/delete operations fail
    SearchUserNotFoundError: Raised when user search returns no results
    UserSharingError: Raised when user sharing operations fail
    DeleteUserError: Raised when user deletion operations fail
    UserAttributes_GET_Error: Raised when user attribute retrieval fails
    UserAttributes_CRUD_Error: Raised when user attribute create/update/delete fails
    ResetPasswordPasswordUsedError: Raised when password was previously used
    DownloadAvatar_Error: Raised when avatar download fails
"""

from ...base.exceptions import RouteError
from ...client import response as rgd

__all__ = [
    "User_GET_Error",
    "User_CRUD_Error",
    "SearchUserNotFoundError",
    "UserSharing_Error",
    "DeleteUserError",
    "UserAttributes_GET_Error",
    "UserAttributes_CRUD_Error",
    "ResetPasswordPasswordUsedError",
    "DownloadAvatar_Error",
]


class User_GET_Error(RouteError):
    """Raised when user retrieval operations fail."""

    def __init__(
        self, user_id: str | None = None, res=None, message: str | None = None, **kwargs
    ):
        if not message:
            message = "User retrieval failed"

        super().__init__(res=res, entity_id=user_id, message=message, **kwargs)


class User_CRUD_Error(RouteError):
    """Raised when user create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        user_id: str | None = None,
        res=None,
        message: str | None = None,
        **kwargs,
    ):
        # Use provided message if available, otherwise create default
        if not message:
            message = f"User {operation} operation failed"

        super().__init__(res=res, entity_id=user_id, message=message, **kwargs)


class SearchUserNotFoundError(RouteError):
    """Raised when user search operations return no results."""

    def __init__(
        self, search_criteria: str, res=None, message: str | None = None, **kwargs
    ):
        if not message:
            message = f"No users found matching: {search_criteria}"
        super().__init__(res=res, entity_id=search_criteria, message=message, **kwargs)


class UserSharing_Error(RouteError):
    """Raised when user sharing operations fail."""

    def __init__(
        self,
        operation: str,
        user_id: str | None = None,
        res=None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            message = f"User sharing {operation} failed"
        super().__init__(res=res, entity_id=user_id, message=message, **kwargs)


class DeleteUserError(RouteError):
    """Raised when user deletion operations fail."""

    def __init__(
        self,
        res: rgd.ResponseGetData,
        message: str | None = None,
        user_id: str | None = None,
        **kwargs,
    ):
        super().__init__(res=res, entity_id=user_id, message=message, **kwargs)


class UserAttributes_GET_Error(RouteError):
    """Raised when user attributes retrieval operations fail."""

    def __init__(
        self,
        attribute_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        if not message:
            message = "User attributes retrieval failed"
        super().__init__(res=res, entity_id=attribute_id, message=message, **kwargs)


class UserAttributes_CRUD_Error(RouteError):
    """Raised when user attributes create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        attribute_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        if not message:
            message = f"User attributes {operation} operation failed"

        super().__init__(res=res, entity_id=attribute_id, message=message, **kwargs)


class ResetPasswordPasswordUsedError(RouteError):
    """Raised when attempting to reset password to a previously used password."""

    def __init__(
        self,
        user_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            message = "Password was previously used"
        super().__init__(res=res, entity_id=user_id, message=message, **kwargs)


class DownloadAvatar_Error(RouteError):
    """Raised when user avatar download operations fail."""

    def __init__(
        self,
        user_id: str | None = None,
        res: rgd.ResponseGetData | None = None,
        message: str | None = None,
        **kwargs,
    ):
        if not message:
            message = "Avatar download failed"
        super().__init__(res=res, entity_id=user_id, message=message, **kwargs)
