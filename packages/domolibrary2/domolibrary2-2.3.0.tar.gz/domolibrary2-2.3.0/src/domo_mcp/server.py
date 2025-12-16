"""
Domo MCP Server

Main FastMCP server that exposes domolibrary routes as MCP tools, resources, and prompts.
"""

from mcp.server.fastmcp import FastMCP

from .auth_context import domo_lifespan

# Create the FastMCP server with Domo authentication lifespan
mcp = FastMCP(
    "Domo MCP Server",
    lifespan=domo_lifespan,
)


def _register_components():
    """Import all component modules to trigger registration decorators."""
    from . import prompts, resources, tools  # noqa: F401


def create_server() -> FastMCP:
    """Create and configure the Domo MCP server.

    Returns:
        FastMCP: Configured MCP server with all tools, resources, and prompts registered
    """
    _register_components()
    return mcp


def main():
    """Entry point for running the MCP server."""
    _register_components()
    mcp.run()


if __name__ == "__main__":
    main()
