"""preferred response class for all API requests"""

import re
from dataclasses import dataclass, field
from typing import Any

import httpx
import requests
from bs4 import BeautifulSoup

__all__ = ["STREAM_FILE_PATH", "ResponseGetData", "find_ip", "RequestMetadata"]


@dataclass
class RequestMetadata:
    url: str
    headers: dict = field(repr=False, default_factory=dict)
    body: str | None = field(default=None)
    params: dict | None = field(default=None)

    def to_dict(self, auth_headers: list[str] | None = None) -> dict:
        """returns dict representation of RequestMetadata"""

        return {
            "url": self.url,
            "headers": {
                k: v for k, v in self.headers.items() if k not in (auth_headers or [])
            },
            "body": self.body,
            "params": self.params,
        }


@dataclass
class ResponseGetData:
    """preferred response class for all API Requests"""

    status: int
    response: dict[str, Any] | str | list[Any]
    is_success: bool

    request_metadata: RequestMetadata | None = field(default=None)
    additional_information: dict | None = field(default=None, repr=False)
    response_headers: dict[str, str] | None = field(default=None, repr=False)
    elapsed: float | None = field(default=None, repr=False)  # seconds
    raw_response: httpx.Response | None = field(
        default=None, repr=False
    )  # For return_raw cases

    def to_dict(self, is_exclude_response: bool = True) -> dict:
        """returns dict representation of ResponseGetData"""
        return {
            "status": self.status,
            "response": None if is_exclude_response else self.response,
            "is_success": self.is_success,
            "request_metadata": (
                self.request_metadata.to_dict() if self.request_metadata else None
            ),
            "additional_information": self.additional_information,
            "response_headers": self.response_headers,
            "elapsed": self.elapsed,
            "raw_response": None,  # Don't serialize raw response
        }

    def get_cache_headers(self) -> dict[str, str]:
        """Extract cache-related headers from response.

        Returns:
            Dictionary of cache-related headers
        """
        if not self.response_headers:
            return {}

        cache_header_names = [
            "cache-control",
            "expires",
            "etag",
            "last-modified",
            "age",
            "date",
            "vary",
            "pragma",
        ]

        return {
            k: v
            for k, v in self.response_headers.items()
            if k.lower() in cache_header_names
        }

    @classmethod
    def from_requests_response(
        cls,
        res: requests.Response,
        request_metadata: RequestMetadata | None = None,
        additional_information: dict | None = None,
    ) -> "ResponseGetData":
        """returns ResponseGetData from requests.Response"""

        # Capture response headers and timing
        response_headers = dict(res.headers) if res.headers else None
        elapsed = (
            res.elapsed.total_seconds()
            if hasattr(res, "elapsed") and res.elapsed
            else None
        )

        # Check for JSON responses
        response = None
        if res.ok:
            if "application/json" in res.headers.get("Content-Type", ""):
                response = res.json()
            else:
                response = res.text

            return cls(
                status=res.status_code,
                response=response,
                additional_information=additional_information,
                request_metadata=request_metadata,
                response_headers=response_headers,
                elapsed=elapsed,
                is_success=True,
            )

        # Error responses
        return cls(
            status=res.status_code,
            response=res.reason,
            additional_information=additional_information,
            request_metadata=request_metadata,
            response_headers=response_headers,
            elapsed=elapsed,
            is_success=False,
        )

    @classmethod
    def from_httpx_response(
        cls,
        res: httpx.Response,
        request_metadata: RequestMetadata | None = None,
        additional_information: dict | None = None,
        raw_response: httpx.Response | None = None,
    ) -> "ResponseGetData":
        """returns ResponseGetData from httpx.Response"""

        # Capture response headers and timing
        response_headers = dict(res.headers) if res.headers else None
        # Try to get elapsed time, but handle case where response hasn't been read yet
        # (e.g., cached responses that are reconstructed)
        # Note: Accessing .elapsed on an unread response raises RuntimeError
        elapsed = None
        try:
            if hasattr(res, "elapsed") and res.elapsed:
                elapsed = res.elapsed.total_seconds()
        except RuntimeError:
            # Response hasn't been read yet (common with cached responses)
            elapsed = None

        # Check if response is successful
        ok = 200 <= res.status_code <= 399

        if ok:
            content_type = res.headers.get("Content-Type", "")

            # Try to parse as JSON if content type indicates it
            response = res.text  # Default to text
            if "application/json" in content_type:
                try:
                    response = res.json()
                except ValueError:
                    pass  # Keep as text if JSON parse fails

            return cls(
                status=res.status_code,
                response=response,
                is_success=True,
                additional_information=additional_information,
                request_metadata=request_metadata,
                response_headers=response_headers,
                elapsed=elapsed,
                raw_response=raw_response or res if raw_response is not None else None,
            )

        # Error responses
        response_text = (
            res.reason_phrase if hasattr(res, "reason_phrase") else "Unknown reason"
        )
        return cls(
            status=res.status_code,
            response=response_text,
            is_success=False,
            request_metadata=request_metadata,
            additional_information=additional_information,
            response_headers=response_headers,
            elapsed=elapsed,
            raw_response=raw_response or res if raw_response is not None else None,
        )

    @classmethod
    async def from_looper(
        cls,
        res: "ResponseGetData",
        array: list,
    ) -> "ResponseGetData":
        """Create ResponseGetData with array response (immutable).

        Args:
            res: Original ResponseGetData from last request
            array: Complete aggregated array from looper

        Returns:
            New ResponseGetData instance with array response
        """
        if not res.is_success:
            return res

        # Create new instance instead of mutating
        return cls(
            status=res.status,
            response=array,  # New array response
            is_success=res.is_success,
            request_metadata=res.request_metadata,
            additional_information=res.additional_information,
            response_headers=res.response_headers,
            elapsed=res.elapsed,
            raw_response=res.raw_response,
        )


def find_ip(html: str, html_tag: str = "p") -> str | None:
    """Extract IP address from HTML content.

    Args:
        html: HTML content to search
        html_tag: HTML tag to search within (default: "p")

    Returns:
        IP address string if found, None otherwise
    """
    ip_address_regex = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    soup = BeautifulSoup(html, "html.parser")

    tag = soup.find(html_tag)
    if not tag:
        return None

    matches = re.findall(ip_address_regex, str(tag))
    return matches[0] if matches else None


STREAM_FILE_PATH = "__large-file.json"
