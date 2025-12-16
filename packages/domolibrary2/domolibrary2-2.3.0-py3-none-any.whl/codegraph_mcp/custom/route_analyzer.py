"""
Route Analyzer

Analyzes route functions and their RouteContext usage patterns.
"""

from __future__ import annotations

from typing import Any

from ..neo4j_client import Neo4jClient


class RouteAnalyzer:
    """Analyzer for route patterns."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize route analyzer.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client

    def get_all_routes(self) -> list[dict[str, Any]]:
        """Get all route functions.

        Returns:
            List of route nodes
        """
        query = """
        MATCH (r:Route)
        RETURN r
        ORDER BY r.file_path, r.name
        """
        return self.client.execute_query(query)

    def get_routes_by_module(self, module_path: str) -> list[dict[str, Any]]:
        """Get routes in a specific module.

        Args:
            module_path: Path to module

        Returns:
            List of route nodes
        """
        query = """
        MATCH (r:Route)
        WHERE r.file_path CONTAINS $module_path
        RETURN r
        ORDER BY r.name
        """
        return self.client.execute_query(query, {"module_path": module_path})

    def get_route_dependencies(self, route_id: str) -> list[dict[str, Any]]:
        """Get dependencies of a route.

        Args:
            route_id: Route node ID

        Returns:
            List of dependency nodes
        """
        query = """
        MATCH (r:Route {id: $route_id})-[:HAS_ROUTE_CONTEXT]->(ctx)
        OPTIONAL MATCH (r)-[:CALLS]->(dep)
        RETURN r, ctx, collect(DISTINCT dep) as dependencies
        """
        return self.client.execute_query(query, {"route_id": route_id})
