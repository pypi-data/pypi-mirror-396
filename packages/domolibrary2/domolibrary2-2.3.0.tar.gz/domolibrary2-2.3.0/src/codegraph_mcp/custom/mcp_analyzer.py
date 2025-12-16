"""
MCP Tool Analyzer

Analyzes MCP server tools and their relationships.
"""

from __future__ import annotations

from typing import Any

from ..neo4j_client import Neo4jClient


class MCPAnalyzer:
    """Analyzer for MCP tool patterns."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize MCP analyzer.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client

    def get_all_tools(self) -> list[dict[str, Any]]:
        """Get all MCP tools.

        Returns:
            List of MCP tool nodes
        """
        query = """
        MATCH (t:MCPTool)
        RETURN t
        ORDER BY t.name
        """
        return self.client.execute_query(query)

    def get_tools_by_module(self, module_path: str) -> list[dict[str, Any]]:
        """Get MCP tools in a specific module.

        Args:
            module_path: Path to module

        Returns:
            List of MCP tool nodes
        """
        query = """
        MATCH (t:MCPTool)
        WHERE t.file_path CONTAINS $module_path
        RETURN t
        ORDER BY t.name
        """
        return self.client.execute_query(query, {"module_path": module_path})

    def get_tool_dependencies(self, tool_id: str) -> list[dict[str, Any]]:
        """Get dependencies of an MCP tool.

        Args:
            tool_id: MCP tool node ID

        Returns:
            List of dependency nodes
        """
        query = """
        MATCH (t:MCPTool {id: $tool_id})
        OPTIONAL MATCH (t)<-[:EXPOSES_MCP_TOOL]-(f:Function)
        OPTIONAL MATCH (f)-[:CALLS]->(dep)
        RETURN t, f, collect(DISTINCT dep) as dependencies
        """
        return self.client.execute_query(query, {"tool_id": tool_id})
