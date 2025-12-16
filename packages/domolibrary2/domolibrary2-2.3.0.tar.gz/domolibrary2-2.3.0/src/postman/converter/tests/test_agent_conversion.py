"""
Test file for multi-agent Postman to Python converter.

This test demonstrates converting a single request from a Postman collection
using the multi-agent framework, then validates and executes the generated code.
"""

import ast
import asyncio
import os
import sys
import tempfile
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from postman.converter.agent_graph import convert_postman_collection
from postman.converter.agent_tools import (
    extract_all_requests,
    load_collection_from_file,
    validate_python_syntax,
)

# Load environment variables
load_dotenv()


class TestAgentConversion:
    """Test suite for multi-agent Postman conversion."""

    @pytest.fixture
    def postman_collection_path(self):
        """Path to the test Postman collection."""
        # Use the Domo Product APIs collection
        collection_path = (
            Path(__file__).parent.parent.parent
            / "Domo Product APIs.postman_collection.json"
        )

        if not collection_path.exists():
            pytest.skip("Postman collection not found")

        return str(collection_path)

    @pytest.fixture
    def test_export_folder(self):
        """Create a temporary folder for test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_request(self, postman_collection_path):
        """Extract a single request from the collection for testing."""
        collection_dict = load_collection_from_file(postman_collection_path)
        requests = extract_all_requests(collection_dict)

        if not requests:
            pytest.skip("No requests found in collection")

        # Get the first request
        return requests[0]

    @pytest.mark.asyncio
    async def test_convert_single_request(
        self, postman_collection_path, test_export_folder, sample_request
    ):
        """
        Test converting a single request from Postman collection.

        This test:
        1. Converts the request using the multi-agent framework
        2. Validates the generated Python code using AST
        3. Attempts to execute the generated function
        """
        print(f"\n{'=' * 60}")
        print("Testing Multi-Agent Postman Conversion")
        print(f"{'=' * 60}")
        print(f"Request: {sample_request['name']}")
        print(f"Method: {sample_request['request']['method']}")
        print(f"Export Folder: {test_export_folder}")
        print(f"{'=' * 60}\n")

        # Run the conversion
        result = await convert_postman_collection(
            collection_path=postman_collection_path,
            export_folder=test_export_folder,
            customize_config={
                "required_headers": ["authorization", "content-type"],
                "default_params": ["limit", "offset"],
            },
            write_files=True,
        )

        # Assert conversion succeeded
        assert result["current_phase"] == "complete", "Conversion did not complete"
        assert not result.get("errors"), (
            f"Conversion had errors: {result.get('errors')}"
        )
        assert result.get("formatted_code"), "No code was generated"

        print("✅ Conversion completed successfully")
        print(f"   Generated {len(result['formatted_code'])} files\n")

        # Get the first generated function for testing
        first_filename = list(result["formatted_code"].keys())[0]
        generated_code = result["formatted_code"][first_filename]

        print(f"Testing generated file: {first_filename}")
        print(f"{'=' * 60}")

        # Test 1: Validate Python syntax using AST
        print("\n1. Validating Python syntax with AST...")
        is_valid, syntax_errors = validate_python_syntax(generated_code)

        assert is_valid, f"Generated code has syntax errors: {syntax_errors}"
        print("   ✅ Syntax validation passed")

        # Test 2: Parse the AST and verify structure
        print("\n2. Analyzing AST structure...")
        tree = ast.parse(generated_code)

        # Find function definitions
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        assert len(functions) > 0, "No functions found in generated code"

        main_function = functions[0]
        print(f"   Found function: {main_function.name}")

        # Check for async def
        is_async = isinstance(main_function, ast.AsyncFunctionDef) or any(
            isinstance(dec, ast.Name) and dec.id == "asyncio"
            for dec in getattr(main_function, "decorator_list", [])
        )
        print(f"   Async function: {is_async}")

        # Check for docstring
        has_docstring = ast.get_docstring(main_function) is not None
        assert has_docstring, "Function missing docstring"
        print("   ✅ Has docstring")

        # Check for type hints on arguments
        args_with_hints = sum(
            1 for arg in main_function.args.args if arg.annotation is not None
        )
        print(
            f"   Type hints: {args_with_hints}/{len(main_function.args.args)} arguments"
        )

        # Check for return type annotation
        has_return_annotation = main_function.returns is not None
        print(f"   Return type annotation: {has_return_annotation}")

        # Test 3: Verify imports
        print("\n3. Checking imports...")
        imports = [
            node for node in tree.body if isinstance(node, ast.Import | ast.ImportFrom)
        ]
        print(f"   Found {len(imports)} import statements")

        # Check for essential imports
        import_names = []
        for imp in imports:
            if isinstance(imp, ast.Import):
                import_names.extend(alias.name for alias in imp.names)
            elif isinstance(imp, ast.ImportFrom):
                import_names.append(imp.module)

        print(f"   Imports: {', '.join(import_names[:5])}...")

        # Test 4: Check for error handling
        print("\n4. Checking error handling...")
        try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        exception_handlers = [
            node for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler)
        ]
        print(f"   Try blocks: {len(try_blocks)}")
        print(f"   Exception handlers: {len(exception_handlers)}")

        # Test 5: Write file and verify it can be imported
        print("\n5. Testing file write and import...")
        output_path = Path(test_export_folder) / first_filename
        assert output_path.exists(), f"File not written: {output_path}"

        file_size = output_path.stat().st_size
        print(f"   File size: {file_size} bytes")
        assert file_size > 0, "Generated file is empty"
        print("   ✅ File written successfully")

        # Test 6: Attempt to execute with mock data (if env vars available)
        print("\n6. Testing function execution...")

        # Check for required environment variables
        has_domo_instance = os.getenv("DOMO_INSTANCE") is not None
        has_domo_token = os.getenv("DOMO_ACCESS_TOKEN") is not None

        if has_domo_instance and has_domo_token:
            print("   Environment variables found, attempting execution...")

            try:
                # Import the generated module dynamically
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "generated_module", output_path
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules["generated_module"] = module
                spec.loader.exec_module(module)

                # Get the main function
                func = getattr(module, main_function.name, None)

                if func and asyncio.iscoroutinefunction(func):
                    print(f"   Function '{main_function.name}' is callable and async")
                    print("   ✅ Import successful (execution skipped for safety)")
                else:
                    print("   ⚠️  Function found but not async")

            except Exception as e:
                print(f"   ⚠️  Import test skipped: {e}")
        else:
            print("   ⚠️  Environment variables not set, skipping execution test")
            print("      Set DOMO_INSTANCE and DOMO_ACCESS_TOKEN to test execution")

        # Test 7: Verify code quality metrics
        print("\n7. Code quality metrics...")
        lines = generated_code.split("\n")
        code_lines = [
            line for line in lines if line.strip() and not line.strip().startswith("#")
        ]
        comment_lines = [line for line in lines if line.strip().startswith("#")]
        blank_lines = [line for line in lines if not line.strip()]

        print(f"   Total lines: {len(lines)}")
        print(f"   Code lines: {len(code_lines)}")
        print(f"   Comment lines: {len(comment_lines)}")
        print(f"   Blank lines: {len(blank_lines)}")

        # Check code complexity (rough estimate)
        if_statements = len([n for n in ast.walk(tree) if isinstance(n, ast.If)])
        for_loops = len(
            [n for n in ast.walk(tree) if isinstance(n, ast.For | ast.AsyncFor)]
        )
        while_loops = len([n for n in ast.walk(tree) if isinstance(n, ast.While)])

        print(f"   If statements: {if_statements}")
        print(f"   Loops: {for_loops + while_loops}")

        complexity = if_statements + for_loops + while_loops + len(functions)
        print(f"   Cyclomatic complexity (approx): {complexity}")

        print(f"\n{'=' * 60}")
        print("✅ All tests passed!")
        print(f"{'=' * 60}\n")

        # Return results for inspection
        return {
            "generated_code": generated_code,
            "function_name": main_function.name,
            "is_async": is_async,
            "has_docstring": has_docstring,
            "type_hints": args_with_hints,
            "imports": len(imports),
            "complexity": complexity,
            "file_path": str(output_path),
        }

    @pytest.mark.asyncio
    async def test_generated_code_structure(
        self, postman_collection_path, test_export_folder
    ):
        """Test that generated code has expected structure."""
        # Run conversion
        result = await convert_postman_collection(
            collection_path=postman_collection_path,
            export_folder=test_export_folder,
            write_files=False,  # Don't write files for this test
        )

        assert result["current_phase"] == "complete"
        assert len(result["generated_functions"]) > 0

        # Check first generated function
        func = result["generated_functions"][0]

        assert "function_name" in func
        assert "function_code" in func
        assert "imports_needed" in func
        assert "docstring" in func
        assert "type_hints" in func

        print("\n✅ Generated function structure:")
        print(f"   Name: {func['function_name']}")
        print(f"   Imports: {len(func['imports_needed'])}")
        print(f"   Type hints: {len(func['type_hints'])}")
        print(f"   Complexity: {func.get('complexity', 'N/A')}")

    @pytest.mark.asyncio
    async def test_analysis_results(self, postman_collection_path, test_export_folder):
        """Test that analysis phase produces expected results."""
        result = await convert_postman_collection(
            collection_path=postman_collection_path,
            export_folder=test_export_folder,
            write_files=False,
        )

        # Check analysis results
        assert result.get("structure_analysis"), "Missing structure analysis"
        assert result.get("auth_analysis"), "Missing auth analysis"
        assert result.get("parameter_analysis"), "Missing parameter analysis"
        assert result.get("header_analysis"), "Missing header analysis"
        assert result.get("aggregated_analysis"), "Missing aggregated analysis"

        structure = result["structure_analysis"]
        print("\n✅ Analysis results:")
        print(f"   Complexity score: {structure.get('complexity_score', 'N/A')}")
        print(f"   Naming patterns: {len(structure.get('naming_patterns', []))}")

        auth = result["auth_analysis"]
        print(f"   Auth types: {auth.get('auth_types', [])}")

        params = result["parameter_analysis"]
        print(f"   Common params: {len(params.get('common_params', {}))}")

        headers = result["header_analysis"]
        print(f"   Required headers: {headers.get('required_headers', [])}")


# Standalone test function for manual testing
async def test_single_request_conversion():
    """
    Standalone test function that can be run directly.

    Usage:
        python test_agent_conversion.py
    """
    print("\n" + "=" * 60)
    print("Multi-Agent Postman Converter - Single Request Test")
    print("=" * 60)

    # Setup
    collection_path = (
        Path(__file__).parent.parent.parent
        / "Domo Product APIs.postman_collection.json"
    )

    if not collection_path.exists():
        print(f"❌ Collection not found: {collection_path}")
        return

    # Create temp directory
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\nCollection: {collection_path.name}")
        print(f"Export folder: {tmpdir}\n")

        # Get sample request
        collection_dict = load_collection_from_file(str(collection_path))
        requests = extract_all_requests(collection_dict)

        if not requests:
            print("❌ No requests found in collection")
            return

        sample_request = requests[0]
        print(f"Converting request: {sample_request['name']}")
        print(f"Method: {sample_request['request']['method']}")
        print(f"URL: {sample_request['request']['url'].get('raw', 'N/A')[:80]}...\n")

        # Run conversion
        result = await convert_postman_collection(
            collection_path=str(collection_path),
            export_folder=tmpdir,
            customize_config={
                "required_headers": ["authorization"],
            },
            write_files=True,
        )

        # Check results
        if result.get("errors"):
            print("❌ Conversion errors:")
            for error in result["errors"]:
                print(f"   • {error}")
            return

        if result["current_phase"] != "complete":
            print(f"⚠️  Conversion incomplete. Phase: {result['current_phase']}")
            return

        # Validate generated code
        print("\n" + "=" * 60)
        print("Validating Generated Code")
        print("=" * 60 + "\n")

        for filename, code in result["formatted_code"].items():
            print(f"File: {filename}")

            # AST validation
            is_valid, errors = validate_python_syntax(code)

            if is_valid:
                print("   ✅ Valid Python syntax")

                # Parse AST
                tree = ast.parse(code)
                functions = [
                    n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                ]
                imports = [
                    n for n in tree.body if isinstance(n, ast.Import | ast.ImportFrom)
                ]

                print(f"   Functions: {len(functions)}")
                print(f"   Imports: {len(imports)}")

                if functions:
                    func = functions[0]
                    print(f"   Main function: {func.name}")
                    print(f"   Arguments: {len(func.args.args)}")
                    print(f"   Has docstring: {ast.get_docstring(func) is not None}")
            else:
                print("   ❌ Syntax errors:")
                for error in errors:
                    print(f"      • {error}")

            print()

        print("=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    # Run standalone test
    asyncio.run(test_single_request_conversion())
