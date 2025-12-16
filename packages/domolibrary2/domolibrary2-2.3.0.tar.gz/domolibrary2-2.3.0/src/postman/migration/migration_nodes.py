"""Node implementations for migration workflow."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

# GeneratedCode and ParameterAnalysis are used in type hints and agent results
from .migration_agents import get_code_generator_agent, get_parameter_analyzer_agent
from .migration_research import CodebaseResearcher
from .migration_state import FunctionMigrationState
from .utils import (
    extract_module_from_path,
    load_route_instructions,
    parse_index_md,
    sanitize_function_name,
)

logger = logging.getLogger(__name__)


async def function_selection_node(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Load and parse unmigrated functions from index.md.

    Args:
        state: Current migration state

    Returns:
        Updated state with unmigrated functions list
    """
    logger.info("Loading unmigrated functions from index.md")

    index_path = state.get("staging_index_path", "")
    if not index_path:
        return {
            "errors": ["staging_index_path not provided"],
            "unmigrated_functions": [],
        }

    parsed = parse_index_md(index_path)
    unmigrated = parsed.get("new_routes", [])

    logger.info(f"Found {len(unmigrated)} unmigrated functions")

    return {
        "unmigrated_functions": unmigrated,
        "current_step": "function_selection",
    }


async def codebase_research_node(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Research codebase for similar routes and patterns.

    Args:
        state: Current migration state

    Returns:
        Updated state with research results
    """
    logger.info("Researching codebase for similar routes")

    selected = state.get("selected_function")
    if not selected:
        return {
            "warnings": ["No function selected for research"],
            "similar_routes": [],
            "route_examples": [],
        }

    # Initialize researcher
    routes_dir = state.get("routes_dir", "src/domolibrary2/routes")
    researcher = CodebaseResearcher(routes_dir=routes_dir)

    if not researcher.is_available:
        logger.warning("Codebase research not available (Neo4j not connected)")
        return {
            "warnings": ["Codebase research unavailable"],
            "similar_routes": [],
            "route_examples": [],
        }

    # Extract URL and method from selected function
    postman_url = selected.get("url", "")
    postman_method = selected.get("method", "GET")
    module_path = selected.get("module", "")

    # Find similar routes
    similar_routes = researcher.find_similar_routes(
        url_pattern=postman_url,
        method=postman_method,
        module_path=module_path if module_path else None,
    )

    # Get routes in target module
    if module_path:
        module_routes = researcher.get_routes_in_module(module_path)
        similar_routes.extend(module_routes[:5])  # Add top 5 from module

    # Get code examples
    route_examples = researcher.get_route_examples(similar_routes)

    # Extract parameter patterns
    parameter_patterns = researcher.extract_parameter_patterns(similar_routes)

    # Find exception classes in module
    if module_path:
        researcher.find_exception_classes(module_path)

    logger.info(
        f"Found {len(similar_routes)} similar routes, {len(route_examples)} examples"
    )

    return {
        "similar_routes": similar_routes,
        "route_examples": route_examples,
        "parameter_patterns": parameter_patterns,
        "current_step": "research",
    }


async def parameter_analysis_node(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Analyze parameters using AI agent with codebase context.

    Args:
        state: Current migration state

    Returns:
        Updated state with parameter analysis
    """
    logger.info("Analyzing function parameters")

    selected = state.get("selected_function")
    if not selected:
        return {
            "errors": ["No function selected for parameter analysis"],
        }

    # Get codebase context
    route_examples = state.get("route_examples", [])
    parameter_patterns = state.get("parameter_patterns", {})

    # Create enhanced parameter analyzer
    analyzer_agent = get_parameter_analyzer_agent(
        codebase_context=str(parameter_patterns) if parameter_patterns else None,
        route_examples=route_examples,
    )

    # Build prompt from Postman request
    postman_request = selected.get("postman_request", {})
    url = postman_request.get("url", "")
    method = postman_request.get("method", "GET")

    prompt = f"""Analyze parameters for this Postman request:
- Method: {method}
- URL: {url}
- Request: {postman_request}

Extract:
1. Query parameters
2. Path variables
3. Body schema (if applicable)
4. Parameter types and defaults
5. Required vs optional parameters

Consider similar route patterns from the codebase when suggesting parameter names and types."""

    try:
        result = await analyzer_agent.run(prompt)
        analysis = result.data

        logger.info("Parameter analysis completed")

        return {
            "parameter_analysis": analysis,
            "current_step": "parameter_analysis",
        }
    except Exception as e:
        logger.error(f"Error in parameter analysis: {e}")
        return {
            "errors": [f"Parameter analysis failed: {str(e)}"],
        }


async def human_review_parameter_node(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Human review node for parameter modification.

    This node should trigger an interrupt in the LangGraph workflow.
    In CLI mode, this will prompt the user. In Streamlit, this will
    display a form.

    Args:
        state: Current migration state

    Returns:
        Updated state with modified parameters (or unchanged if no modifications)
    """
    logger.info("Waiting for human parameter review")

    parameter_analysis = state.get("parameter_analysis")

    # In non-interactive mode, auto-continue with analysis results
    # In interactive mode, this would be handled via interrupt
    # For CLI, we'll just pass through the analysis as modified parameters
    if parameter_analysis:
        # Convert analysis to modified_parameters format
        modified = {}
        if hasattr(parameter_analysis, "required_params"):
            # Extract from analysis structure
            for req_name, req_list in parameter_analysis.required_params.items():
                for param in req_list:
                    modified[param] = "str"  # Default type

        return {
            "modified_parameters": modified if modified else None,
            "current_step": "parameter_review",
        }

    return {
        "current_step": "parameter_review",
    }


async def code_generation_node(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Generate function code using AI agent with multiple context sources.

    Args:
        state: Current migration state

    Returns:
        Updated state with generated code
    """
    logger.info("Generating function code")

    selected = state.get("selected_function")
    if not selected:
        return {
            "errors": ["No function selected for code generation"],
        }

    # Get context sources
    route_instructions = load_route_instructions()
    route_examples = state.get("route_examples", [])
    parameter_patterns = state.get("parameter_patterns", {})
    parameter_analysis = state.get("parameter_analysis")
    modified_parameters = state.get("modified_parameters")

    # Use modified parameters if available, otherwise use analysis
    params_to_use = modified_parameters if modified_parameters else parameter_analysis

    # Create enhanced code generator
    generator_agent = get_code_generator_agent(
        route_instructions=route_instructions,
        codebase_examples=route_examples,
        parameter_patterns=parameter_patterns,
    )

    # Build prompt
    postman_request = selected.get("postman_request", {})
    url = postman_request.get("url", "")
    method = postman_request.get("method", "GET")
    function_name = sanitize_function_name(selected.get("name", "unnamed_function"))

    prompt = f"""Generate a complete route function for this Postman request:

Function Name: {function_name}
Method: {method}
URL: {url}
Request Details: {postman_request}

Parameters: {params_to_use}

Requirements:
1. Follow the route standards documentation exactly
2. Use similar route examples as reference for structure
3. Include proper decorators (@gd.route_function, @log_call if CRUD)
4. Include DomoAuth and RouteContext parameters
5. Include return_raw parameter with immediate check
6. Proper type hints and docstrings
7. Error handling with RouteError-based exceptions
8. Standard parameter order (auth first, control params last)

Generate complete, production-ready code."""

    try:
        result = await generator_agent.run(prompt)
        generated_code_obj = result.data

        # Extract function code from GeneratedCode model
        if hasattr(generated_code_obj, "function_code"):
            generated_code = generated_code_obj.function_code
        elif isinstance(generated_code_obj, str):
            generated_code = generated_code_obj
        else:
            # Try to get it as dict
            generated_code = str(generated_code_obj)

        logger.info(f"Generated code for function: {function_name}")

        return {
            "generated_draft": generated_code,
            "current_step": "code_generation",
        }
    except Exception as e:
        logger.error(f"Error in code generation: {e}")
        return {
            "errors": [f"Code generation failed: {str(e)}"],
        }


async def human_review_code_node(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Human review node for code review and editing.

    This node should trigger an interrupt in the LangGraph workflow.
    In CLI mode, this will allow editing. In Streamlit, this will
    display an editable code editor.

    Args:
        state: Current migration state

    Returns:
        Updated state with edited code (or unchanged if no edits)
    """
    logger.info("Waiting for human code review")

    generated_code = state.get("generated_draft", "")

    # In non-interactive mode, use generated code as-is
    # In interactive mode, this would be handled via interrupt
    return {
        "edited_code": generated_code,  # Use generated code as edited code
        "current_step": "code_review",
    }


async def integration_node(
    state: FunctionMigrationState,
) -> dict[str, Any]:
    """Integrate approved function into domolibrary2 routes.

    Args:
        state: Current migration state
        routes_dir: Directory containing route modules

    Returns:
        Updated state with integration results
    """
    logger.info("Integrating function into domolibrary2")

    selected = state.get("selected_function")
    edited_code = state.get("edited_code") or state.get("generated_draft")

    if not selected or not edited_code:
        return {
            "errors": ["Missing selected function or code for integration"],
        }

    # Get routes directory from state
    routes_dir = state.get("routes_dir", "src/domolibrary2/routes")

    # Determine target location
    module_path = selected.get("module", "")
    if not module_path:
        # Try to infer from function name or URL
        module_path = "core"  # Default

    # Extract module and submodule
    module, submodule = extract_module_from_path(module_path)

    # Build target file path
    routes_path = Path(routes_dir)
    if submodule:
        # Folder module structure
        target_file = routes_path / module / f"{submodule}.py"
        target_module = f"domolibrary2.routes.{module}.{submodule}"
    else:
        # Single-file module
        target_file = routes_path / f"{module}.py"
        target_module = f"domolibrary2.routes.{module}"

    # Ensure directory exists
    target_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if function already exists
    if target_file.exists():
        existing_code = target_file.read_text(encoding="utf-8")
        function_name = sanitize_function_name(selected.get("name", ""))
        if (
            f"def {function_name}" in existing_code
            or f"async def {function_name}" in existing_code
        ):
            return {
                "errors": [f"Function {function_name} already exists in {target_file}"],
            }

    # Write function to file
    try:
        # Append to existing file or create new
        if target_file.exists():
            # Add function to existing file
            existing = target_file.read_text(encoding="utf-8")
            new_content = f"{existing}\n\n{edited_code}\n"
        else:
            # Create new file with imports and function
            imports = _generate_imports_for_module(module, submodule)
            new_content = (
                f'"""{module} route functions."""\n\n{imports}\n\n{edited_code}\n'
            )

        target_file.write_text(new_content, encoding="utf-8")

        # Update __init__.py if folder module
        if submodule:
            init_file = routes_path / module / "__init__.py"
            _update_init_exports(init_file, function_name)

        logger.info(f"Function integrated into {target_file}")

        return {
            "target_module": target_module,
            "target_submodule": submodule,
            "integration_path": str(target_file),
            "current_step": "integration_complete",
        }
    except Exception as e:
        logger.error(f"Error integrating function: {e}")
        return {
            "errors": [f"Integration failed: {str(e)}"],
        }


def _generate_imports_for_module(module: str, submodule: str | None) -> str:
    """Generate standard imports for a route module.

    Args:
        module: Module name
        submodule: Optional submodule name

    Returns:
        Import statements as string
    """
    if submodule:
        # Folder module - use three dots
        return """from ...auth import DomoAuth
from ...base.exceptions import RouteError
from ...client import get_data as gd, response as rgd
from ...client.context import RouteContext
from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)"""
    else:
        # Single-file module - use two dots
        return """from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import get_data as gd, response as rgd
from ..client.context import RouteContext
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)"""


def _update_init_exports(init_file: Path, function_name: str) -> None:
    """Update __init__.py to export the new function.

    Args:
        init_file: Path to __init__.py file
        function_name: Name of function to export
    """
    if not init_file.exists():
        # Create new __init__.py
        content = f'"""Route module exports."""\n\nfrom .core import {function_name}\n\n__all__ = ["{function_name}"]\n'
        init_file.write_text(content, encoding="utf-8")
        return

    # Read existing file
    content = init_file.read_text(encoding="utf-8")

    # Check if already exported
    if function_name in content:
        return

    # Add to imports and __all__
    # Simple approach: append to existing imports
    if (
        "from .core import" in content
        or f"from .{init_file.parent.name} import" in content
    ):
        # Add to existing import line
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if (
                "from .core import" in line
                or f"from .{init_file.parent.name} import" in line
            ):
                # Add function to import
                if function_name not in line:
                    lines[i] = f"{line.rstrip()}, {function_name}"
                break
    else:
        # Add new import
        content = f"{content}\nfrom .core import {function_name}\n"

    # Add to __all__
    if "__all__" in content:
        # Update existing __all__
        import re

        pattern = r"__all__ = \[(.*?)\]"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            existing = match.group(1)
            if function_name not in existing:
                new_all = f'__all__ = [{existing.rstrip()}\n    "{function_name}",\n]'
                content = re.sub(pattern, new_all, content, flags=re.DOTALL)
    else:
        # Add __all__ at end
        content = f'{content}\n__all__ = ["{function_name}"]\n'

    init_file.write_text(content, encoding="utf-8")
