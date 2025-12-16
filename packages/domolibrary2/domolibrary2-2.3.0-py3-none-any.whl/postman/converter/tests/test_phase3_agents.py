"""Tests for Phase 3 agent integration (matching, wrapper generation, docstring updates)."""

from __future__ import annotations

import pytest

from ..agent_models import DocstringUpdate, GeneratedWrapper, MatchValidationResult
from ..deterministic.matcher import MatchType, RouteMatch


class TestMatchValidationResult:
    """Tests for MatchValidationResult model."""

    def test_match_validation_result_creation(self):
        """Test creating MatchValidationResult."""
        result = MatchValidationResult(
            is_valid_match=True,
            confidence_adjusted=0.95,
            match_type="EXACT_MATCH",
            reasoning="URL and method match exactly",
            should_create_wrapper=True,
        )

        assert result.is_valid_match is True
        assert result.confidence_adjusted == 0.95
        assert result.match_type == "EXACT_MATCH"
        assert result.should_create_wrapper is True

    def test_match_validation_result_invalid(self):
        """Test MatchValidationResult for invalid match."""
        result = MatchValidationResult(
            is_valid_match=False,
            confidence_adjusted=0.3,
            match_type="NO_MATCH",
            reasoning="URLs don't match",
            should_create_wrapper=False,
        )

        assert result.is_valid_match is False
        assert result.should_create_wrapper is False


class TestGeneratedWrapper:
    """Tests for GeneratedWrapper model."""

    def test_generated_wrapper_creation(self):
        """Test creating GeneratedWrapper."""
        wrapper = GeneratedWrapper(
            wrapper_function_name="get_accounts_postman",
            wrapper_code='''@gd.route_function
async def get_accounts_postman(auth: DomoAuth) -> rgd.ResponseGetData:
    """Wrapper for get_accounts."""
    from domolibrary2.routes.account.core import get_accounts
    return await get_accounts(auth=auth)
''',
            imports_needed=["domolibrary2.routes.account.core"],
            docstring="Wrapper for get_accounts",
        )

        assert wrapper.wrapper_function_name == "get_accounts_postman"
        assert "async def" in wrapper.wrapper_code
        assert len(wrapper.imports_needed) > 0


class TestDocstringUpdate:
    """Tests for DocstringUpdate model."""

    def test_docstring_update_creation(self):
        """Test creating DocstringUpdate."""
        update = DocstringUpdate(
            updated_docstring="""Get all accounts.

Args:
    auth: DomoAuth instance

Returns:
    ResponseGetData

Postman Reference:
    This route matches Postman request "Get Accounts" in folder "Accounts".
    Match type: EXACT_MATCH, Confidence: 0.95
""",
            changes_made=["Added Postman reference section"],
            postman_reference="Get Accounts (Accounts folder)",
        )

        assert "Postman Reference" in update.updated_docstring
        assert len(update.changes_made) > 0
        assert "Get Accounts" in update.postman_reference


class TestPhase3Integration:
    """Integration tests for Phase 3 components."""

    @pytest.fixture
    def sample_route_match(self):
        """Create a sample RouteMatch for testing."""
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

    def test_match_validation_flow(self, sample_route_match):
        """Test the flow of match validation."""
        # Simulate validation result
        validation = MatchValidationResult(
            is_valid_match=True,
            confidence_adjusted=0.95,
            match_type="EXACT_MATCH",
            reasoning="Exact match found",
            should_create_wrapper=True,
        )

        assert validation.is_valid_match
        assert validation.should_create_wrapper

    def test_wrapper_generation_flow(self, sample_route_match):
        """Test the flow of wrapper generation."""
        # Simulate wrapper generation
        wrapper = GeneratedWrapper(
            wrapper_function_name="get_accounts_postman",
            wrapper_code="async def get_accounts_postman(): pass",
            imports_needed=[],
            docstring="Wrapper",
        )

        assert (
            wrapper.wrapper_function_name.endswith("_postman")
            or "postman" in wrapper.wrapper_function_name.lower()
        )

    def test_docstring_update_flow(self):
        """Test the flow of docstring updates."""
        # Simulate docstring update
        update = DocstringUpdate(
            updated_docstring="Updated docstring with Postman reference",
            changes_made=["Added reference"],
            postman_reference="Get Accounts",
        )

        assert (
            "Postman" in update.updated_docstring
            or "reference" in update.updated_docstring.lower()
        )
