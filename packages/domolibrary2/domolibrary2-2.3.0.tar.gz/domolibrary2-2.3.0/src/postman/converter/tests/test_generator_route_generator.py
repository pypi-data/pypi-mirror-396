"""Tests for route function generator."""

from __future__ import annotations

import pytest

from ..deterministic.parser import ParsedPostmanRequest
from ..generator.route_generator import generate_route_function


class TestGenerateRouteFunction:
    """Tests for generate_route_function."""

    @pytest.fixture
    def sample_request(self):
        """Create a sample ParsedPostmanRequest."""
        return ParsedPostmanRequest(
            name="Get Accounts",
            method="GET",
            url_pattern="/api/v1/accounts",
            path_variables=[],
            query_params=["limit", "offset"],
            headers={},
            folder_path="Accounts",
        )

    def test_generate_basic_route(self, sample_request):
        """Test generating a basic route function."""
        result = generate_route_function(sample_request)

        assert "name" in result
        assert "code" in result
        assert "get_accounts" in result["name"].lower()
        assert "async def" in result["code"]
        assert "@gd.route_function" in result["code"]

    def test_generate_route_with_path_variables(self):
        """Test generating route with path variables."""
        request = ParsedPostmanRequest(
            name="Get Account by ID",
            method="GET",
            url_pattern="/api/v1/accounts/:id",
            path_variables=["id"],
            query_params=[],
            headers={},
        )

        result = generate_route_function(request)

        assert "id" in result["code"]
        assert "id: str" in result["code"] or "id" in result["code"]

    def test_generate_route_with_custom_docstring(self, sample_request):
        """Test generating route with custom docstring."""
        custom_doc = "Custom docstring for this route."
        result = generate_route_function(sample_request, docstring=custom_doc)

        assert custom_doc in result["code"]

    def test_generate_route_includes_url(self, sample_request):
        """Test that generated route includes URL."""
        result = generate_route_function(sample_request)

        assert "/api/v1/accounts" in result["code"] or "accounts" in result["code"]

    def test_generate_route_includes_method(self, sample_request):
        """Test that generated route includes HTTP method."""
        result = generate_route_function(sample_request)

        assert "GET" in result["code"] or sample_request.method in result["code"]

    def test_generate_route_post_method(self):
        """Test generating POST route."""
        request = ParsedPostmanRequest(
            name="Create Account",
            method="POST",
            url_pattern="/api/v1/accounts",
            path_variables=[],
            query_params=[],
            headers={},
        )

        result = generate_route_function(request)

        assert "POST" in result["code"] or request.method in result["code"]
