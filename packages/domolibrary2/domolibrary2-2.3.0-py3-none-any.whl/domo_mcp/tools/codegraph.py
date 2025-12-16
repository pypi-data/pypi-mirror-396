"""
Code Graph Tools for Domo MCP Server

Provides tools for querying the codebase graph to enhance AI coding assistants.
"""

from __future__ import annotations

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from codegraph_mcp.analysis import CodeGraphAnalysis
from codegraph_mcp.context import CodeGraphContext
from codegraph_mcp.neo4j_client import Neo4jClient
from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp


class CodeUsageResult(BaseModel):
    """Structured output for code usage search."""

    node_id: str = Field(description="Node ID")
    name: str = Field(description="Entity name")
    file_path: str = Field(description="File path")
    usage_count: int = Field(description="Number of usages found")
    usages: list[dict] = Field(description="List of usage locations")


class DependencyResult(BaseModel):
    """Structured output for dependency analysis."""

    node_id: str = Field(description="Node ID")
    name: str = Field(description="Entity name")
    dependencies: list[dict] = Field(description="List of dependencies")
    dependents: list[dict] = Field(description="List of dependents")


class ImpactAnalysisResult(BaseModel):
    """Structured output for impact analysis."""

    node_id: str = Field(description="Node ID")
    name: str = Field(description="Entity name")
    affected_nodes: list[dict] = Field(description="Nodes that would be affected")
    impact_count: int = Field(description="Number of affected nodes")


def _get_neo4j_client() -> Neo4jClient | None:
    """Get Neo4j client instance.

    Returns:
        Neo4jClient instance or None if not configured
    """
    try:
        return Neo4jClient()
    except Exception:
        return None


@mcp.tool()
async def find_code_usage(
    function_name: str = Field(description="Name of function or class to find"),
    file_path: str | None = Field(
        default=None, description="Optional file path to limit search"
    ),
    ctx: Context[ServerSession, DomoContext] = Field(default=None),
) -> CodeUsageResult:
    """Find where a function or class is used in the codebase.

    Args:
        function_name: Name of function or class to search for
        file_path: Optional file path to limit search scope
        ctx: MCP context

    Returns:
        CodeUsageResult with usage information
    """
    client = _get_neo4j_client()
    if not client:
        raise ValueError(
            "Neo4j not configured. Set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD"
        )

    analysis = CodeGraphAnalysis(client)
    queries = analysis.queries

    if file_path:
        query = queries.find_usages(function_name, file_path)
    else:
        query = queries.find_usages(function_name)

    results = client.execute_query(query)

    usages = []
    for result in results:
        if "caller" in result:
            usages.append(result["caller"])

    return CodeUsageResult(
        node_id="",
        name=function_name,
        file_path=file_path or "",
        usage_count=len(usages),
        usages=usages,
    )


@mcp.tool()
async def get_dependencies(
    node_id: str = Field(description="Node ID to get dependencies for"),
    ctx: Context[ServerSession, DomoContext] = Field(default=None),
) -> DependencyResult:
    """Get all dependencies of a module, class, or function.

    Args:
        node_id: Node ID to analyze
        ctx: MCP context

    Returns:
        DependencyResult with dependency information
    """
    client = _get_neo4j_client()
    if not client:
        raise ValueError("Neo4j not configured")

    analysis = CodeGraphAnalysis(client)
    dependencies = analysis.get_dependencies(node_id)

    # Get dependents (reverse dependencies)
    query = f"""
    MATCH (n {{id: '{node_id}'}})<-[r]-(dependent)
    RETURN dependent, r
    """
    dependents = client.execute_query(query)

    return DependencyResult(
        node_id=node_id,
        name="",
        dependencies=dependencies,
        dependents=dependents,
    )


@mcp.tool()
async def find_impact(
    node_id: str = Field(description="Node ID to analyze impact for"),
    ctx: Context[ServerSession, DomoContext] = Field(default=None),
) -> ImpactAnalysisResult:
    """Find what would break if this code changes.

    Args:
        node_id: Node ID to analyze
        ctx: MCP context

    Returns:
        ImpactAnalysisResult with affected nodes
    """
    client = _get_neo4j_client()
    if not client:
        raise ValueError("Neo4j not configured")

    analysis = CodeGraphAnalysis(client)
    affected = analysis.analyze_impact(node_id)

    return ImpactAnalysisResult(
        node_id=node_id,
        name="",
        affected_nodes=affected,
        impact_count=len(affected),
    )


@mcp.tool()
async def suggest_refactor(
    ctx: Context[ServerSession, DomoContext] = Field(default=None),
) -> dict:
    """Suggest refactoring opportunities based on code analysis.

    Args:
        ctx: MCP context

    Returns:
        Dictionary with refactoring suggestions
    """
    client = _get_neo4j_client()
    if not client:
        raise ValueError("Neo4j not configured")

    analysis = CodeGraphAnalysis(client)
    suggestions = analysis.suggest_refactoring()

    return {
        "suggestions": suggestions,
        "count": len(suggestions),
    }


@mcp.tool()
async def get_code_context(
    file_path: str = Field(description="Path to file"),
    max_depth: int = Field(default=2, description="Maximum relationship depth"),
    ctx: Context[ServerSession, DomoContext] = Field(default=None),
) -> dict:
    """Get relevant code context for a file or function.

    Args:
        file_path: Path to file
        max_depth: Maximum depth to traverse relationships
        ctx: MCP context

    Returns:
        Dictionary with context information
    """
    client = _get_neo4j_client()
    if not client:
        raise ValueError("Neo4j not configured")

    context_provider = CodeGraphContext(client)
    return context_provider.get_context_for_file(file_path, max_depth)


@mcp.tool()
async def trace_call_chain(
    start_node_id: str = Field(description="Starting node ID"),
    max_depth: int = Field(default=10, description="Maximum chain depth"),
    ctx: Context[ServerSession, DomoContext] = Field(default=None),
) -> dict:
    """Trace execution path through code.

    Args:
        start_node_id: Starting node ID
        max_depth: Maximum depth to traverse
        ctx: MCP context

    Returns:
        Dictionary with call chain information
    """
    client = _get_neo4j_client()
    if not client:
        raise ValueError("Neo4j not configured")

    analysis = CodeGraphAnalysis(client)
    chain = analysis.trace_call_chain(start_node_id, max_depth)

    return {
        "chain": chain,
        "depth": max_depth,
    }
