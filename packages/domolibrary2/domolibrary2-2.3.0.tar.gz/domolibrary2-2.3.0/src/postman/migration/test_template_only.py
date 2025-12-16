"""Test template generation only (no AI dependencies)."""

from __future__ import annotations

from ..converter.generator.templates import RouteTemplate


def test_template_generation():
    """Test template generation with delete_account example."""
    print("=" * 70)
    print("Template Generation Test - delete_account")
    print("=" * 70)
    print()

    # Use delete_account as example
    func_name = "delete_account"
    url = "/api/data/v1/accounts/{account_id}"
    method = "DELETE"

    print(f"Function: {func_name}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print()

    # Generate using template
    template = RouteTemplate()

    # Extract parameters from URL
    params = ["account_id: str"]

    # Determine if CRUD operation (needs log_call)
    use_log_call = method in ["POST", "PUT", "PATCH", "DELETE"]

    # Use Account_CRUD_Error for account operations
    exception_class = "Account_CRUD_Error"

    generated_code = template.generate(
        function_name=func_name,
        url=url,
        method=method,
        params=params,
        docstring="Delete an account by ID.",
        use_log_call=use_log_call,
        exception_class=exception_class,
    )

    print("Generated Code:")
    print("=" * 70)
    print(generated_code)
    print("=" * 70)

    # Validate
    import ast

    try:
        ast.parse(generated_code)
        print("\n✓ Generated code is valid Python syntax")
    except SyntaxError as e:
        print(f"\n✗ Syntax error: {e}")

    # Check requirements
    checks = {
        "@gd.route_function": "@gd.route_function" in generated_code,
        "@log_call": "@log_call" in generated_code if use_log_call else True,
        "DELETE method": 'method="DELETE"' in generated_code,
        "account_id": "account_id: str" in generated_code,
        "RouteContext": "RouteContext" in generated_code,
        "return_raw": "return_raw: bool = False" in generated_code,
        "if return_raw:": "if return_raw:" in generated_code,
        "Account_CRUD_Error": "Account_CRUD_Error" in generated_code,
    }

    print("\nRequirements Check:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

    all_passed = all(checks.values())
    print(f"\n{'All checks passed!' if all_passed else 'Some checks failed'}")


if __name__ == "__main__":
    test_template_generation()
