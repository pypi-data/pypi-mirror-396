"""
Codebase Scanner

Scans codebase directory and processes Python files using AST parser.
"""

from __future__ import annotations

from pathlib import Path

from .ast_parser import ASTParser, CodeNode, CodeRelation
from .custom.domo_visitor import extend_parser_with_domo_patterns


class CodeGraphScanner:
    """Scanner for processing codebase and extracting graph data."""

    def __init__(self, root_directory: str | Path) -> None:
        """Initialize scanner.

        Args:
            root_directory: Root directory to scan
        """
        self.root_directory = Path(root_directory)
        self.parser = ASTParser()
        # Extend parser with domolibrary2-specific patterns
        extend_parser_with_domo_patterns(self.parser)

    def scan(self) -> tuple[dict[str, CodeNode], list[CodeRelation]]:
        """Scan codebase and extract nodes and relationships.

        Returns:
            Tuple of (nodes dictionary, relations list)
        """
        if not self.root_directory.exists():
            raise ValueError(f"Directory does not exist: {self.root_directory}")

        nodes, relations = self.parser.parse_directory(str(self.root_directory))
        return nodes, relations

    def scan_file(
        self, file_path: str | Path
    ) -> tuple[dict[str, CodeNode], list[CodeRelation]]:
        """Scan a single file.

        Args:
            file_path: Path to Python file

        Returns:
            Tuple of (nodes dictionary, relations list)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        nodes, relations = self.parser.parse_file(str(file_path), build_index=False)
        return nodes, relations
