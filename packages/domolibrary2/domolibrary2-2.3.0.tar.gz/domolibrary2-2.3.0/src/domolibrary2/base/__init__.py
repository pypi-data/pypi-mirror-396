"""
Domo entity system.

This package provides foundational classes for all Domo entities with support
for authentication, relationships, lineage tracking, and entity management.

Modules:
- base: Foundational classes and enhanced enums
- entities: Core Domo entity classes and managers
- relationships: Relationship system for entity interactions

The design provides a consistent interface across all Domo entity types
while supporting advanced features like lineage tracking and relationships.
"""

# Import base classes and enums
from .base import DomoBase, DomoEnum, DomoEnumMixin

# Import entities from existing entities.py module
from .entities import (
    DomoEntity,
    DomoEntity_w_Lineage,
    DomoManager,
    DomoPublishEntity,
    DomoSubEntity,
)

# Import federated entities
from .entities_federated import DomoFederatedEntity

# Import relationship system
from .relationships import (
    DomoRelationship,
    DomoRelationshipController,
)

__all__ = [
    # Base classes and enums
    "DomoEnum",
    "DomoEnumMixin",
    "DomoBase",
    # Core entities
    "DomoEntity",
    "DomoEntity_w_Lineage",
    "DomoManager",
    "DomoPublishEntity",
    "DomoSubEntity",
    # Federated entities
    "DomoFederatedEntity",
    # Relationships
    "DomoRelationship",
    "DomoRelationshipController",
]
