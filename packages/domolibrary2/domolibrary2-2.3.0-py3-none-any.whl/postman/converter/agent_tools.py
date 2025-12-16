# agent_tools.py - Tools for agents to interact with Postman models

import ast

from .models import PostmanCollection


def load_collection_from_file(file_path: str) -> dict:
    """Load Postman collection from JSON file.

    Args:
        file_path: Path to the Postman collection JSON file

    Returns:
        Dictionary representation of the collection
    """
    collection = PostmanCollection.from_file(file_path)
    return collection.to_dict()


def validate_collection_structure(collection_dict: dict) -> tuple[bool, list[str]]:
    """Validate that collection structure is complete.

    Args:
        collection_dict: Dictionary representation of collection

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    try:
        collection = PostmanCollection.from_dict(collection_dict)
        reconstructed = collection.to_dict()

        # Check if round-trip conversion preserves data
        if collection_dict != reconstructed:
            issues.append("Collection structure not fully preserved in round-trip")

    except Exception as e:
        issues.append(f"Structure validation failed: {str(e)}")
        return False, issues

    return len(issues) == 0, issues


def extract_collection_metadata(collection_dict: dict) -> dict:
    """Extract metadata from collection.

    Args:
        collection_dict: Dictionary representation of collection

    Returns:
        Dictionary with metadata
    """
    metadata = {
        "name": collection_dict.get("info", {}).get("name", "Unknown"),
        "total_items": len(collection_dict.get("item", [])),
        "has_auth": "auth" in collection_dict,
        "has_variables": "variable" in collection_dict,
        "has_events": "event" in collection_dict,
        "schema": collection_dict.get("info", {}).get("schema", "Unknown"),
    }

    # Count total requests recursively
    def count_requests(items):
        count = 0
        for item in items:
            if "request" in item:
                count += 1
            elif "item" in item:
                count += count_requests(item["item"])
        return count

    metadata["total_requests"] = count_requests(collection_dict.get("item", []))

    return metadata


def extract_folder_structure(collection_dict: dict) -> list[str]:
    """Extract folder paths from collection.

    Args:
        collection_dict: Dictionary representation of collection

    Returns:
        List of folder paths
    """
    folder_paths = []

    def traverse(items, path=""):
        for item in items:
            if "request" not in item and "item" in item:
                # It's a folder
                folder_name = item.get("name", "Unnamed")
                folder_path = f"{path}/{folder_name}" if path else folder_name
                folder_paths.append(folder_path)
                traverse(item["item"], folder_path)

    traverse(collection_dict.get("item", []))
    return folder_paths


def extract_all_requests(collection_dict: dict) -> list[dict]:
    """Extract all requests from collection recursively.

    Args:
        collection_dict: Dictionary representation of collection

    Returns:
        List of request dictionaries
    """
    requests = []

    def traverse(items, folder_path=""):
        for item in items:
            if "request" in item:
                request_data = {
                    "name": item.get("name"),
                    "request": item.get("request"),
                    "folder_path": folder_path,
                    "response": item.get("response", []),
                }
                requests.append(request_data)
            elif "item" in item:
                folder_name = item.get("name", "")
                new_path = (
                    f"{folder_path}/{folder_name}" if folder_path else folder_name
                )
                traverse(item["item"], new_path)

    traverse(collection_dict.get("item", []))
    return requests


def analyze_authentication(collection_dict: dict) -> dict:
    """Analyze authentication patterns in collection.

    Args:
        collection_dict: Dictionary representation of collection

    Returns:
        Dictionary with auth analysis
    """
    auth_analysis = {
        "collection_auth": None,
        "folder_auth": [],
        "request_auth": [],
        "auth_types": set(),
        "auth_variables": set(),
    }

    # Collection-level auth
    if "auth" in collection_dict:
        auth_analysis["collection_auth"] = collection_dict["auth"]
        if "type" in collection_dict["auth"]:
            auth_analysis["auth_types"].add(collection_dict["auth"]["type"])

    # Traverse for folder and request auth
    def traverse(items, folder_path=""):
        for item in items:
            # Check for folder-level auth
            if "auth" in item and "request" not in item:
                auth_analysis["folder_auth"].append(
                    {"folder": item.get("name"), "auth": item["auth"]}
                )
                if "type" in item["auth"]:
                    auth_analysis["auth_types"].add(item["auth"]["type"])

            # Check for request-level auth
            if "request" in item and "auth" in item["request"]:
                auth_analysis["request_auth"].append(
                    {"request": item.get("name"), "auth": item["request"]["auth"]}
                )
                if "type" in item["request"]["auth"]:
                    auth_analysis["auth_types"].add(item["request"]["auth"]["type"])

            # Recurse into folders
            if "item" in item:
                traverse(item["item"], folder_path)

    traverse(collection_dict.get("item", []))

    # Convert sets to lists for JSON serialization
    auth_analysis["auth_types"] = list(auth_analysis["auth_types"])
    auth_analysis["auth_variables"] = list(auth_analysis["auth_variables"])

    return auth_analysis


def analyze_parameters(requests: list[dict]) -> dict:
    """Analyze query parameters across requests.

    Args:
        requests: List of request dictionaries

    Returns:
        Dictionary with parameter analysis
    """
    param_analysis = {
        "all_params": {},
        "common_params": {},
        "param_types": {},
        "default_values": {},
    }

    param_counts = {}

    for request in requests:
        url = request.get("request", {}).get("url", {})
        query_params = url.get("query", [])

        for param in query_params:
            if not param or "key" not in param:
                continue

            key = param["key"]
            value = param.get("value", "")

            # Track all params
            if key not in param_analysis["all_params"]:
                param_analysis["all_params"][key] = []
            param_analysis["all_params"][key].append(value)

            # Count occurrences
            param_counts[key] = param_counts.get(key, 0) + 1

            # Infer type
            if key not in param_analysis["param_types"]:
                param_analysis["param_types"][key] = infer_type(value)

            # Store default value (first occurrence)
            if key not in param_analysis["default_values"]:
                param_analysis["default_values"][key] = value

    # Identify common params (appear in multiple requests)
    total_requests = len(requests)
    for key, count in param_counts.items():
        if count > 1:
            param_analysis["common_params"][key] = {
                "count": count,
                "percentage": round((count / total_requests) * 100, 2),
            }

    return param_analysis


def analyze_headers(requests: list[dict]) -> dict:
    """Analyze headers across requests.

    Args:
        requests: List of request dictionaries

    Returns:
        Dictionary with header analysis
    """
    header_analysis = {
        "all_headers": {},
        "common_headers": {},
        "content_types": set(),
        "auth_headers": [],
    }

    header_counts = {}

    for request in requests:
        headers = request.get("request", {}).get("header", [])

        for header in headers:
            if not header or "key" not in header:
                continue

            key = header["key"].lower()
            value = header.get("value", "")

            # Track all headers
            if key not in header_analysis["all_headers"]:
                header_analysis["all_headers"][key] = []
            header_analysis["all_headers"][key].append(value)

            # Count occurrences
            header_counts[key] = header_counts.get(key, 0) + 1

            # Track content types
            if key == "content-type":
                header_analysis["content_types"].add(value)

            # Identify auth headers
            if "authorization" in key.lower() or "auth" in key.lower():
                if key not in header_analysis["auth_headers"]:
                    header_analysis["auth_headers"].append(key)

    # Identify common headers
    total_requests = len(requests)
    for key, count in header_counts.items():
        if count > 1:
            header_analysis["common_headers"][key] = {
                "count": count,
                "percentage": round((count / total_requests) * 100, 2),
            }

    # Convert sets to lists
    header_analysis["content_types"] = list(header_analysis["content_types"])

    return header_analysis


def infer_type(value: str) -> str:
    """Infer the type of a parameter value.

    Args:
        value: String value to analyze

    Returns:
        Type as string (int, float, bool, str)
    """
    if not value:
        return "str"

    # Check for boolean
    if value.lower() in ("true", "false"):
        return "bool"

    # Check for integer
    try:
        int(value)
        return "int"
    except ValueError:
        pass

    # Check for float
    try:
        float(value)
        return "float"
    except ValueError:
        pass

    return "str"


def validate_python_syntax(code: str) -> tuple[bool, list[str]]:
    """Validate Python code syntax.

    Args:
        code: Python code string

    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []

    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return False, errors
    except Exception as e:
        errors.append(f"Parse error: {str(e)}")
        return False, errors

    return True, []


def format_imports(imports: list[str]) -> str:
    """Format import statements.

    Args:
        imports: List of import statements

    Returns:
        Formatted import block
    """
    if not imports:
        return ""

    # Remove duplicates and sort
    unique_imports = sorted(set(imports))

    # Group imports
    stdlib = []
    third_party = []
    local = []

    for imp in unique_imports:
        if imp.startswith("from .") or imp.startswith("import ."):
            local.append(imp)
        elif any(
            lib in imp
            for lib in ["httpx", "requests", "pydantic", "typing", "dataclasses"]
        ):
            if imp.startswith("from typing") or imp.startswith("import typing"):
                stdlib.append(imp)
            else:
                third_party.append(imp)
        else:
            stdlib.append(imp)

    # Build import block
    result = []
    if stdlib:
        result.extend(stdlib)
    if third_party:
        if stdlib:
            result.append("")
        result.extend(third_party)
    if local:
        if stdlib or third_party:
            result.append("")
        result.extend(local)

    return "\n".join(result)
