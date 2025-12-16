"""State definition for function migration workflow."""

from __future__ import annotations

from typing import TypedDict

from ..converter.agent_models import ParameterAnalysis


class FunctionMigrationState(TypedDict, total=False):
    """State for the function migration workflow.

    This state is passed between all nodes in the LangGraph workflow
    and tracks the entire migration process from selection to integration.
    """

    # Function selection
    staging_index_path: str
    unmigrated_functions: list[dict]  # From index.md "New Routes" section
    selected_function: dict | None

    # Function details
    postman_request: dict | None  # Original Postman request data
    staging_function_code: str | None  # Current code from staging
    postman_url: str | None  # URL pattern for matching
    postman_method: str | None  # HTTP method

    # Codebase research
    similar_routes: list[dict] | None  # Routes found via CypherQAChain
    route_examples: list[str] | None  # Code examples from similar routes
    parameter_patterns: dict | None  # Parameter patterns from similar routes

    # Parameter analysis
    parameter_analysis: ParameterAnalysis | None
    modified_parameters: dict | None  # User-modified parameters

    # Code generation
    generated_draft: str | None
    edited_code: str | None  # User-edited code

    # Integration
    target_module: str | None
    target_submodule: str | None
    integration_path: str | None

    # Status tracking
    current_step: str
    errors: list[str]
    warnings: list[str]

    # Configuration
    routes_dir: str | None  # Routes directory path
