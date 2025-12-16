"""
Unified relationship system for Domo entities.

This module provides a comprehensive relationship modeling framework that unifies
all types of entity interactions within the Domo ecosystem. It standardizes how
entities relate to each other, whether through access control, membership,
sharing permissions, organizational hierarchies, or data lineage connections.

The relationship system enables:
- Consistent access control across all Domo objects (datasets, cards, pages, etc.)
- Unified membership management for groups, roles, and organizations
- Standardized sharing and permission models
- Hierarchical relationships and organizational structures
- Data lineage and dependency tracking
- Extensible relationship types for future needs

Key Design Principles:
- Entity-agnostic: Works with any Domo entity type
- Relationship-centric: Focus on connections rather than entity-specific logic
- Bidirectional awareness: Relationships are navigable in both directions
- Metadata support: Rich context and properties for each relationship
- Async-first: Built for scalable concurrent operations

Classes:
    DomoRelationship: Represents a relationship between two entities with metadata
    DomoRelationshipController: Manages and orchestrates relationship operations

Usage:
    # Create relationships between entities
    relationship = DomoRelationship(
        relationship_type=ShareAccount.VIEWER,
        parent_entity=dataset,
        entity=user,
        metadata={"granted_date": "2023-01-01"}
    )

    # Manage relationships through controller
    controller = DomoRelationshipController()
    await controller.add_relationship("user123", ShareAccount.VIEWER)
    relationships = await controller.get()
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .base import DomoBase, DomoEnumMixin


class ShareAccount(DomoEnumMixin, Enum):
    """Types of relationships between Domo entities."""

    # Access and Permission Relationships
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    PARTICIPANT = "participant"
    VIEWER = "viewer"

    # Membership Relationships
    MEMBER = "member"

    # Lineage Relationships
    PARENT = "parent"
    CHILD = "child"

    # Default fallback
    default = "UNKNOWN"


__all__ = [
    "ShareAccount",
    "DomoRelationship",
    "DomoRelationshipController",
]


@dataclass
class DomoRelationship(DomoBase):
    """Represents a relationship between two Domo entities.

    This unified relationship model can represent any type of connection
    between Domo entities including access control, membership, sharing,
    subscriptions, and organizational structures. Each relationship captures
    the nature of the connection and provides bidirectional navigation.

    The relationship model is designed to be:
    - Lightweight: Minimal required fields for efficiency
    - Extensible: Metadata dictionary for custom properties
    - Navigable: Easy traversal between related entities
    - Comparable: Built-in equality for deduplication

    Attributes:
        relationship_type (ShareAccount): Nature of the relationship (owner, member, viewer, etc.)
        parent_entity (DomoEntity): The entity that owns this relationship
        entity (DomoEntity | None): The related entity instance (optional, default None)
        metadata (dict[str, Any]): Additional properties and context for the relationship

    Examples:
        # User has viewer access to a dataset
        viewer_relationship = DomoRelationship(
            relationship_type=ShareAccount.VIEWER,
            parent_entity=dataset,
            entity=user
        )

        # Dataset is a child of another dataset (lineage)
        lineage_relationship = DomoRelationship(
            relationship_type=ShareAccount.PARENT,
            parent_entity=child_dataset,
            entity=parent_dataset,
            metadata={"lineage_type": "transformation", "created_date": "2023-01-01"}
        )

        # Group membership relationship
        member_relationship = DomoRelationship(
            relationship_type=ShareAccount.MEMBER,
            parent_entity=group,
            entity=user
        )

    Note:
        Relationships are considered equal if they have the same parent_entity.id,
        relationship_type, and entity.id. This enables efficient deduplication
        when working with large sets of relationships.
    """

    relationship_type: ShareAccount

    # Core relationship identifiers
    parent_entity: Any = field(repr=False)  # DomoEntity instance
    entity: Any = field(repr=False, default=None)  # DomoEntity instance

    def __eq__(self, other):
        if not isinstance(other, DomoRelationship):
            return False
        return (
            self.parent_entity.id == other.parent_entity.id
            and self.relationship_type == other.relationship_type
            and self.entity.id == other.entity.id
        )

    @property
    def parent_id(self):
        return self.parent_entity.id

    metadata: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert relationship to dictionary."""
        raise NotImplementedError("Subclasses must implement to_dict method.")

    @abstractmethod
    async def update(self):
        """Update relationship metadata or properties."""
        raise NotImplementedError("Subclasses must implement update method.")


@dataclass
class DomoRelationshipController(DomoBase):
    """Controller for managing Domo entity relationships.

    This class provides high-level operations for creating, managing, and
    querying relationships between Domo entities. It serves as the primary
    interface for relationship operations and acts as a centralized manager
    for all relationship-based interactions.

    The controller is designed to be:
    - Entity-agnostic: Works with any Domo entity type
    - Batch-aware: Efficient bulk operations for large relationship sets
    - Async-optimized: Concurrent operations for performance
    - Cache-friendly: Intelligent caching of frequently accessed relationships
    - Extensible: Easy to subclass for specialized relationship types
    """

    relationships: list[DomoRelationship] = field(default_factory=list)
