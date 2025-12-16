"""
Jupyter Route Functions

This module provides functions for managing Domo Jupyter workspaces including
workspace management, content operations, and configuration.

The module is organized into functional areas:
- core: Basic Jupyter workspace retrieval and management functions
- content: Content operations within Jupyter workspaces
- config: Configuration and settings management
- utils: Utility functions for request body generation
- exceptions: All Jupyter-related exception classes

Functions:
    get_jupyter_workspaces: Retrieve all available Jupyter workspaces
    get_jupyter_workspace_by_id: Retrieve a specific workspace by ID
    start_jupyter_workspace: Start a Jupyter workspace instance
    get_jupyter_content: Retrieve content from a Jupyter workspace
    create_jupyter_obj: Create new content in a Jupyter workspace
    delete_jupyter_content: Delete content from a Jupyter workspace
    update_jupyter_file: Update existing file content in workspace
    get_content: Recursively retrieve all workspace content
    update_jupyter_workspace_config: Update workspace configuration

Utility Functions:
    parse_instance_service_location_and_prefix: Parse service location from instance
    get_workspace_auth_token_params: Get authentication parameters for workspace
    generate_update_jupyter_body: Generate properly formatted request bodies

Exception Classes:
    Jupyter_GET_Error: Raised when Jupyter workspace retrieval fails
    SearchJupyterNotFoundError: Raised when Jupyter search returns no results
    Jupyter_CRUD_Error: Raised when Jupyter create/update/delete operations fail
    JupyterWorkspace_Error: Raised when workspace operations fail
"""

# Import configuration functions
from .config import (
    update_jupyter_workspace_config,
)

# Import utility functions
# Import content management functions
from .content import (
    GenerateUpdateJupyterBody_Enum,
    create_jupyter_obj,
    delete_jupyter_content,
    generate_update_jupyter_body,
    generate_update_jupyter_body__directory,
    generate_update_jupyter_body__ipynb,
    generate_update_jupyter_body__new_content_path,
    generate_update_jupyter_body__text,
    get_content,
    get_content_recursive,
    get_jupyter_content,
    update_jupyter_file,
)

# Import core functions
from .core import (
    get_jupyter_workspace_by_id,
    get_jupyter_workspaces,
    get_workspace_auth_token_params,
    parse_instance_service_location_and_prefix,
    start_jupyter_workspace,
)

# Import all exception classes
from .exceptions import (  # Backward compatibility aliases
    Jupyter_CRUD_Error,
    Jupyter_GET_Error,
    JupyterAPI_Error,
    JupyterAPI_WorkspaceStarted,
    JupyterWorkspace_Error,
    SearchJupyterNotFoundError,
)

__all__ = [
    # Exception classes
    "Jupyter_GET_Error",
    "SearchJupyterNotFoundError",
    "Jupyter_CRUD_Error",
    "JupyterWorkspace_Error",
    "JupyterAPI_Error",  # Backward compatibility
    "JupyterAPI_WorkspaceStarted",  # Backward compatibility
    # Core functions
    "get_jupyter_workspaces",
    "get_jupyter_workspace_by_id",
    "start_jupyter_workspace",
    "parse_instance_service_location_and_prefix",
    "get_workspace_auth_token_params",
    # Content management functions
    "get_jupyter_content",
    "create_jupyter_obj",
    "delete_jupyter_content",
    "update_jupyter_file",
    "get_content",
    "get_content_recursive",
    # Configuration functions
    "update_jupyter_workspace_config",
    # Utility functions
    "generate_update_jupyter_body__new_content_path",
    "generate_update_jupyter_body__text",
    "generate_update_jupyter_body__ipynb",
    "generate_update_jupyter_body__directory",
    "GenerateUpdateJupyterBody_Enum",
    "generate_update_jupyter_body",
]
