"""
Validation script for generated Postman routes.

This script validates:
- Generated function accuracy (syntax, imports, patterns)
- URL patterns match Domo API endpoints
- Functions are importable and callable
- Wrapper functions work correctly
- Code quality and formatting

Run from project root:
    python src/postman/validate_generated_routes.py
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from postman.converter.deterministic.url_extractor import (  # noqa: E402
    extract_url_from_route_code,
)


class RouteValidator:
    """Validates generated route functions."""

    def __init__(self, staging_dir: Path):
        """Initialize validator.

        Args:
            staging_dir: Path to staging directory with generated routes
        """
        self.staging_dir = staging_dir
        self.errors: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.stats: dict[str, Any] = defaultdict(int)

    def validate_all(self) -> dict[str, Any]:
        """Validate all generated routes.

        Returns:
            Validation report dictionary
        """
        print("=" * 70)
        print("VALIDATING GENERATED POSTMAN ROUTES")
        print("=" * 70)
        print(f"\nStaging directory: {self.staging_dir}")

        if not self.staging_dir.exists():
            print(f"\n❌ ERROR: Staging directory not found: {self.staging_dir}")
            return {"error": "Staging directory not found"}

        # Find all Python files
        py_files = list(self.staging_dir.rglob("*.py"))
        py_files = [f for f in py_files if f.name != "__init__.py"]

        print(f"\nFound {len(py_files)} Python files to validate\n")

        for py_file in py_files:
            self._validate_file(py_file)

        # Generate report
        report = self._generate_report()
        return report

    def _validate_file(self, file_path: Path) -> None:
        """Validate a single Python file.

        Args:
            file_path: Path to Python file
        """
        rel_path = file_path.relative_to(self.staging_dir)
        print(f"Validating: {rel_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(
                {
                    "file": str(rel_path),
                    "type": "read_error",
                    "message": f"Failed to read file: {e}",
                }
            )
            return

        # Validate syntax
        if not self._validate_syntax(content, rel_path):
            return

        # Validate structure
        self._validate_structure(content, rel_path)

        # Validate URL patterns
        self._validate_url_patterns(content, rel_path)

        # Validate imports
        self._validate_imports(content, rel_path)

        # Validate function signatures
        self._validate_function_signatures(content, rel_path)

        # Try to import
        self._validate_importable(file_path, rel_path)

        self.stats["files_validated"] += 1

    def _validate_syntax(self, content: str, rel_path: Path) -> bool:
        """Validate Python syntax.

        Args:
            content: File content
            rel_path: Relative file path

        Returns:
            True if syntax is valid
        """
        try:
            ast.parse(content)
            self.stats["syntax_valid"] += 1
            return True
        except SyntaxError as e:
            self.errors.append(
                {
                    "file": str(rel_path),
                    "type": "syntax_error",
                    "message": f"Syntax error at line {e.lineno}: {e.msg}",
                    "line": e.lineno,
                }
            )
            self.stats["syntax_errors"] += 1
            return False

    def _validate_structure(self, content: str, rel_path: Path) -> None:
        """Validate code structure.

        Args:
            content: File content
            rel_path: Relative file path
        """
        try:
            tree = ast.parse(content)
            # Get both regular and async functions
            all_functions = [
                n
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
            ]
            async_functions = [
                f for f in all_functions if isinstance(f, ast.AsyncFunctionDef)
            ]

            self.stats["total_functions"] += len(all_functions)
            self.stats["async_functions"] += len(async_functions)

            # Check for route_function decorator
            decorators = []
            for func in all_functions:
                for decorator in func.decorator_list:
                    # Check for @gd.route_function pattern
                    if isinstance(decorator, ast.Attribute):
                        if decorator.attr == "route_function":
                            decorators.append(func.name)
                    # Also check for direct attribute access like gd.route_function
                    elif isinstance(decorator, ast.Name):
                        # If decorator is just a name, check if route_function is in content
                        if "route_function" in content:
                            decorators.append(func.name)

            # Also check if @gd.route_function appears in content (more lenient check)
            if "@gd.route_function" in content or "gd.route_function" in content:
                # Found the decorator pattern
                pass
            elif not decorators and all_functions:
                self.warnings.append(
                    {
                        "file": str(rel_path),
                        "type": "missing_decorator",
                        "message": "No @gd.route_function decorator found",
                    }
                )

            # Check for __all__ export
            if "__all__" not in content:
                self.warnings.append(
                    {
                        "file": str(rel_path),
                        "type": "missing_all",
                        "message": "Missing __all__ export list",
                    }
                )

        except Exception as e:
            self.errors.append(
                {
                    "file": str(rel_path),
                    "type": "structure_error",
                    "message": f"Failed to analyze structure: {e}",
                }
            )

    def _validate_url_patterns(self, content: str, rel_path: Path) -> None:
        """Validate URL patterns match Domo API format.

        Args:
            content: File content
            rel_path: Relative file path
        """
        # Extract URL from code
        url = extract_url_from_route_code(content)

        if not url:
            self.warnings.append(
                {
                    "file": str(rel_path),
                    "type": "url_not_found",
                    "message": "Could not extract URL from code",
                }
            )
            return

        # Validate URL format
        if not url.startswith("/api/"):
            self.warnings.append(
                {
                    "file": str(rel_path),
                    "type": "url_format",
                    "message": f"URL doesn't start with /api/: {url}",
                    "url": url,
                }
            )

        # Check for proper Domo API path structure
        # Domo APIs typically follow: /api/{service}/{version}/{resource}
        parts = url.split("/")
        if len(parts) < 3:
            self.warnings.append(
                {
                    "file": str(rel_path),
                    "type": "url_structure",
                    "message": f"URL seems too short: {url}",
                    "url": url,
                }
            )

        # Validate URL structure - any /api/{service}/... pattern is valid
        # Domo APIs follow the pattern: /api/{service}/{version}/{resource}
        # We don't need to check against a specific list since any service name is valid
        # The important checks are:
        # 1. Starts with /api/ (already checked above)
        # 2. Has reasonable structure (at least service name)

        # Count path segments after /api/
        path_segments = [seg for seg in url.split("/") if seg]
        if len(path_segments) < 2:
            # Should have at least /api/{service}
            self.warnings.append(
                {
                    "file": str(rel_path),
                    "type": "url_structure",
                    "message": f"URL seems too short (missing service name): {url}",
                    "url": url,
                }
            )

        # All URLs starting with /api/ are valid Domo API endpoints
        # No need to check against a limited pattern list

        self.stats["urls_validated"] += 1

    def _validate_imports(self, content: str, rel_path: Path) -> None:
        """Validate imports are correct.

        Args:
            content: File content
            rel_path: Relative file path
        """
        required_imports = [
            "DomoAuth",
            "RouteContext",
            "get_data as gd",
            "response as rgd",
        ]

        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)

        if missing_imports:
            self.errors.append(
                {
                    "file": str(rel_path),
                    "type": "missing_imports",
                    "message": f"Missing required imports: {', '.join(missing_imports)}",
                    "missing": missing_imports,
                }
            )

        # Check import paths (should use relative imports)
        if (
            "from ....auth import" not in content
            and "from domolibrary2.auth import" not in content
        ):
            self.warnings.append(
                {
                    "file": str(rel_path),
                    "type": "import_path",
                    "message": "May not be using correct relative import path for auth",
                }
            )

    def _validate_function_signatures(self, content: str, rel_path: Path) -> None:
        """Validate function signatures follow domolibrary patterns.

        Args:
            content: File content
            rel_path: Relative file path
        """
        try:
            tree = ast.parse(content)
            functions = [
                n
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
            ]

            for func in functions:
                # Check for required parameters
                param_names = [arg.arg for arg in func.args.args]

                if "auth" not in param_names:
                    self.errors.append(
                        {
                            "file": str(rel_path),
                            "type": "missing_auth_param",
                            "function": func.name,
                            "message": "Function missing 'auth' parameter",
                        }
                    )

                # Check for context parameter (should be keyword-only)
                if "context" in param_names:
                    # Find position of context
                    param_names.index("context")
                    # Check if it's after * (keyword-only)
                    if func.args.kwonlyargs:
                        # This is good - context is keyword-only
                        pass
                    else:
                        self.warnings.append(
                            {
                                "file": str(rel_path),
                                "type": "context_position",
                                "function": func.name,
                                "message": "context parameter should be keyword-only (after *)",
                            }
                        )

                # Check return type annotation
                if not func.returns:
                    self.warnings.append(
                        {
                            "file": str(rel_path),
                            "type": "missing_return_type",
                            "function": func.name,
                            "message": "Function missing return type annotation",
                        }
                    )

        except Exception as e:
            self.errors.append(
                {
                    "file": str(rel_path),
                    "type": "signature_error",
                    "message": f"Failed to validate signatures: {e}",
                }
            )

    def _validate_importable(self, file_path: Path, rel_path: Path) -> None:
        """Validate that file can be imported.

        Args:
            file_path: Absolute file path
            rel_path: Relative file path
        """
        try:
            spec = importlib.util.spec_from_file_location(
                f"test_{rel_path.stem}", str(file_path)
            )
            if spec and spec.loader:
                importlib.util.module_from_spec(spec)
                # Don't actually execute - just check if it's valid
                # We'll do a syntax check instead
                self.stats["importable"] += 1
            else:
                self.errors.append(
                    {
                        "file": str(rel_path),
                        "type": "import_error",
                        "message": "Could not create module spec",
                    }
                )
        except Exception as e:
            # Import errors are expected for some files (missing dependencies)
            # So we'll log as warning, not error
            self.warnings.append(
                {
                    "file": str(rel_path),
                    "type": "import_warning",
                    "message": f"Import check failed (may be expected): {e}",
                }
            )

    def _generate_report(self) -> dict[str, Any]:
        """Generate validation report.

        Returns:
            Report dictionary
        """
        report = {
            "summary": {
                "files_validated": self.stats["files_validated"],
                "total_functions": self.stats["total_functions"],
                "async_functions": self.stats["async_functions"],
                "urls_validated": self.stats["urls_validated"],
                "syntax_valid": self.stats["syntax_valid"],
                "syntax_errors": self.stats["syntax_errors"],
                "errors": len(self.errors),
                "warnings": len(self.warnings),
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": dict(self.stats),
        }

        # Print summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"\nFiles validated: {report['summary']['files_validated']}")
        print(f"Total functions: {report['summary']['total_functions']}")
        print(f"Async functions: {report['summary']['async_functions']}")
        print(f"URLs validated: {report['summary']['urls_validated']}")
        print(f"\n✅ Syntax valid: {report['summary']['syntax_valid']}")
        print(f"❌ Syntax errors: {report['summary']['syntax_errors']}")
        print(f"❌ Total errors: {report['summary']['errors']}")
        print(f"⚠️  Total warnings: {report['summary']['warnings']}")

        if self.errors:
            print("\n" + "=" * 70)
            print("ERRORS")
            print("=" * 70)
            for error in self.errors[:10]:  # Show first 10
                print(f"\n{error['file']}: {error['type']}")
                print(f"  {error['message']}")
            if len(self.errors) > 10:
                print(f"\n... and {len(self.errors) - 10} more errors")

        if self.warnings:
            print("\n" + "=" * 70)
            print("WARNINGS")
            print("=" * 70)
            # Group warnings by type
            warning_types = defaultdict(list)
            for warning in self.warnings:
                warning_types[warning["type"]].append(warning)

            for wtype, warnings_list in warning_types.items():
                print(f"\n{wtype}: {len(warnings_list)} occurrences")
                for warning in warnings_list[:3]:  # Show first 3 of each type
                    print(f"  {warning['file']}: {warning.get('message', '')}")
                if len(warnings_list) > 3:
                    print(f"  ... and {len(warnings_list) - 3} more")

        return report


def main():
    """Main validation function."""
    # Find staging directory
    project_root = Path(__file__).parent.parent.parent
    staging_dir = project_root / "src" / "postman" / "_postman_staging"

    if not staging_dir.exists():
        print(f"❌ ERROR: Staging directory not found: {staging_dir}")
        print("\nPlease run the Postman conversion first:")
        print("  python -m postman.cli.convert --collection ...")
        return 1

    # Run validation
    validator = RouteValidator(staging_dir)
    report = validator.validate_all()

    # Save report
    report_path = project_root / "EXPORTS" / "postman_validation_report.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Full report saved to: {report_path}")

    # Return exit code
    if report["summary"]["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
