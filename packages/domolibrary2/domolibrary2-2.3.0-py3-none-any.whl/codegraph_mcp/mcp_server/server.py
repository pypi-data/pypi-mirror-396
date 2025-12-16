"""
Code Graph MCP Server

Main FastMCP server that exposes codegraph functionality as MCP tools and resources.
This server provides code analysis capabilities through Neo4j graph database.
"""

from mcp.server.fastmcp import FastMCP

# Create the FastMCP server (no lifespan needed - Neo4j connection is per-request)
mcp = FastMCP("Code Graph MCP Server")


def _register_components():
    """Import all component modules to trigger registration decorators."""
    from . import resources, tools  # noqa: F401


def create_server() -> FastMCP:
    """Create and configure the Code Graph MCP server.

    Returns:
        FastMCP: Configured MCP server with all tools and resources registered
    """
    _register_components()
    return mcp


def main():
    """Entry point for running the MCP server."""
    _register_components()
    mcp.run()


if __name__ == "__main__":
    main()
