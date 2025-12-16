"""Lineage handler for Dataset entities."""

from __future__ import annotations

__all__ = ["DomoLineage_Dataset"]

from dataclasses import dataclass
from typing import Any

import httpx

from ....client.context import RouteContext
from ....routes import datacenter as datacenter_routes
from ....utils import chunk_execution as dmce
from .base import DomoLineage, register_lineage
from .link import DomoLineage_Link, _get_lineage_link_class


@register_lineage(
    "DomoDataset",
    "DomoDataset_Default",
    "FederatedDomoDataset",
    "DomoPublishDataset",
    "DomoDatasetView",
)
@dataclass
class DomoLineage_Dataset(DomoLineage):
    """Lineage handler for dataset entities.

    The parent is the dataset entity this lineage is based off of (not a dependency).
    For dataset views, this fetches the parent dataset. For raw datasets, this
    fetches upstream dependencies (if any).
    """

    @staticmethod
    def _is_federated(obj: dict[str, Any]) -> bool:
        """Heuristic: decide if a dataset JSON represents a federated (proxy) dataset.

        Args:
            obj: Dataset metadata dictionary

        Returns:
            True if the dataset is federated, False otherwise
        """
        dpt = obj.get("dataProviderType", "").upper()
        disp = obj.get("displayType", "").upper()

        has_hint = any(
            [
                bool(obj.get("federation")),
                bool(obj.get("federationData")),
                bool(obj.get("federatedDatasetId")),
                bool(obj.get("publisherDomain")),
                obj.get("isFederated") is True,
            ]
        )

        has_federate = any(["FEDERAT" in dpt, "FEDERAT" in disp])
        return has_hint or has_federate

    @property
    def is_federated(self) -> bool:
        """Check if the parent dataset is federated.

        Returns:
            True if parent dataset is federated, False otherwise
        """
        if not self.parent:
            return False
        return self._is_federated(self.parent.raw)

    async def _get_entity_lineage(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
        max_depth: int | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoLineage_Link]:
        """Get the dataset's immediate upstream dependencies.

        The parent is the dataset entity this lineage is based off of (not a dependency).
        For dataset views, this returns the parent dataset. For raw datasets,
        this returns upstream dependencies (typically empty).
        """
        # Filter context_kwargs to only include valid _build_route_context parameters
        valid_context_keys = {
            "session",
            "debug_api",
            "log_level",
            "debug_num_stacks_to_drop",
            "use_cache",
            "invalidate_cache",
            "cache_config",
            "is_verify",
            "dry_run",
            "is_follow_redirects",
        }
        filtered_kwargs = {
            k: v for k, v in context_kwargs.items() if k in valid_context_keys
        }

        base_context = self.parent._build_route_context(
            session=session,
            debug_api=debug_api,
            **filtered_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        # Always traverse upstream when called from get()
        res = await datacenter_routes.get_lineage_upstream(
            auth=self.parent.auth,
            entity_type=self.parent_type,
            entity_id=self.parent.id,
            max_depth=max_depth,
            traverse_up=True,  # Always upstream
            traverse_down=False,
            context=context,
        )

        if return_raw:
            return res

        async def _get_entity_from_dict(obj):
            link_cls = _get_lineage_link_class(obj["type"])
            # First get the entity, then create the link with from_dict
            entity = await link_cls.get_entity(entity_id=obj["id"], auth=self.auth)
            return link_cls.from_dict(obj=obj, entity=entity)

        dx_classes = await dmce.gather_with_concurrency(
            *[
                _get_entity_from_dict(obj)
                for _, obj in res.response.items()
                if str(obj["id"]) != str(self.parent.id)
            ],
            n=10,
        )

        # Return new list instead of mutating self.lineage
        return list(dx_classes)

    def get_parent_dataset(self) -> Any | None:
        """Get the parent dataset entity from lineage for dataset views.

        For dataset views, the parent dataset is included in the lineage as a DATA_SOURCE.
        This method extracts it from the lineage. For non-view datasets, returns None.

        Returns:
            The parent dataset entity instance, or None if not found or not a view

        Example:
            >>> lineage = await dataset_view.Lineage.get(is_recursive=False)
            >>> parent = dataset_view.Lineage.get_parent_dataset()
            >>> if parent:
            ...     print(f"Parent dataset: {parent.name}")
        """
        # Only applicable for dataset views
        if not (hasattr(self.parent, "is_view") and self.parent.is_view):
            return None

        # The parent dataset should be the DATA_SOURCE in the lineage
        # (views typically have one parent dataset)
        for item in self.lineage:
            if item.type == "DATA_SOURCE" and hasattr(item, "entity") and item.entity:
                return item.entity

        return None
