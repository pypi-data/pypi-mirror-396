"""Helper functions for migration workflow."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_route_instructions() -> str:
    """Load route instructions from .github/instructions/routes.instructions.md.

    Returns:
        Contents of the routes instructions file as a string
    """
    instructions_path = Path(".github/instructions/routes.instructions.md")
    if not instructions_path.exists():
        logger.warning(f"Route instructions not found at {instructions_path}")
        return ""

    try:
        return instructions_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading route instructions: {e}")
        return ""


def parse_index_md(index_path: str) -> dict[str, Any]:
    """Parse index.md file to extract unmigrated functions.

    Args:
        index_path: Path to index.md file

    Returns:
        Dictionary with parsed sections from index.md
    """
    index_file = Path(index_path)
    if not index_file.exists():
        logger.error(f"Index file not found: {index_path}")
        return {"new_routes": []}

    try:
        content = index_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        new_routes = []
        in_new_routes = False

        for line in lines:
            line = line.strip()
            if line.startswith("## New Routes"):
                in_new_routes = True
                continue
            elif line.startswith("##") and in_new_routes:
                # Hit next section, stop parsing
                break

            if in_new_routes and line.startswith("|"):
                # Parse markdown table row
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and parts[0] != "Postman Request":
                    # Skip header row and separator rows
                    if parts[0].startswith("-") or "---" in parts[0]:
                        continue

                    # Table columns: Postman Request | Generated Function | Module | Status
                    route_name = parts[0]
                    generated_function = parts[1] if len(parts) > 1 else ""
                    module = parts[2] if len(parts) > 2 else ""

                    # Try to extract URL from staging file if available
                    # For now, we'll need to get it from the actual staging file
                    url = ""  # Will be populated from staging file if needed

                    new_routes.append(
                        {
                            "name": route_name,
                            "url": url,  # May need to load from staging file
                            "module": module,
                            "generated_function": generated_function,
                            "postman_request": {"name": route_name, "url": url},
                        }
                    )

        return {"new_routes": new_routes}
    except Exception as e:
        logger.error(f"Error parsing index.md: {e}")
        return {"new_routes": []}


def extract_module_from_path(file_path: str) -> tuple[str, str | None]:
    """Extract module and submodule from file path.

    Args:
        file_path: File path (e.g., 'src/domolibrary2/routes/account/core.py')

    Returns:
        Tuple of (module, submodule) where submodule may be None
    """
    path = Path(file_path)
    parts = path.parts

    # Find 'routes' in path
    try:
        routes_idx = parts.index("routes")
        route_parts = parts[routes_idx + 1 :]

        if len(route_parts) == 0:
            return ("", None)

        module = route_parts[0].replace(".py", "")
        submodule = None

        if len(route_parts) > 1:
            # Folder module structure
            submodule = route_parts[-1].replace(".py", "")
            module = ".".join(route_parts[:-1])

        return (module, submodule)
    except ValueError:
        # 'routes' not in path
        return ("", None)


def sanitize_function_name(name: str) -> str:
    """Sanitize function name to be Python-compatible.

    Args:
        name: Function name to sanitize

    Returns:
        Sanitized function name
    """
    # Replace spaces and special chars with underscores
    import re

    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Remove multiple underscores
    name = re.sub(r"_+", "_", name)
    # Remove leading/trailing underscores
    name = name.strip("_")
    # Ensure it starts with a letter
    if name and not name[0].isalpha():
        name = "f_" + name

    return name.lower() if name else "unnamed_function"


def format_code_examples(examples: list[str], max_length: int = 2000) -> str:
    """Format code examples for inclusion in prompts.

    Args:
        examples: List of code example strings
        max_length: Maximum total length

    Returns:
        Formatted string with examples
    """
    if not examples:
        return ""

    formatted = []
    current_length = 0

    for i, example in enumerate(examples):
        if current_length + len(example) > max_length:
            break

        formatted.append(f"Example {i + 1}:\n```python\n{example[:1000]}\n```\n")
        current_length += len(example)

    return "\n".join(formatted)
