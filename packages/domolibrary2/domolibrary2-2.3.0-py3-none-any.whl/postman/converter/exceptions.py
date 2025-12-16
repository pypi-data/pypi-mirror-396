"""Custom exceptions for Postman conversion system."""

from __future__ import annotations


class PostmanConversionError(Exception):
    """Base exception for Postman conversion errors."""

    pass


class PostmanParseError(PostmanConversionError):
    """Error parsing Postman collection."""

    pass


class RouteDiscoveryError(PostmanConversionError):
    """Error discovering routes."""

    pass


class RouteMatchError(PostmanConversionError):
    """Error during route matching."""

    pass


class CodeGenerationError(PostmanConversionError):
    """Error generating code."""

    pass


class StagingError(PostmanConversionError):
    """Error in staging area operations."""

    pass


class ValidationError(PostmanConversionError):
    """Error during validation."""

    pass


class ConfigurationError(PostmanConversionError):
    """Error in configuration."""

    pass
