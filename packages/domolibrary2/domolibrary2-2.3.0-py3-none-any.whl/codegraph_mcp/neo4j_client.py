"""
Neo4j Client for Codebase Graph

Adapted from Graph-Codebase-MCP's neo4j_storage/graph_db.py.
Provides connection management and graph operations including batch inserts,
schema creation, and search capabilities.
"""

from __future__ import annotations

import logging
import os
from typing import Any

try:
    from neo4j import Driver, GraphDatabase
except ImportError:
    GraphDatabase = None  # type: ignore
    Driver = None  # type: ignore

logger = logging.getLogger(__name__)


class Neo4jConnectionError(Exception):
    """Raised when Neo4j connection fails."""

    pass


class Neo4jClient:
    """Neo4j client for codebase graph operations.

    Adapted from Graph-Codebase-MCP's Neo4jDatabase class.
    Handles connection management and provides graph operations.
    """

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str = "neo4j",
    ) -> None:
        """Initialize Neo4j client.

        Args:
            uri: Neo4j connection URI (defaults to NEO4J_URI env var)
            username: Neo4j username (defaults to NEO4J_USERNAME env var)
            password: Neo4j password (defaults to NEO4J_PASSWORD env var)
            database: Neo4j database name (defaults to NEO4J_DATABASE env var or "neo4j")

        Raises:
            Neo4jConnectionError: If Neo4j driver is not installed or connection fails
        """
        if GraphDatabase is None:
            raise Neo4jConnectionError(
                "Neo4j driver not installed. Install with: pip install neo4j"
            )

        self.uri = uri or os.getenv("NEO4J_URI", "")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver: Driver | None = None

        if not self.uri:
            raise Neo4jConnectionError(
                "NEO4J_URI not provided. Set in environment or pass as argument."
            )

        if not self.password:
            raise Neo4jConnectionError(
                "NEO4J_PASSWORD not provided. Set in environment or pass as argument."
            )

        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.username, self.password)
            )
            logger.info(f"Successfully connected to Neo4j database: {self.uri}")
        except Exception as e:
            logger.error(f"Error connecting to Neo4j database: {e}")
            raise Neo4jConnectionError(f"Failed to connect to Neo4j: {e}") from e

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j database connection")

    def verify_connection(self) -> bool:
        """Verify database connection is valid.

        Returns:
            True if connection is valid, False otherwise
        """
        if not self.driver:
            return False

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as n").single()
                return result is not None and result.get("n") == 1
        except Exception as e:
            logger.error(f"Error verifying Neo4j connection: {e}")
            return False

    def clear_database(self) -> None:
        """Clear all nodes and relationships from database."""
        if not self.driver:
            raise Neo4jConnectionError("No database connection")

        try:
            with self.driver.session(database=self.database) as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Cleared database")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise

    def create_schema_constraints(self) -> None:
        """Create graph model constraints and indexes."""
        if not self.driver:
            raise Neo4jConnectionError("No database connection")

        try:
            with self.driver.session(database=self.database) as session:
                # Check if constraints already exist
                existing_constraints = session.run("SHOW CONSTRAINTS").data()

                # Check if specific constraint exists
                constraint_exists = False
                for constraint in existing_constraints:
                    if (
                        "name" in constraint
                        and "file_path_constraint" in constraint["name"]
                    ):
                        constraint_exists = True
                        break

                # Only create if constraint doesn't exist
                if not constraint_exists:
                    try:
                        session.run(
                            """
                            CREATE CONSTRAINT file_path_constraint
                            FOR (f:File) REQUIRE f.path IS UNIQUE
                            """
                        )
                        logger.info("Created File.path uniqueness constraint")
                    except Exception as constraint_error:
                        logger.warning(
                            f"Warning creating constraint: {constraint_error}"
                        )

                # Check if indexes already exist
                existing_indexes = session.run("SHOW INDEXES").data()
                index_names = [
                    idx.get("name", "") for idx in existing_indexes if "name" in idx
                ]

                # Create indexes for nodes
                index_configs = [
                    {"name": "file_name_idx", "label": "File", "property": "name"},
                    {"name": "class_name_idx", "label": "Class", "property": "name"},
                    {
                        "name": "function_name_idx",
                        "label": "Function",
                        "property": "name",
                    },
                    {"name": "method_name_idx", "label": "Method", "property": "name"},
                    {
                        "name": "variable_name_idx",
                        "label": "Variable",
                        "property": "name",
                    },
                    {"name": "module_name_idx", "label": "Module", "property": "name"},
                ]

                for config in index_configs:
                    if config["name"] not in index_names:
                        try:
                            session.run(
                                f"CREATE INDEX {config['name']} FOR (n:{config['label']}) ON (n.{config['property']})"
                            )
                            logger.info(f"Created index: {config['name']}")
                        except Exception as index_error:
                            logger.warning(
                                f"Warning creating index {config['name']}: {index_error}"
                            )

                logger.info("Completed graph model constraint and index check/creation")
        except Exception as e:
            logger.error(f"Error creating constraints and indexes: {e}")
            raise

    def batch_create_nodes(self, nodes: list[dict[str, Any]]) -> None:
        """Batch create nodes.

        Args:
            nodes: List of nodes, each node is a dict with 'labels' and 'properties'
                   Format: [{'labels': ['Label1', 'Label2'], 'properties': {...}}]
        """
        if not nodes:
            return

        if not self.driver:
            raise Neo4jConnectionError("No database connection")

        try:
            with self.driver.session(database=self.database) as session:
                batch_size = 1000  # Set appropriate batch size

                for i in range(0, len(nodes), batch_size):
                    batch = nodes[i : i + batch_size]
                    created = 0

                    # Process each node individually
                    for node in batch:
                        labels = node["labels"]
                        properties = node["properties"]

                        # Build label string, e.g., `:Label1:Label2`
                        labels_str = "".join([f":{label}" for label in labels])

                        # Build property string, e.g., `{id: 'test1', name: 'Test 1'}`
                        props_str = "{"
                        props_str += ", ".join(
                            [f"{k}: ${k}" for k in properties.keys()]
                        )
                        props_str += "}"

                        # Create node query
                        query = f"CREATE (n{labels_str} {props_str}) RETURN n"

                        # Execute query
                        session.run(query, properties)
                        created += 1

                    logger.info(f"Created {created} nodes")
        except Exception as e:
            logger.error(f"Error batch creating nodes: {e}")
            raise

    def batch_create_relationships(self, relationships: list[dict[str, Any]]) -> None:
        """Batch create relationships.

        Args:
            relationships: List of relationships, each is a dict with:
                          'start_node_id', 'end_node_id', 'type', 'properties'
        """
        if not relationships:
            return

        if not self.driver:
            raise Neo4jConnectionError("No database connection")

        try:
            with self.driver.session(database=self.database) as session:
                batch_size = 1000  # Set appropriate batch size

                for i in range(0, len(relationships), batch_size):
                    batch = relationships[i : i + batch_size]
                    processed = 0

                    # Process each relationship individually
                    for rel in batch:
                        start_id = rel["start_node_id"]
                        end_id = rel["end_node_id"]
                        rel_type = rel["type"]
                        properties = rel.get("properties") or {}

                        # Use parameterized query
                        query = f"""
                        MATCH (start {{id: $start_id}})
                        MATCH (end {{id: $end_id}})
                        CREATE (start)-[r:{rel_type}]->(end)
                        SET r = $props
                        RETURN r
                        """

                        params = {
                            "start_id": start_id,
                            "end_id": end_id,
                            "props": properties,
                        }

                        session.run(query, params)
                        processed += 1

                    logger.info(f"Processed {processed} relationships")
        except Exception as e:
            logger.error(f"Error batch creating relationships: {e}")
            raise

    def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self.driver:
            raise Neo4jConnectionError("No database connection")

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}")
            raise

    def execute_write(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a write transaction.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self.driver:
            raise Neo4jConnectionError("No database connection")

        try:
            with self.driver.session(database=self.database) as session:
                result = session.execute_write(
                    lambda tx: list(tx.run(query, parameters or {}))
                )
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error executing write transaction: {e}")
            raise

    def __enter__(self) -> Neo4jClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
