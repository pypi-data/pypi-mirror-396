"""Route discovery.

This module discovers existing route functions in domolibrary by scanning
the routes directory and extracting function metadata.
"""

from __future__ import annotations

import ast
import functools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..deterministic.url_extractor import extract_url_from_route_code
from ..exceptions import RouteDiscoveryError


@dataclass
class RouteInfo:
    """Information about a discovered route function."""

    function_name: str
    module: str
    url: str | None = None
    method: str = "GET"
    file_path: str = ""
    line_number: int = 0
    docstring: str = ""
    signature: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function_name": self.function_name,
            "module": self.module,
            "url": self.url,
            "method": self.method,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "docstring": self.docstring,
            "signature": self.signature,
        }


@dataclass
class RouteRegistry:
    """Registry of all discovered routes."""

    routes: dict[str, RouteInfo] = field(default_factory=dict)

    def add_route(self, route_info: RouteInfo) -> None:
        """Add a route to the registry."""
        self.routes[route_info.function_name] = route_info

    def get_route(self, function_name: str) -> RouteInfo | None:
        """Get route by function name."""
        return self.routes.get(function_name)

    def get_routes_by_module(self, module: str) -> list[RouteInfo]:
        """Get all routes in a specific module."""
        return [route for route in self.routes.values() if route.module == module]

    def to_dict(self) -> dict[str, dict[str, Any]]:
        """Convert to dictionary."""
        return {name: info.to_dict() for name, info in self.routes.items()}


@functools.lru_cache(maxsize=1)
def _discover_routes_cached(routes_dir_str: str) -> RouteRegistry:
    """Cached route discovery (internal)."""
    routes_dir = Path(routes_dir_str)
    if not routes_dir.exists():
        raise RouteDiscoveryError(f"Routes directory not found: {routes_dir}")

    registry = RouteRegistry()

    # Walk through all Python files in routes directory
    for py_file in routes_dir.rglob("*.py"):
        # Skip __init__.py and __pycache__
        if py_file.name == "__init__.py" or "__pycache__" in str(py_file):
            continue

        try:
            routes = _extract_routes_from_file(py_file, routes_dir)
            for route in routes:
                registry.add_route(route)
        except Exception as e:
            # Log error but continue
            print(f"Warning: Error processing {py_file}: {e}")

    return registry


def discover_routes(routes_dir: str | Path) -> RouteRegistry:
    """Discover all route functions in the routes directory.

    Args:
        routes_dir: Path to domolibrary routes directory
            (e.g., "src/domolibrary2/routes")

    Returns:
        RouteRegistry with all discovered routes
    """
    # Use cached version for performance
    routes_dir_str = str(Path(routes_dir).resolve())
    return _discover_routes_cached(routes_dir_str)


def _extract_routes_from_file(file_path: Path, routes_dir: Path) -> list[RouteInfo]:
    """Extract route functions from a Python file.

    Args:
        file_path: Path to Python file
        routes_dir: Base routes directory

    Returns:
        List of RouteInfo objects
    """
    routes = []

    # Read file content
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Parse AST
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return routes

    # Calculate module path
    # routes_dir is typically "src/domolibrary2/routes"
    # We want module like "domolibrary2.routes.account.core"
    try:
        # Get path relative to routes_dir parent (src/domolibrary2)
        # file_path: src/domolibrary2/routes/account/core.py
        # routes_dir.parent: src/domolibrary2
        # relative_path should be: domolibrary2/routes/account/core
        relative_path = file_path.relative_to(routes_dir.parent.parent)
        module_parts = list(relative_path.with_suffix("").parts)
        # Should be: ['domolibrary2', 'routes', 'account', 'core']
        module = ".".join(module_parts)
    except ValueError:
        # Fallback: try relative to routes_dir.parent
        try:
            relative_path = file_path.relative_to(routes_dir.parent)
            module_parts = list(relative_path.with_suffix("").parts)
            # If first part is not 'domolibrary2', add it
            if module_parts and module_parts[0] != "domolibrary2":
                # Check if routes_dir contains domolibrary2
                routes_parts = list(routes_dir.parts)
                if "domolibrary2" in routes_parts:
                    domo_idx = routes_parts.index("domolibrary2")
                    # Prepend domolibrary2 and routes
                    module_parts = (
                        ["domolibrary2"]
                        + routes_parts[domo_idx + 1 :]
                        + module_parts[1:]
                    )
            module = ".".join(module_parts)
        except ValueError:
            # Last resort: construct manually
            file_str = str(file_path)
            if "domolibrary2" in file_str and "routes" in file_str:
                # Extract from path string
                parts = file_str.replace("\\", "/").split("/")
                try:
                    domo_idx = parts.index("domolibrary2")
                    module_parts = parts[domo_idx:-1]  # Exclude .py
                    module = ".".join(module_parts)
                except ValueError:
                    module = "domolibrary2.routes.unknown"
            else:
                module = "domolibrary2.routes.unknown"

    # Find all functions decorated with @gd.route_function
    # Use recursive function to find all function definitions (including async)
    def find_functions(node):
        """Recursively find all function definitions."""
        functions = []
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            functions.append(node)
        # Also check nested functions
        for child in ast.iter_child_nodes(node):
            functions.extend(find_functions(child))
        return functions

    all_functions = find_functions(tree)

    for node in all_functions:
        # Check if function has @gd.route_function decorator
        has_route_decorator = False
        for decorator in node.decorator_list:
            # Handle @gd.route_function (Attribute with value=Name(id='gd'), attr='route_function')
            if isinstance(decorator, ast.Attribute):
                if decorator.attr == "route_function":
                    has_route_decorator = True
                    break
            # Handle @route_function() (Call with func=Attribute or Name)
            elif isinstance(decorator, ast.Call):
                func = decorator.func
                if isinstance(func, ast.Attribute) and func.attr == "route_function":
                    has_route_decorator = True
                    break
                elif isinstance(func, ast.Name) and func.id == "route_function":
                    has_route_decorator = True
                    break
            # Handle @route_function (direct Name)
            elif isinstance(decorator, ast.Name):
                if decorator.id == "route_function":
                    has_route_decorator = True
                    break

        if has_route_decorator:
            # Extract function info
            function_name = node.name
            line_number = node.lineno

            # Extract docstring
            docstring = ast.get_docstring(node) or ""

            # Extract signature
            args = [arg.arg for arg in node.args.args]
            signature = f"{function_name}({', '.join(args)})"

            # Try to extract URL from function body
            url = extract_url_from_route_code(content)

            # Try to infer method from function name or content
            method = _infer_method(function_name, content)

            route_info = RouteInfo(
                function_name=function_name,
                module=module,
                url=url,
                method=method,
                file_path=str(file_path),
                line_number=line_number,
                docstring=docstring,
                signature=signature,
            )
            routes.append(route_info)

    return routes


def _infer_method(function_name: str, content: str) -> str:
    """Infer HTTP method from function name or content.

    Args:
        function_name: Name of function
        content: Function content

    Returns:
        HTTP method (default: GET)
    """
    name_lower = function_name.lower()

    # Check function name
    if name_lower.startswith("get_"):
        return "GET"
    elif name_lower.startswith("post_") or name_lower.startswith("create_"):
        return "POST"
    elif name_lower.startswith("put_") or name_lower.startswith("update_"):
        return "PUT"
    elif name_lower.startswith("patch_"):
        return "PATCH"
    elif name_lower.startswith("delete_") or name_lower.startswith("remove_"):
        return "DELETE"

    # Check content for method parameter
    if 'method="POST"' in content or 'method="post"' in content:
        return "POST"
    elif 'method="PUT"' in content or 'method="put"' in content:
        return "PUT"
    elif 'method="PATCH"' in content or 'method="patch"' in content:
        return "PATCH"
    elif 'method="DELETE"' in content or 'method="delete"' in content:
        return "DELETE"

    return "GET"
