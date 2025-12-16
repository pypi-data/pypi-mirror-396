"""
Context Provider for AI Assistants

Generates relevant code context for AI prompts by querying the graph.
"""

from __future__ import annotations

from typing import Any

from .neo4j_client import Neo4jClient
from .queries import CodeGraphQueries


class CodeGraphContext:
    """Context provider for AI coding assistants."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize context provider.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client
        self.queries = CodeGraphQueries()

    def get_context_for_file(
        self, file_path: str, max_depth: int = 2
    ) -> dict[str, Any]:
        """Get relevant context for a file.

        Args:
            file_path: Path to file
            max_depth: Maximum depth to traverse relationships

        Returns:
            Dictionary with context information
        """
        query = f"""
        MATCH (f:File {{path: '{file_path}'}})
        OPTIONAL MATCH (f)-[:CONTAINS]->(entity)
        OPTIONAL MATCH (entity)-[r*1..{max_depth}]->(related)
        RETURN f, collect(DISTINCT entity) as entities, collect(DISTINCT related) as related
        """
        results = self.client.execute_query(query)

        if not results:
            return {"file": None, "entities": [], "related": []}

        result = results[0]
        return {
            "file": result.get("f"),
            "entities": result.get("entities", []),
            "related": result.get("related", []),
        }

    def get_context_for_function(
        self, function_name: str, file_path: str | None = None
    ) -> dict[str, Any]:
        """Get relevant context for a function.

        Args:
            function_name: Name of function
            file_path: Optional file path to limit search

        Returns:
            Dictionary with context information
        """
        # Find function
        if file_path:
            query = f"""
            MATCH (f:Function {{name: '{function_name}', file_path: '{file_path}'}})
            OPTIONAL MATCH (f)<-[:CALLS]-(caller)
            OPTIONAL MATCH (f)-[:CALLS]->(callee)
            OPTIONAL MATCH (f)-[:DEFINES]->(var:Variable)
            RETURN f, collect(DISTINCT caller) as callers,
                   collect(DISTINCT callee) as callees,
                   collect(DISTINCT var) as variables
            """
        else:
            query = f"""
            MATCH (f:Function {{name: '{function_name}'}})
            OPTIONAL MATCH (f)<-[:CALLS]-(caller)
            OPTIONAL MATCH (f)-[:CALLS]->(callee)
            OPTIONAL MATCH (f)-[:DEFINES]->(var:Variable)
            RETURN f, collect(DISTINCT caller) as callers,
                   collect(DISTINCT callee) as callees,
                   collect(DISTINCT var) as variables
            LIMIT 1
            """

        results = self.client.execute_query(query)

        if not results:
            return {"function": None, "callers": [], "callees": [], "variables": []}

        result = results[0]
        return {
            "function": result.get("f"),
            "callers": result.get("callers", []),
            "callees": result.get("callees", []),
            "variables": result.get("variables", []),
        }

    def get_related_code(
        self, node_id: str, relationship_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Get code related to a node.

        Args:
            node_id: Node ID
            relationship_types: Optional list of relationship types to follow

        Returns:
            List of related nodes
        """
        if relationship_types:
            rel_types = "|".join(relationship_types)
            query = f"""
            MATCH (n {{id: '{node_id}'}})-[r:{rel_types}]->(related)
            RETURN related, r
            ORDER BY related.name
            """
        else:
            query = f"""
            MATCH (n {{id: '{node_id}'}})-[r]->(related)
            RETURN related, r
            ORDER BY related.name
            """

        return self.client.execute_query(query)
