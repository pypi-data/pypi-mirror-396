"""
Documentation Generator

Generates dependency diagrams and architecture overviews from the graph.
"""

from __future__ import annotations

from .neo4j_client import Neo4jClient


class CodeGraphDocs:
    """Documentation generator for codebase graph."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize documentation generator.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client

    def generate_dependency_diagram(self, node_id: str, max_depth: int = 3) -> str:
        """Generate Mermaid dependency diagram.

        Args:
            node_id: Starting node ID
            max_depth: Maximum depth to traverse

        Returns:
            Mermaid diagram string
        """
        if not node_id:
            # Generate overview diagram
            query = """
            MATCH (n)-[r]->(m)
            WHERE n.node_type IN ['Class', 'Function', 'Module']
            RETURN n, r, m
            LIMIT 50
            """
        else:
            query = f"""
            MATCH path = (start {{id: '{node_id}'}})-[*1..{max_depth}]->(end)
            RETURN path
            LIMIT 100
            """

        results = self.client.execute_query(query)

        # Build Mermaid diagram
        lines = ["graph TD"]
        node_ids: set[str] = set()
        edges: set[tuple[str, str, str]] = set()

        for result in results:
            if "path" in result:
                # Handle path result (for node_id queries)
                # Neo4j path objects need special handling
                # For now, use a simpler approach
                continue
            else:
                # Handle direct node-relationship-node results
                start_node = result.get("n")
                rel = result.get("r")
                end_node = result.get("m")

                if start_node and end_node:
                    start_id = str(start_node.get("id", "")) or start_node.get(
                        "name", "unknown"
                    )
                    end_id = str(end_node.get("id", "")) or end_node.get(
                        "name", "unknown"
                    )
                    rel_type = rel.get("type", "RELATES") if rel else "RELATES"

                    # Sanitize IDs for Mermaid
                    start_id_clean = start_id.replace(" ", "_").replace("-", "_")
                    end_id_clean = end_id.replace(" ", "_").replace("-", "_")

                    if start_id_clean not in node_ids:
                        node_label = start_node.get("name", start_id)
                        node_type = start_node.get("node_type", "Node")
                        lines.append(
                            f'    {start_id_clean}["{node_label}<br/>{node_type}"]'
                        )
                        node_ids.add(start_id_clean)

                    if end_id_clean not in node_ids:
                        node_label = end_node.get("name", end_id)
                        node_type = end_node.get("node_type", "Node")
                        lines.append(
                            f'    {end_id_clean}["{node_label}<br/>{node_type}"]'
                        )
                        node_ids.add(end_id_clean)

                    edge_key = (start_id_clean, end_id_clean, rel_type)
                    if edge_key not in edges:
                        lines.append(
                            f"    {start_id_clean} -->|{rel_type}| {end_id_clean}"
                        )
                        edges.add(edge_key)

        if len(lines) == 1:  # Only header, no nodes
            lines.append("    A[No relationships found]")

        return "\n".join(lines)

    def generate_architecture_overview(self) -> str:
        """Generate architecture overview from graph.

        Returns:
            Markdown string with architecture overview
        """
        # Get module statistics
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (f)-[:CONTAINS]->(entity)
        WITH f, count(entity) as entity_count
        RETURN f.file_path, entity_count
        ORDER BY entity_count DESC
        LIMIT 20
        """
        results = self.client.execute_query(query)

        lines = ["# Architecture Overview\n"]
        lines.append("## Top Modules by Entity Count\n")
        lines.append("| File | Entity Count |")
        lines.append("|------|--------------|")

        for result in results:
            file_path = result.get("f", {}).get("file_path", "unknown")
            count = result.get("entity_count", 0)
            lines.append(f"| {file_path} | {count} |")

        return "\n".join(lines)

    def export_to_mermaid(self, output_path: str) -> None:
        """Export graph to Mermaid diagram file.

        Args:
            output_path: Path to output file
        """
        # Simplified implementation
        diagram = self.generate_dependency_diagram("", max_depth=2)
        with open(output_path, "w") as f:
            f.write(diagram)
