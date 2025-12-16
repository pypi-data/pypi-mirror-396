"""Compatibility import for legacy modules/tests expecting domolibrary2.client.auth.

Authentication helpers now live in ``domolibrary2.auth`` (and are imported
relatively here), but some downstream code still references the old
``domolibrary2.client.auth`` module.  This shim re-exports the canonical
classes so those imports keep working while callers migrate.
"""

from __future__ import annotations

from ..auth import (
    DomoAuth,
    DomoDeveloperAuth,
    DomoFullAuth,
    DomoJupyterAuth,
    DomoJupyterFullAuth,
    DomoJupyterTokenAuth,
    DomoTokenAuth,
    test_is_full_auth,
    test_is_jupyter_auth,
)

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
