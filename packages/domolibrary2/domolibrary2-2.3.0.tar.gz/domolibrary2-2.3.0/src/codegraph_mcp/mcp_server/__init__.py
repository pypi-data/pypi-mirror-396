"""
Code Graph MCP Server Package

MCP server that exposes codegraph functionality as AI-accessible tools and resources.
"""

from .server import create_server, mcp

__all__ = ["mcp", "create_server"]
