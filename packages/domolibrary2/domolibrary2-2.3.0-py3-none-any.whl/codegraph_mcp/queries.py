"""
Common Graph Queries

Provides common Cypher queries for codebase graph analysis.
"""

from __future__ import annotations


class CodeGraphQueries:
    """Collection of common graph queries for code analysis."""

    @staticmethod
    def find_usages(function_name: str, file_path: str | None = None) -> str:
        """Find where a function is used.

        Args:
            function_name: Name of function to find
            file_path: Optional file path to limit search

        Returns:
            Cypher query string
        """
        if file_path:
            return f"""
            MATCH (caller)-[:CALLS]->(callee:Function {{name: '{function_name}'}})
            WHERE callee.file_path = '{file_path}'
            RETURN caller, callee
            """
        return f"""
        MATCH (caller)-[:CALLS]->(callee:Function {{name: '{function_name}'}})
        RETURN caller, callee
        """

    @staticmethod
    def get_dependencies(node_id: str) -> str:
        """Get all dependencies of a node.

        Args:
            node_id: Node ID to get dependencies for

        Returns:
            Cypher query string
        """
        return f"""
        MATCH (n {{id: '{node_id}'}})-[r]->(dep)
        RETURN dep, r
        ORDER BY dep.name
        """

    @staticmethod
    def find_impact(node_id: str) -> str:
        """Find what would break if a node changes.

        Args:
            node_id: Node ID to analyze

        Returns:
            Cypher query string
        """
        return f"""
        MATCH (n {{id: '{node_id}'}})<-[r]-(dependent)
        RETURN dependent, r
        ORDER BY dependent.name
        """

    @staticmethod
    def trace_call_chain(start_node_id: str, max_depth: int = 10) -> str:
        """Trace execution path through code.

        Args:
            start_node_id: Starting node ID
            max_depth: Maximum depth to traverse

        Returns:
            Cypher query string
        """
        return f"""
        MATCH path = (start {{id: '{start_node_id}'}})-[:CALLS*1..{max_depth}]->(end)
        RETURN path
        ORDER BY length(path)
        LIMIT 100
        """

    @staticmethod
    def find_circular_dependencies() -> str:
        """Find circular dependencies in code.

        Returns:
            Cypher query string
        """
        return """
        MATCH path = (a)-[:IMPORTS_FROM*]->(a)
        RETURN path
        LIMIT 50
        """

    @staticmethod
    def get_class_hierarchy(class_name: str) -> str:
        """Get class inheritance hierarchy.

        Args:
            class_name: Name of class

        Returns:
            Cypher query string
        """
        return f"""
        MATCH (c:Class {{name: '{class_name}'}})
        OPTIONAL MATCH path = (c)-[:EXTENDS*]->(parent)
        RETURN c, path
        """

    @staticmethod
    def find_unused_code() -> str:
        """Find code that is never called.

        Returns:
            Cypher query string
        """
        return """
        MATCH (f:Function)
        WHERE NOT (f)<-[:CALLS]-()
        AND NOT f.name STARTS WITH '_'
        RETURN f
        ORDER BY f.name
        """
