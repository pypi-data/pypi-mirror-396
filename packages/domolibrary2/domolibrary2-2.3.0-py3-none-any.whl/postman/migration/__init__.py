"""Migration module for human-in-the-loop function migration."""

from __future__ import annotations

from .migration_research import CodebaseResearcher
from .migration_state import FunctionMigrationState

# Optional import - langgraph may not be available in all environments
try:
    from .migration_graph import get_migration_graph

    __all__ = [
        "FunctionMigrationState",
        "CodebaseResearcher",
        "get_migration_graph",
    ]
except ImportError:
    __all__ = [
        "FunctionMigrationState",
        "CodebaseResearcher",
    ]
