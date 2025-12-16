"""
Custom AST Visitors for domolibrary2 Patterns

Extends AST parser to detect domolibrary2-specific patterns:
- Route functions with RouteContext
- DomoEntity classes
- MCP tool decorators
- Test relationships
"""

from __future__ import annotations

import ast

from ..ast_parser import ASTParser, CodeNode, CodeRelation


class DomoASTVisitor(ast.NodeVisitor):
    """Custom AST visitor for domolibrary2 patterns."""

    def __init__(self, parser: ASTParser) -> None:
        """Initialize visitor.

        Args:
            parser: ASTParser instance to extend
        """
        self.parser = parser
        self.route_functions: list[str] = []
        self.mcp_tools: list[str] = []
        self.domo_entities: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition to detect routes and MCP tools.

        Args:
            node: AST FunctionDef node
        """
        # Check for RouteContext parameter (route functions)
        has_route_context = False
        for arg in node.args.args:
            if arg.annotation:
                # Check if annotation is RouteContext
                if isinstance(arg.annotation, ast.Name):
                    if arg.annotation.id == "RouteContext":
                        has_route_context = True
                elif isinstance(arg.annotation, ast.Attribute):
                    if arg.annotation.attr == "RouteContext":
                        has_route_context = True

        if has_route_context:
            node_id = self.parser._get_node_id(
                "Function", node.name, self.parser.current_file, node.lineno
            )
            self.route_functions.append(node_id)

            # Create Route node
            route_node = CodeNode(
                node_id=f"route:{node_id}",
                node_type="Route",
                name=node.name,
                file_path=self.parser.current_file,
                line_no=node.lineno,
                end_line_no=getattr(node, "end_lineno", None),
            )
            self.parser.nodes[route_node.node_id] = route_node

            # Create relationship from function to route
            self.parser.relations.append(
                CodeRelation(
                    source_id=node_id,
                    target_id=route_node.node_id,
                    relation_type="HAS_ROUTE_CONTEXT",
                )
            )

        # Check for MCP tool decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if decorator.attr == "tool":
                    # Check if it's mcp.tool
                    if isinstance(decorator.value, ast.Name):
                        if decorator.value.id == "mcp":
                            node_id = self.parser._get_node_id(
                                "Function",
                                node.name,
                                self.parser.current_file,
                                node.lineno,
                            )
                            self.mcp_tools.append(node_id)

                            # Create MCPTool node
                            mcp_node = CodeNode(
                                node_id=f"mcptool:{node_id}",
                                node_type="MCPTool",
                                name=node.name,
                                file_path=self.parser.current_file,
                                line_no=node.lineno,
                                end_line_no=getattr(node, "end_lineno", None),
                            )
                            self.parser.nodes[mcp_node.node_id] = mcp_node

                            # Create relationship
                            self.parser.relations.append(
                                CodeRelation(
                                    source_id=node_id,
                                    target_id=mcp_node.node_id,
                                    relation_type="EXPOSES_MCP_TOOL",
                                )
                            )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition to detect DomoEntity classes.

        Args:
            node: AST ClassDef node
        """

        # Helper function to check if a base class is DomoEntity or DomoEntity_w_Lineage
        def is_domo_entity_base(base: ast.AST) -> bool:
            """Check if base class is DomoEntity or DomoEntity_w_Lineage."""
            if isinstance(base, ast.Name):
                base_name = base.id
                # Direct name match
                if base_name in ("DomoEntity", "DomoEntity_w_Lineage"):
                    return True
                # Check if it's imported
                if base_name in self.parser.imports:
                    imported = self.parser.imports[base_name]
                    return (
                        imported.endswith(".DomoEntity")
                        or imported.endswith(".DomoEntity_w_Lineage")
                        or imported in ("DomoEntity", "DomoEntity_w_Lineage")
                    )
            elif isinstance(base, ast.Attribute):
                # Handle attribute access like entities.DomoEntity_w_Lineage
                base_name = base.attr
                if base_name in ("DomoEntity", "DomoEntity_w_Lineage"):
                    # Check if the module is imported
                    if isinstance(base.value, ast.Name):
                        module_name = base.value.id
                        if module_name in self.parser.imports:
                            imported = self.parser.imports[module_name]
                            # Check if the imported module contains DomoEntity classes
                            return (
                                "entities" in imported
                                or "base" in imported
                                or imported.endswith(".DomoEntity")
                                or imported.endswith(".DomoEntity_w_Lineage")
                            )
                    return True
            return False

        # Check if class inherits from DomoEntity or DomoEntity_w_Lineage
        for base in node.bases:
            if is_domo_entity_base(base):
                node_id = self.parser._get_node_id(
                    "Class", node.name, self.parser.current_file, node.lineno
                )
                self.domo_entities.append(node_id)

                # Create DomoEntity node
                entity_node = CodeNode(
                    node_id=f"entity:{node_id}",
                    node_type="DomoEntity",
                    name=node.name,
                    file_path=self.parser.current_file,
                    line_no=node.lineno,
                    end_line_no=getattr(node, "end_lineno", None),
                )
                self.parser.nodes[entity_node.node_id] = entity_node

                # Create relationship
                self.parser.relations.append(
                    CodeRelation(
                        source_id=node_id,
                        target_id=entity_node.node_id,
                        relation_type="IS_DOMO_ENTITY",
                    )
                )
                # Only need to mark once, so break after first match
                break

        self.generic_visit(node)


def extend_parser_with_domo_patterns(parser: ASTParser) -> None:
    """Extend AST parser with domolibrary2-specific pattern detection.

    Args:
        parser: ASTParser instance to extend
    """
    visitor = DomoASTVisitor(parser)

    # Override parse_file to add custom visitor after standard parsing
    original_parse_file = parser.parse_file

    def enhanced_parse_file(
        file_path: str, build_index: bool = False
    ) -> tuple[dict[str, CodeNode], list[CodeRelation]]:
        """Enhanced file parsing with domolibrary2 patterns."""
        # First do standard parsing
        nodes, relations = original_parse_file(file_path, build_index)

        # Then visit with custom visitor to detect domolibrary2 patterns
        try:
            import ast

            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()
                tree = ast.parse(file_content)
                visitor.visit(tree)
        except Exception as e:
            print(f"Error in custom visitor for {file_path}: {e}")

        return parser.nodes, parser.relations

    parser.parse_file = enhanced_parse_file
