"""
PDP (Personalized Data Permissions) Route Functions

This module provides functions for managing Domo PDP policies including retrieval,
creation, updating, and deletion operations. PDP policies control data access at
the row level based on user, group, or virtual user assignments.

Submodules:
    exceptions: Exception classes for PDP operations
    core: Core retrieval and utility functions
    crud: Create, update, delete, and toggle operations

Exception Classes:
    PDP_GET_Error: Raised when PDP policy retrieval fails
    SearchPDPNotFoundError: Raised when PDP policy search returns no results
    PDP_CRUD_Error: Raised when PDP policy create/update/delete operations fail

Core Functions:
    get_pdp_policies: Retrieve all PDP policies for a dataset
    search_pdp_policies_by_name: Search for specific PDP policies by name
    generate_policy_parameter_simple: Utility function for creating policy parameters
    generate_policy_body: Utility function for creating policy request bodies

CRUD Functions:
    create_policy: Create a new PDP policy
    update_policy: Update an existing PDP policy
    delete_policy: Delete a PDP policy
    toggle_pdp: Enable or disable PDP for a dataset
"""

# Import all functions and classes for backward compatibility
from .core import (
    generate_policy_body,
    generate_policy_parameter_simple,
    get_pdp_policies,
    search_pdp_policies_by_name,
)
from .crud import (
    create_policy,
    delete_policy,
    toggle_pdp,
    update_policy,
)
from .exceptions import (
    CreatePolicy_Error,
    PDP_CRUD_Error,
    PDP_GET_Error,
    PDPNotRetrievedError,
    SearchPDP_Error,
    SearchPDPNotFoundError,
)

__all__ = [
    # Exception classes
    "PDP_GET_Error",
    "SearchPDPNotFoundError",
    "PDP_CRUD_Error",
    # Core functions
    "get_pdp_policies",
    "search_pdp_policies_by_name",
    "generate_policy_parameter_simple",
    "generate_policy_body",
    # CRUD functions
    "create_policy",
    "update_policy",
    "delete_policy",
    "toggle_pdp",
    # Legacy exports for backward compatibility
    "SearchPDP_Error",
    "CreatePolicy_Error",
    "PDPNotRetrievedError",
]
