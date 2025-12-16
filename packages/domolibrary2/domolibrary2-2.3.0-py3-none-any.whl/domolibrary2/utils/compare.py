"""
Data Comparison Utilities

This module provides utilities for comparing complex data structures like
dictionaries and lists, with detailed difference reporting.

Functions:
    compare_dicts: Recursively compare two dictionaries and return differences

Example:
    >>> dict1 = {"user": {"name": "John", "age": 30}, "items": [1, 2, 3]}
    >>> dict2 = {"user": {"name": "Jane", "age": 30}, "items": [1, 2]}
    >>> differences = compare_dicts(dict1, dict2)
    >>> for diff in differences:
    ...     print(f"{diff['key']}: {diff['message']}")
"""

__all__ = ["compare_dicts"]


def compare_dicts(dict1: object, dict2: object, path: str = "") -> list[dict[str, str]]:
    """
    Recursively compare two dictionaries (and lists) and return differences.

    This function performs a deep comparison of two data structures, supporting
    nested dictionaries and lists. It returns a detailed list of all differences
    found between the structures.

    Args:
        dict1 (Any): First data structure to compare (typically dict or list)
        dict2 (Any): Second data structure to compare (typically dict or list)
        path (str): Current path in the data structure (used for recursion)

    Returns:
        list[dict[str, str]]: list of difference dictionaries, each containing:
            - 'key': The path to the difference
            - 'message': Description of the difference

    Example:
        >>> data1 = {
        ...     "user": {"name": "John", "age": 30},
        ...     "active": True,
        ...     "tags": ["admin", "user"]
        ... }
        >>> data2 = {
        ...     "user": {"name": "Jane", "age": 30, "email": "jane@example.com"},
        ...     "tags": ["user"]
        ... }
        >>> differences = compare_dicts(data1, data2)
        >>> for diff in differences:
        ...     print(f"{diff['key']}: {diff['message']}")
        user.name: Value mismatch at 'user.name': John != Jane
        user.email: found in second dict but not in first.
        active: found in first dict but not in second.
        tags[0]: Extra item in first list at 'tags[0]': admin

    Note:
        - Handles nested dictionaries and lists recursively
        - Identifies missing keys in either dictionary
        - Detects value mismatches at any level
        - Reports extra items in lists with their positions
        - Ignores None values when reporting missing keys
    """
    diff_ls = []

    if isinstance(dict1, dict) and isinstance(dict2, dict):
        # Compare dictionary keys and values
        for key in dict1.keys():
            if key not in dict2:
                if dict1[key] is not None:
                    diff_ls.append(
                        {
                            "key": path + str(key),
                            "message": "found in first dict but not in second.",
                        }
                    )
            else:
                # Recursively compare nested values
                nested_diffs = compare_dicts(dict1[key], dict2[key], path + f"{key}.")
                diff_ls.extend(nested_diffs)

        # Check for keys in second dict that aren't in first
        for key in dict2.keys():
            if key not in dict1:
                if dict2[key] is not None:
                    diff_ls.append(
                        {
                            "key": path + str(key),
                            "message": "found in second dict but not in first.",
                        }
                    )

    elif isinstance(dict1, list) and isinstance(dict2, list):
        # Compare lists element by element
        min_len = min(len(dict1), len(dict2))

        # Compare common elements
        for i in range(min_len):
            nested_diffs = compare_dicts(dict1[i], dict2[i], path + f"[{i}].")
            diff_ls.extend(nested_diffs)

        # Check for extra elements in first list
        if len(dict1) > len(dict2):
            for i in range(min_len, len(dict1)):
                diff_ls.append(
                    {
                        "key": f"{path}[{i}]",
                        "message": f"Extra item in first list at '{path}[{i}]': {dict1[i]}",
                    }
                )

        # Check for extra elements in second list
        elif len(dict2) > len(dict1):
            for i in range(min_len, len(dict2)):
                diff_ls.append(
                    {
                        "key": f"{path}[{i}]",
                        "message": f"Extra item in second list at '{path}[{i}]': {dict2[i]}",
                    }
                )
    else:
        # Compare primitive values
        if dict1 != dict2:
            # Remove trailing dot from path for cleaner output
            clean_path = path[:-1] if path.endswith(".") else path
            diff_ls.append(
                {
                    "key": clean_path,
                    "message": f"Value mismatch at '{clean_path}': {dict1} != {dict2}",
                }
            )

    return diff_ls
