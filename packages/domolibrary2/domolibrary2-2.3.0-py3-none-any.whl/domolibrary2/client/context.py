"""Route context for API request configuration.

This module provides the RouteContext dataclass for consolidating
debug and session parameters across route functions.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from dc_logger import LogLevel


@dataclass
class RouteContext:
    """Context object for route function execution.

    Consolidates debugging, session, and cache control parameters that are
    commonly passed to route functions and get_data calls.

    Attributes:
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        log_level: Optional log level for the request
        dry_run: If True, return request parameters without executing the API call
        is_follow_redirects: Follow HTTP redirects (default: True)
        use_cache: Enable HTTP response caching (default: True)
        invalidate_cache: Invalidate cache before this request (default: False)
        is_verify: SSL certificate verification (default: False)
        cache_config: Optional cache configuration dict
    """

    session: httpx.AsyncClient | None = None
    debug_num_stacks_to_drop: int = 1  # Explicit default
    parent_class: str | None = None
    log_level: LogLevel | str | None = None
    debug_api: bool = False  # Explicit default
    dry_run: bool = False  # Explicit default
    is_follow_redirects: bool = True  # Explicit default

    # Cache control (Phase 2)
    use_cache: bool = True  # Default enabled for optimization
    invalidate_cache: bool = False

    # Session configuration
    is_verify: bool = False
    cache_config: dict | None = None

    @classmethod
    def build_context(
        cls,
        context: RouteContext | None = None,
        **kwargs,
    ) -> RouteContext:
        """Build RouteContext from either existing context or individual parameters.

        This helper allows route functions to accept either a pre-built context
        or individual parameters, enabling clean signatures while maintaining
        backward compatibility.

        Args:
            context: Optional pre-built RouteContext
            **kwargs: Individual context parameters (session, debug_api, debug_num_stacks_to_drop,
                    parent_class, log_level, dry_run)

        Returns:
            RouteContext built from provided parameters

        Example:
            >>> # In a route function
            >>> def my_route(auth, *, context=None, **context_kwargs):
            ...     context = build_context(context, **context_kwargs)
            ...     res = await get_data(auth=auth, url=url, context=context)
        """
        context = context or RouteContext()

        # Update context attributes from kwargs if provided
        # For boolean values, allow False to be set explicitly

        for key, value in kwargs.items():
            if hasattr(context, key):
                if value is not None:
                    setattr(context, key, value)

        return context
