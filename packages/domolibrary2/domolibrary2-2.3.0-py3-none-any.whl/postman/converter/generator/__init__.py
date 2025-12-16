"""Code generation for route functions.

This module provides code generation for:
- Full route functions (for new endpoints)
- Wrapper functions (for matched endpoints)
- Code templates and formatting
"""

from .formatter import format_code
from .route_generator import generate_route_function
from .templates import RouteTemplate, WrapperTemplate
from .wrapper_generator import generate_wrapper_function

__all__ = [
    "generate_route_function",
    "generate_wrapper_function",
    "RouteTemplate",
    "WrapperTemplate",
    "format_code",
]
