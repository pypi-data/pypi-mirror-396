"""
Unified Relationship System for Domo Objects

This module provides a comprehensive relationship framework that models
all types of connections between Domo entities including access control,
group membership, lineage tracking, and certification.

Key Concepts:
1. **Relationships**: Directional connections between entities (A → B)
2. **Relationship Types**: The nature of the connection (access, membership, lineage, etc.)
3. **Entity Types**: What kinds of objects can have relationships (users, groups, datasets, etc.)
4. **Relationship Controllers**: Manage specific types of relationships for objects

Examples of Relationships:
- User HAS_ACCESS_EDITOR → Card
- User IS_MEMBER_OF → Group
- Dataset IS_DERIVED_FROM → Dataset
- Card IS_CERTIFIED_BY → User
- Dataset IS_TAGGED_WITH → Tag
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ...auth import DomoAuth
from ...base.base import DomoEnum
from ...base.entities import DomoEntity
from ...client.context import RouteContext


class EntityType(DomoEnum):
    """Types of entities that can participate in relationships."""

    USER = "USER"
    GROUP = "GROUP"
    ROLE = "ROLE"
    DATASET = "DATASET"
    CARD = "CARD"
    PAGE = "PAGE"
    ACCOUNT = "ACCOUNT"
    TAG = "TAG"

    default = USER


class RelationshipType(DomoEnum):
    """Types of relationships between entities."""

    # Access relationships (Entity → Object)
    HAS_ACCESS_OWNER = "HAS_ACCESS_OWNER"  # Full control including deletion
    HAS_ACCESS_ADMIN = (
        "HAS_ACCESS_ADMIN"  # Administrative access, can manage permissions
    )
    HAS_ACCESS_EDITOR = "HAS_ACCESS_EDITOR"  # Can modify content but not permissions
    HAS_ACCESS_CONTRIBUTOR = (
        "HAS_ACCESS_CONTRIBUTOR"  # Can add content but not modify existing
    )
    HAS_ACCESS_VIEWER = "HAS_ACCESS_VIEWER"  # Read-only access

    # Group membership relationships (User/Group → Group)
    IS_OWNER_OF = "IS_OWNER_OF"  # Group owner
    IS_MEMBER_OF = "IS_MEMBER_OF"  # Group member
    IS_ADMIN_OF = "IS_ADMIN_OF"  # Group administrator

    # Lineage relationships (Dataset → Dataset, Card → Dataset, etc.)
    IS_DERIVED_FROM = "IS_DERIVED_FROM"  # Dataset created from another dataset
    IS_FEDERATED_FROM = "IS_FEDERATED_FROM"  # Federated dataset relationship
    IS_PUBLISHED_FROM = "IS_PUBLISHED_FROM"  # Published dataset relationship
    USES_DATA_FROM = "USES_DATA_FROM"  # Card uses data from dataset

    # Certification relationships (Object → User/Group)
    IS_CERTIFIED_BY = "IS_CERTIFIED_BY"  # Content certified by user

    # Tagging relationships (Object → Tag)
    IS_TAGGED_WITH = "IS_TAGGED_WITH"  # Object tagged with tag

    # Account relationships (User/Group → Account)
    HAS_ACCOUNT_ACCESS = "HAS_ACCOUNT_ACCESS"  # Access to credential account

    default = HAS_ACCESS_VIEWER


@dataclass
class Relationship:
    """Represents a directional relationship between two entities."""

    from_entity_id: str
    from_entity_type: EntityType
    to_entity_id: str
    to_entity_type: EntityType
    relationship_type: RelationshipType

    # Relationship metadata
    created_date: str | None = None
    created_by: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None

    # For resolved relationships (e.g., inherited through groups)
    source_relationship_id: str | None = (
        None  # ID of relationship this was derived from
    )

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_access_relationship(self) -> bool:
        """Check if this is an access-related relationship."""
        return self.relationship_type.value.startswith("HAS_ACCESS_")

    @property
    def is_membership_relationship(self) -> bool:
        """Check if this is a membership-related relationship."""
        return self.relationship_type in [
            RelationshipType.IS_OWNER_OF,
            RelationshipType.IS_MEMBER_OF,
            RelationshipType.IS_ADMIN_OF,
        ]

    @property
    def is_lineage_relationship(self) -> bool:
        """Check if this is a lineage-related relationship."""
        return self.relationship_type in [
            RelationshipType.IS_DERIVED_FROM,
            RelationshipType.IS_FEDERATED_FROM,
            RelationshipType.IS_PUBLISHED_FROM,
            RelationshipType.USES_DATA_FROM,
        ]


@dataclass
class RelationshipSummary:
    """Summary of relationships for a specific entity."""

    entity_id: str
    entity_type: EntityType
    relationships: list[Relationship] = field(default_factory=list)

    def get_relationships_by_type(
        self, relationship_type: RelationshipType
    ) -> list[Relationship]:
        """Get all relationships of a specific type."""
        return [
            r for r in self.relationships if r.relationship_type == relationship_type
        ]

    def get_access_relationships(self) -> list[Relationship]:
        """Get all access-related relationships."""
        return [r for r in self.relationships if r.is_access_relationship]

    def get_membership_relationships(self) -> list[Relationship]:
        """Get all membership-related relationships."""
        return [r for r in self.relationships if r.is_membership_relationship]

    def get_lineage_relationships(self) -> list[Relationship]:
        """Get all lineage-related relationships."""
        return [r for r in self.relationships if r.is_lineage_relationship]

    @property
    def effective_access_level(self) -> RelationshipType:
        """Get the highest access level from all access relationships."""
        access_rels = self.get_access_relationships()
        if not access_rels:
            return RelationshipType.default

        # Define access hierarchy (highest to lowest)
        access_hierarchy = [
            RelationshipType.HAS_ACCESS_OWNER,
            RelationshipType.HAS_ACCESS_ADMIN,
            RelationshipType.HAS_ACCESS_EDITOR,
            RelationshipType.HAS_ACCESS_CONTRIBUTOR,
            RelationshipType.HAS_ACCESS_VIEWER,
        ]

        for level in access_hierarchy:
            if any(r.relationship_type == level for r in access_rels):
                return level

        return RelationshipType.default


class DomoRelationshipController(ABC):
    """Abstract base class for managing relationships for specific object types."""

    def __init__(self, auth: DomoAuth, parent_object: DomoEntity):
        self.auth = auth
        self.parent_object = parent_object
        self.parent_id = parent_object.id

        # Cache for relationship data
        self._relationship_cache: dict[str, RelationshipSummary] = {}
        self._cache_valid = False

    @abstractmethod
    async def get_direct_relationships(self) -> list[Relationship]:
        """Get all direct relationships for the parent object."""
        pass

    @abstractmethod
    async def create_relationship(
        self,
        target_entity_id: str,
        target_entity_type: EntityType,
        relationship_type: RelationshipType,
        **kwargs,
    ) -> bool:
        """Create a new relationship."""
        pass

    @abstractmethod
    async def remove_relationship(
        self,
        target_entity_id: str,
        target_entity_type: EntityType,
        relationship_type: RelationshipType,
        **kwargs,
    ) -> bool:
        """Remove a relationship."""
        pass

    async def get_resolved_relationships(self) -> list[Relationship]:
        """Get resolved relationships (including those derived from group memberships)."""
        resolved_relationships = []
        direct_relationships = await self.get_direct_relationships()

        # Add direct relationships
        resolved_relationships.extend(direct_relationships)

        # Resolve group memberships for access relationships
        group_relationships = [
            r
            for r in direct_relationships
            if r.from_entity_type == EntityType.GROUP and r.is_access_relationship
        ]

        for group_rel in group_relationships:
            group_members = await self._get_group_members(group_rel.from_entity_id)

            for member in group_members:
                resolved_rel = Relationship(
                    from_entity_id=member.id,
                    from_entity_type=(
                        EntityType.USER
                        if hasattr(member, "email")
                        else EntityType.GROUP
                    ),
                    to_entity_id=group_rel.to_entity_id,
                    to_entity_type=group_rel.to_entity_type,
                    relationship_type=group_rel.relationship_type,
                    source_relationship_id=f"{group_rel.from_entity_id}_{group_rel.to_entity_id}",
                )
                resolved_relationships.append(resolved_rel)

        return resolved_relationships

    async def get_relationship_summary(self, entity_id: str) -> RelationshipSummary:
        """Get comprehensive relationship summary for a specific entity."""
        if not self._cache_valid or entity_id not in self._relationship_cache:
            await self._refresh_relationship_cache()

        return self._relationship_cache.get(
            entity_id,
            RelationshipSummary(
                entity_id=entity_id,
                entity_type=EntityType.USER,  # Default, should be determined properly
            ),
        )

    async def get_all_relationship_summaries(self) -> dict[str, RelationshipSummary]:
        """Get relationship summaries for all entities with relationships to this object."""
        if not self._cache_valid:
            await self._refresh_relationship_cache()

        return self._relationship_cache.copy()

    async def _refresh_relationship_cache(self):
        """Refresh the internal relationship cache."""
        all_relationships = await self.get_resolved_relationships()

        # Group relationships by from_entity
        entity_relationships: dict[str, list[Relationship]] = {}
        for rel in all_relationships:
            if rel.from_entity_id not in entity_relationships:
                entity_relationships[rel.from_entity_id] = []
            entity_relationships[rel.from_entity_id].append(rel)

        # Create relationship summaries
        self._relationship_cache = {}
        for entity_id, relationships in entity_relationships.items():
            # Determine entity type from relationships
            entity_type = (
                relationships[0].from_entity_type if relationships else EntityType.USER
            )

            summary = RelationshipSummary(
                entity_id=entity_id,
                entity_type=entity_type,
                relationships=relationships,
            )
            self._relationship_cache[entity_id] = summary

        self._cache_valid = True

    async def _get_group_members(self, group_id: str) -> list[Any]:
        """Get members of a group. Override in subclasses for specific implementations."""
        # This would be implemented to get actual group members
        return []

    def invalidate_cache(self):
        """Invalidate the relationship cache to force refresh on next access."""
        self._cache_valid = False


class DomoRelationshipManager:
    """Main relationship manager that provides unified relationship management across all Domo objects."""

    def __init__(self, auth: DomoAuth):
        self.auth = auth
        self._controllers: dict[str, type] = {}

    def register_controller(self, object_type: str, controller_class: type):
        """Register a relationship controller for a specific object type."""
        self._controllers[object_type] = controller_class

    def get_controller(
        self, domo_object: DomoEntity
    ) -> DomoRelationshipController | None:
        """Get the appropriate relationship controller for a Domo object."""
        object_type = type(domo_object).__name__

        if object_type in self._controllers:
            return self._controllers[object_type](self.auth, domo_object)

        return None

    async def get_entity_relationships(
        self,
        entity_id: str,
        entity_type: EntityType,
        relationship_types: list[RelationshipType] | None = None,
    ) -> list[Relationship]:
        """Get all relationships for an entity across all objects."""
        # This would query relationships across all object types
        # Implementation depends on available APIs and indexing
        pass


# Concrete implementations for specific object types


class DomoAccessRelationshipController(DomoRelationshipController):
    """Relationship controller for access/sharing relationships."""

    async def get_direct_relationships(self) -> list[Relationship]:
        """Get direct access relationships for the object."""
        # Implementation depends on the specific object type
        # This would be specialized in subclasses
        pass

    async def create_relationship(
        self,
        target_entity_id: str,
        target_entity_type: EntityType,
        relationship_type: RelationshipType,
        **kwargs,
    ) -> bool:
        """Create an access relationship."""
        # Implementation would use sharing routes
        pass

    async def remove_relationship(
        self,
        target_entity_id: str,
        target_entity_type: EntityType,
        relationship_type: RelationshipType,
        **kwargs,
    ) -> bool:
        """Remove an access relationship."""
        # Implementation would use unsharing routes
        pass


class DomoMembershipRelationshipController(DomoRelationshipController):
    """Relationship controller for group membership relationships."""

    async def get_direct_relationships(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[Relationship]:
        """Get direct membership relationships for the group."""
        from ...routes import group as group_routes

        base_context = self.parent_object._build_route_context(
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        # Get owners and members
        owners_res = await group_routes.get_group_owners(
            auth=self.auth, group_id=self.parent_id, context=context
        )

        members_res = await group_routes.get_group_membership(
            auth=self.auth, group_id=self.parent_id, context=context
        )

        relationships = []

        # Process owners
        for owner in owners_res.response:
            rel = Relationship(
                from_entity_id=owner.get("userId") or owner.get("id"),
                from_entity_type=(
                    EntityType.USER
                    if owner.get("type", "USER") == "USER"
                    else EntityType.GROUP
                ),
                to_entity_id=self.parent_id,
                to_entity_type=EntityType.GROUP,
                relationship_type=RelationshipType.IS_OWNER_OF,
            )
            relationships.append(rel)

        # Process members
        for member in members_res.response:
            rel = Relationship(
                from_entity_id=member.get("userId") or member.get("id"),
                from_entity_type=(
                    EntityType.USER
                    if member.get("type", "USER") == "USER"
                    else EntityType.GROUP
                ),
                to_entity_id=self.parent_id,
                to_entity_type=EntityType.GROUP,
                relationship_type=RelationshipType.IS_MEMBER_OF,
            )
            relationships.append(rel)

        return relationships

    async def create_relationship(
        self,
        target_entity_id: str,
        target_entity_type: EntityType,
        relationship_type: RelationshipType,
        **kwargs,
    ) -> bool:
        """Add entity to group with specified relationship."""
        # Implementation would use group membership routes
        pass

    async def remove_relationship(
        self,
        target_entity_id: str,
        target_entity_type: EntityType,
        relationship_type: RelationshipType,
        **kwargs,
    ) -> bool:
        """Remove entity from group."""
        # Implementation would use group membership routes
        pass


__all__ = [
    "EntityType",
    "RelationshipType",
    "Relationship",
    "RelationshipSummary",
    "DomoRelationshipController",
    "DomoRelationshipManager",
    "DomoAccessRelationshipController",
    "DomoMembershipRelationshipController",
]
