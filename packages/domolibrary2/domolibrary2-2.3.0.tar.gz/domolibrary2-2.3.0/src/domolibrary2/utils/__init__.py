"""
Utilities Library

A comprehensive collection of utility functions for data processing, file operations,
image handling, and common programming tasks. This library is designed to be
standalone and reusable across different projects.

Modules:
    chunk_execution: Async execution utilities with retry logic and concurrency control
    compare: Data comparison utilities for dictionaries and lists
    convert: Data conversion utilities for various formats and types
    DictDot: Dot notation access for dictionaries
    files: File and folder operation utilities
    images: Image processing and manipulation utilities
    logging: Custom logging processors and utilities for domolibrary2
    read_creds_from_dotenv: Environment credential reading utilities
    upload_data: Data upload utilities (may require external dependencies)
    xkcd_password: Password generation utilities
    exceptions: Custom exception classes for error handling

Usage:
    >>> from utils import chunk_execution, convert, DictDot
    >>> from utils.exceptions import UtilityError

    >>> # Use async utilities
    >>> await chunk_execution.run_with_retry(my_function)

    >>> # Convert data formats
    >>> datetime_obj = convert.convert_string_to_datetime("2023-01-01")

    >>> # Use dot notation for dictionaries
    >>> data = DictDot.DictDot({"user": {"name": "John"}})
    >>> print(data.user.name)  # "John"

Version: 1.0.0
Author: Domo Utils Contributors
License: MIT
"""

from importlib import import_module
from typing import Any

from .exceptions import (
    ConcatDataframeError,
    CredentialsError,
    FileOperationError,
    ImageProcessingError,
    InvalidEmailError,
    UtilityError,
)

_LAZY_MODULES: dict[str, str] = {
    "DictDot": "DictDot",
    "chunk_execution": "chunk_execution",
    "compare": "compare",
    "convert": "convert",
    "enums": "enums",
    "files": "files",
    "images": "images",
    "logging": "logging",
    "read_creds_from_dotenv": "read_creds_from_dotenv",
    "xkcd_password": "xkcd_password",
}


def __getattr__(name: str) -> Any:
    """Lazily import utility submodules to avoid circular imports."""
    if name in _LAZY_MODULES:
        module = import_module(f"{__name__}.{_LAZY_MODULES[name]}")
        globals()[name] = module
        return module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Exception classes
    "UtilityError",
    "InvalidEmailError",
    "ConcatDataframeError",
    "FileOperationError",
    "ImageProcessingError",
    "CredentialsError",
    # Utility modules
    "chunk_execution",
    "compare",
    "convert",
    "DictDot",
    "enums",
    "files",
    "images",
    "lineage_utils",
    "logging",
    "read_creds_from_dotenv",
    "xkcd_password",
]
