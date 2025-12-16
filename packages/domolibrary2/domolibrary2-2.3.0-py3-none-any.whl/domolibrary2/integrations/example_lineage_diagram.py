"""Example: Generate Mermaid lineage diagrams for Domo entities.

This example demonstrates how to use the Mermaid integration to visualize
the lineage (dependency graph) of any Domo entity that supports lineage.

Supported Entity Types:
    - Cards (DomoCard)
    - Datasets (DomoDataset, including views)
    - Pages (DomoPage)
    - App Studios (DomoAppStudio)
    - Dataflows (DomoDataflow)
    - Publications (DomoPublication)

The script:
    1. Fetches a Domo entity by ID
    2. Retrieves its recursive lineage (all upstream dependencies)
    3. Generates a Mermaid flowchart diagram showing relationships
    4. Exports the diagram to a Markdown file

Usage:
    Basic usage (requires DOMO_INSTANCE and DOMO_ACCESS_TOKEN in environment):

    ```python
    from domolibrary2.auth import DomoTokenAuth
    from domolibrary2.classes.DomoPage import DomoPage
    from domolibrary2.integrations.example_lineage_diagram import generate_lineage_diagram

    auth = DomoTokenAuth(
        domo_instance="your-instance",
        domo_access_token="your-token"
    )

    # Generate diagram for a page
    await generate_lineage_diagram(
        entity_id="384424178",
        entity_type="page",
        auth=auth
    )
    ```

    Command-line usage:

    ```bash
    python -m domolibrary2.integrations.example_lineage_diagram page 384424178
    python -m domolibrary2.integrations.example_lineage_diagram card 1027750237 --output my_diagram.md
    ```

Example Output:
    The script generates a Mermaid diagram showing:
    - The root entity (e.g., a page)
    - Its dependencies (e.g., cards on the page)
    - Recursive dependencies (e.g., datasets used by cards)
    - All relationships between entities

    The diagram is exported as Markdown with embedded Mermaid syntax,
    which can be rendered in GitHub, Notion, or any Mermaid-compatible viewer.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from domolibrary2.auth import DomoAuth, DomoTokenAuth
from domolibrary2.base.exceptions import DomoError
from domolibrary2.classes.DomoAppStudio import DomoAppStudio
from domolibrary2.classes.DomoCard import DomoCard
from domolibrary2.classes.DomoDataset import DomoDataset
from domolibrary2.classes.DomoPage import DomoPage
from domolibrary2.integrations.mermaid import MermaidDiagram, MermaidRelationship

# Default export directory (can be overridden)
# Path calculation: from integrations/example_lineage_diagram.py to project root
EXPORT_DIR = Path(__file__).resolve().parents[3] / "EXPORTS"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _load_dotenv_from_repo_root() -> None:
    """Load environment variables from the project root .env if present."""
    repo_root = (
        Path(__file__).resolve().parents[3]
    )  # From integrations/ to project root
    env_file = repo_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()


async def _get_entity_by_type(entity_type: str, entity_id: str, auth: DomoAuth) -> Any:
    """Retrieve a Domo entity by type and ID.

    Args:
        entity_type: Type of entity ("card", "dataset", "page", "appstudio")
        entity_id: The entity ID
        auth: Authentication object

    Returns:
        The retrieved entity instance

    Raises:
        ValueError: If entity_type is not supported
    """
    entity_type_lower = entity_type.lower()

    if entity_type_lower == "card":
        return await DomoCard.get_by_id(card_id=entity_id, auth=auth, debug_api=False)
    elif entity_type_lower == "dataset":
        return await DomoDataset.get_by_id(
            dataset_id=entity_id, auth=auth, debug_api=False
        )
    elif entity_type_lower == "page":
        return await DomoPage.get_by_id(page_id=entity_id, auth=auth, debug_api=False)
    elif entity_type_lower in ("appstudio", "app", "data_app"):
        return await DomoAppStudio.get_by_id(
            app_id=entity_id, auth=auth, debug_api=False
        )
    else:
        raise ValueError(
            f"Unsupported entity type: {entity_type}. "
            f"Supported types: card, dataset, page, appstudio"
        )


async def generate_lineage_diagram(
    entity_id: str,
    entity_type: str,
    auth: DomoAuth,
    output_file: str | Path | None = None,
    export_dir: Path | None = None,
    is_recursive: bool = True,
    max_depth: int | None = None,
) -> str:
    """Generate a Mermaid lineage diagram for any Domo entity.

    This function demonstrates the core workflow for using the Mermaid integration:
    1. Fetch the entity
    2. Create a Mermaid diagram from the entity
    3. Retrieve recursive lineage (all upstream dependencies)
    4. Add lineage links to the diagram (relationships are created automatically)
    5. Export to Markdown

    Args:
        entity_id: The ID of the entity to generate a diagram for
        entity_type: Type of entity ("card", "dataset", "page", "appstudio")
        auth: Authentication object
        output_file: Optional output file path. If None, uses export_dir/<entity_id>.md
        export_dir: Directory for exports (default: EXPORTS/ in project root)
        is_recursive: Whether to fetch recursive lineage (default: True)
        max_depth: Maximum depth for recursive lineage (None = unlimited)

    Returns:
        The generated markdown content with the diagram

    Example:
        ```python
        from domolibrary2.auth import DomoTokenAuth
        from domolibrary2.integrations.example_lineage_diagram import generate_lineage_diagram

        auth = DomoTokenAuth(domo_instance="...", domo_access_token="...")
        markdown = await generate_lineage_diagram(
            entity_id="384424178",
            entity_type="page",
            auth=auth
        )
        ```
    """
    print(f"Fetching {entity_type} {entity_id}...")
    entity = await _get_entity_by_type(
        entity_type=entity_type, entity_id=entity_id, auth=auth
    )

    entity_name = (
        getattr(entity, "title", None)
        or getattr(entity, "name", None)
        or getattr(entity, "display_name", None)
        or entity_id
    )
    print(f"Entity: {entity_name} (ID: {entity.id})")

    # Create Mermaid diagram from the entity
    print("Creating Mermaid diagram...")
    diagram = MermaidDiagram.from_entity(entity=entity, direction="TD")

    # For pages, we need to track immediate cards to create "contains" relationships
    immediate_card_ids = set()
    if entity_type.lower() == "page":
        immediate_lineage = await entity.Lineage.get(is_recursive=False)
        immediate_card_ids = {
            (item.entity.id, item.entity.entity_type)
            for item in immediate_lineage
            if item.entity and item.entity.entity_type == "CARD"
        }

    # Fetch recursive lineage (builds complete tree with relationships)
    print(f"Fetching {'recursive' if is_recursive else 'immediate'} lineage...")
    lineage = await entity.Lineage.get(
        is_recursive=is_recursive,
        max_depth=max_depth,
    )
    print(f"Processing {len(lineage)} lineage items...")

    # Get the root node (the entity itself)
    root_node = diagram.nodes[0]  # Root node added by from_entity

    # Add all lineage links to the diagram
    # The add_lineage_link method automatically:
    # - Creates nodes for each lineage link and its dependencies
    # - Creates relationships from source nodes to their dependencies
    for item in lineage:
        diagram.add_lineage_link(item)

        # For pages, create explicit "contains" relationships from page to its immediate cards
        # This represents the compositional relationship (page contains cards)
        if (
            entity_type.lower() == "page"
            and item.entity
            and (item.entity.id, item.entity.entity_type) in immediate_card_ids
        ):
            card_node = diagram._find_node(item.entity.id, item.entity.entity_type)
            if card_node and root_node != card_node:
                # Check if relationship already exists
                existing_rel = any(
                    rel.from_node == root_node and rel.to_node == card_node
                    for rel in diagram.relationships
                )
                if not existing_rel:
                    rel = MermaidRelationship(
                        from_node=root_node,
                        to_node=card_node,
                        type="contains",  # Page contains cards
                    )
                    diagram.add_relationship(rel)

    # Determine output file path
    if output_file:
        export_path = Path(output_file)
    else:
        # Default: export to export_dir/<entity_id>.md
        if export_dir is None:
            export_dir = EXPORT_DIR
        entity_id_safe = str(entity.id).replace("-", "_")
        export_path = export_dir / f"{entity_id_safe}.md"

    # Export to file
    markdown_content = diagram.export_to_markdown(export_file=export_path)
    print(f"\n✓ Diagram written to: {export_path}")
    print(f"  Total nodes: {len(diagram.nodes)}")
    print(f"  Total relationships: {len(diagram.relationships)}")

    return markdown_content


async def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Generate a Mermaid lineage diagram for a Domo entity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "entity_type",
        choices=["card", "dataset", "page", "appstudio"],
        help="Type of entity to generate diagram for",
    )
    parser.add_argument(
        "entity_id",
        help="ID of the entity to generate diagram for",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path (default: EXPORTS/<entity_id>.md)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only fetch immediate lineage (not recursive)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum depth for recursive lineage (default: unlimited)",
    )

    args = parser.parse_args()

    # Load environment variables
    _load_dotenv_from_repo_root()

    # Get authentication credentials
    domo_instance = os.getenv("DOMO_INSTANCE")
    domo_access_token = os.getenv("DOMO_ACCESS_TOKEN")

    if not domo_instance or not domo_access_token:
        print(
            "ERROR: DOMO_INSTANCE and DOMO_ACCESS_TOKEN must be set in environment",
            file=sys.stderr,
        )
        print("Create a .env file in the project root with:", file=sys.stderr)
        print("  DOMO_INSTANCE=your-instance", file=sys.stderr)
        print("  DOMO_ACCESS_TOKEN=your-token", file=sys.stderr)
        sys.exit(1)

    auth = DomoTokenAuth(
        domo_instance=domo_instance,
        domo_access_token=domo_access_token,
    )

    # Validate authentication
    whoami = await auth.who_am_i()
    print(f"Authenticated as: {whoami.response}")
    assert auth.is_valid_token, "Expected auth token to be valid after who_am_i()"

    try:
        await generate_lineage_diagram(
            entity_id=args.entity_id,
            entity_type=args.entity_type,
            auth=auth,
            output_file=args.output,
            is_recursive=not args.no_recursive,
            max_depth=args.max_depth,
        )
    except (ValueError, KeyError, AttributeError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except (DomoError, httpx.HTTPError, OSError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
