"""Legacy import compatibility layer.

DEPRECATED: This module maintains backward compatibility by re-exporting from new locations.
Import directly from postman.converter instead.
"""

import warnings

# Re-export from new locations
from ..core import PostmanCollectionConverter, PostmanRequestConverter
from ..models import PostmanCollection, PostmanFolder, PostmanRequest

warnings.warn(
    "Importing from postman.converter.legacy is deprecated. "
    "Use 'from postman.converter import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "PostmanCollection",
    "PostmanFolder",
    "PostmanRequest",
    "PostmanRequestConverter",
    "PostmanCollectionConverter",
]
