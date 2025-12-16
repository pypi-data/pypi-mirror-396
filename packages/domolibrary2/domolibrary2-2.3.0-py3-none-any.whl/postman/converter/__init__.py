"""Postman to Python converter with multi-agent support.

This package provides tools to convert Postman collections into Python API client functions.
Includes both traditional converter and new multi-agent framework using pydantic-ai.
"""

# Core converter imports
from .core import PostmanCollectionConverter, PostmanRequestConverter
from .models import PostmanCollection, PostmanFolder, PostmanRequest

__all__ = [
    # Traditional converter (always available)
    "PostmanCollection",
    "PostmanFolder",
    "PostmanRequest",
    "PostmanRequestConverter",
    "PostmanCollectionConverter",
]

# Optional multi-agent framework (requires pydantic-ai and langgraph)
try:
    from .agent_graph import (
        conversion_graph,
        convert_postman_collection,
        convert_postman_collection_sync,
        create_postman_conversion_graph,
    )

    __all__.extend(
        [
            "convert_postman_collection",
            "convert_postman_collection_sync",
            "conversion_graph",
            "create_postman_conversion_graph",
        ]
    )

    _MULTI_AGENT_AVAILABLE = True

except ImportError:
    _MULTI_AGENT_AVAILABLE = False

    # Multi-agent features not available
    def _not_available(*args, **kwargs):
        raise ImportError(
            "Multi-agent framework requires: pip install pydantic-ai langgraph"
        )

    convert_postman_collection = _not_available
    convert_postman_collection_sync = _not_available
    conversion_graph = None
    create_postman_conversion_graph = _not_available
