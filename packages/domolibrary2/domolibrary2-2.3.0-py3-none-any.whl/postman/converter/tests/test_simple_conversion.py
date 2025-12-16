"""
Quick test for single request conversion.

This is a simplified test that converts just one request from a Postman collection,
validates the Python code, and optionally executes it with real credentials.

Run from project root:
    python src/postman/converter/tests/test_simple_conversion.py
"""

import ast
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure src is in path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Setup EXPORTS directory
exports_dir = project_root / "EXPORTS"
exports_dir.mkdir(exist_ok=True)

from postman.converter.core import PostmanRequestConverter  # noqa: E402
from postman.converter.models import PostmanCollection  # noqa: E402

# Load environment variables
load_dotenv()


async def test_single_request():
    """Test converting a single request."""

    print("\n" + "=" * 70)
    print("[TEST] SINGLE REQUEST CONVERSION TEST")
    print("=" * 70)

    # 1. Load collection
    collection_path = (
        Path(__file__).parent.parent.parent
        / "Domo Product APIs.postman_collection.json"
    )

    if not collection_path.exists():
        print(f"[ERROR] Collection not found: {collection_path}")
        return

    print(f"\n[FILE] Loading collection: {collection_path.name}")
    collection = PostmanCollection.from_file(str(collection_path))

    # 2. Get first request
    if not collection.requests:
        print("[ERROR] No requests found")
        return

    test_request_obj = collection.requests[0]
    print("\n[TARGET] Selected Request:")
    print(f"   Name: {test_request_obj.name}")
    print(f"   Method: {test_request_obj.method}")
    print(f"   URL: {test_request_obj.url.raw[:70]}...")

    # Check collection auth
    if collection.auth:
        print(f"\n[AUTH] Collection Auth Type: {collection.auth.type}")
        if collection.auth.type == "apikey" and collection.auth.apikey:
            for item in collection.auth.apikey:
                if item.get("key") == "key":
                    print(f"   API Key Header: {item.get('value')}")

    # 3. Use simplified code generation (without full agent graph)
    print("\n[CODE] Generating Python code...")

    # Generate function code with collection auth
    converter = PostmanRequestConverter(
        Request=test_request_obj, collection_auth=collection.auth
    )
    function_code = converter.build_request_code(include_original_json=False)
    test_code = converter.build_test_code()

    complete_code = f"""# Generated from Postman Collection
import httpx
from typing import Dict, Optional

def gd_requests(method: str, url: str, headers: dict, params: dict,
                body: Optional[dict] = None, debug_api: bool = False) -> httpx.Response:
    \"\"\"Helper function to make HTTP requests.\"\"\"
    import httpx
    with httpx.Client() as client:
        if method.lower() == 'get':
            return client.get(url, headers=headers, params=params)
        elif method.lower() == 'post':
            return client.post(url, headers=headers, params=params, json=body)
        elif method.lower() == 'put':
            return client.put(url, headers=headers, params=params, json=body)
        elif method.lower() == 'delete':
            return client.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {{method}}")

{function_code}

{test_code}
"""

    print(f"[OK] Generated {len(complete_code)} characters of code")
    print(f"   Function: {converter.function_name}")

    # 4. Validate Python syntax with AST
    print("\n[SEARCH] Validating Python syntax...")

    try:
        tree = ast.parse(complete_code)
        print("[OK] Valid Python syntax")

        # Analyze AST
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        imports = [n for n in tree.body if isinstance(n, ast.Import | ast.ImportFrom)]

        print("\n[STATS] Code Analysis:")
        print(f"   Functions: {len(functions)}")
        print(f"   Imports: {len(imports)}")
        print(f"   Lines: {len(complete_code.splitlines())}")

        # Check main function
        main_func = None
        for func in functions:
            if func.name == converter.function_name:
                main_func = func
                break

        if main_func:
            print(f"\n[TARGET] Main Function: {main_func.name}")
            print(f"   Arguments: {len(main_func.args.args)}")

            # Check for docstring
            docstring = ast.get_docstring(main_func)
            if docstring:
                print(f"   Docstring: [OK] ({len(docstring)} chars)")
                print(f"      Preview: {docstring[:60]}...")
            else:
                print("   Docstring: [ERROR] Missing")

            # Check type hints
            typed_args = sum(1 for arg in main_func.args.args if arg.annotation)
            print(f"   Type hints: {typed_args}/{len(main_func.args.args)} parameters")

            # Check return annotation
            if main_func.returns:
                print("   Return type: [OK]")
            else:
                print("   Return type: [ERROR] Missing")

    except SyntaxError as e:
        print(f"[ERROR] Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return

    # 5. Write to EXPORTS folder
    print("\n[SAVE] Writing to EXPORTS folder...")

    output_filename = f"{converter.function_name}.py"
    output_path = exports_dir / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(complete_code)

    print(f"[OK] Written to: {output_path}")

    # 6. Try to import and validate
    print("\n[PACKAGE] Testing import...")

    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_module", str(output_path))
        module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = module
        spec.loader.exec_module(module)

        print("[OK] Module imported successfully")

        # Check if function exists
        func = getattr(module, converter.function_name, None)
        if func and callable(func):
            print(f"[OK] Function '{converter.function_name}' is callable")

            # Get function signature
            import inspect

            sig = inspect.signature(func)
            print("\n[NOTE] Function Signature:")
            print(f"   {converter.function_name}{sig}")

        else:
            print(
                f"[WARN]  Function '{converter.function_name}' not found or not callable"
            )

    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return

    # 7. Optionally test execution with real credentials
    print("\n[EXECUTE] Testing Execution:")

    domo_instance = os.getenv("DOMO_INSTANCE")
    domo_token = os.getenv("DOMO_ACCESS_TOKEN")

    if domo_instance and domo_token:
        print(f"   Found credentials for: {domo_instance}")

        # Create auth dict
        auth = {
            "base_url": f"https://{domo_instance}.domo.com",
            "headers": {
                "Authorization": f"Bearer {domo_token}",
                "Content-Type": "application/json",
            },
        }

        # Try to call the function
        try:
            print(f"   Calling {converter.function_name}...")
            response = func(auth=auth, debug_api=True)

            print(f"   [OK] Response: {response.status_code}")

            if response.status_code == 200:
                print("   [OK] SUCCESS! API call worked")
                try:
                    data = response.json()
                    print(f"   Response data type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())[:5]}")
                    elif isinstance(data, list):
                        print(f"   Items: {len(data)}")
                except Exception:
                    print(f"   Response (text): {response.text[:100]}...")
            else:
                print(f"   [WARN]  Non-200 status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

        except Exception as e:
            print(f"   [WARN]  Execution error (expected for some endpoints): {e}")
    else:
        print("   [WARN]  No credentials found in .env")
        print("   Set DOMO_INSTANCE and DOMO_ACCESS_TOKEN to test execution")

    # 8. Show generated code preview
    print("\n[FILE] Generated Code Preview:")
    print("=" * 70)
    lines = complete_code.splitlines()
    for i, line in enumerate(lines[10:30], start=11):  # Show lines 11-30
        print(f"{i:3d} | {line}")
    if len(lines) > 30:
        print(f"... ({len(lines) - 30} more lines)")
    print("=" * 70)

    print(f"\n{'=' * 70}")
    print("[OK] TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)

    return {
        "function_name": converter.function_name,
        "code_length": len(complete_code),
        "valid_syntax": True,
        "importable": True,
        "output_file": str(output_path),
    }


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_single_request())

    if result:
        print("\n[STATS] Summary:")
        print(f"   Function: {result['function_name']}")
        print(f"   Code size: {result['code_length']} chars")
        print(f"   Valid: {result['valid_syntax']}")
        print(f"   Importable: {result['importable']}")
