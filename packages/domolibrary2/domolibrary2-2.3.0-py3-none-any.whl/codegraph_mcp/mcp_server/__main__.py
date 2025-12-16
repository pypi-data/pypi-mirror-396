"""
Code Graph MCP Server Entry Point

Run the server with:
    python -m codegraph_mcp.mcp_server

Environment Variables:
    NEO4J_URI: Neo4j connection URI (required)
    NEO4J_USERNAME: Neo4j username (required)
    NEO4J_PASSWORD: Neo4j password (required)
    NEO4J_DATABASE: Neo4j database name (optional, defaults to 'neo4j')
"""

from .server import main

if __name__ == "__main__":
    main()
