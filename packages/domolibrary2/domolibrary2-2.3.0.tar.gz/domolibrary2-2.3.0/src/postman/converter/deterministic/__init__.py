"""Deterministic processing for Postman collection conversion.

This module provides rule-based, deterministic processing for:
- Parsing Postman collections
- Matching Postman endpoints to existing routes
- URL pattern extraction
- Conversion state tracking
"""

from .matcher import MatchType, RouteMatch, RouteMatcher
from .parser import ParsedPostmanCollection, parse_postman_collection
from .tracker import ConversionState, ConversionTracker
from .url_extractor import URLPattern, extract_url_pattern

__all__ = [
    "ParsedPostmanCollection",
    "parse_postman_collection",
    "RouteMatch",
    "RouteMatcher",
    "MatchType",
    "URLPattern",
    "extract_url_pattern",
    "ConversionTracker",
    "ConversionState",
]
