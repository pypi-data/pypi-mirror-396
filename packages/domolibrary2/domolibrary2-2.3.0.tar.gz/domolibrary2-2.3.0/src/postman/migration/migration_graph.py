"""LangGraph workflow for function migration."""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from .migration_nodes import (
    code_generation_node,
    codebase_research_node,
    function_selection_node,
    human_review_code_node,
    human_review_parameter_node,
    integration_node,
    parameter_analysis_node,
)
from .migration_state import FunctionMigrationState

logger = logging.getLogger(__name__)


def create_migration_graph(
    checkpointer: Any | None = None,
) -> StateGraph:
    """Create the function migration LangGraph workflow.

    Args:
        checkpointer: Optional checkpointer for state persistence
        routes_dir: Directory containing route modules

    Returns:
        Compiled LangGraph ready for execution
    """
    graph_builder = StateGraph(FunctionMigrationState)

    # Add all nodes
    graph_builder.add_node("function_selection", function_selection_node)
    graph_builder.add_node("codebase_research", codebase_research_node)
    graph_builder.add_node("parameter_analysis", parameter_analysis_node)
    graph_builder.add_node("parameter_review", human_review_parameter_node)
    graph_builder.add_node("code_generation", code_generation_node)
    graph_builder.add_node("code_review", human_review_code_node)
    graph_builder.add_node("integration", integration_node)

    # Define workflow edges
    graph_builder.add_edge(START, "function_selection")
    graph_builder.add_edge("function_selection", "codebase_research")
    graph_builder.add_edge("codebase_research", "parameter_analysis")
    graph_builder.add_edge("parameter_analysis", "parameter_review")

    # Parameter review can interrupt - handled via conditional edge
    graph_builder.add_edge("parameter_review", "code_generation")
    graph_builder.add_edge("code_generation", "code_review")

    # Code review can interrupt - handled via conditional edge
    graph_builder.add_edge("code_review", "integration")
    graph_builder.add_edge("integration", END)

    # Compile graph
    if checkpointer:
        return graph_builder.compile(checkpointer=checkpointer)
    else:
        return graph_builder.compile()


def create_migration_graph_with_interrupts(
    checkpointer: Any | None = None,
) -> StateGraph:
    """Create migration graph with explicit interrupt handling.

    This version uses LangGraph's interrupt() function for human-in-the-loop.

    Args:
        checkpointer: Optional checkpointer for state persistence
        routes_dir: Directory containing route modules

    Returns:
        Compiled LangGraph with interrupt support
    """
    graph_builder = StateGraph(FunctionMigrationState)

    # Add nodes
    graph_builder.add_node("function_selection", function_selection_node)
    graph_builder.add_node("codebase_research", codebase_research_node)
    graph_builder.add_node("parameter_analysis", parameter_analysis_node)
    graph_builder.add_node("parameter_review", _parameter_review_with_interrupt)
    graph_builder.add_node("code_generation", code_generation_node)
    graph_builder.add_node("code_review", _code_review_with_interrupt)
    graph_builder.add_node("integration", integration_node)

    # Define workflow
    graph_builder.add_edge(START, "function_selection")
    graph_builder.add_edge("function_selection", "codebase_research")
    graph_builder.add_edge("codebase_research", "parameter_analysis")
    graph_builder.add_edge("parameter_analysis", "parameter_review")
    graph_builder.add_edge("parameter_review", "code_generation")
    graph_builder.add_edge("code_generation", "code_review")
    graph_builder.add_edge("code_review", "integration")
    graph_builder.add_edge("integration", END)

    if checkpointer:
        return graph_builder.compile(checkpointer=checkpointer)
    else:
        return graph_builder.compile()


async def _parameter_review_with_interrupt(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Parameter review node with interrupt for human input.

    Args:
        state: Current migration state

    Returns:
        Updated state with modified parameters
    """
    parameter_analysis = state.get("parameter_analysis")
    route_examples = state.get("route_examples", [])

    # Interrupt for human review
    user_feedback = interrupt(
        "Please review and modify parameters",
        {
            "analysis": parameter_analysis.model_dump() if parameter_analysis else {},
            "examples": route_examples[:2],  # Show top 2 examples
        },
    )

    # user_feedback will contain modified parameters from user
    return {
        "modified_parameters": user_feedback,
        "current_step": "parameter_review",
    }


async def _code_review_with_interrupt(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Code review node with interrupt for human input.

    Args:
        state: Current migration state

    Returns:
        Updated state with edited code
    """
    generated_code = state.get("generated_draft", "")
    route_examples = state.get("route_examples", [])

    # Interrupt for human review
    user_feedback = interrupt(
        "Please review and edit the generated code",
        {
            "generated_code": generated_code,
            "examples": route_examples[:2],  # Show top 2 examples for comparison
        },
    )

    # user_feedback will contain edited code from user
    return {
        "edited_code": user_feedback,
        "current_step": "code_review",
    }


# Default export
def get_migration_graph(
    checkpointer: Any | None = None,
    use_interrupts: bool = False,
) -> StateGraph:
    """Get a configured migration graph.

    Args:
        checkpointer: Optional checkpointer for state persistence
        use_interrupts: Whether to use LangGraph interrupts (for Streamlit)

    Returns:
        Compiled migration graph
    """
    if use_interrupts:
        return create_migration_graph_with_interrupts(checkpointer=checkpointer)
    else:
        return create_migration_graph(checkpointer=checkpointer)
