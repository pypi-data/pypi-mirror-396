"""Simple test script for migration workflow (no LangGraph required)."""

from __future__ import annotations

from pathlib import Path

from .migration_nodes import (
    code_generation_node,
    codebase_research_node,
    function_selection_node,
    parameter_analysis_node,
)
from .migration_state import FunctionMigrationState


async def test_workflow_steps():
    """Test individual workflow steps without full LangGraph."""
    print("=" * 70)
    print("Migration Workflow - Step-by-Step Test")
    print("=" * 70)
    print()

    # Step 1: Function Selection
    print("Step 1: Function Selection")
    print("-" * 70)
    staging_path = "src/postman/_postman_staging"
    index_path = Path(staging_path) / "index.md"

    if not index_path.exists():
        print(f"ERROR: {index_path} not found")
        print(
            "Run: python -m postman convert --collection <path> --staging {staging_path}"
        )
        return

    state: FunctionMigrationState = {
        "staging_index_path": str(index_path),
        "unmigrated_functions": [],
        "current_step": "function_selection",
        "errors": [],
        "warnings": [],
    }

    result = await function_selection_node(state)
    state.update(result)

    unmigrated = state.get("unmigrated_functions", [])
    print(f"Found {len(unmigrated)} unmigrated functions")

    if not unmigrated:
        print("No functions to migrate")
        return

    # Select first function
    selected = unmigrated[0]
    state["selected_function"] = selected
    state["postman_request"] = selected.get("postman_request", {})
    state["postman_url"] = selected.get("url", "")
    state["postman_method"] = selected.get("method", "GET")
    state["routes_dir"] = "src/domolibrary2/routes"

    print(f"Selected: {selected.get('name')}")
    print(f"URL: {selected.get('url')}")
    print(f"Method: {selected.get('method')}")
    print()

    # Step 2: Codebase Research
    print("Step 2: Codebase Research")
    print("-" * 70)
    result = await codebase_research_node(state)
    state.update(result)

    similar_count = len(state.get("similar_routes", []))
    examples_count = len(state.get("route_examples", []))
    print(f"Found {similar_count} similar routes")
    print(f"Found {examples_count} code examples")
    print()

    # Step 3: Parameter Analysis
    print("Step 3: Parameter Analysis")
    print("-" * 70)
    result = await parameter_analysis_node(state)
    state.update(result)

    analysis = state.get("parameter_analysis")
    if analysis:
        print("Parameter analysis completed")
        # Display key findings
        if hasattr(analysis, "required_params"):
            print(f"Required params: {analysis.required_params}")
        if hasattr(analysis, "optional_params"):
            print(f"Optional params: {analysis.optional_params}")
    else:
        print("Parameter analysis failed (check errors)")
    print()

    # Step 4: Code Generation
    print("Step 4: Code Generation")
    print("-" * 70)
    result = await code_generation_node(state)
    state.update(result)

    generated_code = state.get("generated_draft", "")
    if generated_code:
        print(f"Generated {len(generated_code)} characters of code")
        print("\nGenerated Code Preview:")
        print("-" * 70)
        print(generated_code[:800])
        if len(generated_code) > 800:
            print("...")
        print("-" * 70)
    else:
        print("Code generation failed (check errors)")

    # Display errors/warnings
    errors = state.get("errors", [])
    warnings = state.get("warnings", [])

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    print("\n" + "=" * 70)
    print("Workflow Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_workflow_steps())
