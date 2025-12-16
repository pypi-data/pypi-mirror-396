# agent_graph_state.py - State definition for the conversion graph


from typing import TypedDict


class PostmanConversionState(TypedDict, total=False):
    """State for the Postman to Python conversion graph.

    This state is passed between all nodes in the graph and tracks
    the entire conversion process from input to output.
    """

    # Input
    collection_path: str
    export_folder: str
    customize_config: dict | None

    # Orchestration
    conversion_plan: dict | None
    current_phase: str

    # Parsing
    parsed_collection: dict | None
    validation_report: dict | None

    # Parallel Analysis Results
    structure_analysis: dict | None
    auth_analysis: dict | None
    parameter_analysis: dict | None
    header_analysis: dict | None

    # Aggregated Analysis
    aggregated_analysis: dict | None

    # Route Matching (Phase 3)
    route_registry: dict | None  # Discovered routes registry
    route_matches: list[dict] | None  # Deterministic matches
    validated_matches: list[dict] | None  # Agent-validated matches
    generated_wrappers: list[dict] | None  # Generated wrapper functions
    docstring_updates: list[dict] | None  # Docstring updates for existing routes

    # Code Generation
    generated_functions: list[dict]
    generated_tests: list[dict]

    # Validation
    validation_results: list[dict]

    # Final Output
    formatted_code: dict[str, str]  # filename -> code
    export_paths: list[str]

    # Error Handling
    errors: list[str]
    warnings: list[str]
