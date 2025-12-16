"""Agent wrappers with routes.instructions.md integration."""

from __future__ import annotations

from ..converter.agent_graph_agents import (
    initialize_code_generator,
    initialize_parameter_analyzer,
)
from ..converter.agent_models import GeneratedCode, ParameterAnalysis
from .utils import format_code_examples, load_route_instructions


def create_enhanced_parameter_analyzer(
    codebase_context: str | None = None,
    route_examples: list[str] | None = None,
):
    """Create an enhanced parameter analyzer agent with codebase context.

    Args:
        codebase_context: Additional context from codebase research
        route_examples: Code examples from similar routes

    Returns:
        Agent instance
    """
    from pydantic_ai import Agent

    # Build enhanced system prompt
    base_prompt = """You are a parameter analysis specialist. Examine query parameters and path
variables across all requests.

Your analysis should:
1. Identify common parameters used across multiple endpoints
2. Infer parameter types from examples and values
3. Determine which parameters should be required vs optional
4. Suggest sensible default values
5. Identify path variables (URL segments that vary)

Consider:
- Pagination params (limit, offset, page)
- Filtering params (filter, search, query)
- Sorting params (sort, order)
- Format params (format, output)
- API versioning params

Provide recommendations for parameter handling in generated functions."""

    enhanced_prompt = base_prompt

    if codebase_context:
        enhanced_prompt += f"\n\n## Codebase Context\n{codebase_context}"

    if route_examples:
        examples_text = format_code_examples(route_examples)
        enhanced_prompt += f"\n\n## Similar Route Examples\n{examples_text}"
        enhanced_prompt += "\n\nUse these examples to understand parameter patterns and naming conventions."

    # Create new agent with enhanced prompt
    return Agent(
        "openai:gpt-4o",
        output_type=ParameterAnalysis,
        system_prompt=enhanced_prompt,
    )


def create_enhanced_code_generator(
    route_instructions: str | None = None,
    codebase_examples: list[str] | None = None,
    parameter_patterns: dict | None = None,
):
    """Create an enhanced code generator agent with multiple context sources.

    Args:
        route_instructions: Contents of routes.instructions.md
        codebase_examples: Code examples from similar routes
        parameter_patterns: Parameter patterns from similar routes

    Returns:
        Agent instance
    """
    from pydantic_ai import Agent

    # Load route instructions if not provided
    if route_instructions is None:
        route_instructions = load_route_instructions()

    # Build base system prompt
    base_prompt = """You are a Python code generation expert specializing in API client functions.

Generate code that:
1. Uses async/await patterns consistently
2. Includes comprehensive type hints
3. Has detailed docstrings (Args, Returns, Raises)
4. Handles errors gracefully
5. Follows Python best practices (PEP 8, PEP 484)

CRITICAL - HTTP Library:
- ALWAYS use httpx library (NOT requests)
- Import: import httpx
- Return type: MUST be httpx.Response (NOT requests.Response)"""

    enhanced_prompt = base_prompt

    # Add route instructions
    if route_instructions:
        enhanced_prompt += f"\n\n## Route Standards Documentation\n{route_instructions}"
        enhanced_prompt += "\n\nCRITICAL: Follow these standards exactly when generating route functions."

    # Add codebase examples
    if codebase_examples:
        examples_text = format_code_examples(codebase_examples)
        enhanced_prompt += f"\n\n## Similar Route Code Examples\n{examples_text}"
        enhanced_prompt += (
            "\n\nUse these examples as reference for:"
            "\n- Function structure and decorators"
            "\n- Import patterns"
            "\n- Exception handling"
            "\n- Parameter ordering"
            "\n- Docstring format"
        )

    # Add parameter patterns
    if parameter_patterns:
        patterns_text = (
            f"Common parameters: {parameter_patterns.get('common_params', [])}"
        )
        enhanced_prompt += (
            f"\n\n## Parameter Patterns from Similar Routes\n{patterns_text}"
        )
        enhanced_prompt += (
            "\n\nUse these patterns to ensure consistency with existing routes."
        )

    # Create new agent with enhanced prompt
    return Agent(
        "openai:gpt-4o",
        output_type=GeneratedCode,
        system_prompt=enhanced_prompt,
    )


def get_parameter_analyzer_agent(
    codebase_context: str | None = None,
    route_examples: list[str] | None = None,
):
    """Get an enhanced parameter analyzer agent instance.

    Args:
        codebase_context: Additional context from codebase research
        route_examples: Code examples from similar routes

    Returns:
        Agent instance
    """
    if codebase_context or route_examples:
        return create_enhanced_parameter_analyzer(
            codebase_context=codebase_context, route_examples=route_examples
        )
    return initialize_parameter_analyzer()


def get_code_generator_agent(
    route_instructions: str | None = None,
    codebase_examples: list[str] | None = None,
    parameter_patterns: dict | None = None,
):
    """Get an enhanced code generator agent instance.

    Args:
        route_instructions: Contents of routes.instructions.md
        codebase_examples: Code examples from similar routes
        parameter_patterns: Parameter patterns from similar routes

    Returns:
        Agent instance
    """
    if route_instructions or codebase_examples or parameter_patterns:
        return create_enhanced_code_generator(
            route_instructions=route_instructions,
            codebase_examples=codebase_examples,
            parameter_patterns=parameter_patterns,
        )
    return initialize_code_generator()
