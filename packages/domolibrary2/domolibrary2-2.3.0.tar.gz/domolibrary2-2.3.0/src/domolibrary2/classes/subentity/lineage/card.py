"""Lineage handler for Card entities."""

from __future__ import annotations

__all__ = ["DomoLineage_Card"]

from dataclasses import dataclass
from typing import Any

from .base import DomoLineage, register_lineage
from .link import DomoLineage_Link


@register_lineage(
    "DomoCard", "DomoCard_Default", "FederatedDomoCard", "DomoPublishCard"
)
@dataclass
class DomoLineage_Card(DomoLineage):
    """Lineage handler for card entities."""

    def _filter_lineage(
        self, lineage: list[DomoLineage_Link]
    ) -> list[DomoLineage_Link]:
        """Filter card lineage to only include direct datasources.

        A card's lineage should only contain its direct datasource (dataset or dataset_view),
        not the parent dataset of a view. The parent dataset belongs to the view's lineage, not the card's.

        Args:
            lineage: The lineage list to filter

        Returns:
            Filtered lineage list containing only direct datasources
        """
        # Get direct datasource IDs from card metadata
        direct_datasource_ids = set()
        parent_raw = getattr(self.parent, "raw", None)
        if parent_raw:
            datasources = parent_raw.get("datasources", [])
            direct_datasource_ids = {
                str(ds.get("dataSourceId"))
                for ds in datasources
                if ds.get("dataSourceId")
            }

        if not direct_datasource_ids:
            return lineage

        return [
            item
            for item in lineage
            if item.type == "DATA_SOURCE" and str(item.id) in direct_datasource_ids
        ]

    def validate_datasources(self) -> dict[str, Any]:
        """Validate that this card has at most one datasource.

        CustomApp/EnterpriseApp cards (identified by having a datastore_id) are allowed
        to have multiple datasources. Regular cards should have at most one.

        Returns:
            Dictionary with validation results:
            - valid: bool - True if card has valid datasource count
            - datasource_count: int - Number of datasources
            - is_custom_app: bool - True if card is part of CustomApp/EnterpriseApp
            - violation: dict | None - Violation details if invalid, None otherwise
        """
        # Count DATA_SOURCE items in lineage
        datasource_count = sum(1 for item in self.lineage if item.type == "DATA_SOURCE")

        # Check if card is part of CustomApp/EnterpriseApp
        # Cards with datastore_id are CustomApp/EnterpriseApp cards
        is_custom_app = bool(getattr(self.parent, "datastore_id", None))

        # CustomApp/EnterpriseApp cards can have multiple datasources
        # Regular cards should have at most one
        max_allowed = float("inf") if is_custom_app else 1
        is_valid = datasource_count <= max_allowed

        result = {
            "valid": is_valid,
            "datasource_count": datasource_count,
            "is_custom_app": is_custom_app,
            "violation": None,
        }

        if not is_valid:
            # Use entity_name property if available
            if hasattr(self.parent, "entity_name"):
                card_name = self.parent.entity_name
            else:
                card_name = (
                    getattr(self.parent, "title", None)
                    or getattr(self.parent, "name", None)
                    or str(self.parent.id)
                )

            result["violation"] = {
                "card_id": self.parent.id,
                "card_name": card_name,
                "datasource_count": datasource_count,
                "max_allowed": max_allowed,
                "datasources": [
                    {
                        "id": item.id,
                        "name": (
                            item.entity.entity_name
                            if item.entity and hasattr(item.entity, "entity_name")
                            else (
                                getattr(item.entity, "name", item.id)
                                if item.entity
                                else item.id
                            )
                        ),
                    }
                    for item in self.lineage
                    if item.type == "DATA_SOURCE"
                ],
            }

        return result
