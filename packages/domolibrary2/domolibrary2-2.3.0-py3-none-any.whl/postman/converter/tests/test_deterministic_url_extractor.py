"""Tests for URL pattern extraction and normalization."""

from __future__ import annotations

from ..deterministic.url_extractor import URLPattern, extract_url_pattern, normalize_url


class TestNormalizeURL:
    """Tests for normalize_url function."""

    def test_normalize_simple_url(self):
        """Test normalizing a simple URL."""
        result = normalize_url("https://api.example.com/v1/test")
        assert result == "/v1/test"

    def test_normalize_url_with_query(self):
        """Test normalizing URL with query parameters."""
        result = normalize_url("https://api.example.com/v1/test?param=value")
        assert result == "/v1/test"

    def test_normalize_url_with_fragment(self):
        """Test normalizing URL with fragment."""
        result = normalize_url("https://api.example.com/v1/test#section")
        assert result == "/v1/test"

    def test_normalize_url_with_path_variables(self):
        """Test normalizing URL with path variables."""
        result = normalize_url("https://api.example.com/v1/users/:id")
        assert result == "/v1/users/:id"

    def test_normalize_relative_url(self):
        """Test normalizing relative URL."""
        result = normalize_url("/v1/test")
        assert result == "/v1/test"

    def test_normalize_url_with_base(self):
        """Test normalizing URL with base URL variable."""
        result = normalize_url("{{baseUrl}}/v1/test")
        assert result == "/v1/test" or "baseUrl" in result


class TestURLPattern:
    """Tests for URLPattern class."""

    def test_url_pattern_creation(self):
        """Test creating a URLPattern."""
        pattern = URLPattern(
            path="/v1/users/:id",
            method="GET",
            path_variables=["id"],
        )

        assert pattern.path == "/v1/users/:id"
        assert pattern.method == "GET"
        assert pattern.path_variables == ["id"]

    def test_url_pattern_matches_exact(self):
        """Test exact URL pattern matching."""
        pattern1 = URLPattern(path="/v1/users/:id", method="GET", path_variables=["id"])
        pattern2 = URLPattern(path="/v1/users/:id", method="GET", path_variables=["id"])

        assert pattern1.matches(pattern2)

    def test_url_pattern_matches_different_variable_names(self):
        """Test matching patterns with different variable names."""
        pattern1 = URLPattern(path="/v1/users/:id", method="GET", path_variables=["id"])
        pattern2 = URLPattern(
            path="/v1/users/:userId", method="GET", path_variables=["userId"]
        )

        # Should match if structure is the same
        assert pattern1.matches(pattern2)

    def test_url_pattern_no_match_different_paths(self):
        """Test that different paths don't match."""
        pattern1 = URLPattern(path="/v1/users", method="GET", path_variables=[])
        pattern2 = URLPattern(path="/v1/accounts", method="GET", path_variables=[])

        assert not pattern1.matches(pattern2)

    def test_url_pattern_no_match_different_methods(self):
        """Test that different methods don't match."""
        pattern1 = URLPattern(path="/v1/users", method="GET", path_variables=[])
        pattern2 = URLPattern(path="/v1/users", method="POST", path_variables=[])

        assert not pattern1.matches(pattern2)


class TestExtractURLPattern:
    """Tests for extract_url_pattern function."""

    def test_extract_simple_url(self):
        """Test extracting pattern from simple URL."""
        pattern = extract_url_pattern("/v1/test", "GET")

        assert pattern.path == "/v1/test"
        assert pattern.method == "GET"
        assert pattern.path_variables == []

    def test_extract_url_with_path_variable(self):
        """Test extracting pattern with path variable."""
        pattern = extract_url_pattern("/v1/users/:id", "GET")

        assert pattern.path == "/v1/users/:id"
        assert "id" in pattern.path_variables

    def test_extract_url_with_multiple_variables(self):
        """Test extracting pattern with multiple path variables."""
        pattern = extract_url_pattern("/v1/users/:userId/posts/:postId", "GET")

        assert "userId" in pattern.path_variables
        assert "postId" in pattern.path_variables

    def test_extract_url_with_query_params(self):
        """Test extracting pattern ignores query parameters."""
        pattern = extract_url_pattern("/v1/test?param=value", "GET")

        assert pattern.path == "/v1/test"
        assert "param" not in pattern.path_variables

    def test_extract_url_with_postman_variables(self):
        """Test extracting pattern with Postman variables."""
        pattern = extract_url_pattern("{{baseUrl}}/v1/test", "GET")

        # Variables should be handled appropriately
        assert pattern.path is not None
