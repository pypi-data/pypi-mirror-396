"""CLI command for function migration."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

# Optional imports - workflow requires langgraph
try:
    from ..migration.migration_graph import get_migration_graph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    get_migration_graph = None  # type: ignore

from ..migration.migration_research import CodebaseResearcher
from ..migration.migration_state import FunctionMigrationState
from ..migration.utils import parse_index_md

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for migrate command."""
    parser = argparse.ArgumentParser(
        description="Migrate functions from staging to domolibrary2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--staging",
        type=str,
        default="src/postman/_postman_staging",
        help="Path to staging directory (default: src/postman/_postman_staging)",
    )

    parser.add_argument(
        "--routes-dir",
        type=str,
        default="src/domolibrary2/routes",
        help="Path to routes directory (default: src/domolibrary2/routes)",
    )

    parser.add_argument(
        "--function",
        type=str,
        help="Specific function name to migrate (optional, otherwise interactive selection)",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive mode with human-in-the-loop",
    )

    parser.add_argument(
        "--neo4j-uri",
        type=str,
        help="Neo4j connection URI (optional, uses NEO4J_URI env var if not provided)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Validate paths
    staging_path = Path(args.staging)
    if not staging_path.exists():
        print(f"Error: Staging directory not found: {staging_path}")
        sys.exit(1)

    index_path = staging_path / "index.md"
    if not index_path.exists():
        print(f"Error: index.md not found in staging directory: {index_path}")
        sys.exit(1)

    routes_dir = Path(args.routes_dir)
    if not routes_dir.exists():
        print(f"Error: Routes directory not found: {routes_dir}")
        sys.exit(1)

    # Initialize codebase researcher
    if args.neo4j_uri:
        try:
            from codegraph_mcp.neo4j_client import Neo4jClient

            client = Neo4jClient(uri=args.neo4j_uri)
            CodebaseResearcher(neo4j_client=client, routes_dir=str(routes_dir))
        except Exception as e:
            logger.warning(f"Could not initialize codebase researcher: {e}")
            CodebaseResearcher(routes_dir=str(routes_dir))
    else:
        CodebaseResearcher(routes_dir=str(routes_dir))

    # Load unmigrated functions
    parsed = parse_index_md(str(index_path))
    unmigrated = parsed.get("new_routes", [])

    if not unmigrated:
        print("No unmigrated functions found in staging area.")
        sys.exit(0)

    print(f"\nFound {len(unmigrated)} unmigrated functions\n")

    # Select function
    selected_function = None
    if args.function:
        # Find function by name
        for func in unmigrated:
            if func.get("name") == args.function:
                selected_function = func
                break
        if not selected_function:
            print(
                f"Error: Function '{args.function}' not found in unmigrated functions"
            )
            sys.exit(1)
    else:
        # Interactive selection
        print("Available functions:")
        for i, func in enumerate(unmigrated[:20], 1):  # Show first 20
            print(f"  {i}. {func.get('name', 'Unknown')} - {func.get('url', '')}")

        if len(unmigrated) > 20:
            print(f"  ... and {len(unmigrated) - 20} more")

        try:
            choice = input("\nSelect function number (or 'q' to quit): ").strip()
            if choice.lower() == "q":
                sys.exit(0)

            idx = int(choice) - 1
            if 0 <= idx < len(unmigrated):
                selected_function = unmigrated[idx]
            else:
                print("Invalid selection")
                sys.exit(1)
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled")
            sys.exit(0)

    print(f"\nSelected: {selected_function.get('name')}")
    print(f"URL: {selected_function.get('url')}\n")

    # Check if langgraph is available
    if not LANGGRAPH_AVAILABLE:
        print("ERROR: langgraph is required for migration workflow")
        print("Install with: pip install langgraph pydantic-ai")
        print("\nFor template-only testing, use:")
        print("  python -m postman.migration.test_template_only")
        sys.exit(1)

    # Initialize migration graph
    graph = get_migration_graph(use_interrupts=args.interactive)

    # Initial state
    initial_state: FunctionMigrationState = {
        "staging_index_path": str(index_path),
        "unmigrated_functions": unmigrated,
        "selected_function": selected_function,
        "postman_request": selected_function.get("postman_request", {}),
        "postman_url": selected_function.get("url", ""),
        "postman_method": selected_function.get("method", "GET"),
        "routes_dir": str(routes_dir),
        "current_step": "function_selection",
        "errors": [],
        "warnings": [],
    }

    # Run migration
    try:
        config = {"configurable": {"thread_id": "migration-1"}}

        if args.interactive:
            # Stream with interrupts
            print("Starting migration workflow (interactive mode)...\n")
            for event in graph.stream(initial_state, config, stream_mode="values"):
                _handle_stream_event(event, args.interactive)

            # Get final state
            final_state = graph.get_state(config)
            if final_state.values:
                _display_result(final_state.values)
        else:
            # Simple invoke (for CLI, auto-continue through review steps)
            print("Starting migration workflow (non-interactive mode)...\n")
            print("Note: Parameter and code review steps will auto-continue\n")

            result = graph.invoke(initial_state, config)
            _display_result(result)

        print("\nMigration completed successfully!")
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Migration failed")
        print(f"\nError: {e}")
        sys.exit(1)


def _handle_stream_event(event: dict[str, Any], interactive: bool) -> None:
    """Handle stream event from graph execution.

    Args:
        event: Event from graph stream
        interactive: Whether in interactive mode
    """
    current_step = event.get("current_step", "")

    if current_step == "codebase_research":
        print("Researching codebase for similar routes...")
        similar_count = len(event.get("similar_routes", []))
        if similar_count > 0:
            print(f"  Found {similar_count} similar routes")
    elif current_step == "parameter_analysis":
        print("Analyzing parameters...")
    elif current_step == "parameter_review":
        if interactive:
            print("\n=== Parameter Review ===")
            analysis = event.get("parameter_analysis")
            if analysis:
                print("AI Parameter Analysis:")
                # Display analysis (simplified)
                print("  Review and modify parameters as needed")
            # In real implementation, would show form here
        else:
            print("Parameter review (auto-continuing in non-interactive mode)...")
    elif current_step == "code_generation":
        print("Generating function code...")
    elif current_step == "code_review":
        if interactive:
            print("\n=== Code Review ===")
            code = event.get("generated_draft", "")
            if code:
                print("Generated code preview (first 500 chars):")
                print(code[:500] + "..." if len(code) > 500 else code)
            # In real implementation, would show editor here
        else:
            print("Code review (auto-continuing in non-interactive mode)...")
    elif current_step == "integration_complete":
        print("Integrating function into domolibrary2...")
        integration_path = event.get("integration_path")
        if integration_path:
            print(f"  Function written to: {integration_path}")


def _display_result(result: dict[str, Any]) -> None:
    """Display migration result.

    Args:
        result: Final state from graph execution
    """
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    integration_path = result.get("integration_path")
    if integration_path:
        print(f"\nFunction integrated: {integration_path}")
