"""Codebase research using CypherQAChain and Neo4j graph."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dc_logger import get_logger

try:
    from codegraph_mcp.context import CodeGraphContext
    from codegraph_mcp.neo4j_client import Neo4jClient, Neo4jConnectionError
    from codegraph_mcp.queries import CodeGraphQueries
except ImportError:
    CodeGraphContext = None  # type: ignore
    Neo4jClient = None  # type: ignore
    Neo4jConnectionError = Exception  # type: ignore
    CodeGraphQueries = None  # type: ignore

logger = get_logger("migration_research")


@dataclass
class CodebaseResearcher:
    """Research codebase using CypherQAChain and Neo4j graph.

    Attributes:
        neo4j_client: Optional Neo4j client instance. If None, will attempt to create one.
        routes_dir: Directory containing route files for code extraction
        client: Neo4j client instance (initialized in __post_init__)
        context: CodeGraphContext instance (initialized in __post_init__)
        queries: CodeGraphQueries instance (initialized in __post_init__)
        _available: Whether codebase research is available (initialized in __post_init__)
    """

    neo4j_client: Neo4jClient | None = None
    routes_dir: str = "src/domolibrary2/routes"
    client: Neo4jClient | None = field(default=None, init=False)
    context: CodeGraphContext | None = field(default=None, init=False)
    queries: CodeGraphQueries | None = field(default=None, init=False)
    _available: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Initialize Neo4j client and related components after dataclass initialization."""
        if self.neo4j_client:
            self.client = self.neo4j_client
            self._initialize_from_client()
        else:
            self._try_initialize()

    def _initialize_from_client(self) -> None:
        """Initialize context and queries from existing client."""
        if CodeGraphContext and CodeGraphQueries and self.client:
            try:
                self.context = CodeGraphContext(self.client)
                self.queries = CodeGraphQueries()
                self._available = True
            except Exception as e:
                logger.warning(f"Failed to initialize codegraph context: {e}")
                self._available = False

    def _try_initialize(self) -> None:
        """Try to initialize Neo4j client from environment variables."""
        if not Neo4jClient:
            logger.warning("codegraph_mcp not available. Codebase research disabled.")
            return

        try:
            uri = os.getenv("NEO4J_URI")
            if not uri:
                logger.warning("NEO4J_URI not set. Codebase research disabled.")
                return

            self.client = Neo4jClient()
            self._initialize_from_client()
        except Neo4jConnectionError as e:
            logger.warning(
                f"Could not connect to Neo4j: {e}. Codebase research disabled."
            )
        except Exception as e:
            logger.warning(
                f"Failed to initialize Neo4j client: {e}. Codebase research disabled."
            )

    @property
    def is_available(self) -> bool:
        """Check if codebase research is available."""
        return self._available and self.client is not None

    def find_similar_routes(
        self, url_pattern: str, method: str, module_path: str | None = None
    ) -> list[dict[str, Any]]:
        """Find routes with similar URL patterns.

        Args:
            url_pattern: URL pattern to match against
            method: HTTP method (GET, POST, etc.)
            module_path: Optional module path to limit search

        Returns:
            List of route dictionaries with function info
        """
        if not self.is_available or not self.client:
            return []

        try:
            # Extract URL segments for matching
            url_segments = [s for s in url_pattern.split("/") if s and s != "api"]
            "/".join(url_segments[:3])  # First few segments

            # Build query to find similar routes
            module_filter = ""
            if module_path:
                # Convert module path to file path pattern
                path_pattern = module_path.replace(".", "/")
                module_filter = f"AND f.file_path CONTAINS '{path_pattern}'"

            query = f"""
            MATCH (f:Function)
            WHERE f.file_path CONTAINS 'routes'
            AND (f.name CONTAINS '{method.lower()}' OR f.name CONTAINS 'get' OR f.name CONTAINS 'post')
            {module_filter}
            RETURN f.name as name, f.file_path as file_path, f.parameters as parameters
            LIMIT 10
            """
            results = self.client.execute_query(query)

            # Score results by URL similarity
            scored_results = []
            for result in results:
                file_path = result.get("file_path", "")
                if "routes" in file_path.lower():
                    scored_results.append(result)

            return scored_results[:5]  # Return top 5
        except Exception as e:
            logger.error(f"Error finding similar routes: {e}")
            return []

    def get_routes_in_module(self, module_path: str) -> list[dict[str, Any]]:
        """Get all routes in a specific module.

        Args:
            module_path: Module path (e.g., 'routes.account')

        Returns:
            List of route dictionaries
        """
        if not self.is_available or not self.client:
            return []

        try:
            # Convert module path to file path pattern
            path_pattern = module_path.replace(".", "/")
            query = f"""
            MATCH (f:Function)
            WHERE f.file_path CONTAINS '{path_pattern}'
            AND f.file_path CONTAINS 'routes'
            RETURN f.name as name, f.file_path as file_path, f.parameters as parameters
            ORDER BY f.name
            LIMIT 20
            """
            return self.client.execute_query(query)
        except Exception as e:
            logger.error(f"Error getting routes in module: {e}")
            return []

    def get_route_examples(self, route_results: list[dict[str, Any]]) -> list[str]:
        """Get code examples from route function file paths.

        Args:
            route_results: List of route dictionaries with file_path

        Returns:
            List of code examples as strings
        """
        examples = []
        for route in route_results[:3]:  # Limit to 3 examples
            file_path = route.get("file_path")
            if not file_path:
                continue

            # Try to find the actual file
            # file_path might be relative or absolute
            possible_paths = [
                Path(file_path),
                Path(self.routes_dir) / file_path,
                Path("src") / file_path,
            ]

            for path in possible_paths:
                if path.exists() and path.is_file():
                    try:
                        code = path.read_text(encoding="utf-8")
                        # Extract function code (simplified - could be improved)
                        examples.append(code[:2000])  # Limit size
                        break
                    except Exception as e:
                        logger.warning(f"Could not read file {path}: {e}")

        return examples

    def find_exception_classes(self, module_path: str) -> list[dict[str, Any]]:
        """Find exception classes in a module.

        Args:
            module_path: Module path (e.g., 'routes.account')

        Returns:
            List of exception class dictionaries
        """
        if not self.is_available or not self.client:
            return []

        try:
            path_pattern = module_path.replace(".", "/")
            query = f"""
            MATCH (c:Class)
            WHERE c.file_path CONTAINS '{path_pattern}'
            AND (c.name ENDS WITH 'Error' OR c.name ENDS WITH 'Exception')
            RETURN c.name as name, c.file_path as file_path
            ORDER BY c.name
            LIMIT 10
            """
            return self.client.execute_query(query)
        except Exception as e:
            logger.error(f"Error finding exception classes: {e}")
            return []

    def query_codebase(self, question: str) -> str:
        """Use natural language to query codebase patterns.

        This is a simplified implementation. A full CypherQAChain would
        use an LLM to convert questions to Cypher queries.

        Args:
            question: Natural language question about the codebase

        Returns:
            Formatted answer string
        """
        if not self.is_available:
            return "Codebase research is not available (Neo4j not connected)."

        # Simple keyword-based query generation
        # In a full implementation, this would use an LLM to generate Cypher
        question_lower = question.lower()

        if "similar" in question_lower and "route" in question_lower:
            return "Use find_similar_routes() method for finding similar routes."
        elif "exception" in question_lower or "error" in question_lower:
            return "Use find_exception_classes() method for finding exception patterns."
        elif "module" in question_lower:
            return "Use get_routes_in_module() method for finding routes in a module."

        return "Query not recognized. Available methods: find_similar_routes, get_routes_in_module, find_exception_classes."

    def extract_parameter_patterns(
        self, route_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Extract parameter patterns from similar routes.

        Args:
            route_results: List of route dictionaries

        Returns:
            Dictionary with parameter patterns
        """
        patterns: dict[str, Any] = {
            "common_params": [],
            "param_types": {},
            "param_order": [],
        }

        if not route_results:
            return patterns

        # Analyze parameters from route results
        all_params = []
        for route in route_results:
            params = route.get("parameters", [])
            if isinstance(params, list):
                all_params.extend(params)
            elif isinstance(params, str):
                # Try to parse if it's a string representation
                try:
                    import ast

                    parsed = ast.literal_eval(params)
                    if isinstance(parsed, list):
                        all_params.extend(parsed)
                except Exception:
                    pass

        # Count parameter frequency
        param_counts: dict[str, int] = {}
        for param in all_params:
            if isinstance(param, str):
                param_counts[param] = param_counts.get(param, 0) + 1

        # Get most common parameters
        sorted_params = sorted(param_counts.items(), key=lambda x: x[1], reverse=True)
        patterns["common_params"] = [p[0] for p in sorted_params[:10]]

        return patterns
