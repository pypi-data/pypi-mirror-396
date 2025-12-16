"""Route function generation.

This module generates full route functions for new Postman endpoints
that don't match existing routes.
"""

from __future__ import annotations

from ...utils import to_snake_case
from ..deterministic.parser import ParsedPostmanRequest
from .templates import RouteTemplate


def generate_route_function(
    request: ParsedPostmanRequest,
    docstring: str | None = None,
) -> dict[str, str]:
    """Generate route function for a Postman request.

    Args:
        request: ParsedPostmanRequest with request information
        docstring: Optional custom docstring

    Returns:
        Dictionary with "name" and "code" keys
    """
    # Generate function name
    function_name = to_snake_case(request.name)

    # Build parameter list
    params = []
    for var in request.path_variables:
        params.append(f"{var}: str")
    for param in request.query_params:
        # Skip common params that are handled by context
        if param.lower() not in ["limit", "offset", "page"]:
            params.append(f"{param}: str | None = None")

    # Generate docstring if not provided
    if not docstring:
        docstring = f"""{request.name}

    {request.method} {request.url_pattern}
    """

    # Generate code
    code = RouteTemplate.generate(
        function_name=function_name,
        url=request.url_pattern,
        method=request.method,
        params=params,
        docstring=docstring,
    )

    return {
        "name": function_name,
        "code": code,
    }
