"""
Graph Schema Definitions

Defines the Neo4j graph schema for codebase mapping, including base schema
from Graph-Codebase-MCP and domolibrary2-specific extensions.
"""

from __future__ import annotations

# Base node types (from Graph-Codebase-MCP)
BASE_NODE_TYPES = [
    "Module",
    "Class",
    "Function",
    "Variable",
    "Import",
    "Decorator",
]

# Base relationship types (from Graph-Codebase-MCP)
BASE_RELATIONSHIPS = [
    "IMPORTS",
    "CALLS",
    "INHERITS",
    "USES",
    "DECORATES",
]

# domolibrary2-specific node types
DOMO_NODE_TYPES = [
    "Route",  # API route endpoints
    "MCPTool",  # MCP server tools
    "DomoEntity",  # DomoEntity classes
    "Test",  # Test files and test functions
]

# domolibrary2-specific relationships
DOMO_RELATIONSHIPS = [
    "HAS_ROUTE_CONTEXT",  # Route → RouteContext
    "TESTS",  # Test → CodeUnderTest
    "IS_DOMO_ENTITY",  # Class → DomoEntity
    "EXPOSES_MCP_TOOL",  # Function → MCPTool
]

# All node types
ALL_NODE_TYPES = BASE_NODE_TYPES + DOMO_NODE_TYPES

# All relationship types
ALL_RELATIONSHIPS = BASE_RELATIONSHIPS + DOMO_RELATIONSHIPS
