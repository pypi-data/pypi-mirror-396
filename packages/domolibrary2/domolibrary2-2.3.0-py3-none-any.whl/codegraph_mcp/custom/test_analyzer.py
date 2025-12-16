"""
Test Analyzer

Analyzes test files and their relationships to code under test.
"""

from __future__ import annotations

from typing import Any

from ..neo4j_client import Neo4jClient


class TestAnalyzer:
    """Analyzer for test patterns."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        """Initialize test analyzer.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client

    def get_all_tests(self) -> list[dict[str, Any]]:
        """Get all test files.

        Returns:
            List of test file nodes
        """
        query = """
        MATCH (f:File)
        WHERE f.file_path CONTAINS 'test' OR f.name STARTS WITH 'test_'
        RETURN f
        ORDER BY f.file_path
        """
        return self.client.execute_query(query)

    def get_tests_for_code(self, code_file_path: str) -> list[dict[str, Any]]:
        """Get tests that test a specific code file.

        Args:
            code_file_path: Path to code file

        Returns:
            List of test nodes
        """
        # Extract module name from file path
        import os

        module_name = os.path.splitext(os.path.basename(code_file_path))[0]

        query = """
        MATCH (test:File)
        WHERE (test.file_path CONTAINS 'test' OR test.name STARTS WITH 'test_')
        AND test.file_path CONTAINS $module_name
        RETURN test
        ORDER BY test.file_path
        """
        return self.client.execute_query(query, {"module_name": module_name})

    def get_code_under_test(self, test_file_path: str) -> list[dict[str, Any]]:
        """Get code that is tested by a test file.

        Args:
            test_file_path: Path to test file

        Returns:
            List of code nodes being tested
        """
        # Extract module name from test file path
        import os

        test_name = os.path.basename(test_file_path)
        # Remove 'test_' prefix and '.py' suffix
        if test_name.startswith("test_"):
            module_name = (
                test_name[5:-3] if test_name.endswith(".py") else test_name[5:]
            )
        else:
            module_name = os.path.splitext(test_name)[0]

        query = """
        MATCH (code:File)
        WHERE code.name = $module_name OR code.name = $module_name + '.py'
        RETURN code
        """
        return self.client.execute_query(query, {"module_name": module_name})
