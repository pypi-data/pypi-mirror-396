"""Domo authentication classes for various authentication methods.

This module provides authentication classes for different Domo authentication methods:
- DomoAuth: Base authentication class
- DomoFullAuth: Username/password authentication
- DomoTokenAuth: Access token authentication
- DomoDeveloperAuth: OAuth2 client credentials authentication
- DomoJupyterAuth: Base Jupyter authentication
- DomoJupyterFullAuth: Jupyter with username/password
- DomoJupyterTokenAuth: Jupyter with access token

Example:
    >>> from domolibrary2.auth import DomoTokenAuth
    >>> auth = DomoTokenAuth(
    ...     domo_instance="mycompany",
    ...     domo_access_token="your-token"
    ... )
"""

__all__ = [
    "DomoAuth",
    "DomoFullAuth",
    "DomoTokenAuth",
    "DomoDeveloperAuth",
    "DomoJupyterAuth",
    "DomoJupyterFullAuth",
    "DomoJupyterTokenAuth",
    "test_is_full_auth",
    "test_is_jupyter_auth",
]

from .base import DomoAuth
from .developer import DomoDeveloperAuth
from .full import DomoFullAuth
from .jupyter import DomoJupyterAuth, DomoJupyterFullAuth, DomoJupyterTokenAuth
from .token import DomoTokenAuth
from .utils import test_is_full_auth, test_is_jupyter_auth
