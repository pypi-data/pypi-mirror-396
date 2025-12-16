"""Code templates for route generation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RouteTemplate:
    """Template for generating route functions."""

    @staticmethod
    def generate(
        function_name: str,
        url: str,
        method: str,
        params: list[str],
        docstring: str,
        return_type: str = "rgd.ResponseGetData",
        use_log_call: bool = True,
        exception_class: str | None = None,
    ) -> str:
        """Generate route function code.

        Args:
            function_name: Name of function
            url: URL pattern
            method: HTTP method
            params: List of parameter names (excluding auth, context, return_raw)
            docstring: Function docstring
            return_type: Return type annotation
            use_log_call: Whether to include @log_call decorator (for CRUD operations)
            exception_class: Optional exception class name for error handling

        Returns:
            Generated function code
        """
        # Build parameter list - standard order: auth, entity params, control params
        param_list = ["auth: DomoAuth"]

        # Add entity-specific parameters
        param_list.extend(params)

        # Add control parameters (after *)
        param_list.append("*")
        param_list.append("context: RouteContext | None = None")
        param_list.append("return_raw: bool = False")

        params_str = ",\n    ".join(param_list)

        # Build URL construction
        # Escape special characters and handle f-string syntax
        if url.startswith("http"):
            # Full URL - use regular string (not f-string)
            url_final = url.replace('"', '\\"').replace("'", "\\'")
            url_line = f'url = "{url_final}"'
        else:
            # Relative URL - need to properly escape for f-string
            # Remove leading slash if present
            url_clean = url.lstrip("/")
            # Escape any quotes
            url_clean = url_clean.replace('"', '\\"').replace("'", "\\'")
            # For f-string, we need to double braces that aren't variables
            # But since we're using a variable, we can just use it directly
            url_line = f'url = f"https://{{auth.domo_instance}}.domo.com/{url_clean}"'

        # Build decorators
        decorators = "@gd.route_function"
        if use_log_call:
            decorators += '\n@log_call(\n    level_name="route",\n    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),\n)'

        # Build exception handling
        # Extract first parameter name (if available)
        first_param_name = None
        if params:
            first_param = params[0]
            # Extract name from "name: type" or just "name"
            first_param_name = first_param.split(":")[0].strip()

        if exception_class:
            entity_id_arg = first_param_name if first_param_name else "None"
            error_handling = f"""    if not res.is_success:
        raise {exception_class}(
            entity_id={entity_id_arg},
            res=res,
        )"""
        else:
            error_handling = """    if not res.is_success:
        raise RouteError(
            message=f"Request failed with status {res.status}",
            res=res,
        )"""

        # Build docstring args section
        docstring_args = "auth: Authentication object"
        if params:
            for param in params:
                # Extract param name and type if provided
                param_name = param.split(":")[0].strip()
                docstring_args += f"\n        {param_name}: Parameter description"
        docstring_args += "\n        return_raw: Return raw response without processing"
        docstring_args += "\n        context: RouteContext for request configuration"

        code = f'''{decorators}
async def {function_name}(
    {params_str}
) -> {return_type}:
    """{docstring}

    Args:
        {docstring_args}

    Returns:
        {return_type} object

    Raises:
        {exception_class or "RouteError"}: If the request fails
    """
    {url_line}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="{method}",
        context=context,
    )

    if return_raw:
        return res

{error_handling}

    return res
'''
        return code


@dataclass
class WrapperTemplate:
    """Template for generating wrapper functions."""

    @staticmethod
    def generate(
        wrapper_name: str,
        existing_route_module: str,
        existing_route_name: str,
        postman_name: str,
        postman_folder: str,
        docstring: str | None = None,
    ) -> str:
        """Generate wrapper function code.

        Args:
            wrapper_name: Name of wrapper function
            existing_route_module: Module path of existing route
            existing_route_name: Name of existing route function
            postman_name: Original Postman request name
            postman_folder: Postman folder path
            docstring: Optional custom docstring

        Returns:
            Generated wrapper function code
        """
        if not docstring:
            # Use format() instead of f-string to avoid issues with curly braces
            docstring = f"""{postman_name} (Postman: {postman_folder})

    This function is a wrapper around the existing {existing_route_name} route.
    Generated from Postman collection.

    See: {existing_route_module}.{existing_route_name}
    """

        # Build parameter list (match existing route signature)
        param_list = [
            "auth: DomoAuth",
            "*",
            "context: RouteContext | None = None",
            "return_raw: bool = False",
            "**kwargs",
        ]

        params_str = ",\n    ".join(param_list)

        code = f'''@gd.route_function
async def {wrapper_name}(
    {params_str}
) -> rgd.ResponseGetData:
    """{docstring}
    """
    from {existing_route_module} import {existing_route_name}
    return await {existing_route_name}(
        auth=auth,
        context=context,
        return_raw=return_raw,
        **kwargs
    )
'''
        return code
