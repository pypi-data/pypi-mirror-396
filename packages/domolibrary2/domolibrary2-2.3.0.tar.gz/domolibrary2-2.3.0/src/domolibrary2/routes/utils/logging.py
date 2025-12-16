"""Route-level logging shims.

This module bridges legacy imports like ``from .utils.logging import ...``
that existed before the logging helpers were promoted to ``domolibrary2.utils``.
It simply re-exports the canonical implementations so older modules keep
working without touching every import site.
"""

from ...utils.logging import (  # noqa: F401 (re-exported names)
    ColoredLogger,
    DomoEntityExtractor,
    DomoEntityObjectProcessor,
    DomoEntityProcessor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    NoOpEntityExtractor,
    ResponseGetDataProcessor,
    get_colored_logger,
    log_call,
    set_domolibrary_logger,
)

__all__ = [
    "ResponseGetDataProcessor",
    "DomoEntityProcessor",
    "DomoEntityObjectProcessor",
    "DomoEntityExtractor",
    "DomoEntityResultProcessor",
    "NoOpEntityExtractor",
    "ColoredLogger",
    "get_colored_logger",
    "set_domolibrary_logger",
    "log_call",
    "LogDecoratorConfig",
]
