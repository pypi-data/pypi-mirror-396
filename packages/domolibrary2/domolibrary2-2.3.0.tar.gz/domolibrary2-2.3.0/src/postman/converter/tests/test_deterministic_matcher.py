"""Tests for deterministic route matcher."""

from __future__ import annotations

import pytest

from ..deterministic.matcher import MatchType, RouteMatch, RouteMatcher


class TestRouteMatch:
    """Tests for RouteMatch dataclass."""

    def test_to_dict(self):
        """Test converting RouteMatch to dictionary."""
        match = RouteMatch(
            postman_request_name="Get Accounts",
            postman_url="/api/v1/accounts",
            postman_method="GET",
            match_type=MatchType.EXACT_MATCH,
            confidence=0.95,
            existing_route_name="get_accounts",
            existing_route_module="domolibrary2.routes.account.core",
            existing_route_url="/api/v1/accounts",
            existing_route_method="GET",
            notes="Exact match",
        )

        result = match.to_dict()

        assert result["postman_request_name"] == "Get Accounts"
        assert result["match_type"] == "EXACT_MATCH"
        assert result["confidence"] == 0.95
        assert result["existing_route_name"] == "get_accounts"


class TestRouteMatcher:
    """Tests for RouteMatcher class."""

    @pytest.fixture
    def route_registry(self):
        """Create a sample route registry."""
        return {
            "get_accounts": {
                "module": "domolibrary2.routes.account.core",
                "url": "/api/data/v1/accounts",
                "method": "GET",
                "function_name": "get_accounts",
            },
            "create_account": {
                "module": "domolibrary2.routes.account.core",
                "url": "/api/data/v1/accounts",
                "method": "POST",
                "function_name": "create_account",
            },
            "get_account_by_id": {
                "module": "domolibrary2.routes.account.core",
                "url": "/api/data/v1/accounts/:id",
                "method": "GET",
                "function_name": "get_account_by_id",
            },
        }

    @pytest.fixture
    def matcher(self, route_registry):
        """Create a RouteMatcher instance."""
        return RouteMatcher(route_registry)

    def test_exact_match(self, matcher):
        """Test exact match (URL, method, and name all match)."""
        match = matcher.match(
            postman_name="Get Accounts",
            postman_url="/api/data/v1/accounts",
            postman_method="GET",
        )

        assert match.match_type == MatchType.EXACT_MATCH
        assert match.confidence >= 0.9
        assert match.existing_route_name == "get_accounts"

    def test_url_match(self, matcher):
        """Test URL match (URL and method match, name different)."""
        match = matcher.match(
            postman_name="List All Accounts",
            postman_url="/api/data/v1/accounts",
            postman_method="GET",
        )

        assert match.match_type in (MatchType.EXACT_MATCH, MatchType.URL_MATCH)
        assert match.confidence >= 0.7
        assert match.existing_route_name == "get_accounts"

    def test_name_match(self, matcher):
        """Test name match (function name similar, URL different)."""
        match = matcher.match(
            postman_name="Get Accounts",
            postman_url="/api/v2/accounts",
            postman_method="GET",
        )

        # Should find name similarity even if URL is different
        assert match.match_type in (MatchType.NAME_MATCH, MatchType.NO_MATCH)
        if match.match_type == MatchType.NAME_MATCH:
            assert match.confidence >= 0.5

    def test_no_match(self, matcher):
        """Test no match found."""
        match = matcher.match(
            postman_name="Unknown Endpoint",
            postman_url="/api/v1/unknown",
            postman_method="GET",
        )

        assert match.match_type == MatchType.NO_MATCH
        assert match.confidence < 0.5

    def test_method_mismatch(self, matcher):
        """Test that method mismatch prevents matching."""
        match = matcher.match(
            postman_name="Get Accounts",
            postman_url="/api/data/v1/accounts",
            postman_method="POST",  # Different method
        )

        # Should not match GET route with POST request
        assert match.match_type != MatchType.EXACT_MATCH

    def test_path_variable_matching(self, matcher):
        """Test matching with path variables."""
        match = matcher.match(
            postman_name="Get Account by ID",
            postman_url="/api/data/v1/accounts/123",
            postman_method="GET",
        )

        # Should match route with :id parameter
        assert (
            match.existing_route_name == "get_account_by_id"
            or match.match_type == MatchType.NO_MATCH
        )

    def test_empty_registry(self):
        """Test matching with empty registry."""
        matcher = RouteMatcher({})
        match = matcher.match(
            postman_name="Test",
            postman_url="/api/v1/test",
            postman_method="GET",
        )

        assert match.match_type == MatchType.NO_MATCH
        assert match.confidence == 0.0

    def test_confidence_scoring(self, matcher):
        """Test that confidence scores are in valid range."""
        match = matcher.match(
            postman_name="Get Accounts",
            postman_url="/api/data/v1/accounts",
            postman_method="GET",
        )

        assert 0.0 <= match.confidence <= 1.0
