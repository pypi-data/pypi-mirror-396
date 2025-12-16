"""
Entity Analyzer

Analyzes DomoEntity classes and their relationships.
"""

from __future__ import annotations

from typing import Any

from ..neo4j_client import Neo4jClient


class EntityAnalyzer:
    """Analyzer for DomoEntity patterns."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize entity analyzer.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client

    def get_all_entities(self) -> list[dict[str, Any]]:
        """Get all DomoEntity classes.

        Returns:
            List of entity nodes
        """
        query = """
        MATCH (e:DomoEntity)
        RETURN e
        ORDER BY e.name
        """
        return self.client.execute_query(query)

    def get_entity_hierarchy(self, entity_name: str) -> list[dict[str, Any]]:
        """Get inheritance hierarchy for an entity.

        Args:
            entity_name: Name of entity class

        Returns:
            List of hierarchy nodes
        """
        query = """
        MATCH (e:DomoEntity {name: $entity_name})
        OPTIONAL MATCH path = (e)-[:EXTENDS*]->(parent)
        RETURN e, path
        """
        return self.client.execute_query(query, {"entity_name": entity_name})

    def get_entity_relationships(self, entity_id: str) -> list[dict[str, Any]]:
        """Get relationships for an entity.

        Args:
            entity_id: Entity node ID

        Returns:
            List of relationship nodes
        """
        query = """
        MATCH (e:DomoEntity {id: $entity_id})
        OPTIONAL MATCH (e)-[r]->(related)
        RETURN e, collect(DISTINCT {rel: r, node: related}) as relationships
        """
        return self.client.execute_query(query, {"entity_id": entity_id})
