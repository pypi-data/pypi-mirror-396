import os
import re
import shutil
from typing import Any

import httpx


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case.

    Args:
        name (str): The string to convert

    Returns:
        str: The string in snake_case format
    """
    # Remove any special characters and replace spaces/underscores with hyphens
    name = re.sub(r"[^\w\s-]", "", name)
    # Convert to lowercase and replace spaces/underscores with hyphens
    name = name.lower().replace(" ", "-").replace("_", "-")
    # Split on hyphens and join with underscores
    snake_name = "_".join(name.split("-"))

    # Ensure the name doesn't start with a digit (invalid Python identifier)
    if snake_name and snake_name[0].isdigit():
        snake_name = "api_" + snake_name

    # Ensure we have a valid identifier
    if not snake_name or not snake_name.replace("_", "").isalnum():
        snake_name = "api_endpoint"

    return snake_name


def upsert_folder(folder_path: str, is_replace: bool = False) -> None:
    """Create or update a folder based on the provided parameters.

    If the path appears to be a file path (has an extension),
    it creates only the directory part of the path.

    Args:
        folder_path (str): The path of the folder or file to create directory for
        is_replace (bool, optional): If True, removes existing folder before creating.
            Defaults to False.

    Raises:
        OSError: If there are permission issues or other OS-related errors
    """
    # Check if path looks like a file path (has extension)
    if os.path.splitext(folder_path)[1]:
        # Extract directory part only
        directory = os.path.dirname(folder_path)
    else:
        directory = folder_path

    # Only proceed if we have a directory to create
    if directory:
        if is_replace and os.path.exists(directory):
            shutil.rmtree(directory)

        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)


def gd_requests(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    body: str | dict[str, Any] | None = None,
    debug_api: bool = False,
) -> httpx.Response:
    """Wrapper around httpx.Client that handles authentication and common parameters.

    Args:
        method (str): HTTP method (GET, POST, etc.)
        url (str): The URL to make the request to
        auth (dict[str, str]): Authentication credentials
        headers (Optional[dict[str, str]]): Request headers
        params (Optional[dict[str, str]]): Query parameters
        body (Optional[Union[str, dict[str, Any]]]): Request body

    Returns:
        httpx.Response: The response from the request
    """
    # Merge auth headers with provided headers

    # Prepare request data
    data = body if isinstance(body, str) else None
    json_data = body if isinstance(body, dict) else None

    if debug_api:
        print(f"🚀 Making {method} request to {url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        print(f"Data: {data}")
        print(f"JSON: {json_data}")

    with httpx.Client() as client:
        return client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
        )


def normalize_json_to_python(json_str: str) -> str:
    """Convert JSON-style boolean and null values to Python syntax (True, False, None).

    Args:
        json_str (str): JSON string that might contain 'true', 'false', or 'null'

    Returns:
        str: String with Python-style boolean and None values
    """
    if not json_str:
        return json_str

    # Replace JSON booleans with Python booleans
    # Use word boundaries to ensure we only replace complete words
    result = json_str
    result = result.replace("true", "True")
    result = result.replace("false", "False")
    result = result.replace("null", "None")

    return result
