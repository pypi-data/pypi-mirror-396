from typing import Any

__all__ = ["generate_share_account_package"]


def generate_share_account_package(
    code: str,
    package_id: str,
    version: str,
    name: str,
    account_mappings: list[dict[str, Any]],
    environment: str = "LAMBDA",
    language: str = "PYTHON",
    functions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Generate a CodeEngine package dictionary structure.

    Same parameters as generate_package_json but returns a dict instead of JSON string.
    Useful when you need to manipulate the structure before serializing.

    Returns:
        Dictionary in CodeEngine package format
    """
    return {
        "code": code,
        "environment": environment,
        "id": package_id,
        "language": language,
        "manifest": {
            "functions": functions or [],
            "configuration": {"accountsMapping": account_mappings},
        },
        "name": name,
        "version": version,
    }
