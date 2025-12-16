"""Utility functions for working with enums."""

from __future__ import annotations

from enum import Enum
from typing import TypeVar

__all__ = ["normalize_enum", "normalize_optional_parts"]

T = TypeVar("T")


def normalize_enum[T](value: Enum | T) -> str | T:
    """Convert enum to string value, or pass through non-enum values.

    This utility function normalizes enum values to their string representation
    while preserving non-enum values unchanged. This is useful when working with
    parameters that can accept either enum instances or plain string values.

    Args:
        value: Either an Enum instance or any other value

    Returns:
        The enum's value (string) if value is an Enum, otherwise the original value

    Example:
        >>> from enum import Enum
        >>> class Status(Enum):
        ...     ACTIVE = "active"
        ...     INACTIVE = "inactive"
        >>> normalize_enum(Status.ACTIVE)
        'active'
        >>> normalize_enum("already_a_string")
        'already_a_string'
    """
    return value.value if isinstance(value, Enum) else value


def normalize_optional_parts(
    value: list[Enum] | str,
) -> str:
    """Normalize optional_parts parameter to comma-separated string.

    Converts a list of enum values to a comma-separated string for API consumption.

    **Note:** Enum values are preferred over strings for type safety and better IDE support.
    String values are accepted for backward compatibility only.

    Args:
        value: Either a list of Enum instances (preferred) or a comma-separated string
            (for backward compatibility)

    Returns:
        Comma-separated string of enum values

    Example:
        >>> from enum import Enum
        >>> class Parts(Enum):
        ...     METADATA = "metadata"
        ...     CERTIFICATION = "certification"
        >>> # Preferred: use enum list
        >>> normalize_optional_parts([Parts.METADATA, Parts.CERTIFICATION])
        'metadata,certification'
        >>> # Backward compatibility: string still works
        >>> normalize_optional_parts("metadata,certification")
        'metadata,certification'
    """
    if isinstance(value, str):
        return value
    return ",".join([normalize_enum(member) for member in value])
