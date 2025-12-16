"""Utility functions for authentication validation."""

from ..base.exceptions import AuthError
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)


@log_call(
    level_name="auth",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
def test_is_full_auth(
    auth,
    function_name=None,
    debug_num_stacks_to_drop=1,
):
    """Test that the provided object is a DomoFullAuth instance.

    This validation function ensures that the authentication object is of the
    correct type for functions that specifically require full authentication.

    Args:
        auth: The authentication object to validate
        function_name (str | None): Override function name for error reporting
        debug_num_stacks_to_drop (int): Number of stack frames to drop for debugging

    Raises:
        InvalidAuthTypeError: If auth is not a DomoFullAuth instance
    """
    function_name = function_name or "test_is_full_auth"

    if auth.__class__.__name__ != "DomoFullAuth":
        raise AuthError(
            message=f"{function_name} requires DomoFullAuth authentication."
        )


@log_call(
    level_name="auth",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
def test_is_jupyter_auth(
    auth,
    required_auth_type_ls: list | None = None,
):
    """Test that the provided object is a valid Jupyter authentication instance.

    This validation function ensures that the authentication object is one of the
    accepted Jupyter authentication types for functions that specifically require
    Jupyter authentication capabilities.

    Args:
        auth: The authentication object to validate
        required_auth_type_ls (list | None): list of acceptable auth types.
            Defaults to [DomoJupyterFullAuth, DomoJupyterTokenAuth]

    Raises:
        InvalidAuthTypeError: If auth is not one of the required Jupyter auth types
    """
    from .jupyter import DomoJupyterFullAuth, DomoJupyterTokenAuth

    if required_auth_type_ls is None:
        required_auth_type_ls = [DomoJupyterFullAuth, DomoJupyterTokenAuth]

    if auth.__class__.__name__ not in [
        auth_type.__name__ for auth_type in required_auth_type_ls
    ]:
        raise AuthError(
            message=f"test_is_jupyter_auth requires {[auth_type.__name__ for auth_type in required_auth_type_ls]} authentication, got {auth.__class__.__name__}",
            function_name="test_is_jupyter_auth",
            domo_instance=auth.domo_instance,
        )
