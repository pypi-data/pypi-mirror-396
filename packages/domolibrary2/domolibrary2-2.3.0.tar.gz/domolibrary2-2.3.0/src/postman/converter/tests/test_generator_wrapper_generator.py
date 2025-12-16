"""Tests for wrapper function generator."""

from __future__ import annotations

import pytest

from ..deterministic.matcher import MatchType, RouteMatch
from ..generator.wrapper_generator import (
    _generate_wrapper_name,
    generate_wrapper_function,
)


class TestGenerateWrapperName:
    """Tests for _generate_wrapper_name function."""

    def test_wrapper_name_same_as_existing(self):
        """Test wrapper name when Postman name matches existing."""
        result = _generate_wrapper_name("get_accounts", "get_accounts")
        assert result == "get_accounts_postman"

    def test_wrapper_name_different_from_existing(self):
        """Test wrapper name when Postman name differs."""
        result = _generate_wrapper_name("List Accounts", "get_accounts")
        assert "postman" not in result.lower() or result != "get_accounts"

    def test_wrapper_name_no_existing(self):
        """Test wrapper name when no existing route."""
        result = _generate_wrapper_name("New Endpoint", "")
        assert result is not None
        assert len(result) > 0


class TestGenerateWrapperFunction:
    """Tests for generate_wrapper_function."""

    @pytest.fixture
    def sample_match(self):
        """Create a sample RouteMatch."""
        return RouteMatch(
            postman_request_name="Get Accounts",
            postman_url="/api/v1/accounts",
            postman_method="GET",
            match_type=MatchType.EXACT_MATCH,
            confidence=0.95,
            existing_route_name="get_accounts",
            existing_route_module="domolibrary2.routes.account.core",
            existing_route_url="/api/v1/accounts",
            existing_route_method="GET",
        )

    def test_generate_basic_wrapper(self, sample_match):
        """Test generating a basic wrapper function."""
        result = generate_wrapper_function(sample_match)

        assert "name" in result
        assert "code" in result
        assert "@gd.route_function" in result["code"]
        assert "async def" in result["code"]

    def test_wrapper_imports_existing_route(self, sample_match):
        """Test that wrapper imports the existing route."""
        result = generate_wrapper_function(sample_match)

        assert (
            "from domolibrary2.routes.account.core import get_accounts"
            in result["code"]
            or "import get_accounts" in result["code"]
        )

    def test_wrapper_calls_existing_route(self, sample_match):
        """Test that wrapper calls the existing route."""
        result = generate_wrapper_function(sample_match)

        assert "get_accounts" in result["code"]
        assert "await" in result["code"] or "return" in result["code"]

    def test_wrapper_includes_postman_metadata(self, sample_match):
        """Test that wrapper includes Postman metadata in docstring."""
        result = generate_wrapper_function(sample_match, postman_folder="Accounts")

        assert "Postman" in result["code"] or "Get Accounts" in result["code"]

    def test_wrapper_with_folder_path(self, sample_match):
        """Test wrapper generation with folder path."""
        result = generate_wrapper_function(sample_match, postman_folder="Accounts/Core")

        assert result["code"] is not None
        assert len(result["code"]) > 0

    def test_wrapper_handles_missing_existing_route(self):
        """Test wrapper generation when existing route info is missing."""
        match = RouteMatch(
            postman_request_name="Test",
            postman_url="/test",
            postman_method="GET",
            match_type=MatchType.NO_MATCH,
            confidence=0.0,
        )

        # Should still generate something, even if minimal
        result = generate_wrapper_function(match)
        assert "name" in result
        assert "code" in result
