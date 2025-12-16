"""Validation and sanitization utilities."""

from __future__ import annotations

import re
from pathlib import Path

from ..exceptions import ValidationError


def validate_collection_path(path: str | Path) -> Path:
    """Validate and normalize collection path.

    Args:
        path: Path to Postman collection

    Returns:
        Normalized Path object

    Raises:
        ValidationError: If path is invalid
    """
    path = Path(path)
    if not path.exists():
        raise ValidationError(f"Collection file does not exist: {path}")
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {path}")
    if not path.suffix == ".json":
        raise ValidationError(f"Collection file must be JSON: {path}")
    return path


def validate_routes_dir(path: str | Path) -> Path:
    """Validate and normalize routes directory path.

    Args:
        path: Path to routes directory

    Returns:
        Normalized Path object

    Raises:
        ValidationError: If path is invalid
    """
    path = Path(path)
    if not path.exists():
        raise ValidationError(f"Routes directory does not exist: {path}")
    if not path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")
    return path


def sanitize_function_name(name: str) -> str:
    """Sanitize function name to valid Python identifier.

    Args:
        name: Function name to sanitize

    Returns:
        Sanitized function name
    """
    # Remove invalid characters
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Remove leading numbers
    name = re.sub(r"^[0-9]+", "", name)
    # Ensure it starts with letter or underscore
    if not name or name[0].isdigit():
        name = "_" + name
    return name


def validate_url(url: str) -> str:
    """Validate and normalize URL.

    Args:
        url: URL to validate

    Returns:
        Normalized URL

    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    # Basic URL validation
    if not (
        url.startswith("http://") or url.startswith("https://") or url.startswith("/")
    ):
        # Allow Postman variables
        if not url.startswith("{{"):
            raise ValidationError(f"Invalid URL format: {url}")
    return url


def validate_http_method(method: str) -> str:
    """Validate HTTP method.

    Args:
        method: HTTP method to validate

    Returns:
        Uppercase HTTP method

    Raises:
        ValidationError: If method is invalid
    """
    valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
    method_upper = method.upper()
    if method_upper not in valid_methods:
        raise ValidationError(
            f"Invalid HTTP method: {method}. Must be one of {valid_methods}"
        )
    return method_upper
