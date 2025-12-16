"""URL pattern extraction and normalization.

This module provides utilities for extracting and normalizing URL patterns
from Postman requests and existing route functions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


@dataclass
class URLPattern:
    """Normalized URL pattern with extracted components."""

    path: str
    method: str
    path_variables: list[str]
    query_params: list[str]
    normalized_path: str  # Path with variables normalized to {var_name}

    def matches(self, other: URLPattern) -> bool:
        """Check if this pattern matches another pattern."""
        if self.method != other.method:
            return False

        # Normalize paths for comparison
        self_norm = self._normalize_path(self.path)
        other_norm = self._normalize_path(other.path)

        return self_norm == other_norm

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path by replacing variables with placeholders."""
        # Replace :variable, {variable}, {{variable}} with {variable}
        normalized = re.sub(r":(\w+)", r"{\1}", path)
        normalized = re.sub(r"\{\{(\w+)\}\}", r"{\1}", normalized)
        return normalized

    def to_dict(self) -> dict[str, any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "method": self.method,
            "path_variables": self.path_variables,
            "query_params": self.query_params,
            "normalized_path": self.normalized_path,
        }


def extract_url_pattern(url: str, method: str = "GET") -> URLPattern:
    """Extract and normalize URL pattern from a URL string.

    Args:
        url: URL string (may contain variables like :id or {{variable}})
        method: HTTP method

    Returns:
        URLPattern with extracted components

    Example:
        >>> pattern = extract_url_pattern("/api/v1/users/:id?limit=10", "GET")
        >>> pattern.path_variables
        ['id']
        >>> pattern.query_params
        ['limit']
    """
    parsed = urlparse(url)

    # Extract path
    path = parsed.path

    # Extract path variables
    path_variables = []
    # Match :variable, {variable}, {{variable}}
    var_pattern = r":(\w+)|(?:\{\{)?(\w+)(?:\}\})?"
    matches = re.findall(var_pattern, path)
    for match in matches:
        var_name = match[0] or match[1]
        if var_name and var_name not in path_variables:
            path_variables.append(var_name)

    # Normalize path
    normalized_path = URLPattern._normalize_path(path)

    # Extract query parameters
    query_params = []
    if parsed.query:
        query_dict = parse_qs(parsed.query)
        query_params = list(query_dict.keys())

    return URLPattern(
        path=path,
        method=method.upper(),
        path_variables=path_variables,
        query_params=query_params,
        normalized_path=normalized_path,
    )


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize a URL by removing base URL and standardizing variables.

    Args:
        url: URL string to normalize
        base_url: Optional base URL to remove

    Returns:
        Normalized URL path
    """
    # Remove base URL if present
    if base_url and url.startswith(base_url):
        url = url[len(base_url) :]

    # Remove protocol and domain if present
    parsed = urlparse(url)
    path = parsed.path

    # Normalize variables
    path = re.sub(r":(\w+)", r"{\1}", path)
    path = re.sub(r"\{\{(\w+)\}\}", r"{\1}", path)

    return path


def extract_url_from_route_code(code: str) -> str | None:
    """Extract URL from route function code.

    Looks for patterns like:
    - url = f"https://{auth.domo_instance}.domo.com/api/..."
    - url = "https://..."

    Returns the path part after .domo.com, which should include /api prefix
    to match Postman format (after normalization).

    Args:
        code: Python source code of route function

    Returns:
        Extracted URL path (e.g., "/api/data/v1/accounts") or None if not found
    """
    # Pattern 1: f-string with domo_instance (most common in domolibrary)
    # url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"
    pattern1 = r'url\s*=\s*f"https://\{auth\.domo_instance\}\.domo\.com([^"]+)"'
    match = re.search(pattern1, code)
    if match:
        path = match.group(1)
        # Ensure it starts with / for consistency
        if not path.startswith("/"):
            path = "/" + path
        return path

    # Pattern 2: Regular string with .domo.com
    # url = "https://instance.domo.com/api/data/v1/accounts"
    pattern2 = r'url\s*=\s*["\']https://[^"\']+\.domo\.com([^"\']+)["\']'
    match = re.search(pattern2, code)
    if match:
        path = match.group(1)
        if not path.startswith("/"):
            path = "/" + path
        return path

    # Pattern 3: f-string without domo_instance variable
    # url = f"https://{instance}.domo.com/api/data/v1/accounts"
    pattern3 = r'url\s*=\s*f"https://[^"]+\.domo\.com([^"]+)"'
    match = re.search(pattern3, code)
    if match:
        path = match.group(1)
        if not path.startswith("/"):
            path = "/" + path
        return path

    return None
