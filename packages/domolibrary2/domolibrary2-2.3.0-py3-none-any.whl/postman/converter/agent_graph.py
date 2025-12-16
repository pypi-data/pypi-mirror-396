# agent_graph.py - LangGraph workflow for Postman to Python conversion

import os

from langgraph.graph import END, START, StateGraph

from .agent_graph_nodes import (
    aggregation_node,
    code_generation_node,
    code_validation_node,
    docstring_update_node,
    formatting_node,
    matching_node,
    orchestration_node,
    parallel_analysis_node,
    parsing_node,
    test_generation_node,
    validation_node,
    wrapper_generation_node,
)
from .agent_graph_state import PostmanConversionState


def create_postman_conversion_graph():
    """Create the Postman to Python conversion graph.

    Returns:
        Compiled LangGraph ready for execution
    """
    graph_builder = StateGraph(PostmanConversionState)

    # Add all nodes
    graph_builder.add_node("orchestrator", orchestration_node)
    graph_builder.add_node("parser", parsing_node)
    graph_builder.add_node("validator", validation_node)
    graph_builder.add_node("matching", matching_node)  # Phase 3: Route matching
    graph_builder.add_node(
        "wrapper_generation", wrapper_generation_node
    )  # Phase 3: Wrappers
    graph_builder.add_node(
        "docstring_update", docstring_update_node
    )  # Phase 3: Docstrings
    graph_builder.add_node("parallel_analysis", parallel_analysis_node)
    graph_builder.add_node("aggregator", aggregation_node)
    graph_builder.add_node("code_generator", code_generation_node)
    graph_builder.add_node("test_generator", test_generation_node)
    graph_builder.add_node("code_validator", code_validation_node)
    graph_builder.add_node("formatter", formatting_node)

    # Define edges (workflow)
    graph_builder.add_edge(START, "orchestrator")
    graph_builder.add_edge("orchestrator", "parser")
    graph_builder.add_edge("parser", "validator")
    graph_builder.add_edge("validator", "matching")  # Phase 3: Match routes
    graph_builder.add_edge(
        "matching", "wrapper_generation"
    )  # Phase 3: Generate wrappers
    graph_builder.add_edge(
        "wrapper_generation", "docstring_update"
    )  # Phase 3: Update docstrings
    graph_builder.add_edge(
        "docstring_update", "parallel_analysis"
    )  # Continue to analysis
    graph_builder.add_edge("parallel_analysis", "aggregator")
    graph_builder.add_edge("aggregator", "code_generator")
    graph_builder.add_edge("code_generator", "test_generator")
    graph_builder.add_edge("test_generator", "code_validator")
    graph_builder.add_edge("code_validator", "formatter")
    graph_builder.add_edge("formatter", END)

    return graph_builder.compile()


# Export the configured graph
conversion_graph = create_postman_conversion_graph()


async def convert_postman_collection(
    collection_path: str,
    export_folder: str,
    customize_config: dict | None = None,
    write_files: bool = True,
) -> dict:
    """Convert a Postman collection to Python functions using the multi-agent graph.

    Args:
        collection_path: Path to the Postman collection JSON file
        export_folder: Directory where generated files should be saved
        customize_config: Optional customization configuration
        write_files: Whether to write files to disk (default: True)

    Returns:
        Final state dictionary with all results

    Example:
        >>> result = await convert_postman_collection(
        ...     collection_path="api.postman_collection.json",
        ...     export_folder="./generated",
        ...     customize_config={
        ...         "required_headers": ["authorization", "content-type"],
        ...         "default_params": ["limit", "offset"]
        ...     }
        ... )
        >>> print(f"Generated {len(result['formatted_code'])} files")
    """
    print("=" * 60)
    print("🚀 Starting Postman to Python Conversion")
    print("=" * 60)
    print(f"Collection: {collection_path}")
    print(f"Export Folder: {export_folder}")
    print("=" * 60)

    initial_state: PostmanConversionState = {
        "collection_path": collection_path,
        "export_folder": export_folder,
        "customize_config": customize_config or {},
        "current_phase": "init",
        "generated_functions": [],
        "generated_tests": [],
        "validation_results": [],
        "errors": [],
        "warnings": [],
        "conversion_plan": None,
        "parsed_collection": None,
        "validation_report": None,
        "route_registry": None,  # Phase 3
        "route_matches": None,  # Phase 3
        "validated_matches": None,  # Phase 3
        "generated_wrappers": None,  # Phase 3
        "docstring_updates": None,  # Phase 3
        "structure_analysis": None,
        "auth_analysis": None,
        "parameter_analysis": None,
        "header_analysis": None,
        "aggregated_analysis": None,
        "formatted_code": {},
        "export_paths": [],
    }

    # Run the graph
    print("\n🔄 Running conversion graph...\n")
    result = await conversion_graph.ainvoke(initial_state)

    # Check for errors
    if result.get("errors"):
        print("\n" + "=" * 60)
        print("❌ Conversion completed with errors:")
        for error in result["errors"]:
            print(f"   • {error}")
        print("=" * 60)
        return result

    # Write files if requested
    if write_files and result.get("formatted_code"):
        print("\n" + "=" * 60)
        print("💾 Writing files to disk...")
        print("=" * 60)

        # Create export folder if it doesn't exist
        os.makedirs(export_folder, exist_ok=True)

        export_paths = []
        for filename, code in result["formatted_code"].items():
            filepath = os.path.join(export_folder, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            export_paths.append(filepath)
            print(f"   ✓ {filepath}")

        result["export_paths"] = export_paths

    print("\n" + "=" * 60)
    print("✅ Conversion Complete!")
    print("=" * 60)
    print(f"Generated Files: {len(result.get('formatted_code', {}))}")
    print(f"Phase: {result.get('current_phase')}")

    if result.get("warnings"):
        print(f"Warnings: {len(result['warnings'])}")

    print("=" * 60)

    return result


# Convenience function for synchronous usage
def convert_postman_collection_sync(
    collection_path: str,
    export_folder: str,
    customize_config: dict | None = None,
    write_files: bool = True,
) -> dict:
    """Synchronous wrapper for convert_postman_collection.

    Args:
        collection_path: Path to the Postman collection JSON file
        export_folder: Directory where generated files should be saved
        customize_config: Optional customization configuration
        write_files: Whether to write files to disk (default: True)

    Returns:
        Final state dictionary with all results

    Example:
        >>> result = convert_postman_collection_sync(
        ...     collection_path="api.postman_collection.json",
        ...     export_folder="./generated"
        ... )
    """
    import asyncio

    return asyncio.run(
        convert_postman_collection(
            collection_path=collection_path,
            export_folder=export_folder,
            customize_config=customize_config,
            write_files=write_files,
        )
    )
