"""Utilities for working with Domo lineage data.

This module provides functions for:
- Generating Mermaid diagrams from lineage
- Visualizing lineage relationships
- Validating lineage data structure

Note: Assumes lineage.get() returns properly deduplicated and filtered data.
"""

from typing import Any

from ..integrations.mermaid import MermaidDiagram


def _extract_entity_name(item: Any) -> str:
    """Extract a display name from a lineage item.

    Args:
        item: Lineage link item

    Returns:
        Entity name, title, or ID as fallback
    """
    if hasattr(item, "entity") and item.entity:
        name = (
            getattr(item.entity, "name", None)
            or getattr(item.entity, "title", None)
            or getattr(item.entity, "display_name", None)
            or None
        )
        if name:
            return str(name)

    # Fallback to ID
    return item.id


# Convenience function for backwards compatibility
async def generate_mermaid_diagram(
    entity: Any,
    direction: str = "TD",
) -> MermaidDiagram:
    """Generate a Mermaid diagram from an entity's lineage.

    This is a convenience wrapper that creates a diagram and populates it with lineage.

    Args:
        entity: The entity (DomoPage, DomoDataset, etc.) to generate a diagram for
        direction: Diagram direction - "TD" (top-down), "LR" (left-right), etc.

    Returns:
        MermaidDiagram object populated with lineage

    Example:
        >>> diagram = await generate_mermaid_diagram(page)
        >>> print(diagram.to_string())
    """
    # Create diagram shell
    diagram = MermaidDiagram.from_entity(entity=entity, direction=direction)

    # Fetch and populate lineage (upstream, unlimited depth)
    lineage = await entity.Lineage.get(
        recursive=True,
        direction="upstream",
        max_depth=None,
    )
    for item in lineage:
        diagram.add_lineage_link(item)

    return diagram


def validate_card_datasources(lineage: list[Any]) -> dict[str, Any]:
    """Validate that each card has at most one datasource.

    Args:
        lineage: List of lineage link items

    Returns:
        Dictionary with validation results:
        - valid: bool - True if all cards have <= 1 datasource
        - violations: list - List of cards with multiple datasources
        - card_datasource_counts: dict - Mapping of card_id -> datasource_count
    """
    card_datasource_counts = {}
    violations = []

    for item in lineage:
        if item.type == "CARD":
            # Count DATA_SOURCE dependencies (datasets the card uses)
            datasource_count = 0
            if hasattr(item, "dependencies") and item.dependencies:
                datasource_count = sum(
                    1 for dep in item.dependencies if dep and dep.type == "DATA_SOURCE"
                )

            card_datasource_counts[item.id] = datasource_count

            if datasource_count > 1:
                card_name = _extract_entity_name(item)
                violations.append(
                    {
                        "card_id": item.id,
                        "card_name": card_name,
                        "datasource_count": datasource_count,
                        "datasources": [
                            {"id": dep.id, "name": _extract_entity_name(dep)}
                            for dep in item.dependencies
                            if dep and dep.type == "DATA_SOURCE"
                        ],
                    }
                )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "card_datasource_counts": card_datasource_counts,
    }


def print_lineage_summary(
    parent_entity: Any,
    lineage: list[Any],
) -> None:
    """Print a formatted summary of lineage data.

    Args:
        parent_entity: The parent entity
        lineage: List of lineage items (already deduplicated by lineage.get())
    """
    parent_name = (
        getattr(parent_entity, "title", None)
        or getattr(parent_entity, "name", None)
        or str(parent_entity.id)
    )
    parent_type = (
        getattr(parent_entity, "entity_type", None) or parent_entity.__class__.__name__
    )

    print(f"\n{'=' * 60}")
    print(f"Lineage Summary: {parent_name}")
    print(f"Type: {parent_type}, ID: {parent_entity.id}")
    print(f"{'=' * 60}")
    print(f"\nTotal lineage items: {len(lineage)}")

    if lineage:
        # Group by type
        by_type = {}
        for item in lineage:
            item_type = item.type
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)

        print("\nBy Type:")
        for item_type, items in sorted(by_type.items()):
            print(f"  {item_type}: {len(items)}")

        print("\nDetailed Items:")
        for idx, item in enumerate(lineage, 1):
            entity_name = _extract_entity_name(item)
            print(f"\n  {idx}. {item.type}: {item.id}")
            print(f"     Name: {entity_name}")
            if hasattr(item, "dependencies") and item.dependencies:
                print(f"     Dependencies: {len(item.dependencies)}")
            if hasattr(item, "dependents") and item.dependents:
                print(f"     Dependents: {len(item.dependents)}")
    else:
        print("No lineage items found.")

    print(f"\n{'=' * 60}\n")
