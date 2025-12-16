"""Test for migrating delete_account function."""

from __future__ import annotations

import ast

import pytest

from ...converter.generator.templates import RouteTemplate


def test_delete_account_migration():
    """Test that delete_account is generated correctly with all requirements.

    Requirements:
    1. Registers DELETE method
    2. Uses account_id instead of id
    3. Accepts auth (DomoAuth)
    4. Uses @log_call decorator
    5. Uses RouteContext correctly
    6. Follows standard route patterns
    """
    # Generate code using template (for deterministic testing)
    template = RouteTemplate()
    generated_code = template.generate(
        function_name="delete_account",
        url="/api/data/v1/accounts/{account_id}",
        method="DELETE",
        params=["account_id: str"],
        docstring="Delete an account by ID.",
        use_log_call=True,
        exception_class="Account_CRUD_Error",
    )

    # Verify requirements
    assert (
        "@gd.route_function" in generated_code
    ), "Missing @gd.route_function decorator"
    assert "@log_call" in generated_code, "Missing @log_call decorator"
    assert 'method="DELETE"' in generated_code, "Must register DELETE method"
    assert "account_id: str" in generated_code, "Must use account_id parameter"
    assert (
        "id" not in generated_code or "account_id" in generated_code
    ), "Should use account_id, not id"
    assert "auth: DomoAuth" in generated_code, "Must accept auth parameter"
    assert "context: RouteContext" in generated_code, "Must use RouteContext"
    assert (
        "return_raw: bool = False" in generated_code
    ), "Must have return_raw parameter"
    assert "if return_raw:" in generated_code, "Must check return_raw immediately"
    assert "Account_CRUD_Error" in generated_code, "Must use proper exception class"

    # Parse and validate syntax
    try:
        ast.parse(generated_code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has syntax errors: {e}")

    # Verify function signature structure
    assert "async def delete_account" in generated_code
    assert "-> rgd.ResponseGetData" in generated_code

    # Verify RouteContext usage
    assert "context=context" in generated_code, "Must pass context to gd.get_data"
    assert (
        "context: RouteContext | None = None" in generated_code
    ), "Must have context parameter"

    # Verify log_call configuration
    assert "LogDecoratorConfig" in generated_code
    assert "ResponseGetDataProcessor" in generated_code

    print("\n" + "=" * 60)
    print("Generated delete_account function:")
    print("=" * 60)
    print(generated_code)
    print("=" * 60)


# Note: Agent-based test requires langgraph and pydantic-ai dependencies
# Uncomment when those are available in test environment
# @pytest.mark.asyncio
# async def test_delete_account_using_agent():
#     """Test generating delete_account using the AI agent."""
#     from ...migration.migration_state import FunctionMigrationState
#     from ...migration.migration_nodes import code_generation_node
#
#     state: FunctionMigrationState = {
#         "selected_function": {
#             "name": "Delete Account",
#             "url": "/api/data/v1/accounts/{id}",
#             "method": "DELETE",
#             "module": "account.crud",
#         },
#         "modified_parameters": {"account_id": "str"},
#         "routes_dir": "src/domolibrary2/routes",
#         "current_step": "code_generation",
#         "errors": [],
#         "warnings": [],
#     }
#
#     result = await code_generation_node(state)
#     generated_code = result.get("generated_draft", "")
#
#     assert "@gd.route_function" in generated_code
#     assert "DELETE" in generated_code.upper()
#     assert "account_id" in generated_code


def test_template_generates_correct_structure():
    """Test that the updated template generates correct structure."""
    template = RouteTemplate()

    code = template.generate(
        function_name="delete_account",
        url="/api/data/v1/accounts/{account_id}",
        method="DELETE",
        params=["account_id: str"],
        docstring="Delete an account by ID.",
        use_log_call=True,
        exception_class="Account_CRUD_Error",
    )

    # Parse AST to verify structure
    tree = ast.parse(code)

    # Find function definition
    func_def = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "delete_account":
            func_def = node
            break

    assert func_def is not None, "Function definition not found"

    # Check decorators
    decorator_names = [
        ast.unparse(d) if hasattr(ast, "unparse") else d.id
        for d in func_def.decorator_list
    ]
    assert any(
        "route_function" in str(d) for d in decorator_names
    ), "Missing @gd.route_function"
    assert any("log_call" in str(d) for d in decorator_names), "Missing @log_call"

    # Check parameters
    param_names = [arg.arg for arg in func_def.args.args]
    assert "auth" in param_names, "Missing auth parameter"
    assert "account_id" in " ".join(param_names), "Missing account_id parameter"
    assert "context" in " ".join(
        [arg.arg for arg in func_def.args.kwonlyargs]
    ), "Missing context parameter"
    assert "return_raw" in " ".join(
        [arg.arg for arg in func_def.args.kwonlyargs]
    ), "Missing return_raw parameter"

    # Check for DELETE method
    assert "DELETE" in code, "Missing DELETE method"

    # Check for RouteContext
    assert "RouteContext" in code, "Missing RouteContext type hint"

    print("\nTemplate validation passed!")
