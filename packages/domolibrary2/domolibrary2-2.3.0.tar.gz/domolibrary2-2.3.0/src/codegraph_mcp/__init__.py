"""
Codebase Graph Mapping Module

This module provides Neo4j-based codebase mapping capabilities by adapting
Graph-Codebase-MCP for library integration. It enables code dependency analysis,
refactoring support, and enhanced AI coding assistant context.
"""

from __future__ import annotations

from .analysis import CodeGraphAnalysis
from .ast_parser import ASTParser, CodeNode, CodeRelation
from .builder import CodeGraphBuilder
from .context import CodeGraphContext
from .neo4j_client import Neo4jClient
from .queries import CodeGraphQueries
from .scanner import CodeGraphScanner

__all__ = [
    "Neo4jClient",
    "ASTParser",
    "CodeNode",
    "CodeRelation",
    "CodeGraphBuilder",
    "CodeGraphScanner",
    "CodeGraphAnalysis",
    "CodeGraphContext",
    "CodeGraphQueries",
]
