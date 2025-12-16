"""Route matching logic.

This module provides deterministic matching between Postman endpoints
and existing domolibrary route functions.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from enum import Enum

from .url_extractor import URLPattern, extract_url_pattern, normalize_url


class MatchType(str, Enum):
    """Type of match found."""

    EXACT_MATCH = "EXACT_MATCH"  # URL, method, and function name match
    URL_MATCH = "URL_MATCH"  # URL and method match, different function name
    NAME_MATCH = "NAME_MATCH"  # Function name similar, URL different
    NO_MATCH = "NO_MATCH"  # No existing route found


@dataclass
class RouteMatch:
    """Result of matching a Postman endpoint to an existing route."""

    postman_request_name: str
    postman_url: str
    postman_method: str
    match_type: MatchType
    confidence: float  # 0.0 to 1.0
    existing_route_name: str | None = None
    existing_route_module: str | None = None
    existing_route_url: str | None = None
    existing_route_method: str | None = None
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "postman_request_name": self.postman_request_name,
            "postman_url": self.postman_url,
            "postman_method": self.postman_method,
            "match_type": self.match_type.value,
            "confidence": self.confidence,
            "existing_route_name": self.existing_route_name,
            "existing_route_module": self.existing_route_module,
            "existing_route_url": self.existing_route_url,
            "existing_route_method": self.existing_route_method,
            "notes": self.notes,
        }


class RouteMatcher:
    """Matches Postman endpoints to existing routes."""

    def __init__(self, route_registry: dict[str, dict]):
        """Initialize matcher with route registry.

        Args:
            route_registry: Dictionary mapping route names to route info:
                {
                    "function_name": {
                        "module": "domolibrary2.routes.account.core",
                        "url": "/api/data/v1/accounts",
                        "method": "GET",
                        "function_name": "get_accounts"
                    }
                }
        """
        self.route_registry = route_registry

    def match(
        self,
        postman_name: str,
        postman_url: str,
        postman_method: str,
    ) -> RouteMatch:
        """Match a Postman endpoint to existing routes.

        Args:
            postman_name: Name of Postman request
            postman_url: URL from Postman request (already normalized from parser)
            postman_method: HTTP method from Postman request

        Returns:
            RouteMatch with match results
        """
        # Normalize Postman URL (should already be normalized from parser, but ensure consistency)
        postman_pattern = extract_url_pattern(postman_url, postman_method)
        postman_normalized = normalize_url(postman_url)

        # Ensure /api prefix alignment - Postman URLs should already have this from parser
        # but double-check for consistency
        if not postman_normalized.startswith(
            "/api"
        ) and not postman_normalized.startswith("/"):
            postman_normalized = "/api/" + postman_normalized

        best_match: RouteMatch | None = None
        best_confidence = 0.0

        # Try to match against all routes
        for route_name, route_info in self.route_registry.items():
            route_url = route_info.get("url", "")
            route_method = route_info.get("method", "GET")
            route_module = route_info.get("module", "")

            # Normalize route URL (extracted from code, should include /api prefix)
            route_normalized = normalize_url(route_url)

            # Ensure /api prefix alignment - route URLs from code extraction should have this
            # but ensure consistency for matching
            if (
                route_normalized
                and not route_normalized.startswith("/api")
                and route_normalized.startswith("/")
            ):
                # Check if it's a known non-API path (rare) or add /api prefix
                # Most Domo Product API paths include /api, so we'll add it for matching
                route_normalized = "/api" + route_normalized

            # Calculate match confidence
            confidence, match_type, notes = self._calculate_match(
                postman_pattern,
                postman_normalized,
                postman_method,
                postman_name,
                route_normalized,
                route_method,
                route_name,
            )

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = RouteMatch(
                    postman_request_name=postman_name,
                    postman_url=postman_url,
                    postman_method=postman_method,
                    match_type=match_type,
                    confidence=confidence,
                    existing_route_name=route_name,
                    existing_route_module=route_module,
                    existing_route_url=route_url,
                    existing_route_method=route_method,
                    notes=notes,
                )

        # Return best match or no match
        if best_match and best_confidence >= 0.5:
            return best_match

        return RouteMatch(
            postman_request_name=postman_name,
            postman_url=postman_url,
            postman_method=postman_method,
            match_type=MatchType.NO_MATCH,
            confidence=0.0,
            notes="No matching route found",
        )

    def _calculate_match(
        self,
        postman_pattern: URLPattern,
        postman_normalized: str,
        postman_method: str,
        postman_name: str,
        route_normalized: str,
        route_method: str,
        route_name: str,
    ) -> tuple[float, MatchType, str]:
        """Calculate match confidence and type.

        Returns:
            Tuple of (confidence, match_type, notes)
        """
        # Method must match
        if postman_method.upper() != route_method.upper():
            return (0.0, MatchType.NO_MATCH, "Method mismatch")

        # Check URL pattern match
        route_pattern = extract_url_pattern(route_normalized, route_method)
        url_matches = postman_pattern.matches(route_pattern)

        # Check function name similarity
        name_similarity = self._name_similarity(postman_name, route_name)

        # Determine match type and confidence
        if url_matches and name_similarity > 0.8:
            # EXACT_MATCH: URL and name both match
            confidence = 0.95
            match_type = MatchType.EXACT_MATCH
            notes = "Exact match: URL and function name"
        elif url_matches:
            # URL_MATCH: URL matches, name different
            confidence = 0.85
            match_type = MatchType.URL_MATCH
            notes = f"URL matches, name similarity: {name_similarity:.2f}"
        elif name_similarity > 0.7:
            # NAME_MATCH: Name similar, URL different
            confidence = 0.6
            match_type = MatchType.NAME_MATCH
            notes = f"Name similar, URL different. Similarity: {name_similarity:.2f}"
        else:
            # NO_MATCH
            confidence = max(0.0, name_similarity * 0.3)
            match_type = MatchType.NO_MATCH
            notes = f"Low similarity: {name_similarity:.2f}"

        return (confidence, match_type, notes)

    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two function names.

        Args:
            name1: First function name
            name2: Second function name

        Returns:
            Similarity score between 0.0 and 1.0
        """

        # Normalize names (to snake_case, lowercase)
        def normalize(name: str) -> str:
            return name.lower().replace("-", "_").replace(" ", "_")

        norm1 = normalize(name1)
        norm2 = normalize(name2)

        # Exact match
        if norm1 == norm2:
            return 1.0

        # Use SequenceMatcher for similarity
        similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()

        # Boost if one contains the other
        if norm1 in norm2 or norm2 in norm1:
            similarity = min(1.0, similarity + 0.2)

        return similarity
