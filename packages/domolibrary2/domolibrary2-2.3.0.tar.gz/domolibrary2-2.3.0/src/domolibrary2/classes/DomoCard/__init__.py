"""
DomoCard Package

This package provides comprehensive card management functionality for Domo instances,
including card operations, dataset associations, federated cards, and published cards.

Classes:
    DomoCard_Default: Core card operations and management
    FederatedDomoCard: Federated card functionality
    DomoPublishCard: Published card operations
    DomoCard: Smart factory class that returns appropriate card type
    CardDatasets: Manager for datasets associated with a card

Exceptions:
    Card_DownloadSourceCodeError: Raised when card source code download fails
"""

# Import all classes and functionality from the package modules
from .card_default import (
    Card_DownloadSourceCodeError,
    CardDatasets,
    DomoCard_Default,
)
from .core import (
    DomoCard,
    DomoPublishCard,
    FederatedDomoCard,
)

__all__ = [
    # Main card classes
    "DomoCard",
    "DomoCard_Default",
    "FederatedDomoCard",
    "DomoPublishCard",
    # Dataset management
    "CardDatasets",
    # Exceptions
    "Card_DownloadSourceCodeError",
]
