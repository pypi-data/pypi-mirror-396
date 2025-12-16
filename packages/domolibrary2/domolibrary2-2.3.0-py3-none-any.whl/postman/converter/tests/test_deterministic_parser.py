"""Tests for deterministic Postman collection parser."""

from __future__ import annotations

import json

import pytest

from ..deterministic.parser import (
    ParsedPostmanCollection,
    ParsedPostmanRequest,
    parse_postman_collection,
)


class TestParsedPostmanRequest:
    """Tests for ParsedPostmanRequest dataclass."""

    def test_to_dict(self):
        """Test converting ParsedPostmanRequest to dictionary."""
        request = ParsedPostmanRequest(
            name="Test Request",
            method="GET",
            url_pattern="/api/v1/test",
            path_variables=["id"],
            query_params=["limit", "offset"],
            headers={"Content-Type": "application/json"},
            folder_path="Test/Folder",
        )

        result = request.to_dict()

        assert result["name"] == "Test Request"
        assert result["method"] == "GET"
        assert result["url_pattern"] == "/api/v1/test"
        assert result["path_variables"] == ["id"]
        assert result["query_params"] == ["limit", "offset"]
        assert result["headers"] == {"Content-Type": "application/json"}
        assert result["folder_path"] == "Test/Folder"


class TestParsePostmanCollection:
    """Tests for parse_postman_collection function."""

    @pytest.fixture
    def sample_collection_path(self, tmp_path):
        """Create a sample Postman collection file."""
        collection = {
            "info": {
                "name": "Test Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [
                {
                    "name": "Test Folder",
                    "item": [
                        {
                            "name": "Get Test",
                            "request": {
                                "method": "GET",
                                "url": {
                                    "raw": "https://api.example.com/v1/test?id=123",
                                    "host": ["api", "example", "com"],
                                    "path": ["v1", "test"],
                                    "query": [{"key": "id", "value": "123"}],
                                },
                                "header": [
                                    {"key": "Content-Type", "value": "application/json"}
                                ],
                            },
                        }
                    ],
                }
            ],
        }

        file_path = tmp_path / "test_collection.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(collection, f)

        return str(file_path)

    def test_parse_basic_collection(self, sample_collection_path):
        """Test parsing a basic Postman collection."""
        parsed = parse_postman_collection(sample_collection_path)

        assert isinstance(parsed, ParsedPostmanCollection)
        assert len(parsed.requests) == 1
        assert parsed.requests[0].name == "Get Test"
        assert parsed.requests[0].method == "GET"
        assert parsed.requests[0].folder_path == "Test Folder"

    def test_parse_collection_with_variables(self, tmp_path):
        """Test parsing collection with Postman variables."""
        collection = {
            "info": {
                "name": "Test Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "variable": [{"key": "baseUrl", "value": "https://api.example.com"}],
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "GET",
                        "url": {
                            "raw": "{{baseUrl}}/v1/test",
                            "host": ["{{baseUrl}}"],
                            "path": ["v1", "test"],
                        },
                    },
                }
            ],
        }

        file_path = tmp_path / "test_collection.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(collection, f)

        parsed = parse_postman_collection(str(file_path))

        assert len(parsed.requests) == 1
        # Variables should be converted to path parameters
        assert (
            "{{baseUrl}}" in parsed.requests[0].url_pattern
            or "baseUrl" in parsed.requests[0].url_pattern
        )

    def test_parse_collection_with_nested_folders(self, tmp_path):
        """Test parsing collection with nested folder structure."""
        collection = {
            "info": {
                "name": "Test Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [
                {
                    "name": "Parent Folder",
                    "item": [
                        {
                            "name": "Child Folder",
                            "item": [
                                {
                                    "name": "Nested Request",
                                    "request": {
                                        "method": "POST",
                                        "url": {
                                            "raw": "https://api.example.com/v1/nested"
                                        },
                                    },
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        file_path = tmp_path / "test_collection.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(collection, f)

        parsed = parse_postman_collection(str(file_path))

        assert len(parsed.requests) == 1
        assert parsed.requests[0].folder_path == "Parent Folder/Child Folder"

    def test_parse_collection_with_body(self, tmp_path):
        """Test parsing collection with request body."""
        collection = {
            "info": {
                "name": "Test Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [
                {
                    "name": "Post Request",
                    "request": {
                        "method": "POST",
                        "url": {"raw": "https://api.example.com/v1/create"},
                        "body": {
                            "mode": "raw",
                            "raw": '{"name": "test", "value": 123}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                }
            ],
        }

        file_path = tmp_path / "test_collection.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(collection, f)

        parsed = parse_postman_collection(str(file_path))

        assert len(parsed.requests) == 1
        assert parsed.requests[0].body_schema is not None

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            parse_postman_collection("nonexistent.json")

    def test_parse_invalid_json(self, tmp_path):
        """Test parsing invalid JSON raises appropriate error."""
        file_path = tmp_path / "invalid.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        with pytest.raises((json.JSONDecodeError, ValueError)):
            parse_postman_collection(str(file_path))
