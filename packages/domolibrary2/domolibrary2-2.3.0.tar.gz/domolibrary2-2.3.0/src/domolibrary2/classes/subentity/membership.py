from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass

from ...base import exceptions as dmde
from ...base.entities import DomoSubEntity
from ...base.relationships import (
    DomoRelationship,
    DomoRelationshipController,
    ShareAccount,
)

__all__ = [
    "UpdateMembership",
    "MembershipRelationship",
    "DomoMembership",
]


class UpdateMembership(dmde.ClassError):
    def __init__(self, cls_instance, member_name=None, entity_id=None):
        super().__init__(
            entity_id=entity_id,
            cls_instance=cls_instance,
            message=f"unable to alter membership {member_name if member_name else ''}",
        )


@dataclass
class MembershipRelationship(DomoRelationship):
    """Represents a membership relationship between entities."""

    @property
    def entity_type(self) -> str:
        """Return the entity type (USER or GROUP)."""
        if hasattr(self.entity, "entity_type"):
            return self.entity.entity_type.upper()
        return self.entity.__class__.__name__.replace("Domo", "").upper()

    def to_dict(self):
        """Convert relationship to dictionary for API requests."""
        entity_type = self.entity_type

        if entity_type == "USER":
            return {"type": "USER", "id": str(self.entity.id)}

        if entity_type == "GROUP":
            return {"type": "GROUP", "id": int(self.entity.id)}

        raise UpdateMembership(cls_instance=self, entity_id=self.entity.id)

    async def update(self):
        """Update relationship - not implemented for membership."""
        raise NotImplementedError("Update not implemented for membership relationships")


@dataclass
class DomoMembership(DomoRelationshipController, DomoSubEntity):
    """
    Base membership management using the relationship system.

    This class provides a minimal interface for managing membership relationships.
    Most implementation is in DomoGroup_Membership for group-specific logic.
    """

    @property
    def owners(self) -> list[MembershipRelationship]:
        """Get all owner relationships from relationships list."""
        return [
            rel
            for rel in self.relationships
            if rel.relationship_type == ShareAccount("OWNER")
        ]

    @property
    def members(self) -> list[MembershipRelationship]:
        """Get all member relationships from relationships list."""
        return [
            rel
            for rel in self.relationships
            if rel.relationship_type == ShareAccount("MEMBER")
        ]

    @abstractmethod
    async def get(self) -> list[MembershipRelationship]:
        """Get all membership relationships for this object."""
        raise NotImplementedError(
            "DomoMembership.get must be implemented by subclasses"
        )

    @abstractmethod
    async def update(self):
        """Update membership relationships."""
        raise NotImplementedError(
            "DomoMembership.update must be implemented by subclasses"
        )
