"""Code formatting utilities."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from ..exceptions import CodeGenerationError


def format_code(code: str) -> str:
    """Format Python code using Black and isort.

    Args:
        code: Python source code

    Returns:
        Formatted code

    Raises:
        ValueError: If code is invalid Python
    """
    # Validate syntax first
    try:
        ast.parse(code)
    except SyntaxError as e:
        # Raise CodeGenerationError for syntax errors
        raise CodeGenerationError(f"Syntax error in generated code: {e}") from e

    # Try to format with Black
    try:
        code = _format_with_black(code)
    except Exception:
        # If Black fails, return original code
        pass

    # Try to sort imports with isort
    try:
        code = _sort_imports(code)
    except Exception:
        # If isort fails, return code as-is
        pass

    return code


def _format_with_black(code: str) -> str:
    """Format code with Black."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "black", "--code", code],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: write to temp file and format
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "black", str(temp_path)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            formatted = temp_path.read_text(encoding="utf-8")
            return formatted
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    finally:
        temp_path.unlink(missing_ok=True)

    return code


def _sort_imports(code: str) -> str:
    """Sort imports with isort."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "isort", "--code", code],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return code
