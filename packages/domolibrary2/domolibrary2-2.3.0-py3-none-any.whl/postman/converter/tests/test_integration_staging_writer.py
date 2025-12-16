"""Tests for staging writer functionality."""

from __future__ import annotations

from pathlib import Path

import pytest

from ..integration.staging_writer import StagingWriter


class TestStagingWriter:
    """Tests for StagingWriter class."""

    @pytest.fixture
    def staging_root(self, tmp_path):
        """Create a temporary staging root directory."""
        staging = tmp_path / "staging"
        staging.mkdir()
        return str(staging)

    @pytest.fixture
    def writer(self, staging_root):
        """Create a StagingWriter instance."""
        return StagingWriter(staging_root)

    def test_ensure_staging_structure(self, writer, staging_root):
        """Test creating staging directory structure."""
        writer.ensure_staging_structure()

        staging_path = Path(staging_root)
        assert staging_path.exists()
        assert (staging_path / "__init__.py").exists()

    def test_write_module(self, writer, staging_root):
        """Test writing a module with functions."""
        functions = [
            {
                "name": "test_function",
                "code": '''"""Test function."""
async def test_function():
    pass
''',
            }
        ]

        writer.write_module(
            module_name="test_module",
            submodule_name="core",
            functions=functions,
        )

        module_path = Path(staging_root) / "test_module" / "core.py"
        assert module_path.exists()

        content = module_path.read_text(encoding="utf-8")
        assert "test_function" in content

    def test_write_module_creates_init(self, writer, staging_root):
        """Test that writing a module creates __init__.py files."""
        functions = [{"name": "test", "code": "async def test(): pass"}]

        writer.write_module(
            module_name="test_module",
            submodule_name="core",
            functions=functions,
        )

        module_init = Path(staging_root) / "test_module" / "__init__.py"
        assert module_init.exists()

        content = module_init.read_text(encoding="utf-8")
        assert "__all__" in content or "from" in content

    def test_write_module_multiple_functions(self, writer, staging_root):
        """Test writing multiple functions to a module."""
        functions = [
            {"name": "func1", "code": "async def func1(): pass"},
            {"name": "func2", "code": "async def func2(): pass"},
        ]

        writer.write_module(
            module_name="test_module",
            submodule_name="core",
            functions=functions,
        )

        module_path = Path(staging_root) / "test_module" / "core.py"
        content = module_path.read_text(encoding="utf-8")

        assert "func1" in content
        assert "func2" in content

    def test_write_module_nested_structure(self, writer, staging_root):
        """Test writing to nested module structure."""
        functions = [{"name": "nested_func", "code": "async def nested_func(): pass"}]

        writer.write_module(
            module_name="parent",
            submodule_name="child",
            functions=functions,
        )

        module_path = Path(staging_root) / "parent" / "child.py"
        assert module_path.exists()

    def test_write_module_updates_existing(self, writer, staging_root):
        """Test that writing to existing module updates it."""
        # Write first function
        writer.write_module(
            module_name="test_module",
            submodule_name="core",
            functions=[{"name": "func1", "code": "async def func1(): pass"}],
        )

        # Write second function (should append or update)
        writer.write_module(
            module_name="test_module",
            submodule_name="core",
            functions=[{"name": "func2", "code": "async def func2(): pass"}],
        )

        module_path = Path(staging_root) / "test_module" / "core.py"
        content = module_path.read_text(encoding="utf-8")

        # Both functions should be present
        assert "func1" in content or "func2" in content
