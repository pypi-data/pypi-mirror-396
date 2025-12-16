"""Deterministic parser for Postman collections.

This module provides rule-based parsing of Postman collections into
structured models without using AI agents.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..exceptions import PostmanParseError
from ..models import PostmanCollection, PostmanRequest


@dataclass
class ParsedPostmanRequest:
    """Parsed Postman request with extracted metadata."""

    name: str
    method: str
    url_pattern: str
    path_variables: list[str] = field(default_factory=list)
    query_params: list[str] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)
    body_schema: dict[str, Any] | None = None
    folder_path: str = ""
    postman_request: PostmanRequest | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "method": self.method,
            "url_pattern": self.url_pattern,
            "path_variables": self.path_variables,
            "query_params": self.query_params,
            "headers": self.headers,
            "body_schema": self.body_schema,
            "folder_path": self.folder_path,
        }


@dataclass
class ParsedPostmanCollection:
    """Parsed Postman collection with structured metadata."""

    collection: PostmanCollection
    requests: list[ParsedPostmanRequest] = field(default_factory=list)
    folder_structure: dict[str, list[str]] = field(default_factory=dict)
    variables: dict[str, str] = field(default_factory=dict)
    base_url: str = ""

    def get_requests_by_folder(self, folder_path: str) -> list[ParsedPostmanRequest]:
        """Get all requests in a specific folder."""
        return [req for req in self.requests if req.folder_path == folder_path]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "collection_name": self.collection.info.name,
            "total_requests": len(self.requests),
            "folder_structure": self.folder_structure,
            "variables": self.variables,
            "base_url": self.base_url,
            "requests": [req.to_dict() for req in self.requests],
        }


def _extract_path_variables(url_path: list[str]) -> list[str]:
    """Extract path variables from URL path segments."""
    variables = []
    for segment in url_path:
        if (
            segment.startswith(":")
            or segment.startswith("{{")
            and segment.endswith("}}")
        ):
            var_name = segment.lstrip(":").strip("{}")
            variables.append(var_name)
    return variables


def _extract_query_params(url_query: list[dict[str, Any]]) -> list[str]:
    """Extract query parameter names."""
    return [param.get("key", "") for param in url_query if param.get("key")]


def _extract_headers(request_headers: list[dict[str, Any]]) -> dict[str, str]:
    """Extract headers from request."""
    headers = {}
    for header in request_headers:
        key = header.get("key", "")
        value = header.get("value", "")
        if key:
            headers[key.lower()] = value
    return headers


def _extract_body_schema(request_body: dict[str, Any] | None) -> dict[str, Any] | None:
    """Extract body schema from request."""
    if not request_body:
        return None

    mode = request_body.get("mode", "")
    if mode == "raw":
        raw = request_body.get("raw", "")
        if raw:
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return {"raw": raw}
    elif mode == "formdata" or mode == "urlencoded":
        return {"mode": mode, "data": request_body.get(mode, [])}

    return None


def _build_url_pattern(url_data: dict[str, Any], base_url: str = "") -> str:
    """Build normalized URL pattern from Postman URL data.

    Postman format: {{baseUrl}}/data/v1/accounts
    where baseUrl = {{instanceUrl}}/api = https://{{instance}}.domo.com/api

    domolibrary format: https://{auth.domo_instance}.domo.com/api/data/v1/accounts

    We normalize both to: /api/data/v1/accounts for matching.
    """
    import re

    raw_url = url_data.get("raw", "")
    if raw_url:
        # Handle Postman {{baseUrl}} variable
        # baseUrl = {{instanceUrl}}/api, so {{baseUrl}}/path becomes /api/path
        if "{{baseUrl}}" in raw_url:
            # Replace {{baseUrl}} with /api to align with domolibrary format
            raw_url = raw_url.replace("{{baseUrl}}", "/api")
        elif "{{instanceUrl}}" in raw_url:
            # instanceUrl = https://{{instance}}.domo.com, add /api if not present
            raw_url = raw_url.replace("{{instanceUrl}}", "")
            if not raw_url.startswith("/api"):
                raw_url = "/api" + raw_url

        # Remove protocol and host if present (handle full URLs)
        if "://" in raw_url:
            # Extract just the path part after .domo.com
            parts = raw_url.split("://", 1)
            if len(parts) > 1:
                # Find .domo.com and extract path after it
                domo_part = parts[1]
                if ".domo.com" in domo_part:
                    path_part = "/" + "/".join(
                        domo_part.split(".domo.com", 1)[1].split("/")[1:]
                    )
                    raw_url = path_part
                else:
                    # Fallback: extract path after host
                    path_part = "/" + "/".join(domo_part.split("/")[1:])
                    raw_url = path_part

        # Normalize remaining Postman variables: {{var}} -> {var}, :var -> {var}
        raw_url = raw_url.replace("{{instance}}", "")
        raw_url = raw_url.replace("{{", "{").replace("}}", "}")
        # Convert :variable to {variable}
        raw_url = re.sub(r":(\w+)", r"{\1}", raw_url)

        # Ensure /api prefix for consistency with domolibrary format
        # (domolibrary always includes /api in the path)
        if not raw_url.startswith("/"):
            raw_url = "/" + raw_url

        # Clean up double slashes
        raw_url = re.sub(r"/+", "/", raw_url)
        return raw_url

    # Build from components (fallback when raw URL not available)
    import re

    url_data.get("protocol", "https")
    host = url_data.get("host", [])
    path = url_data.get("path", [])
    query = url_data.get("query", [])

    if isinstance(host, list):
        ".".join(host)
    else:
        str(host)

    # Build path, converting :variable to {variable}
    path_parts = []
    for p in path:
        p_str = str(p)
        # Convert :variable to {variable}
        if p_str.startswith(":"):
            path_parts.append("{" + p_str[1:] + "}")
        else:
            path_parts.append(p_str)

    path_str = "/" + "/".join(path_parts)

    # If host contains {{baseUrl}}, add /api prefix
    # Postman baseUrl = {{instanceUrl}}/api, so paths should include /api
    if "{{baseUrl}}" in str(host) or "baseUrl" in str(host).lower():
        if not path_str.startswith("/api"):
            path_str = "/api" + path_str

    if query:
        query_str = "?" + "&".join(
            f"{q.get('key', '')}={q.get('value', '')}" for q in query
        )
    else:
        query_str = ""

    full_url = f"{path_str}{query_str}"

    # Clean up double slashes
    full_url = re.sub(r"/+", "/", full_url)
    return full_url


def _extract_folder_path(item: dict[str, Any], parent_path: str = "") -> str:
    """Extract folder path from Postman item."""
    if "item" in item:
        # This is a folder
        folder_name = item.get("name", "")
        current_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
        return current_path
    return parent_path


def parse_postman_collection(
    collection_path: str | Path,
    base_url: str | None = None,
) -> ParsedPostmanCollection:
    """Parse a Postman collection into structured format.

    Args:
        collection_path: Path to Postman collection JSON file
        base_url: Optional base URL to normalize against

    Returns:
        ParsedPostmanCollection with extracted metadata

    Raises:
        FileNotFoundError: If collection file doesn't exist
        ValueError: If collection is invalid
    """
    path = Path(collection_path)
    if not path.exists():
        raise PostmanParseError(f"Collection file not found: {collection_path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise PostmanParseError(f"Invalid JSON in collection file: {e}") from e
    except Exception as e:
        raise PostmanParseError(f"Error reading collection file: {e}") from e

    # Parse using existing PostmanCollection model
    try:
        collection = PostmanCollection.from_dict(data)
    except Exception as e:
        raise PostmanParseError(
            f"Error parsing Postman collection structure: {e}"
        ) from e

    # Extract base URL from variables if not provided
    if not base_url:
        for var in collection.variable or []:
            if var.key == "baseUrl" or var.key == "instance":
                base_url = var.value or ""
                break

    parsed = ParsedPostmanCollection(
        collection=collection,
        base_url=base_url or "",
        variables={var.key: var.value for var in (collection.variable or [])},
    )

    # Extract folder structure and requests
    def process_items(items: list[Any], folder_path: str = ""):
        """Recursively process collection items."""
        from ..models import PostmanFolder

        for item in items:
            if isinstance(item, PostmanRequest):
                # Extract request metadata
                # PostmanRequest has url, method, header, body directly
                url_obj = item.url
                if hasattr(url_obj, "to_dict"):
                    url_data = url_obj.to_dict()
                elif isinstance(url_obj, dict):
                    url_data = url_obj
                else:
                    # Try to get raw URL from PostmanUrl object
                    if hasattr(url_obj, "raw"):
                        url_data = {"raw": url_obj.raw}
                        if hasattr(url_obj, "path") and url_obj.path:
                            url_data["path"] = url_obj.path
                        if hasattr(url_obj, "query") and url_obj.query:
                            url_data["query"] = [
                                q.to_dict() if hasattr(q, "to_dict") else q
                                for q in url_obj.query
                            ]
                    else:
                        url_data = {"raw": str(url_obj) if url_obj else ""}

                url_pattern = _build_url_pattern(url_data, parsed.base_url)
                path_list = url_data.get("path", [])
                if path_list:
                    path_vars = _extract_path_variables(path_list)
                else:
                    path_vars = []
                query_list = url_data.get("query", [])
                if query_list:
                    # Handle PostmanQueryParam objects
                    if hasattr(query_list[0], "to_dict"):
                        query_dicts = [q.to_dict() for q in query_list]
                    else:
                        query_dicts = query_list
                    query_params = _extract_query_params(query_dicts)
                else:
                    query_params = []

                # Extract headers
                header_list = item.header or []
                if hasattr(header_list, "__iter__") and not isinstance(
                    header_list, str
                ):
                    headers = _extract_headers(
                        [
                            h.to_dict() if hasattr(h, "to_dict") else h
                            for h in header_list
                        ]
                    )
                else:
                    headers = {}

                # Extract body
                body_obj = item.body
                if body_obj:
                    if hasattr(body_obj, "to_dict"):
                        body_data = body_obj.to_dict()
                    elif isinstance(body_obj, dict):
                        body_data = body_obj
                    else:
                        body_data = None
                    body_schema = _extract_body_schema(body_data)
                else:
                    body_schema = None

                parsed_request = ParsedPostmanRequest(
                    name=item.name,
                    method=item.method or "GET",
                    url_pattern=url_pattern,
                    path_variables=path_vars,
                    query_params=query_params,
                    headers=headers,
                    body_schema=body_schema,
                    folder_path=folder_path,
                    postman_request=item,
                )
                parsed.requests.append(parsed_request)

                # Track folder structure
                if folder_path:
                    if folder_path not in parsed.folder_structure:
                        parsed.folder_structure[folder_path] = []
                    parsed.folder_structure[folder_path].append(item.name)

            elif isinstance(item, PostmanFolder):
                # Process folder
                folder_name = item.name
                new_folder_path = (
                    f"{folder_path}/{folder_name}" if folder_path else folder_name
                )
                if item.item:
                    process_items(item.item, new_folder_path)
            else:
                # Try to process as dict (fallback)
                if isinstance(item, dict):
                    item_name = item.get("name", "")
                    new_folder_path = (
                        f"{folder_path}/{item_name}" if folder_path else item_name
                    )
                    nested_items = item.get("item", [])
                    if nested_items:
                        process_items(nested_items, new_folder_path)

    # Process all items
    process_items(collection.item)

    return parsed
