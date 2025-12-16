"""
Code Analysis Tools

Provides analysis functions for code quality, dependencies, and refactoring.
"""

from __future__ import annotations

from typing import Any

from .neo4j_client import Neo4jClient
from .queries import CodeGraphQueries


class CodeGraphAnalysis:
    """Analysis tools for codebase graph."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize analysis tools.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client
        self.queries = CodeGraphQueries()

    def find_unused_code(self) -> list[dict[str, Any]]:
        """Find unused code (functions never called).

        Returns:
            List of unused function nodes
        """
        query = self.queries.find_unused_code()
        return self.client.execute_query(query)

    def find_circular_dependencies(self) -> list[dict[str, Any]]:
        """Find circular import dependencies.

        Returns:
            List of circular dependency paths
        """
        query = self.queries.find_circular_dependencies()
        return self.client.execute_query(query)

    def analyze_impact(self, node_id: str) -> list[dict[str, Any]]:
        """Analyze impact of changing a node.

        Args:
            node_id: Node ID to analyze

        Returns:
            List of dependent nodes
        """
        query = self.queries.find_impact(node_id)
        return self.client.execute_query(query)

    def get_dependencies(self, node_id: str) -> list[dict[str, Any]]:
        """Get all dependencies of a node.

        Args:
            node_id: Node ID

        Returns:
            List of dependency nodes
        """
        query = self.queries.get_dependencies(node_id)
        return self.client.execute_query(query)

    def trace_call_chain(
        self, start_node_id: str, max_depth: int = 10
    ) -> list[dict[str, Any]]:
        """Trace execution path through code.

        Args:
            start_node_id: Starting node ID
            max_depth: Maximum depth to traverse

        Returns:
            List of call chain paths
        """
        query = self.queries.trace_call_chain(start_node_id, max_depth)
        return self.client.execute_query(query)

    def suggest_refactoring(self) -> list[dict[str, Any]]:
        """Suggest refactoring opportunities.

        Returns:
            List of refactoring suggestions
        """
        # Find functions with many dependencies (high coupling)
        query = """
        MATCH (f:Function)-[r]->(dep)
        WITH f, count(dep) as dep_count
        WHERE dep_count > 10
        RETURN f, dep_count
        ORDER BY dep_count DESC
        LIMIT 20
        """
        return self.client.execute_query(query)
