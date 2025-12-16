#!/usr/bin/env python3
"""
Postman Collection Structure Validation Script

This script validates that the PostmanCollection dataclass models completely
capture the structure of Postman collections, including all variables,
parameters, events, authentication, folders, and other components.
"""

import json
import sys
from pathlib import Path
from typing import Any

from .models import PostmanCollection


def deep_compare_structures(
    original: Any, reconstructed: Any, path: str = ""
) -> list[str]:
    """
    Recursively compare two data structures and return a list of differences.

    Args:
        original: Original data structure
        reconstructed: Reconstructed data structure
        path: Current path in the structure (for error reporting)

    Returns:
        List of difference descriptions
    """
    differences = []

    if type(original) != type(reconstructed):  # noqa: E721
        differences.append(
            f"Type mismatch at {path}: {type(original).__name__} != {type(reconstructed).__name__}"
        )
        return differences

    if isinstance(original, dict):
        # Check for missing keys in reconstructed
        orig_keys = set(original.keys())
        recon_keys = set(reconstructed.keys())

        missing_keys = orig_keys - recon_keys
        extra_keys = recon_keys - orig_keys

        for key in missing_keys:
            differences.append(f"Missing key at {path}: '{key}'")

        for key in extra_keys:
            differences.append(f"Extra key at {path}: '{key}'")

        # Compare values for common keys
        for key in orig_keys & recon_keys:
            key_path = f"{path}.{key}" if path else key
            differences.extend(
                deep_compare_structures(original[key], reconstructed[key], key_path)
            )

    elif isinstance(original, list):
        if len(original) != len(reconstructed):
            differences.append(
                f"Length mismatch at {path}: {len(original)} != {len(reconstructed)}"
            )
            return differences

        for i, (orig_item, recon_item) in enumerate(zip(original, reconstructed)):
            item_path = f"{path}[{i}]"
            differences.extend(
                deep_compare_structures(orig_item, recon_item, item_path)
            )

    else:
        # Compare primitive values
        if original != reconstructed:
            differences.append(
                f"Value mismatch at {path}: {repr(original)} != {repr(reconstructed)}"
            )

    return differences


def analyze_collection_features(collection_data: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze what features are present in a Postman collection.

    Args:
        collection_data: Raw collection data

    Returns:
        Dictionary describing collection features
    """
    features = {
        "has_collection_variables": False,
        "has_collection_auth": False,
        "has_collection_events": False,
        "has_folders": False,
        "has_nested_folders": False,
        "request_count": 0,
        "folder_count": 0,
        "auth_types": set(),
        "event_types": set(),
        "body_modes": set(),
        "response_examples": 0,
        "max_nesting_depth": 0,
    }

    # Check collection-level features
    if collection_data.get("variable"):
        features["has_collection_variables"] = True
    if collection_data.get("auth"):
        features["has_collection_auth"] = True
        features["auth_types"].add(collection_data["auth"].get("type", "unknown"))
    if collection_data.get("event"):
        features["has_collection_events"] = True
        for event in collection_data["event"]:
            features["event_types"].add(event.get("listen", "unknown"))

    # Analyze items recursively
    def analyze_items(items: list[dict[str, Any]], depth: int = 0):
        features["max_nesting_depth"] = max(features["max_nesting_depth"], depth)

        for item in items:
            if "request" in item:
                # It's a request
                features["request_count"] += 1

                request = item["request"]
                if request.get("auth"):
                    features["auth_types"].add(request["auth"].get("type", "unknown"))

                if request.get("body"):
                    body_mode = request["body"].get("mode", "none")
                    features["body_modes"].add(body_mode)

                if item.get("event"):
                    for event in item["event"]:
                        features["event_types"].add(event.get("listen", "unknown"))

                if item.get("response"):
                    features["response_examples"] += len(item["response"])

            else:
                # It's a folder
                features["folder_count"] += 1
                features["has_folders"] = True
                if depth > 0:
                    features["has_nested_folders"] = True

                if item.get("item"):
                    analyze_items(item["item"], depth + 1)

    if collection_data.get("item"):
        analyze_items(collection_data["item"])

    # Convert sets to lists for JSON serialization
    features["auth_types"] = list(features["auth_types"])
    features["event_types"] = list(features["event_types"])
    features["body_modes"] = list(features["body_modes"])

    return features


def validate_postman_collection(json_file_path: str) -> dict[str, Any]:
    """
    Validate that PostmanCollection dataclass completely models a Postman collection.

    Args:
        json_file_path: Path to Postman collection JSON file

    Returns:
        Validation results dictionary
    """
    print(f"🔍 Validating Postman collection: {json_file_path}")

    # Load original JSON
    try:
        with open(json_file_path, encoding="utf-8") as f:
            original_data = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to load JSON: {e}"}

    print(f"✅ Loaded JSON file ({len(json.dumps(original_data))} characters)")

    # Analyze collection features
    features = analyze_collection_features(original_data)
    print("📊 Collection Analysis:")
    print(f"   - Requests: {features['request_count']}")
    print(f"   - Folders: {features['folder_count']}")
    print(f"   - Max nesting depth: {features['max_nesting_depth']}")
    print(f"   - Collection variables: {features['has_collection_variables']}")
    print(f"   - Collection auth: {features['has_collection_auth']}")
    print(f"   - Collection events: {features['has_collection_events']}")
    print(f"   - Auth types: {features['auth_types']}")
    print(f"   - Event types: {features['event_types']}")
    print(f"   - Body modes: {features['body_modes']}")
    print(f"   - Response examples: {features['response_examples']}")

    # Parse into PostmanCollection
    try:
        collection = PostmanCollection.from_dict(original_data)
        print("✅ Successfully parsed into PostmanCollection dataclass")
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse collection: {e}",
            "features": features,
        }

    # Convert back to dictionary
    try:
        reconstructed_data = collection.to_dict()
        print("✅ Successfully converted back to dictionary")
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to convert to dict: {e}",
            "features": features,
        }

    # Compare structures
    differences = deep_compare_structures(original_data, reconstructed_data)

    if differences:
        print(f"❌ Found {len(differences)} structural differences:")
        for diff in differences[:10]:  # Show first 10 differences
            print(f"   - {diff}")
        if len(differences) > 10:
            print(f"   ... and {len(differences) - 10} more differences")

        return {
            "success": False,
            "differences": differences,
            "features": features,
            "difference_count": len(differences),
        }
    else:
        print("🎉 Perfect match! All structure captured by dataclass models.")

        return {
            "success": True,
            "features": features,
            "message": "Complete structural validation passed",
        }


def main():
    """Main validation function."""
    if len(sys.argv) != 2:
        print("Usage: python validate_structure.py <postman_collection.json>")
        sys.exit(1)

    json_file = sys.argv[1]

    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        sys.exit(1)

    # Run validation
    result = validate_postman_collection(json_file)

    # Print results
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    if result["success"]:
        print(
            "✅ SUCCESS: Dataclass models completely capture the collection structure!"
        )
        print(
            f"✅ All {result['features']['request_count']} requests modeled correctly"
        )
        print(f"✅ All {result['features']['folder_count']} folders modeled correctly")
        print("✅ All variables, parameters, events, and auth captured")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        if "difference_count" in result:
            print(f"❌ Found {result['difference_count']} structural differences")
            print("❌ Dataclass models need enhancement to capture missing structure")
        sys.exit(1)


if __name__ == "__main__":
    main()
