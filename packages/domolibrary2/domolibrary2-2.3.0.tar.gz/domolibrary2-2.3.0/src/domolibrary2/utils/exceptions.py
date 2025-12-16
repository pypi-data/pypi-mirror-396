"""
Utility Exceptions Module

This module provides custom exception classes used throughout the utilities library.
All exceptions inherit from a base UtilityError class for consistent error handling.

Classes:
    UtilityError: Base exception class for all utility errors
    InvalidEmailError: Raised when email validation fails
    ConcatDataframeError: Raised when dataframe concatenation fails
    FileOperationError: Raised when file operations fail
    ImageProcessingError: Raised when image processing fails
    CredentialsError: Raised when credential reading fails
"""

__all__ = [
    "UtilityError",
    "InvalidEmailError",
    "ConcatDataframeError",
    "FileOperationError",
    "ImageProcessingError",
    "CredentialsError",
]

from typing import Any


class UtilityError(Exception):
    """
    Base exception class for all utility errors.

    Provides consistent error handling and message formatting across all utilities.
    All other utility exceptions should inherit from this class.

    Args:
        message (str): The error message
        details (Any, optional): Additional error details for debugging

    Attributes:
        message (str): The error message
        details (Any): Additional error details
    """

    def __init__(self, message: str, details: Any | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class InvalidEmailError(UtilityError):
    """
    Raised when email validation fails.

    This exception is raised when a provided email address does not match
    the expected email format pattern.

    Args:
        email (str): The invalid email address that caused the error

    Example:
        >>> try:
        ...     validate_email("invalid-email")
        ... except InvalidEmailError as e:
        ...     print(f"Error: {e}")
        Error: Invalid email format: "invalid-email"
    """

    def __init__(self, email: str):
        message = f'Invalid email format: "{email}"'
        super().__init__(message, {"email": email})
        self.email = email


class ConcatDataframeError(UtilityError):
    """
    Raised when dataframe concatenation operations fail.

    This exception is raised when attempting to concatenate objects that
    are not pandas DataFrames or when concatenation operations fail.

    Args:
        element (Any): The invalid element that caused the error
        operation (str, optional): The operation being performed

    Example:
        >>> try:
        ...     concat_dataframes([df1, "not_a_dataframe", df2])
        ... except ConcatDataframeError as e:
        ...     print(f"Error: {e}")
        Error: Invalid element type for concatenation: <class 'str'>
    """

    def __init__(self, element: Any, operation: str = "concatenation"):
        element_type = type(element).__name__
        message = f"Invalid element type for {operation}: {element_type}"
        super().__init__(message, {"element": element, "type": element_type})
        self.element = element
        self.operation = operation


class FileOperationError(UtilityError):
    """
    Raised when file operations fail.

    This exception is raised when file creation, reading, writing, or other
    file system operations encounter errors.

    Args:
        operation (str): The file operation that failed
        file_path (str): The file path involved in the operation
        details (Any, optional): Additional error details

    Example:
        >>> try:
        ...     create_folder("/invalid/path")
        ... except FileOperationError as e:
        ...     print(f"Error: {e}")
        Error: Failed to create folder at "/invalid/path"
    """

    def __init__(self, operation: str, file_path: str, details: Any | None = None):
        message = f'Failed to {operation} at "{file_path}"'
        super().__init__(message, details)
        self.operation = operation
        self.file_path = file_path


class ImageProcessingError(UtilityError):
    """
    Raised when image processing operations fail.

    This exception is raised when image loading, processing, or manipulation
    operations encounter errors.

    Args:
        operation (str): The image operation that failed
        details (Any, optional): Additional error details

    Example:
        >>> try:
        ...     load_image("invalid.jpg")
        ... except ImageProcessingError as e:
        ...     print(f"Error: {e}")
        Error: Failed to load image
    """

    def __init__(self, operation: str, details: Any | None = None):
        message = f"Failed to {operation}"
        super().__init__(message, details)
        self.operation = operation


class CredentialsError(UtilityError):
    """
    Raised when credential reading or validation fails.

    This exception is raised when attempting to read credentials from
    environment files or when credential validation fails.

    Args:
        source (str): The credential source (file path, environment, etc.)
        details (Any, optional): Additional error details

    Example:
        >>> try:
        ...     read_credentials(".env")
        ... except CredentialsError as e:
        ...     print(f"Error: {e}")
        Error: Failed to read credentials from ".env"
    """

    def __init__(self, source: str, details: Any | None = None):
        message = f'Failed to read credentials from "{source}"'
        super().__init__(message, details)
        self.source = source
