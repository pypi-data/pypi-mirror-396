"""
Code Graph Resources for Domo MCP Server

Exposes code graph data as MCP resources for AI assistants.
"""

from __future__ import annotations

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from ...codegraph_mcp.context import CodeGraphContext
from ...codegraph_mcp.custom.entity_analyzer import EntityAnalyzer
from ...codegraph_mcp.custom.mcp_analyzer import MCPAnalyzer
from ...codegraph_mcp.custom.route_analyzer import RouteAnalyzer
from ...codegraph_mcp.neo4j_client import Neo4jClient, Neo4jConnectionError
from ..auth_context import DomoContext
from ..server import mcp


def _get_neo4j_client() -> Neo4jClient | None:
    """Get Neo4j client instance.

    Returns:
        Neo4jClient instance or None if not configured
    """
    try:
        return Neo4jClient()
    except Neo4jConnectionError:
        return None


@mcp.resource("codegraph://file/{file_path}")
async def get_file_context(
    file_path: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Get code context for a specific file.

    Args:
        file_path: Path to file
        ctx: MCP context

    Returns:
        JSON string with file context
    """
    client = _get_neo4j_client()
    if not client:
        return '{"error": "Neo4j not configured"}'

    context_provider = CodeGraphContext(client)
    context = context_provider.get_context_for_file(file_path)

    import json

    return json.dumps(context, indent=2)


@mcp.resource("codegraph://function/{function_name}")
async def get_function_context(
    function_name: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Get code context for a specific function.

    Args:
        function_name: Name of function
        ctx: MCP context

    Returns:
        JSON string with function context
    """
    client = _get_neo4j_client()
    if not client:
        return '{"error": "Neo4j not configured"}'

    context_provider = CodeGraphContext(client)
    context = context_provider.get_context_for_function(function_name)

    import json

    return json.dumps(context, indent=2)


@mcp.resource("codegraph://routes")
async def get_all_routes(
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Get all route functions.

    Args:
        ctx: MCP context

    Returns:
        JSON string with all routes
    """
    client = _get_neo4j_client()
    if not client:
        return '{"error": "Neo4j not configured"}'

    route_analyzer = RouteAnalyzer(client)
    routes = route_analyzer.get_all_routes()

    import json

    return json.dumps({"routes": routes}, indent=2)


@mcp.resource("codegraph://entities")
async def get_all_entities(
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Get all DomoEntity classes.

    Args:
        ctx: MCP context

    Returns:
        JSON string with all entities
    """
    client = _get_neo4j_client()
    if not client:
        return '{"error": "Neo4j not configured"}'

    entity_analyzer = EntityAnalyzer(client)
    entities = entity_analyzer.get_all_entities()

    import json

    return json.dumps({"entities": entities}, indent=2)


@mcp.resource("codegraph://mcp-tools")
async def get_all_mcp_tools(
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Get all MCP server tools.

    Args:
        ctx: MCP context

    Returns:
        JSON string with all MCP tools
    """
    client = _get_neo4j_client()
    if not client:
        return '{"error": "Neo4j not configured"}'

    mcp_analyzer = MCPAnalyzer(client)
    tools = mcp_analyzer.get_all_tools()

    import json

    return json.dumps({"tools": tools}, indent=2)
