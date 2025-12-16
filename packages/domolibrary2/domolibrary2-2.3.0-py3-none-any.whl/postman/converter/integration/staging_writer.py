"""Staging area writer.

This module writes generated route functions to the staging area
in an organized structure.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class StagingWriter:
    """Writes generated code to staging area."""

    def __init__(self, staging_root: str | Path):
        """Initialize staging writer.

        Args:
            staging_root: Root directory for staging area
                (e.g., "src/postman/_postman_staging")
        """
        self.staging_root = Path(staging_root)
        self.staging_root.mkdir(parents=True, exist_ok=True)

    def write_module(
        self,
        module_name: str,
        submodule_name: str,
        functions: list[dict[str, Any]],
        imports: list[str] | None = None,
    ) -> Path:
        """Write a module file with functions.

        Args:
            module_name: Module name (e.g., "accounts") - should be sanitized
            submodule_name: Submodule name (e.g., "core") - should be sanitized
            functions: List of function dictionaries with "name" and "code"
            imports: List of import statements

        Returns:
            Path to written file
        """
        # Sanitize module and submodule names for safe file paths
        module_name = self._sanitize_path_component(module_name)
        submodule_name = self._sanitize_path_component(submodule_name)

        # Create module directory
        module_dir = self.staging_root / module_name
        module_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py if it doesn't exist
        init_file = module_dir / "__init__.py"
        if not init_file.exists():
            self._write_init_file(init_file, [])

        # Write submodule file (ensure .py extension is safe)
        submodule_file = module_dir / f"{submodule_name}.py"

        # Build file content
        content_parts = []

        # Add header
        content_parts.append('"""')
        content_parts.append(f"{module_name.title()} {submodule_name.title()} Routes")
        content_parts.append("")
        content_parts.append(
            f"Generated from Postman collection. Module: {module_name}, Submodule: {submodule_name}"
        )
        content_parts.append('"""')
        content_parts.append("")

        # Add imports
        if imports:
            for imp in imports:
                content_parts.append(imp)
            content_parts.append("")

        # Add standard imports if not provided
        if not imports or not any("DomoAuth" in imp for imp in imports):
            content_parts.append("import httpx")
            content_parts.append("")
            content_parts.append("from ....auth import DomoAuth")
            content_parts.append(
                "from ....client import get_data as gd, response as rgd"
            )
            content_parts.append("from ....client.context import RouteContext")
            content_parts.append("")
            content_parts.append("")

        # Add functions
        function_names = []
        for func in functions:
            func_code = func.get("code", "")
            func_name = func.get("name", "")
            if func_code:
                content_parts.append(func_code)
                content_parts.append("")
                content_parts.append("")
                if func_name:
                    function_names.append(func_name)

        # Add __all__
        if function_names:
            content_parts.append("__all__ = [")
            for name in function_names:
                content_parts.append(f'    "{name}",')
            content_parts.append("]")

        # Write file
        content = "\n".join(content_parts)
        with open(submodule_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Update __init__.py
        self._update_init_file(init_file, function_names, submodule_name)

        return submodule_file

    def _write_init_file(self, init_file: Path, exports: list[str]) -> None:
        """Write or update __init__.py file."""
        content_parts = ['"""', "Module exports", '"""', ""]

        if exports:
            content_parts.append("__all__ = [")
            for export in exports:
                content_parts.append(f'    "{export}",')
            content_parts.append("]")
            content_parts.append("")

        content = "\n".join(content_parts)
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(content)

    def _update_init_file(
        self, init_file: Path, new_exports: list[str], submodule: str
    ) -> None:
        """Update __init__.py with new exports."""
        # Read existing content
        existing_exports = []
        if init_file.exists():
            with open(init_file, encoding="utf-8") as f:
                content = f.read()
                # Try to extract existing __all__
                if "__all__" in content:
                    # Simple extraction (could be improved)
                    for line in content.split("\n"):
                        if line.strip().startswith('"') and "__all__" in content:
                            export = line.strip().strip('",')
                            if export:
                                existing_exports.append(export)

        # Add import statement for submodule
        all_exports = list(set(existing_exports + new_exports))

        # Write updated __init__.py
        content_parts = ['"""', "Module exports", '"""', ""]
        content_parts.append(f"from .{submodule} import *")
        content_parts.append("")

        if all_exports:
            content_parts.append("__all__ = [")
            for export in sorted(all_exports):
                content_parts.append(f'    "{export}",')
            content_parts.append("]")

        content = "\n".join(content_parts)
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(content)

    def ensure_staging_structure(self) -> None:
        """Ensure staging directory structure exists."""
        # Create root __init__.py
        root_init = self.staging_root / "__init__.py"
        if not root_init.exists():
            with open(root_init, "w", encoding="utf-8") as f:
                f.write('"""Postman-generated routes."""\n')

    def _sanitize_path_component(self, name: str) -> str:
        """Sanitize a path component to be alphanumeric with underscores/hyphens only.

        Args:
            name: Path component name

        Returns:
            Sanitized name safe for file/folder names
        """
        # Replace spaces and special chars with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        # Remove leading/trailing underscores and hyphens
        sanitized = sanitized.strip("_-")
        # Ensure it's not empty
        if not sanitized:
            sanitized = "misc"
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = "_" + sanitized
        return sanitized.lower()
