"""Integration logic for migrating functions to domolibrary2."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_integration(
    function_code: str,
    target_path: Path,
    function_name: str,
) -> tuple[bool, list[str]]:
    """Validate function before integration.

    Args:
        function_code: Generated function code
        target_path: Target file path
        function_name: Function name

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    # Check if function code is not empty
    if not function_code or not function_code.strip():
        errors.append("Function code is empty")

    # Check if function name is in code
    if function_name not in function_code:
        errors.append(f"Function name '{function_name}' not found in code")

    # Check for required decorators
    if "@gd.route_function" not in function_code:
        errors.append("Missing @gd.route_function decorator")

    # Check if target file exists and function already exists
    if target_path.exists():
        existing_code = target_path.read_text(encoding="utf-8")
        if (
            f"def {function_name}" in existing_code
            or f"async def {function_name}" in existing_code
        ):
            errors.append(f"Function '{function_name}' already exists in {target_path}")

    return len(errors) == 0, errors


def check_naming_conflicts(
    function_name: str,
    module_path: str,
    routes_dir: str = "src/domolibrary2/routes",
) -> list[str]:
    """Check for naming conflicts in the target module.

    Args:
        function_name: Function name to check
        module_path: Target module path
        routes_dir: Directory containing routes

    Returns:
        List of conflict warnings
    """
    warnings = []

    # This could be enhanced with codegraph queries
    # For now, simple file-based check
    routes_path = Path(routes_dir)
    module_parts = module_path.split(".")

    if len(module_parts) > 1:
        target_file = (
            routes_path / "/".join(module_parts[:-1]) / f"{module_parts[-1]}.py"
        )
    else:
        target_file = routes_path / f"{module_path}.py"

    if target_file.exists():
        content = target_file.read_text(encoding="utf-8")
        if function_name in content:
            # Check if it's actually a function definition
            if (
                f"def {function_name}" in content
                or f"async def {function_name}" in content
            ):
                warnings.append(
                    f"Function '{function_name}' may conflict with existing code in {target_file}"
                )

    return warnings
