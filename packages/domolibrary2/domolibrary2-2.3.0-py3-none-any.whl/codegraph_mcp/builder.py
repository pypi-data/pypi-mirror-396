"""
Graph Builder

Builds Neo4j graph from parsed code nodes and relationships.
Handles batch insertion and incremental updates.
"""

from __future__ import annotations

import hashlib
from typing import Any

from .ast_parser import CodeNode, CodeRelation
from .neo4j_client import Neo4jClient


class CodeGraphBuilder:
    """Builder for creating Neo4j graph from code analysis."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize graph builder.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client
        self.file_hashes: dict[str, str] = {}

    def build_graph(
        self,
        nodes: dict[str, CodeNode],
        relations: list[CodeRelation],
        clear_existing: bool = False,
    ) -> None:
        """Build graph from nodes and relationships.

        Args:
            nodes: Dictionary of code nodes
            relations: List of code relationships
            clear_existing: Whether to clear existing graph first
        """
        if clear_existing:
            self.client.clear_database()

        # Create schema constraints and indexes
        self.client.create_schema_constraints()

        # Convert nodes to Neo4j format
        neo4j_nodes = self._convert_nodes(nodes)
        self.client.batch_create_nodes(neo4j_nodes)

        # Convert relations to Neo4j format (filter out invalid relationships)
        neo4j_relations = self._convert_relations(relations, nodes)
        if neo4j_relations:
            self.client.batch_create_relationships(neo4j_relations)

    def _convert_nodes(self, nodes: dict[str, CodeNode]) -> list[dict[str, Any]]:
        """Convert CodeNode objects to Neo4j node format.

        Args:
            nodes: Dictionary of CodeNode objects

        Returns:
            List of Neo4j node dictionaries
        """
        neo4j_nodes = []
        for node_id, node in nodes.items():
            # Determine labels based on node type
            labels = [node.node_type]
            # Add Base label for nodes that need it (for relationship matching)
            if node.node_type in [
                "File",
                "Class",
                "Function",
                "Method",
                "Variable",
                "Route",
                "MCPTool",
                "DomoEntity",
                "Test",
            ]:
                labels.append("Base")

            # Build properties
            properties: dict[str, Any] = {
                "id": node_id,
                "name": node.name,
                "file_path": node.file_path,
                "line_no": node.line_no,
            }

            if node.end_line_no:
                properties["end_line_no"] = node.end_line_no

            # Add node type specific properties
            if node.node_type == "File":
                properties["path"] = node.file_path

            # Merge additional properties
            properties.update(node.properties)

            neo4j_nodes.append({"labels": labels, "properties": properties})

        return neo4j_nodes

    def _convert_relations(
        self, relations: list[CodeRelation], nodes: dict[str, CodeNode]
    ) -> list[dict[str, Any]]:
        """Convert CodeRelation objects to Neo4j relationship format.

        Args:
            relations: List of CodeRelation objects
            nodes: Dictionary of all nodes to validate relationships against

        Returns:
            List of Neo4j relationship dictionaries (only valid relationships)
        """
        neo4j_relations = []
        skipped = 0

        for relation in relations:
            # Only include relationships where both source and target nodes exist
            # This filters out relationships to standard library functions/classes
            if relation.source_id in nodes and relation.target_id in nodes:
                neo4j_relations.append(
                    {
                        "start_node_id": relation.source_id,
                        "end_node_id": relation.target_id,
                        "type": relation.relation_type,
                        "properties": relation.properties,
                    }
                )
            else:
                skipped += 1

        if skipped > 0:
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                f"Skipped {skipped} relationships with missing target/source nodes"
            )

        return neo4j_relations

    def get_file_hash(self, file_path: str) -> str:
        """Calculate hash of file for change detection.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash of file content
        """
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def has_file_changed(self, file_path: str) -> bool:
        """Check if file has changed since last scan.

        Args:
            file_path: Path to file

        Returns:
            True if file has changed, False otherwise
        """
        current_hash = self.get_file_hash(file_path)
        previous_hash = self.file_hashes.get(file_path)

        if previous_hash is None or previous_hash != current_hash:
            self.file_hashes[file_path] = current_hash
            return True

        return False
