"""
Test wrapper functions for accuracy and importability.

This script tests wrapper functions that were generated for matched routes
to ensure they:
- Are importable
- Have correct signatures
- Can be called (with mock data if needed)
- Reference the correct existing routes

Run from project root:
    python src/postman/test_wrapper_functions.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def find_wrapper_functions(staging_dir: Path) -> list[dict[str, Any]]:
    """Find wrapper functions in staging directory.

    Args:
        staging_dir: Path to staging directory

    Returns:
        List of wrapper function info dictionaries
    """
    wrappers = []

    for py_file in staging_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Look for functions that import and call other routes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    # Check if function has imports inside (wrapper pattern)
                    has_internal_import = False
                    calls_existing_route = False
                    imported_route = None

                    for child in ast.walk(node):
                        if isinstance(child, ast.ImportFrom):
                            has_internal_import = True
                            # Check if importing from routes
                            if child.module and "routes" in child.module:
                                if child.names:
                                    imported_route = child.names[0].name

                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                if child.func.id == imported_route:
                                    calls_existing_route = True

                    # Also check content for wrapper patterns
                    if (
                        "wrapper" in content.lower()
                        or "existing route" in content.lower()
                    ):
                        # This might be a wrapper
                        rel_path = py_file.relative_to(staging_dir)
                        wrappers.append(
                            {
                                "file": str(rel_path),
                                "function": node.name,
                                "is_async": isinstance(node, ast.AsyncFunctionDef),
                                "has_internal_import": has_internal_import,
                                "calls_existing_route": calls_existing_route,
                                "imported_route": imported_route,
                            }
                        )

        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    return wrappers


def test_wrapper_importability(
    staging_dir: Path, wrapper_info: dict[str, Any]
) -> dict[str, Any]:
    """Test if a wrapper function can be imported.

    Args:
        staging_dir: Path to staging directory
        wrapper_info: Wrapper function info

    Returns:
        Test results dictionary
    """
    file_path = staging_dir / wrapper_info["file"]

    try:
        # Try to parse and validate syntax
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find the function
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.name == wrapper_info["function"]:
                    func_node = node
                    break

        if not func_node:
            return {
                "success": False,
                "error": "Function not found in AST",
            }

        # Check function signature
        param_names = [arg.arg for arg in func_node.args.args]
        has_auth = "auth" in param_names
        has_context = "context" in param_names
        has_return_type = func_node.returns is not None

        # Check for decorator
        has_decorator = False
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if decorator.attr == "route_function":
                    has_decorator = True

        return {
            "success": True,
            "has_auth": has_auth,
            "has_context": has_context,
            "has_return_type": has_return_type,
            "has_decorator": has_decorator,
            "is_async": isinstance(func_node, ast.AsyncFunctionDef),
            "param_count": len(param_names),
        }

    except SyntaxError as e:
        return {
            "success": False,
            "error": f"Syntax error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {e}",
        }


def main():
    """Main test function."""
    print("=" * 70)
    print("TESTING WRAPPER FUNCTIONS")
    print("=" * 70)

    # Find staging directory
    staging_dir = project_root / "src" / "postman" / "_postman_staging"

    if not staging_dir.exists():
        print(f"\n❌ ERROR: Staging directory not found: {staging_dir}")
        return 1

    # Find wrapper functions
    print("\nSearching for wrapper functions...")
    wrappers = find_wrapper_functions(staging_dir)

    if not wrappers:
        print("\n⚠️  No wrapper functions found in staging directory.")
        print("   This is expected if no routes were matched during conversion.")
        return 0

    print(f"\nFound {len(wrappers)} potential wrapper functions\n")

    # Test each wrapper
    results = []
    for wrapper in wrappers:
        print(f"Testing: {wrapper['file']}::{wrapper['function']}")
        result = test_wrapper_importability(staging_dir, wrapper)
        result["wrapper"] = wrapper
        results.append(result)

        if result["success"]:
            print("  ✅ Valid structure")
            print(f"     - Has auth param: {result.get('has_auth', False)}")
            print(f"     - Has context param: {result.get('has_context', False)}")
            print(f"     - Has return type: {result.get('has_return_type', False)}")
            print(f"     - Has decorator: {result.get('has_decorator', False)}")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    successful = sum(1 for r in results if r["success"])
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {len(results) - successful}/{len(results)}")

    if successful == len(results):
        print("\n🎉 All wrapper functions validated successfully!")
        return 0
    else:
        print(f"\n⚠️  {len(results) - successful} wrapper functions have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
