from __future__ import annotations

__all__ = [
    "DomoLineage_Link",
    "DomoLineageLink_Dataflow",
    "DomoLineageLink_Publication",
    "DomoLineageLink_Subscription",
    "DomoLineageLink_Card",
    "DomoLineageLink_Dataset",
]

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth


def _map_entity_type(entity_type: str) -> str:
    """Map entity type strings to lineage type strings.

    Args:
        entity_type: The entity type string (e.g., "DATASET")

    Returns:
        The mapped lineage type string, or the original if no mapping exists
    """
    type_mapping = {
        "DATASET": "DATA_SOURCE",
    }
    return type_mapping.get(entity_type, entity_type)


@dataclass
class DomoLineage_Link(ABC):
    """Represents a link in the dependency lineage graph.

    **Terminology:**
    Uses dependency graph terminology:

    - **dependencies**: Upstream dependencies (what this entity depends on)
      Example: A card's dependencies are the datasets it uses for data
      Example: A view's dependencies are the datasets it depends on

    - **dependents**: Downstream dependents (what depends on this entity)
      Example: A dataset's dependents are the cards/pages/views that use it

    This matches standard dependency graph terminology and the Domo API structure.
    Note: This is different from composition (e.g., a page "contains" cards).

    The datacenter lineage payload frequently references entities only by ID/type; we
    therefore construct placeholder links with ``entity=None`` and materialize the real
    entity later via :meth:`get_entity`.  The ``_type`` cache allows those placeholder
    links to behave consistently (hashing, comparisons, rendering) until their backing
    entity is fetched.
    """

    auth: DomoAuth = field(repr=False)
    id: str
    entity: Any = field(repr=False)  # DomoDataset, DomoDataflow, DomoPublication
    _type: str | None = field(
        default=None, repr=False
    )  # Cached type for when entity is None

    dependencies: list[DomoLineage_Link] = field(
        default_factory=list,
        metadata={"description": "Upstream dependencies (what this entity depends on)"},
    )
    dependents: list[DomoLineage_Link] = field(
        default_factory=list,
        metadata={"description": "Downstream dependents (what depends on this entity)"},
    )

    @property
    def type(self) -> str:
        """Get the lineage type, derived from entity if available, otherwise from cached _type."""
        if self.entity:
            entity_type = getattr(self.entity, "entity_type", None)
            if entity_type:
                return _map_entity_type(entity_type)

        # Fallback to cached type (for when entity is None during initialization)
        if self._type:
            return self._type

        raise ValueError(
            f"Cannot determine type: entity is None and _type is not set for link {self.id}"
        )

    def __eq__(self, other: object) -> bool:
        """Compare lineage links by ID and entity type, ignoring class name differences.

        This allows DomoCard and DomoPublishCard (or other entity variants)
        to be considered equal if they have the same ID and entity type, since they
        represent the same underlying entity.

        Uses entity.entity_type if available, otherwise falls back to self.type.
        """
        # Check if other is an instance of DomoLineage_Link
        if not isinstance(other, DomoLineage_Link):
            return False

        return self.id == other.id and self.type == other.type

    def __hash__(self) -> int:
        return hash((self.id, self.type))

    @staticmethod
    @abstractmethod
    async def get_entity(entity_id, auth):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    def _create_lineage_links_from_dicts(
        cls,
        link_dicts: list[dict[str, Any]],
        entity: Any,  # DomoEntity (DomoCard, DomoDataset, DomoPublication, etc.)
    ) -> list[DomoLineage_Link]:
        """
        Create a list of DomoLineage_Link instances from a list of dictionary representations.

        Args:
            link_dicts: List of dictionaries containing link information (id, type)
            entity: The parent entity that these links relate to

        Returns:
            List of DomoLineage_Link instances
        """
        return [
            _get_lineage_link_class(link_dict["type"])(
                auth=entity.auth,
                id=link_dict["id"],
                entity=entity,
                _type=link_dict["type"],
                dependencies=[],
                dependents=[],
            )
            for link_dict in link_dicts
        ]

    @classmethod
    def from_dict(
        cls,
        obj: dict[str, Any],
        entity: Any,  # DomoEntity (DomoCard, DomoDataset, DomoPublication, etc.)
    ) -> DomoLineage_Link:
        """
        Create a DomoLineage_Link instance from a JSON object.
        """
        raw_dependents: list[dict[str, Any]] = cls._filter_dependents_dicts(
            obj.get("children", []), entity=entity
        )
        dependents = cls._create_lineage_links_from_dicts(raw_dependents, entity=entity)

        raw_dependencies: list[dict[str, Any]] = cls._filter_dependencies_dicts(
            obj.get("parents", []), entity=entity
        )
        dependencies = cls._create_lineage_links_from_dicts(
            raw_dependencies, entity=entity
        )

        return cls(
            id=obj["id"],
            auth=entity.auth,
            entity=entity,
            _type=None,  # Type will be derived from entity via property
            dependents=dependents,
            dependencies=dependencies,
        )

    @classmethod
    def _filter_dependents_dicts(
        cls,
        dependents: list[dict[str, Any]],
        *,
        entity: (
            Any | None
        ) = None,  # DomoEntity (DomoCard, DomoDataset, DomoPublication, etc.)
    ) -> list[dict[str, Any]]:
        """Hook for subclasses to filter raw dependent payloads before conversion.

        Called by :meth:`from_dict` for each link as it materializes its dependents.
        Override this when a specific lineage link should drop or rewrite certain
        child entries coming back from the datacenter API. The base implementation
        performs no filtering.
        """
        return dependents

    @classmethod
    def _filter_dependencies_dicts(
        cls,
        dependencies: list[dict[str, Any]],
        *,
        entity: (
            Any | None
        ) = None,  # DomoEntity (DomoCard, DomoDataset, DomoPublication, etc.)
    ) -> list[dict[str, Any]]:
        """Hook for subclasses to filter raw dependency payloads before conversion.

        Invoked by :meth:`from_dict` before upstream items are converted into
        :class:`DomoLineage_Link` instances. Override to prune or adjust entries
        reported by the API for this link. The base implementation is a no-op.
        """
        return dependencies


# ============================================================================
# Registry and Decorator for Lineage Links
# ============================================================================

_LINEAGE_LINK_REGISTRY: dict[str, type[DomoLineage_Link]] = {}


def register_lineage_link(link_type: str):
    """Decorator to register a DomoLineage_Link subclass by datacenter type string."""

    def decorator(cls: type[DomoLineage_Link]) -> type[DomoLineage_Link]:
        _LINEAGE_LINK_REGISTRY[link_type] = cls
        return cls

    return decorator


def _get_lineage_link_class(link_type: str) -> type[DomoLineage_Link]:
    cls = _LINEAGE_LINK_REGISTRY.get(link_type)
    if cls is None:
        raise ValueError(
            f"No lineage link registered for type '{link_type}'. "
            f"Known types: {sorted(_LINEAGE_LINK_REGISTRY.keys())}"
        )
    return cls


@register_lineage_link("DATAFLOW")
@dataclass
class DomoLineageLink_Dataflow(DomoLineage_Link):
    @staticmethod
    async def get_entity(
        entity_id, auth, session: httpx.AsyncClient = None, debug_api: bool = False
    ):
        from ..DomoDataflow import core as dmdf

        return await dmdf.DomoDataflow.get_by_id(
            dataflow_id=entity_id, auth=auth, session=session, debug_api=debug_api
        )

    def __eq__(self, other):
        if not isinstance(other, DomoLineageLink_Dataflow):
            return False
        return self.id == other.id and self.type == other.type


@register_lineage_link("PUBLICATION")
@dataclass
class DomoLineageLink_Publication(DomoLineage_Link):
    @staticmethod
    async def get_entity(
        entity_id, auth, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        """
        from ..DomoEverywhere.core import DomoPublication

        return await DomoPublication.get_by_id(
            publication_id=entity_id, auth=auth, session=session, debug_api=debug_api
        )


@register_lineage_link("SUBSCRIPTION")
@dataclass
class DomoLineageLink_Subscription(DomoLineage_Link):
    @staticmethod
    async def get_entity(
        entity_id, auth, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        from ..DomoEverywhere.core import DomoSubscription

        return await DomoSubscription.get_by_id(
            subscription_id=entity_id,
            auth=auth,
            session=session,
            debug_api=debug_api,
        )


@register_lineage_link("CARD")
@dataclass
class DomoLineageLink_Card(DomoLineage_Link):
    @staticmethod
    async def get_entity(
        entity_id, auth, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        """
        from .. import DomoCard as dmcd

        return await dmcd.DomoCard.get_by_id(
            card_id=entity_id, auth=auth, session=session, debug_api=debug_api
        )


@register_lineage_link("DATA_SOURCE")
@dataclass
class DomoLineageLink_Dataset(DomoLineage_Link):
    @staticmethod
    async def get_entity(
        entity_id, auth, debug_api: bool = False, session: httpx.AsyncClient = None
    ):
        """
        Get the entity associated with this lineage link.
        This method should be implemented by subclasses to return the appropriate entity.
        Uses DomoDataset factory to automatically detect views, federated datasets, etc.
        """
        from ..DomoDataset.core import DomoDataset

        return await DomoDataset.get_by_id(
            dataset_id=entity_id, auth=auth, session=session, debug_api=debug_api
        )
