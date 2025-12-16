import os
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from . import utils
from .models import PostmanCollection, PostmanRequest
from .utils import to_snake_case


@dataclass
class PostmanRequestConverter:
    """Class to convert Postman requests to Python API client code.

    Extends the PostmanRequest class to add functionality for converting
    requests to Python code.
    """

    Request: PostmanRequest

    url: str = None
    function_name: str = None
    params: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)

    # Collection-level auth (optional)
    collection_auth: any | None = None

    # Instance variables to store filter configurations
    required_headers: list[str] = field(default_factory=list)
    # Removed ignored_headers

    default_params: list[str] = field(default_factory=list)
    ignored_params: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.generate_function_name()
        self.generate_headers()
        self.generate_url()
        self.generate_params()

    def export_function(
        self,
        export_folder: str,
        prefix: str = "",
        include_test_code: bool = True,
        is_replace: bool = False,
        include_original_json: bool = True,
    ) -> str:
        """Export the function code to a Python file.

        Args:
            export_folder (str): Directory where the file should be created
            prefix (str): Prefix for the filename
            include_test_code (bool): Whether to include test code
            is_replace (bool): Whether to replace existing files
            include_original_json (bool): Whether to include original Postman JSON
            prefix (str, optional): Prefix to add to the filename. Defaults to "".
            include_test_code (bool, optional): Whether to include test code. Defaults to True.
            overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.

        Returns:
            str: Path to the created file

        Raises:
            FileExistsError: If the file already exists and overwrite is False
        """
        # Create export folder if it doesn't exist
        filename = f"{prefix}{self.function_name}.py"
        filepath = os.path.join(export_folder, filename)

        utils.upsert_folder(filepath, is_replace=is_replace)

        # Generate filename with optional prefix

        # Generate the function code
        request_code = self.build_request_code(
            include_original_json=include_original_json
        )

        # Add test code if requested
        if include_test_code:
            test_code = self.build_test_code()
            complete_code = request_code + "\n\n" + test_code
        else:
            complete_code = request_code

        # Write to file with appropriate imports
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("from utils import gd_requests\n\n")
            f.write("import requests\n")
            f.write("from typing import Dict\n\n")
            f.write(complete_code)

        print(f"Exported function to {filepath}")
        return filepath

    @staticmethod
    def _generate_function_name(url, method) -> str:
        """Get a valid Python function name from a URL.

        Args:
            url (str): The URL to convert

        Returns:
            str: A valid Python function name in snake_case
        """
        # Parse the URL to get meaningful parts
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split("/") if part]

        # Try to create a meaningful name from the path
        if len(path_parts) >= 2:
            # Use the last two meaningful parts
            endpoint_parts = path_parts[-2:]
            # Filter out purely numeric IDs and UUIDs
            meaningful_parts = []
            for part in endpoint_parts:
                # Skip if it's purely numeric or looks like a UUID
                if not (
                    part.isdigit()
                    or (len(part) > 30 and any(c in part for c in "abcdef-"))
                    or len(part) > 50
                ):  # Skip very long composite parameters
                    meaningful_parts.append(part)

            if meaningful_parts:
                endpoint = "_".join(meaningful_parts)
            else:
                # Fallback to a generic name based on the parent path
                endpoint = path_parts[-2] if len(path_parts) >= 2 else path_parts[-1]
        else:
            endpoint = path_parts[-1] if path_parts else "endpoint"

        # Include query parameters in the name if they're short and meaningful
        if parsed.query:
            query_params = parse_qs(parsed.query)
            short_params = []
            for key, values in query_params.items():
                if (
                    len(key) <= 15 and key.isalpha()
                ):  # Only include short, alphabetic keys
                    short_params.append(key)

            if short_params and len("_".join(short_params)) <= 30:
                endpoint = (
                    f"{endpoint}_{'_'.join(short_params[:3])}"  # Limit to 3 params
                )

        # Combine method and endpoint
        name = f"{endpoint}_{method.lower()}"

        # Convert to snake_case and ensure it's a valid identifier
        return to_snake_case(name)

    def generate_function_name(self) -> str:
        """Generate a function name from this PostmanRequest.

        Returns:
            str: A valid Python function name in snake_case
        """

        # Combine method and endpoint
        self.function_name = self._generate_function_name(
            url=self.Request.url.raw, method=self.Request.method.lower()
        )

        # Convert to snake_case
        self.function_name = to_snake_case(self.function_name)

        return self.function_name

    def generate_headers(
        self,
        required_headers: list[str] | None = None,
    ) -> dict[str, str]:
        """Build headers dictionary from this PostmanRequest, optionally filtered by required headers.

        Args:
            required_headers (Optional[list[str]]): List of header keys to include. If None, all headers are included.

        Returns:
            dict[str, str]: Dictionary of headers
        """

        if required_headers:
            self.required_headers = required_headers

        # Start with all headers
        self.headers = {h.key.lower(): h.value for h in self.Request.header}

        # Filter by required headers if specified
        if self.required_headers:
            self.headers = {
                key: value
                for key, value in self.headers.items()
                if key.lower()
                in [req_header.lower() for req_header in self.required_headers]
            }

        return self.headers

    def generate_url(self) -> str:
        """Build the complete URL from this PostmanRequest.

        Returns:
            str: The complete URL
        """
        # Handle host as either string or list
        if isinstance(self.Request.url.host, list):
            host = ".".join(self.Request.url.host)
        else:
            host = self.Request.url.host
        base_url = f"{self.Request.url.protocol}://{host}"
        path = "/".join(self.Request.url.path)
        self.url = str(urljoin(base_url, path))
        return self.url

    def generate_params(
        self,
        default_params: list[str] | None = None,
        ignored_params: list[str] | None = None,
    ) -> dict[str, str]:
        """Build query parameters dictionary from this PostmanRequest.

        Args:
            default_params (Optional[list[str]]): List of parameter keys that must be included. If None, all parameters are included.
            ignored_params (Optional[list[str]]): List of parameter keys that should be excluded. If None, no parameters are excluded.

        Returns:
            dict[str, str]: Dictionary of query parameters
        """
        # Store the parameters configuration
        if default_params:
            self.default_params = default_params

        if ignored_params:
            self.ignored_params = ignored_params or []

        # Start with all parameters
        self.params = {
            q.key.lower(): q.value
            for q in (self.Request.url.query or [])
            if q and q.key
        }

        # Filter out ignored parameters
        if self.ignored_params:
            self.parms = {
                k: v
                for k, v in self.params.items()
                if k.lower() not in self.ignored_params
            }

        return self.params

    def build_request_code(self, include_original_json: bool = True) -> str:
        """Build the request code for a function.

        Args:
            default_params (Optional[list[str]]): List of parameters to expose as function arguments

        Returns:
            str: The request code as a string
        """
        # Parse the URL to extract the path part
        parsed_url = urlparse(self.url)
        path = parsed_url.path
        if parsed_url.query:
            path += f"?{parsed_url.query}"

        # Build function signature with default parameters
        signature = f"def {self.function_name}( auth: dict[str, str], "
        param_args = []

        if self.default_params and self.params:
            for param in self.default_params:
                if param in self.params:
                    param_args.append(f"{param}: str = '{self.params[param]}', ")

        # Add auth parameter after any default parameters
        signature += (
            ", ".join(param_args) + "debug_api: bool = False ) -> httpx.Response:"
        )

        code = [
            signature,
            f'    """Make a {self.Request.method} request to {self.url}',
            "    ",
        ]

        # Add parameter documentation
        if self.default_params and self.params:
            code.append("    Args:")
            for param in self.default_params:
                if param in self.params:
                    code.append(
                        f"        {param} (str, optional): Value for the {param} parameter"
                    )
            code.append("        auth (dict[str, str]): Authentication information")
            code.append(
                "        debug_api (bool, optional): Enable debug output for API calls"
            )

        # Add original Postman request JSON for reference (if requested)
        if include_original_json:
            code.extend(
                [
                    "    ",
                    "    Original Postman Request:",
                ]
            )

            # Convert the request to JSON and add as comment
            import json

            try:
                request_json = self.Request.to_dict()
                request_json_str = json.dumps(request_json, indent=8)
                for line in request_json_str.split("\n"):
                    code.append(f"    # {line}")
            except Exception as e:
                code.append(f"    # Error serializing request: {e}")
                code.append(f"    # Request URL: {self.Request.url.raw}")
                code.append(f"    # Request Method: {self.Request.method}")

        code.extend(
            [
                "    ",
                "    Returns:",
                "        httpx.Response: The response from the API",
                '    """',
                '    base_url = auth.get("base_url") if auth else ""',
                f'    url = f"{{base_url}}{path}"',
                f"    headers = {{**{self.headers}, **auth.get('headers', {{}})}}",
            ]
        )

        # Handle parameters, including any custom default parameters
        if self.default_params and self.params:
            # Start with original params dictionary
            code.append(f"    params = {self.params}")

            # Update with provided parameter values
            for param in self.default_params:
                if param in self.params:
                    code.append(f"    if {param} is not None:")
                    code.append(f"        params['{param}'] = {param}")
        else:
            code.append(f"    params = {self.params}")

        if self.Request.body:
            # Normalize JSON values in body to Python syntax
            body_value = utils.normalize_json_to_python(self.Request.body.raw)
            code.extend(
                [
                    f"    data = {body_value}",
                    f"    response = gd_requests(method='{self.Request.method.lower()}', url=url, headers=headers, params=params, body=data, debug_api=debug_api)",
                ]
            )
        else:
            code.append(
                f"    response = gd_requests(method='{self.Request.method.lower()}', url=url, headers=headers, params=params, debug_api=debug_api)"
            )

        code.append("    return response")
        return "\n".join(code)

    def build_test_code(
        self,
        func_name: str | None = None,
        default_params: list[str] | None = None,
    ) -> str:
        """Build the test code for a function.

        Args:
            func_name (Optional[str]): Name of the function to test.
                If None, uses the converter's function_name.
            default_params (Optional[list[str]]): List of parameters
                exposed as function arguments.

        Returns:
            str: The test code as a string
        """
        # Use provided function name or fall back to the converter's function name
        func_name = func_name or self.function_name

        # Use provided default params or fall back to the converter's default params
        params_to_use = default_params or self.default_params

        param_args = []
        if params_to_use:
            # Add default values for all parameters in test function
            param_args = [f"{param}= {self.parms or 'None'}" for param in params_to_use]

        # Determine auth header configuration from collection auth
        auth_header_key = "Authorization"
        auth_header_value_template = 'f"Bearer {domo_token}"'

        if self.collection_auth and self.collection_auth.type == "apikey":
            # Extract API key configuration
            apikey_config = self.collection_auth.apikey or []
            key_field = next(
                (item for item in apikey_config if item.get("key") == "key"), None
            )

            if key_field:
                auth_header_key = key_field.get("value", "X-DOMO-Developer-Token")
                auth_header_value_template = (
                    'f"{domo_token}"'  # No Bearer prefix for API key
                )

        code_lines = [
            "",
            f"def test_{func_name}({', '.join(param_args + ['auth: dict[str, str] = None, debug_api: bool = False'])}):",
            f'    """Test the {func_name} function."""',
            "    auth = {'base_url': '', 'headers': {}} if auth is None else auth",
            f"    response = {func_name}(auth = auth, debug_api = debug_api, {', '.join(param_args)})",
            '    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"',
            "    return response",
            "",
            "",
            'if __name__ == "__main__":',
            "    import os",
            "    from dotenv import load_dotenv",
            "    ",
            "    load_dotenv()",
            "    ",
            "    # Setup auth from environment variables",
            '    domo_instance = os.getenv("DOMO_INSTANCE")',
            '    domo_token = os.getenv("DOMO_ACCESS_TOKEN")',
            "    ",
            "    if not domo_instance or not domo_token:",
            '        print("Error: DOMO_INSTANCE and DOMO_ACCESS_TOKEN must be set in .env file")',
            "        exit(1)",
            "    ",
            "    auth = {",
            '        "base_url": f"https://{domo_instance}.domo.com/",',
            '        "headers": {',
            f'            "{auth_header_key}": {auth_header_value_template},',
            '            "Content-Type": "application/json"',
            "        }",
            "    }",
            "    ",
            f"    print(f'Testing {func_name}...')",
            "    try:",
            f"        response = test_{func_name}(auth=auth, debug_api=True)",
            '        print(f"Success! Status code: {response.status_code}")',
            "        print(f'Response: {response.text[:200]}...' if len(response.text) > 200 else f'Response: {response.text}')",
            "    except AssertionError as e:",
            '        print(f"Test failed: {e}")',
            "    except Exception as e:",
            '        print(f"Error occurred: {e}")',
        ]

        return "\n".join(code_lines)

    @classmethod
    def from_postman_request(
        cls,
        request: PostmanRequest,
        required_headers: dict | None = None,
        # Removed ignored_headers parameter
        default_params: dict | None = None,
        ignored_params: dict | None = None,
        export_folder: str | None = None,
        is_include_test_code: bool = True,
        is_replace: bool | None = True,
        include_original_json: bool = False,
    ):
        """Create a PostmanRequestConverter from a PostmanRequest and generate function code."""

        converter = cls(
            Request=request,
            required_headers=required_headers,
            # Removed ignored_headers
            default_params=default_params,
            ignored_params=ignored_params,
        )

        if not export_folder:
            return converter

        # Generate code using the converter
        converter.export_function(
            export_folder=export_folder,
            include_test_code=is_include_test_code,
            is_replace=is_replace,
            include_original_json=include_original_json,
        )
        return converter


@dataclass
class PostmanCollectionConverter:
    """Class to handle conversions for entire Postman Collections."""

    export_folder: str
    collection: PostmanCollection
    converters: list[PostmanRequestConverter] = field(default_factory=list)

    customize: dict[str, dict] = field(default_factory=dict)
    required_headers: list[str] = field(default_factory=list)

    @classmethod
    def from_postman_collection(
        cls,
        postman_path: str,
        export_folder: str,
        customize: dict[str, dict] | None = None,
        required_headers: list[str] | None = None,
        is_replace: bool = False,
        is_include_test_code: bool = True,
        include_original_json: bool = False,
    ) -> "PostmanCollectionConverter":
        """Load a PostmanCollection from a file.

        Args:
            postman_path (str): Path to the Postman collection file
            export_folder (str): Folder to export the generated files to
            customize (Optional[dict[str, Dict]]): Customization options for functions
            required_headers (Optional[list[str]]): List of header keys to include

        Returns:
            PostmanCollectionConverter: Converter instance for the collection
        """
        collection = PostmanCollection.from_file(postman_path)

        collection_converter = cls(
            collection=collection,
            export_folder=export_folder,
            customize=customize or {},
            required_headers=required_headers or [],
        )

        if is_replace:
            utils.upsert_folder(export_folder, is_replace=True)

        collection_converter.generate_conversion_files(
            is_replace=False,
            is_include_test_code=is_include_test_code,
            include_original_json=include_original_json,
        )
        return collection_converter

    def get_customize(self, function_name):
        """Get the customization options for a specific function."""
        return self.customize.get(function_name, {})

    def generate_conversion_files(
        self,
        is_replace: bool = False,
        is_include_test_code: bool = True,
        include_original_json: bool = False,
    ) -> list[PostmanRequestConverter]:
        """Generate implementation files for each request in the collection.

        Args:
            is_replace (bool): Whether to replace existing files. Defaults to True.
            is_include_test_code (bool): Whether to include test code. Defaults to True
            include_original_json (bool): Whether to include original Postman JSON in generated functions. Defaults to False.

        Returns:
            list[PostmanRequestConverter]: List of converters used to generate the files
        """

        for request in self.collection.requests:
            # Generate the function name that would be used
            function_name = PostmanRequestConverter._generate_function_name(
                request.name, request.method
            )

            # Get any customizations for this function
            customize = self.get_customize(function_name)

            # Use function-specific required_headers if provided, or class-wide required_headers otherwise
            req_headers = customize.get("required_headers", self.required_headers)

            # Convert request to a PostmanRequestConverter
            converter = PostmanRequestConverter.from_postman_request(
                request=request,
                export_folder=self.export_folder,
                is_include_test_code=is_include_test_code,
                is_replace=is_replace,
                required_headers=req_headers,
                include_original_json=include_original_json,
                **{k: v for k, v in customize.items() if k != "required_headers"},
            )

            self.converters.append(converter)

        return self.converters

    def export_functions(self, include_original_json: bool = False) -> str:
        """Export all functions as a single string.

        Args:
            include_original_json (bool): Whether to include original Postman JSON in generated functions.

        Returns:
            str: Combined function code for all requests in the collection.
        """
        functions = []

        for request in self.collection.requests:
            # Create a converter for this request
            converter = PostmanRequestConverter(Request=request)

            # Generate the function code
            function_code = converter.build_request_code(
                include_original_json=include_original_json
            )
            functions.append(function_code)

        # Add common imports at the top
        imports = [
            "from utils import gd_requests",
            "import requests",
            "from typing import Dict",
            "",
        ]

        return "\n".join(imports + functions)
