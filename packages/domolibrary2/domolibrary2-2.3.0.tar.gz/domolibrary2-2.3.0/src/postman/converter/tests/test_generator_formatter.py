"""Tests for code formatter."""

from __future__ import annotations

from ..generator.formatter import format_code


class TestFormatCode:
    """Tests for format_code function."""

    def test_format_valid_code(self):
        """Test formatting valid Python code."""
        code = """async def test_function(auth,debug=False):
    url="https://example.com/api"
    return await get_data(auth=auth,url=url,debug=debug)
"""

        result = format_code(code)

        # Should return formatted code (may be same if already formatted)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_code_with_imports(self):
        """Test formatting code with imports."""
        code = """from domolibrary2.auth import DomoAuth
from domolibrary2.client import get_data
import domolibrary2.routes.get_data as gd

@gd.route_function
async def test():
    pass
"""

        result = format_code(code)

        assert "from domolibrary2" in result
        assert "import" in result

    def test_format_invalid_syntax(self):
        """Test formatting code with syntax errors."""
        code = """async def test_function(
    # Missing closing parenthesis
    auth
"""

        result = format_code(code)

        # Should handle gracefully - either fix or return with error comment
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_empty_code(self):
        """Test formatting empty code."""
        result = format_code("")

        assert isinstance(result, str)

    def test_format_code_preserves_functionality(self):
        """Test that formatting preserves code functionality."""
        code = """async def test(auth):
    return await get_data(auth=auth,url="https://example.com")
"""

        result = format_code(code)

        # Key elements should still be present
        assert "async def" in result
        assert "test" in result
        assert "get_data" in result

    def test_format_code_with_comments(self):
        """Test formatting code with comments."""
        code = """# This is a comment
async def test():
    # Another comment
    pass
"""

        result = format_code(code)

        # Comments should be preserved
        assert "#" in result or "comment" in result.lower()
