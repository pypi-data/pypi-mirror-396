"""Wrapper function generation.

This module generates wrapper functions for Postman endpoints that
match existing route functions.
"""

from __future__ import annotations

from ...utils import to_snake_case
from ..deterministic.matcher import RouteMatch
from .templates import WrapperTemplate


def generate_wrapper_function(
    match: RouteMatch,
    postman_folder: str = "",
) -> dict[str, str]:
    """Generate wrapper function for a matched route.

    Args:
        match: RouteMatch with match information
        postman_folder: Postman folder path

    Returns:
        Dictionary with "name" and "code" keys
    """
    # Generate wrapper function name
    wrapper_name = _generate_wrapper_name(
        match.postman_request_name,
        match.existing_route_name or "",
    )

    # Generate wrapper code
    code = WrapperTemplate.generate(
        wrapper_name=wrapper_name,
        existing_route_module=match.existing_route_module or "",
        existing_route_name=match.existing_route_name or "",
        postman_name=match.postman_request_name,
        postman_folder=postman_folder,
    )

    return {
        "name": wrapper_name,
        "code": code,
    }


def _generate_wrapper_name(postman_name: str, existing_name: str) -> str:
    """Generate wrapper function name.

    Args:
        postman_name: Postman request name
        existing_name: Existing route function name

    Returns:
        Wrapper function name
    """
    # Convert Postman name to snake_case
    base_name = to_snake_case(postman_name)

    # If it's similar to existing name, add _postman suffix
    if existing_name and base_name == existing_name:
        return f"{base_name}_postman"

    return base_name
