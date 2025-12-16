"""
Domo MCP Server Entry Point

Run the server with:
    python -m domo_mcp

Environment Variables:
    DOMO_INSTANCE: Your Domo instance name (required)
    DOMO_ACCESS_TOKEN: Your Domo access token (required)
"""

from .server import main

if __name__ == "__main__":
    main()
