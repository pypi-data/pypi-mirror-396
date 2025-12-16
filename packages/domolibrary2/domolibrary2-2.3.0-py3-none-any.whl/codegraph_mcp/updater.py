"""
Incremental Update System

Tracks file changes and updates graph incrementally.
"""

from __future__ import annotations

from .builder import CodeGraphBuilder
from .scanner import CodeGraphScanner


class CodeGraphUpdater:
    """Handles incremental updates to the graph."""

    def __init__(self, builder: CodeGraphBuilder, scanner: CodeGraphScanner) -> None:
        """Initialize updater.

        Args:
            builder: Graph builder instance
            scanner: Code scanner instance
        """
        self.builder = builder
        self.scanner = scanner

    def update_file(self, file_path: str) -> None:
        """Update graph for a single changed file.

        Args:
            file_path: Path to changed file
        """
        # Check if file has actually changed
        if not self.builder.has_file_changed(file_path):
            return

        # Parse the file
        nodes, relations = self.scanner.scan_file(file_path)

        # Remove old nodes for this file
        self._remove_file_nodes(file_path)

        # Add new nodes and relations
        if nodes:
            neo4j_nodes = self.builder._convert_nodes(nodes)
            self.builder.client.batch_create_nodes(neo4j_nodes)

        if relations:
            neo4j_relations = self.builder._convert_relations(relations, nodes)
            if neo4j_relations:
                self.builder.client.batch_create_relationships(neo4j_relations)

    def _remove_file_nodes(self, file_path: str) -> None:
        """Remove all nodes for a file from the graph.

        Args:
            file_path: Path to file
        """
        query = """
        MATCH (n {file_path: $file_path})
        DETACH DELETE n
        """
        self.builder.client.execute_write(query, {"file_path": file_path})

    def batch_update_files(self, file_paths: list[str]) -> None:
        """Update graph for multiple changed files.

        Args:
            file_paths: List of file paths to update
        """
        for file_path in file_paths:
            try:
                self.update_file(file_path)
            except Exception as e:
                print(f"Error updating file {file_path}: {e}")
