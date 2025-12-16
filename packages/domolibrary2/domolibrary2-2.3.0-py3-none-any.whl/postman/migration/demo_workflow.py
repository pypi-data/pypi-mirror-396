"""Demo script for testing the complete migration workflow."""

from __future__ import annotations

import asyncio
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver

from .migration_graph import get_migration_graph
from .migration_research import CodebaseResearcher
from .migration_state import FunctionMigrationState
from .utils import parse_index_md


async def demo_migration_workflow(
    function_name: str | None = None,
    staging_path: str = "src/postman/_postman_staging",
    routes_dir: str = "src/domolibrary2/routes",
    interactive: bool = False,
) -> None:
    """Demo the complete migration workflow.

    Args:
        function_name: Optional specific function name to migrate
        staging_path: Path to staging directory
        routes_dir: Path to routes directory
        interactive: Whether to enable interactive mode
    """
    print("=" * 70)
    print("Function Migration Workflow Demo")
    print("=" * 70)
    print()

    # Step 1: Load unmigrated functions
    print("Step 1: Loading unmigrated functions from staging...")
    index_path = Path(staging_path) / "index.md"
    if not index_path.exists():
        print(f"ERROR: index.md not found at {index_path}")
        return

    parsed = parse_index_md(str(index_path))
    unmigrated = parsed.get("new_routes", [])

    if not unmigrated:
        print("No unmigrated functions found.")
        return

    print(f"Found {len(unmigrated)} unmigrated functions\n")

    # Step 2: Select function
    print("Step 2: Function Selection")
    if function_name:
        selected = next((f for f in unmigrated if f.get("name") == function_name), None)
        if not selected:
            print(
                f"ERROR: Function '{function_name}' not found in unmigrated functions"
            )
            return
    else:
        # Show first 10 functions
        print("Available functions (showing first 10):")
        for i, func in enumerate(unmigrated[:10], 1):
            print(f"  {i}. {func.get('name', 'Unknown')} - {func.get('url', '')}")

        if len(unmigrated) > 10:
            print(f"  ... and {len(unmigrated) - 10} more")

        # Select first one for demo
        selected = unmigrated[0]
        print(f"\nSelected: {selected.get('name')} (first function)")

    print(f"  Name: {selected.get('name')}")
    print(f"  URL: {selected.get('url')}")
    print(f"  Module: {selected.get('module', 'unknown')}\n")

    # Step 3: Initialize workflow
    print("Step 3: Initializing migration workflow...")
    checkpointer = MemorySaver()
    graph = get_migration_graph(checkpointer=checkpointer, use_interrupts=interactive)
    config = {"configurable": {"thread_id": "demo-migration-1"}}

    # Step 4: Initialize codebase researcher
    print("Step 4: Initializing codebase researcher...")
    researcher = CodebaseResearcher(routes_dir=routes_dir)
    if researcher.is_available:
        print("  Codebase research available (Neo4j connected)")
    else:
        print(
            "  Codebase research unavailable (Neo4j not connected, continuing without it)"
        )

    # Step 5: Create initial state
    print("\nStep 5: Creating initial state...")
    initial_state: FunctionMigrationState = {
        "staging_index_path": str(index_path),
        "unmigrated_functions": unmigrated,
        "selected_function": selected,
        "postman_request": selected.get("postman_request", {}),
        "postman_url": selected.get("url", ""),
        "postman_method": selected.get("method", "GET"),
        "routes_dir": routes_dir,
        "current_step": "function_selection",
        "errors": [],
        "warnings": [],
    }

    # Step 6: Run workflow
    print("\n" + "=" * 70)
    print("Running Migration Workflow")
    print("=" * 70)
    print()

    try:
        if interactive:
            # Stream workflow with interrupts
            print("Running in interactive mode (streaming)...\n")
            for event in graph.stream(initial_state, config, stream_mode="values"):
                _display_workflow_step(event)
        else:
            # Simple invoke (for demo)
            print("Running workflow (non-interactive mode)...\n")
            result = graph.invoke(initial_state, config)
            _display_final_result(result)

    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user")
    except Exception as e:
        print(f"\nERROR: Workflow failed: {e}")
        import traceback

        traceback.print_exc()


def _display_workflow_step(state: dict) -> None:
    """Display workflow step information.

    Args:
        state: Current workflow state
    """
    current_step = state.get("current_step", "unknown")
    print(f"Current Step: {current_step}")

    if current_step == "codebase_research":
        similar_count = len(state.get("similar_routes", []))
        examples_count = len(state.get("route_examples", []))
        print(f"  Found {similar_count} similar routes")
        print(f"  Found {examples_count} code examples")

    elif current_step == "parameter_analysis":
        analysis = state.get("parameter_analysis")
        if analysis:
            print("  Parameter analysis completed")
            # Could display analysis details here

    elif current_step == "parameter_review":
        print("  Waiting for parameter review (interrupt point)")

    elif current_step == "code_generation":
        print("  Code generation completed")
        code = state.get("generated_draft", "")
        if code:
            print(f"  Generated {len(code)} characters of code")

    elif current_step == "code_review":
        print("  Waiting for code review (interrupt point)")

    elif current_step == "integration_complete":
        path = state.get("integration_path")
        if path:
            print(f"  Function integrated: {path}")

    errors = state.get("errors", [])
    if errors:
        print(f"  Errors: {errors}")

    warnings = state.get("warnings", [])
    if warnings:
        print(f"  Warnings: {warnings}")

    print()


def _display_final_result(state: dict) -> None:
    """Display final workflow result.

    Args:
        state: Final workflow state
    """
    print("\n" + "=" * 70)
    print("Workflow Complete")
    print("=" * 70)
    print()

    errors = state.get("errors", [])
    warnings = state.get("warnings", [])

    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
        print()

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    integration_path = state.get("integration_path")
    if integration_path:
        print(f"SUCCESS: Function integrated at {integration_path}")
        print()

        # Show generated code preview
        generated_code = state.get("generated_draft") or state.get("edited_code", "")
        if generated_code:
            print("Generated Code Preview (first 500 chars):")
            print("-" * 70)
            print(generated_code[:500])
            if len(generated_code) > 500:
                print("...")
            print("-" * 70)
    else:
        print("Function not integrated (check errors above)")


async def demo_with_mock_function() -> None:
    """Demo workflow with a mock function (for testing without staging)."""
    print("=" * 70)
    print("Migration Workflow Demo - Mock Function")
    print("=" * 70)
    print()

    # Create mock function data
    mock_function = {
        "name": "Get Account Details",
        "url": "/api/data/v1/accounts/{account_id}",
        "method": "GET",
        "module": "account.core",
        "postman_request": {
            "name": "Get Account Details",
            "url": "/api/data/v1/accounts/{account_id}",
            "method": "GET",
        },
    }

    print(f"Mock Function: {mock_function['name']}")
    print(f"URL: {mock_function['url']}")
    print(f"Method: {mock_function['method']}\n")

    # Initialize workflow
    checkpointer = MemorySaver()
    graph = get_migration_graph(checkpointer=checkpointer, use_interrupts=False)
    config = {"configurable": {"thread_id": "demo-mock-1"}}

    # Create state
    initial_state: FunctionMigrationState = {
        "staging_index_path": "mock",
        "unmigrated_functions": [mock_function],
        "selected_function": mock_function,
        "postman_request": mock_function["postman_request"],
        "postman_url": mock_function["url"],
        "postman_method": mock_function["method"],
        "routes_dir": "src/domolibrary2/routes",
        "current_step": "function_selection",
        "errors": [],
        "warnings": [],
    }

    print("Running workflow...\n")
    try:
        result = graph.invoke(initial_state, config)
        _display_final_result(result)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Demo migration workflow")
    parser.add_argument(
        "--function",
        type=str,
        help="Specific function name to migrate",
    )
    parser.add_argument(
        "--staging",
        type=str,
        default="src/postman/_postman_staging",
        help="Path to staging directory",
    )
    parser.add_argument(
        "--routes-dir",
        type=str,
        default="src/domolibrary2/routes",
        help="Path to routes directory",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode with interrupts",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock function instead of staging area",
    )

    args = parser.parse_args()

    if args.mock:
        asyncio.run(demo_with_mock_function())
    else:
        asyncio.run(
            demo_migration_workflow(
                function_name=args.function,
                staging_path=args.staging,
                routes_dir=args.routes_dir,
                interactive=args.interactive,
            )
        )
