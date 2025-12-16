"""
Environment Credentials Reading Utilities

This module provides utilities for reading credentials and configuration
from environment files (.env) with proper error handling and validation.

Functions:
    read_creds_from_dotenv: Read credentials from .env file and return as DictDot object

Exception Classes:
    CredentialsError: Raised when credential reading fails

Example:
    >>> # Read all environment variables
    >>> creds = read_creds_from_dotenv(".env")
    >>> print(creds.DATABASE_URL)

    >>> # Read specific parameters
    >>> creds = read_creds_from_dotenv(".env", ["API_KEY", "SECRET_KEY"])
    >>> print(creds.API_KEY)

    >>> # Handle missing file gracefully
    >>> try:
    ...     creds = read_creds_from_dotenv("missing.env")
    ... except CredentialsError as e:
    ...     print(f"Error: {e}")
"""

__all__ = ["read_creds_from_dotenv"]

import os

# Optional dependency with fallback
from dotenv import load_dotenv

from . import DictDot as utils_dd
from .exceptions import CredentialsError


def read_creds_from_dotenv(
    env_path: str = ".env",
    params: list[str] | None = None,
) -> utils_dd.DictDot:
    """
    Read credentials from .env file and return as DictDot object for easy access.

    Loads environment variables from the specified .env file and returns them
    as a DictDot object for convenient dot notation access.

    Args:
        env_path (str): Path to the .env file (default: ".env")
        params (list[str], optional): list of specific parameters to extract.
                                    If None, extracts all environment variables.

    Returns:
        DictDot: Object containing environment variables accessible via dot notation

    Raises:
        ImportError: If python-dotenv package is not available
        CredentialsError: If .env file doesn't exist or cannot be read

    Example:
        >>> # Read all variables from .env file
        >>> creds = read_creds_from_dotenv()
        >>> print(creds.DATABASE_URL)
        >>> print(creds.API_KEY)

        >>> # Read specific variables only
        >>> creds = read_creds_from_dotenv(
        ...     env_path="config.env",
        ...     params=["DOMO_INSTANCE", "DOMO_TOKEN"]
        ... )
        >>> print(creds.DOMO_INSTANCE)
        >>> print(creds.DOMO_TOKEN)

        >>> # Handle missing variables gracefully
        >>> print(creds.MISSING_VAR)  # Returns None instead of error

    Note:
        - Requires python-dotenv package for .env file parsing
        - Missing environment variables return None when accessed
        - Environment variables are loaded into os.environ during execution
        - Supports standard .env file format with KEY=value pairs
    """

    # Check if file exists
    if not os.path.exists(env_path):
        raise CredentialsError(env_path, f"Environment file not found at: {env_path}")

    try:
        # Load environment variables from file
        load_dotenv(env_path)

        # Determine which parameters to extract
        if params is None:
            # Get all environment variables
            params = list(os.environ.keys())

        # Extract specified parameters
        params_res = {}
        for param in params:
            param_str = str(param)
            value = os.environ.get(param_str)
            params_res[param_str] = value

        return utils_dd.DictDot(params_res)

    except (OSError, ValueError) as e:
        raise CredentialsError(
            env_path, f"Failed to read or parse environment file: {str(e)}"
        )
