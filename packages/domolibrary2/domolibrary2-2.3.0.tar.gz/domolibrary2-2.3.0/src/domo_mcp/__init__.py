"""
Domo MCP Server

A Model Context Protocol (MCP) server that exposes domolibrary routes as AI-accessible tools.
This enables AI agents to interact with Domo for DevOps automation, data pipeline management,
content management, and governance operations.

Usage:
    # Run with stdio transport (default)
    python -m domo_mcp

    # Set environment variables
    export DOMO_INSTANCE="your-instance"
    export DOMO_ACCESS_TOKEN="your-access-token"
"""

from .server import create_server, mcp

__all__ = ["mcp", "create_server"]
