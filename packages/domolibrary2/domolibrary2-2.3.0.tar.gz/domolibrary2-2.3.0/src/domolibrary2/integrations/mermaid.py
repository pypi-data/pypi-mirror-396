"""Mermaid diagram integration for Domo lineage visualization.

This module provides classes and utilities for generating Mermaid diagrams
from Domo entity lineage data.

Classes:
    MermaidNode: Represents a node in a Mermaid diagram
    MermaidRelationship: Represents a relationship/edge between nodes
    MermaidDiagram: Complete Mermaid diagram with nodes and relationships

Quick Example:
    >>> diagram = await MermaidDiagram.from_entity(page)
    >>> print(diagram.to_string())
    >>> diagram.export_to_markdown("output.md")

For a complete working example, see:
    :mod:`domolibrary2.integrations.example_lineage_diagram`

This example demonstrates how to:
    - Fetch entities and their lineage
    - Generate Mermaid diagrams with relationships
    - Export diagrams to Markdown files
    - Handle different entity types (cards, datasets, pages, app studios)
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _extract_entity_name(entity: Any) -> str:  # DomoEntity
    """DEPRECATED: Extract a display name from a DomoEntity.

    .. deprecated::
        This function is deprecated. Use the `entity_name` property on entities
        instead: `entity.entity_name`.

    Args:
        entity: A DomoEntity instance

    Returns:
        Display name for the entity, or entity ID as fallback

    Example:
        >>> # Old way (deprecated):
        >>> name = _extract_entity_name(entity)
        >>> # New way:
        >>> name = entity.entity_name
    """
    import warnings

    warnings.warn(
        "_extract_entity_name() is deprecated. "
        "Use entity.entity_name instead. This function will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Use the entity_name property if available
    if hasattr(entity, "entity_name"):
        return entity.entity_name

    # Fallback to old logic for backwards compatibility
    return (
        getattr(entity, "name", None)
        or getattr(entity, "title", None)
        or getattr(entity, "display_name", None)
        or entity.id
    )


@dataclass
class MermaidNode:
    """Represents a node in a Mermaid diagram.

    Attributes:
        id: Unique identifier for the node
        name: Display name for the node
        type: Type of the node (e.g., PAGE, CARD, DATA_SOURCE)
        alias: Short alias for the node (e.g., "A", "B", "C") - auto-generated
    """

    id: str
    name: str
    type: str
    alias: str | None = None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MermaidNode):
            return False
        return self.id == other.id and self.type == other.type

    def __hash__(self) -> int:
        return hash((self.id, self.type))

    @property
    def mermaid_id(self) -> str:
        """Generate a Mermaid-safe node ID."""
        return f"{self.type}_{self.id}".replace("-", "_").replace(" ", "_")

    def to_string(self, use_alias: bool = False, indentation: int = 4) -> str:
        """Render the node as a Mermaid node definition.

        Args:
            use_alias: If True, use the alias instead of mermaid_id
            indentation: Number of spaces to indent
        """
        # Escape special characters for Mermaid
        safe_name = self.name.replace('"', "'").replace("\n", " ")
        node_id = self.alias if (use_alias and self.alias) else self.mermaid_id
        return f'{" " * indentation}{node_id}["{safe_name}<br/>{self.type}: {self.id}"]'

    @classmethod
    def from_domo_entity(cls, entity: Any) -> "MermaidNode":
        """Create a MermaidNode from a Domo entity (DomoPage, DomoDataset, etc.).

        Args:
            entity: A Domo entity object

        Returns:
            MermaidNode instance
        """
        # Use entity_name property if available, otherwise fall back to helper
        if hasattr(entity, "entity_name"):
            name = entity.entity_name
        else:
            name = _extract_entity_name(entity)  # Deprecated but still works
        return cls(id=entity.id, name=name, type=entity.entity_type)

    @classmethod
    def from_lineage_link(cls, lineage_link: Any) -> "MermaidNode":
        """Create a MermaidNode from a lineage link item.

        Args:
            lineage_link: A DomoLineage_Link object

        Returns:
            MermaidNode instance
        """
        # Handle case where entity might not be loaded yet
        if lineage_link.entity:
            # Use entity_name property if available, otherwise fall back to helper
            if hasattr(lineage_link.entity, "entity_name"):
                name = lineage_link.entity.entity_name
            else:
                name = _extract_entity_name(
                    lineage_link.entity
                )  # Deprecated but still works
            return cls(
                id=lineage_link.entity.id,
                name=name,
                type=lineage_link.entity.entity_type,
            )
        else:
            # Use link's ID and type when entity is not loaded
            return cls(
                id=lineage_link.id,
                name=lineage_link.id,  # Fallback to ID as name
                type=lineage_link.type,  # Uses _type if entity is None
            )


@dataclass
class MermaidRelationship:
    """Represents a relationship between two nodes in a Mermaid diagram.

    Attributes:
        from_node: The source node
        to_node: The target node
        type: Type of relationship (default: "dependency")
    """

    from_node: MermaidNode
    to_node: MermaidNode
    type: str = "dependency"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MermaidRelationship):
            return False
        return (
            self.from_node == other.from_node
            and self.to_node == other.to_node
            and self.type == other.type
        )

    def __hash__(self) -> int:
        return hash((self.from_node, self.to_node, self.type))

    def to_string(self, use_alias: bool = False, indentation: int = 4) -> str:
        """Render the relationship as a Mermaid arrow.

        Args:
            use_alias: If True, use aliases instead of mermaid_ids
            indentation: Number of spaces to indent
        """
        from_id = (
            self.from_node.alias
            if (use_alias and self.from_node.alias)
            else self.from_node.mermaid_id
        )
        to_id = (
            self.to_node.alias
            if (use_alias and self.to_node.alias)
            else self.to_node.mermaid_id
        )
        return f"{' ' * indentation}{from_id} --> {to_id}"


@dataclass
class MermaidDiagram:
    """Complete Mermaid diagram with nodes and relationships.

    This class is responsible for:
    - Managing nodes and relationships
    - Deduplicating nodes and relationships
    - Rendering diagrams as Mermaid syntax or Markdown
    - Exporting diagrams to files

    Attributes:
        nodes: List of nodes in the diagram
        relationships: List of relationships between nodes
        direction: Diagram direction (TD, LR, etc.)
        title: Optional title for the diagram
        entity_id: Optional ID of the root entity
        entity_type: Optional type of the root entity
    """

    nodes: list[MermaidNode] = field(default_factory=list)
    relationships: list[MermaidRelationship] = field(default_factory=list)
    direction: str = "TD"
    title: str | None = None
    entity_id: str | None = None
    entity_type: str | None = None
    use_aliases: bool = True

    def _find_node(self, node_id: str, node_type: str) -> MermaidNode | None:
        """Find a node by ID and type.

        Args:
            node_id: Node ID
            node_type: Node type

        Returns:
            MermaidNode if found, None otherwise
        """
        return next(
            (n for n in self.nodes if n.id == node_id and n.type == node_type), None
        )

    def _generate_alias(self, index: int) -> str:
        """Generate an alias for a node based on its index.

        Generates: A, B, C, ..., Z, AA, AB, AC, ...

        Args:
            index: Zero-based index of the node

        Returns:
            Alias string (e.g., "A", "B", "AA")
        """
        if index < 26:
            return chr(65 + index)  # A-Z
        else:
            # AA, AB, AC, ...
            first_letter = chr(65 + (index // 26) - 1)
            second_letter = chr(65 + (index % 26))
            return first_letter + second_letter

    def add_node(self, node: MermaidNode) -> None:
        """Add a node to the diagram if it doesn't already exist.

        Automatically assigns an alias if use_aliases is True and node doesn't have one.

        Args:
            node: The MermaidNode to add
        """
        if node not in self.nodes:
            # Assign alias if not already set and aliases are enabled
            if self.use_aliases and node.alias is None:
                node.alias = self._generate_alias(len(self.nodes))
            self.nodes.append(node)

    def add_relationship(self, relationship: MermaidRelationship) -> None:
        """Add a relationship to the diagram if it doesn't already exist.

        Uses the __eq__ method to check for duplicates.

        Args:
            relationship: The MermaidRelationship to add
        """
        if relationship not in self.relationships:
            self.relationships.append(relationship)

    def add_lineage_link(self, lineage_link: Any) -> None:
        """Add a lineage link's node and relationships to the diagram.

        This method:
        1. Creates and adds the node for the lineage link
        2. Looks up dependency and dependent nodes
        3. Creates and adds relationships

        Args:
            lineage_link: A DomoLineage_Link object
        """
        if not lineage_link:
            return

        # Create and add the node
        source_node = MermaidNode.from_lineage_link(lineage_link)
        self.add_node(source_node)

        # Skip relationship creation if entity is not set
        if not lineage_link.entity:
            return

        # Look up the node (might have been added earlier)
        source_node = self._find_node(
            lineage_link.entity.id, lineage_link.entity.entity_type
        )
        if not source_node:
            return

        # Create relationships for dependencies (items this depends on)
        # Only create relationships if source and dependency are different nodes
        if lineage_link.dependencies:
            for dependency in lineage_link.dependencies:
                if dependency and dependency.entity:
                    # Ensure the dependency node is in the diagram first
                    dep_source_node = MermaidNode.from_lineage_link(dependency)
                    self.add_node(dep_source_node)

                    # Look up the node (might have been added earlier or just now)
                    dep_node = self._find_node(
                        dependency.entity.id, dependency.entity.entity_type
                    )
                    # Only create relationship if nodes are different (avoid self-referential)
                    if dep_node and source_node != dep_node:
                        rel = MermaidRelationship(
                            from_node=source_node,
                            to_node=dep_node,
                            type="dependency",
                        )
                        self.add_relationship(rel)

    def add_lineage_items(
        self,
        lineage_items: Iterable[Any] | None,
        *,
        recursive: bool = False,
    ) -> None:
        """Add a collection of lineage items, optionally following dependencies."""

        if not lineage_items:
            return

        visited: set[tuple[str, str]] = set()

        def _add(link: Any) -> None:
            if not link or not getattr(link, "entity", None):
                return

            entity = link.entity
            key = (str(getattr(entity, "id", "")), getattr(entity, "entity_type", ""))
            if key in visited:
                return
            visited.add(key)

            self.add_lineage_link(link)

            if recursive and getattr(link, "dependencies", None):
                for dependency in link.dependencies:
                    _add(dependency)

        for root in lineage_items:
            _add(root)

    def add_entity_dependency(
        self,
        from_entity: Any,
        to_entity: Any,
        *,
        relationship_type: str = "dependency",
    ) -> None:
        """Add a relationship between two Domo entities."""

        if not from_entity or not to_entity:
            return

        from_node = MermaidNode.from_domo_entity(from_entity)
        to_node = MermaidNode.from_domo_entity(to_entity)
        self.add_node(from_node)
        self.add_node(to_node)

        from_ref = self._find_node(from_entity.id, from_entity.entity_type)
        to_ref = self._find_node(to_entity.id, to_entity.entity_type)

        if from_ref and to_ref and from_ref != to_ref:
            self.add_relationship(
                MermaidRelationship(
                    from_node=from_ref,
                    to_node=to_ref,
                    type=relationship_type,
                )
            )

    def to_string(self) -> str:
        """Render the complete Mermaid diagram."""
        lines = [f"flowchart {self.direction}"]

        # Add nodes (using aliases if enabled)
        for node in self.nodes:
            lines.append(node.to_string(use_alias=self.use_aliases))

        # Add relationships (using aliases if enabled)
        if self.relationships:
            lines.append("")  # Empty line before relationships
            for rel in self.relationships:
                lines.append(rel.to_string(use_alias=self.use_aliases))

        return "\n".join(lines)

    def export_to_markdown(
        self,
        export_file: str | None = None,
        footer_text: str | None = None,
    ) -> str:
        """Render the diagram as a Markdown document with optional file export.

        Args:
            export_file: Optional file path to write the markdown content to
            footer_text: Optional text to append to the bottom of the document

        Returns:
            The markdown content as a string

        Example:
            >>> diagram.export_to_markdown("lineage.md", footer_text="Run ID: 123")
            # Returns markdown string and writes to file
        """
        lines = []

        # Add title if provided
        if self.title:
            lines.append(f"# {self.title}")
            lines.append("")

        # Add entity metadata if provided
        if self.entity_id and self.entity_type:
            lines.append(f"**Entity Type**: {self.entity_type}")
            lines.append(f"**Entity ID**: {self.entity_id}")
            lines.append("")

        # Add diagram statistics
        lines.append(f"**Nodes**: {len(self.nodes)}")
        lines.append(f"**Relationships**: {len(self.relationships)}")
        lines.append("")

        # Add the Mermaid diagram
        lines.append("```mermaid")
        lines.append(self.to_string())
        lines.append("```")

        if footer_text:
            lines.append("")
            lines.append(footer_text.strip())

        markdown_content = "\n".join(lines)

        # Export to file if requested
        if export_file:
            output_path = Path(export_file)
            output_path.write_text(markdown_content, encoding="utf-8")

        return markdown_content

    def print_lineage_summary(self, lineage: list[Any]) -> None:
        """Print a formatted summary of lineage data.

        Args:
            lineage: List of lineage items (already deduplicated by lineage.get())

        Example:
            >>> diagram = MermaidDiagram.from_entity(entity)
            >>> lineage = await entity.Lineage.get(is_recursive=True)
            >>> diagram.print_lineage_summary(lineage)
        """
        # Get parent name from root node (first node is always the root entity)
        if self.nodes:
            parent_name = self.nodes[0].name
        elif self.title:
            # Fallback: extract from title
            parent_name = self.title.replace("Lineage Diagram for ", "")
        else:
            parent_name = self.entity_id or "Unknown"

        print(f"\n{'=' * 60}")
        print(f"Lineage Summary: {parent_name}")
        if self.entity_type:
            print(f"Type: {self.entity_type}, ID: {self.entity_id}")
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
                # Use entity_name property if available
                if (
                    hasattr(item, "entity")
                    and item.entity
                    and hasattr(item.entity, "entity_name")
                ):
                    entity_name = item.entity.entity_name
                else:
                    # Fallback: try to get name from entity or use ID
                    if hasattr(item, "entity") and item.entity:
                        entity_name = (
                            getattr(item.entity, "name", None)
                            or getattr(item.entity, "title", None)
                            or getattr(item.entity, "display_name", None)
                            or item.id
                        )
                    else:
                        entity_name = item.id
                print(f"\n  {idx}. {item.type}: {item.id}")
                print(f"     Name: {entity_name}")
                if hasattr(item, "dependencies") and item.dependencies:
                    print(f"     Dependencies: {len(item.dependencies)}")
                if hasattr(item, "dependents") and item.dependents:
                    print(f"     Dependents: {len(item.dependents)}")
        else:
            print("No lineage items found.")

        print(f"\n{'=' * 60}\n")

    @classmethod
    def from_entity(
        cls,
        entity: Any,
        direction: str = "TD",
        use_aliases: bool = True,
    ) -> "MermaidDiagram":
        """Create a Mermaid diagram shell for a Domo entity.

        Creates an empty diagram with the entity as the root node.
        Use `add_lineage_link()` to populate with lineage data.

        Args:
            entity: The entity (DomoPage, DomoDataset, etc.) to create diagram for
            direction: Diagram direction - "TD" (top-down), "LR" (left-right), etc.
            use_aliases: Whether to use short aliases (A, B, C) instead of long IDs

        Returns:
            MermaidDiagram object ready to be populated

        Example:
            >>> diagram = MermaidDiagram.from_entity(page)
            >>> lineage = await page.Lineage.get(is_recursive=True)
            >>> for item in lineage:
            ...     diagram.add_lineage_link(item)
            >>> print(diagram.to_string())
        """
        # Use entity_name property if available, otherwise fall back to helper
        if hasattr(entity, "entity_name"):
            entity_display_name = entity.entity_name
        else:
            entity_display_name = _extract_entity_name(
                entity
            )  # Deprecated but still works
        diagram = cls(
            nodes=[],
            direction=direction,
            title=f"Lineage Diagram for {entity_display_name}",
            entity_id=str(entity.id),
            entity_type=entity.entity_type,
            use_aliases=use_aliases,
        )
        # Add root node (will get alias "A" automatically)
        root_node = MermaidNode.from_domo_entity(entity)
        diagram.add_node(root_node)
        return diagram
