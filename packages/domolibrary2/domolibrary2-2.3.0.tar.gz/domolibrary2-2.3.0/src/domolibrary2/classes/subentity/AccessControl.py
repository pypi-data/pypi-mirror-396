"""
Unified Access Control System for Domo Objects

This module provides a comprehensive access control framework that intelligently maps
users and groups to various Domo objects with different permission levels.

The system handles access control for:
- DomoAccounts (credential sharing)
- DomoCards (content sharing)
- DomoDatasets (data access)
- DomoGroups (membership management)
- PDP Policies (data row-level security)
- DomoPages (dashboard sharing)

Key Concepts:
1. **Access Levels**: Standardized permission levels (OWNER, ADMIN, EDITOR, VIEWER, etc.)
2. **Access Types**: Different types of access (DIRECT, INHERITED, POLICY_BASED)
3. **Entity Relationships**: Unified representation of user/group relationships to objects
4. **Access Inheritance**: How permissions cascade through groups and hierarchies
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ...auth import DomoAuth
from ...base.base import DomoEnum
from ...base.entities import DomoEntity
from ...base.exceptions import ClassError
from ...client.context import RouteContext


class AccessLevel(DomoEnum):
    """Standardized access levels across all Domo objects."""

    OWNER = "OWNER"  # Full control including deletion
    ADMIN = "ADMIN"  # Administrative access, can manage permissions
    EDITOR = "EDITOR"  # Can modify content but not permissions
    CONTRIBUTOR = "CONTRIBUTOR"  # Can add content but not modify existing
    VIEWER = "VIEWER"  # Read-only access
    NONE = "NONE"  # No access

    default = NONE


class EntityType(DomoEnum):
    """Types of entities that can have access."""

    USER = "USER"
    GROUP = "GROUP"
    ROLE = "ROLE"

    default = USER


@dataclass
class AccessGrant:
    """Represents a single access grant to an entity."""

    entity_id: str
    entity_type: EntityType
    access_level: AccessLevel
    granted_by: str | None = None  # ID of who granted access
    granted_date: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None

    # Optional: track if this came from group membership resolution
    source_group_id: str | None = None  # Group ID if resolved from group

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessSummary:
    """Summary of all access grants for a specific entity."""

    entity_id: str
    entity_type: EntityType
    effective_access_level: AccessLevel  # Highest level from all grants
    access_grants: list[AccessGrant] = field(default_factory=list)

    @property
    def direct_access_level(self) -> AccessLevel:
        """Get the highest direct access level (not from group resolution)."""
        direct_grants = [g for g in self.access_grants if g.source_group_id is None]
        if not direct_grants:
            return AccessLevel.NONE

        # Return highest access level (assuming enum order represents hierarchy)
        access_levels = [g.access_level for g in direct_grants]
        return max(access_levels, key=lambda x: list(AccessLevel).index(x))

    @property
    def group_access_level(self) -> AccessLevel:
        """Get the highest access level from group membership."""
        group_grants = [g for g in self.access_grants if g.source_group_id is not None]
        if not group_grants:
            return AccessLevel.NONE

        access_levels = [g.access_level for g in group_grants]
        return max(access_levels, key=lambda x: list(AccessLevel).index(x))


class DomoAccessController(ABC):
    """Abstract base class for object-specific access controllers."""

    def __init__(self, auth: DomoAuth, parent_object: DomoEntity):
        self.auth = auth
        self.parent_object = parent_object
        self.parent_id = parent_object.id

        # Cache for access data
        self._access_cache: dict[str, AccessSummary] = {}
        self._cache_valid = False

    @abstractmethod
    async def get_direct_access_grants(self) -> list[AccessGrant]:
        """Get all direct access grants for the parent object."""
        pass

    @abstractmethod
    async def grant_access(
        self,
        entity_id: str,
        entity_type: EntityType,
        access_level: AccessLevel,
        **kwargs,
    ) -> bool:
        """Grant access to an entity."""
        pass

    @abstractmethod
    async def revoke_access(
        self, entity_id: str, entity_type: EntityType, **kwargs
    ) -> bool:
        """Revoke access from an entity."""
        pass

    async def get_inherited_access_grants(self) -> list[AccessGrant]:
        """Get inherited access grants (through group memberships)."""
        # This would query group memberships and calculate inherited permissions
        # Implementation depends on group hierarchy and membership resolution
        inherited_grants = []

        # Get all direct grants for groups
        direct_grants = await self.get_direct_access_grants()
        group_grants = [g for g in direct_grants if g.entity_type == EntityType.GROUP]

        # For each group, get its members and create inherited grants
        for group_grant in group_grants:
            group_members = await self._get_group_members(group_grant.entity_id)

            for member in group_members:
                inherited_grant = AccessGrant(
                    entity_id=member.id,
                    entity_type=(
                        EntityType.USER
                        if hasattr(member, "email")
                        else EntityType.GROUP
                    ),
                    access_level=group_grant.access_level,
                    source_group_id=group_grant.entity_id,
                )
                inherited_grants.append(inherited_grant)

        return inherited_grants

    async def get_all_access_grants(
        self, include_inherited: bool = True
    ) -> list[AccessGrant]:
        """Get all access grants (direct and optionally inherited)."""
        grants = await self.get_direct_access_grants()

        if include_inherited:
            inherited_grants = await self.get_inherited_access_grants()
            grants.extend(inherited_grants)

        return grants

    async def get_access_summary(self, entity_id: str) -> AccessSummary:
        """Get comprehensive access summary for a specific entity."""
        if not self._cache_valid or entity_id not in self._access_cache:
            await self._refresh_access_cache()

        return self._access_cache.get(
            entity_id,
            AccessSummary(
                entity_id=entity_id,
                entity_type=EntityType.USER,  # Default, should be determined
                effective_access_level=AccessLevel.NONE,
            ),
        )

    async def get_all_access_summaries(self) -> dict[str, AccessSummary]:
        """Get access summaries for all entities with access."""
        if not self._cache_valid:
            await self._refresh_access_cache()

        return self._access_cache.copy()

    async def _refresh_access_cache(self):
        """Refresh the internal access cache."""
        all_grants = await self.get_all_access_grants()

        # Group grants by entity
        entity_grants: dict[str, list[AccessGrant]] = {}
        for grant in all_grants:
            if grant.entity_id not in entity_grants:
                entity_grants[grant.entity_id] = []
            entity_grants[grant.entity_id].append(grant)

        # Create access summaries
        self._access_cache = {}
        for entity_id, grants in entity_grants.items():
            # Calculate effective access level (highest level from all grants)
            access_levels = [g.access_level for g in grants]
            effective_level = max(
                access_levels, key=lambda x: list(AccessLevel).index(x)
            )

            # Determine entity type from grants
            entity_type = grants[0].entity_type if grants else EntityType.USER

            summary = AccessSummary(
                entity_id=entity_id,
                entity_type=entity_type,
                effective_access_level=effective_level,
                access_grants=grants,
            )
            self._access_cache[entity_id] = summary

        self._cache_valid = True

    async def _get_group_members(self, group_id: str) -> list[Any]:
        """Get members of a group. Override in subclasses for specific implementations."""
        # This would be implemented to get actual group members
        # For now, return empty list
        return []

    def invalidate_cache(self):
        """Invalidate the access cache to force refresh on next access."""
        self._cache_valid = False


class DomoObjectAccessManager:
    """Main access manager that provides unified access control across all Domo objects."""

    def __init__(self, auth: DomoAuth):
        self.auth = auth
        self._controllers: dict[str, DomoAccessController] = {}

    def register_controller(self, object_type: str, controller_class: type):
        """Register an access controller for a specific object type."""
        self._controllers[object_type] = controller_class

    def get_controller(self, domo_object: DomoEntity) -> DomoAccessController | None:
        """Get the appropriate access controller for a Domo object."""
        object_type = type(domo_object).__name__

        if object_type in self._controllers:
            return self._controllers[object_type](self.auth, domo_object)

        return None

    async def get_user_access_across_objects(
        self, user_id: str, object_types: list[str] | None = None
    ) -> dict[str, dict[str, AccessSummary]]:
        """Get a user's access across all objects of specified types."""
        # This would query all objects of specified types and check user access
        # Implementation would depend on available APIs and object discovery methods
        pass

    async def get_object_access_summary(
        self, domo_object: DomoEntity, include_inherited: bool = True
    ) -> dict[str, AccessSummary]:
        """Get complete access summary for a Domo object."""
        controller = self.get_controller(domo_object)
        if not controller:
            raise ClassError(
                message=f"No access controller found for object type: {type(domo_object).__name__}",
                cls_instance=self,
            )

        return await controller.get_all_access_summaries()


# Concrete implementations for specific object types


class DomoAccountAccessController(DomoAccessController):
    """Access controller for DomoAccount objects."""

    async def get_direct_access_grants(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[AccessGrant]:
        """Get direct access grants for the account."""
        from ...routes import account as account_routes

        base_context = self.parent_object._build_route_context(
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.get_account_accesslist(
            auth=self.auth, account_id=self.parent_id, context=context
        )

        grants = []
        for item in res.response:
            grant = AccessGrant(
                entity_id=item["id"],
                entity_type=(
                    EntityType.USER if item["type"] == "USER" else EntityType.GROUP
                ),
                access_level=self._map_account_access_level(item["accessLevel"]),
            )
            grants.append(grant)

        return grants

    async def grant_access(
        self,
        entity_id: str,
        entity_type: EntityType,
        access_level: AccessLevel,
        **kwargs,
    ) -> bool:
        """Grant account access to an entity."""
        # Implementation would use account sharing routes
        pass

    async def revoke_access(
        self, entity_id: str, entity_type: EntityType, **kwargs
    ) -> bool:
        """Revoke account access from an entity."""
        # Implementation would use account unsharing routes
        pass

    def _map_account_access_level(self, domo_access_level: str) -> AccessLevel:
        """Map Domo account access levels to standardized access levels."""
        mapping = {
            "OWNER": AccessLevel.OWNER,
            "ADMIN": AccessLevel.ADMIN,
            "EDIT": AccessLevel.EDITOR,
            "VIEW": AccessLevel.VIEWER,
        }
        return mapping.get(domo_access_level, AccessLevel.NONE)


class DomoGroupAccessController(DomoAccessController):
    """Access controller for DomoGroup objects (membership management)."""

    async def get_direct_access_grants(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[AccessGrant]:
        """Get direct membership grants for the group."""
        from ...routes import group as group_routes

        base_context = self.parent_object._build_route_context(
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        # Get owners
        owners_res = await group_routes.get_group_owners(
            auth=self.auth, group_id=self.parent_id, context=context
        )

        # Get members
        members_res = await group_routes.get_group_membership(
            auth=self.auth, group_id=self.parent_id, context=context
        )

        grants = []

        # Process owners
        for owner in owners_res.response:
            grant = AccessGrant(
                entity_id=owner.get("userId") or owner.get("id"),
                entity_type=(
                    EntityType.USER
                    if owner.get("type", "USER") == "USER"
                    else EntityType.GROUP
                ),
                access_level=AccessLevel.OWNER,
            )
            grants.append(grant)

        # Process members
        for member in members_res.response:
            grant = AccessGrant(
                entity_id=member.get("userId") or member.get("id"),
                entity_type=(
                    EntityType.USER
                    if member.get("type", "USER") == "USER"
                    else EntityType.GROUP
                ),
                access_level=AccessLevel.VIEWER,  # Regular members
            )
            grants.append(grant)

        return grants

    async def grant_access(
        self,
        entity_id: str,
        entity_type: EntityType,
        access_level: AccessLevel,
        **kwargs,
    ) -> bool:
        """Add entity to group with specified access level."""
        # Implementation would use group membership routes
        pass

    async def revoke_access(
        self, entity_id: str, entity_type: EntityType, **kwargs
    ) -> bool:
        """Remove entity from group."""
        # Implementation would use group membership routes
        pass


__all__ = [
    "AccessLevel",
    "EntityType",
    "AccessGrant",
    "AccessSummary",
    "DomoAccessController",
    "DomoObjectAccessManager",
    "DomoAccountAccessController",
    "DomoGroupAccessController",
]
