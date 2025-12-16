"""Route pattern analysis.

This module analyzes existing route patterns to identify conventions
and help with matching.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .route_discovery import RouteRegistry


@dataclass
class RoutePatterns:
    """Analyzed patterns from routes."""

    naming_conventions: dict[str, list[str]] = field(default_factory=dict)
    url_patterns: dict[str, list[str]] = field(default_factory=dict)
    module_organization: dict[str, list[str]] = field(default_factory=dict)
    common_prefixes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "naming_conventions": self.naming_conventions,
            "url_patterns": self.url_patterns,
            "module_organization": self.module_organization,
            "common_prefixes": self.common_prefixes,
        }


class RouteAnalyzer:
    """Analyzes route patterns and conventions."""

    def __init__(self, registry: RouteRegistry):
        """Initialize analyzer with route registry.

        Args:
            registry: RouteRegistry with discovered routes
        """
        self.registry = registry

    def analyze(self) -> RoutePatterns:
        """Analyze route patterns.

        Returns:
            RoutePatterns with identified patterns
        """
        patterns = RoutePatterns()

        # Analyze naming conventions
        patterns.naming_conventions = self._analyze_naming_conventions()

        # Analyze URL patterns
        patterns.url_patterns = self._analyze_url_patterns()

        # Analyze module organization
        patterns.module_organization = self._analyze_module_organization()

        # Find common prefixes
        patterns.common_prefixes = self._find_common_prefixes()

        return patterns

    def _analyze_naming_conventions(self) -> dict[str, list[str]]:
        """Analyze function naming conventions."""
        conventions = defaultdict(list)

        for route in self.registry.routes.values():
            name = route.function_name

            # Group by prefix
            if name.startswith("get_"):
                conventions["get_"].append(name)
            elif name.startswith("create_"):
                conventions["create_"].append(name)
            elif name.startswith("update_"):
                conventions["update_"].append(name)
            elif name.startswith("delete_"):
                conventions["delete_"].append(name)
            elif name.startswith("search_"):
                conventions["search_"].append(name)
            elif name.startswith("list_"):
                conventions["list_"].append(name)

        return dict(conventions)

    def _analyze_url_patterns(self) -> dict[str, list[str]]:
        """Analyze URL patterns."""
        patterns = defaultdict(list)

        for route in self.registry.routes.values():
            if route.url:
                # Extract base pattern (first few segments)
                parts = route.url.split("/")
                if len(parts) >= 3:
                    base_pattern = "/".join(parts[:3])
                    patterns[base_pattern].append(route.url)

        return dict(patterns)

    def _analyze_module_organization(self) -> dict[str, list[str]]:
        """Analyze how routes are organized by module."""
        organization = defaultdict(list)

        for route in self.registry.routes.values():
            # Extract top-level module
            module_parts = route.module.split(".")
            if len(module_parts) >= 2:
                top_module = module_parts[1]  # Skip "domolibrary2"
                organization[top_module].append(route.function_name)

        return dict(organization)

    def _find_common_prefixes(self) -> list[str]:
        """Find common URL prefixes."""
        prefixes = defaultdict(int)

        for route in self.registry.routes.values():
            if route.url:
                # Extract prefix (first segment after domain)
                parts = route.url.split("/")
                if len(parts) >= 2:
                    prefix = "/" + parts[1]
                    prefixes[prefix] += 1

        # Return prefixes that appear in multiple routes
        return [prefix for prefix, count in prefixes.items() if count >= 3]
