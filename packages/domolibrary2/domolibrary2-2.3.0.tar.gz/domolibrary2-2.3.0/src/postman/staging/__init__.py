"""Staging area management.

This module provides utilities for managing the staging area where
generated route functions are stored before integration.
"""

from .manager import StagingManager
from .metadata import StagingMetadata

__all__ = [
    "StagingManager",
    "StagingMetadata",
]
