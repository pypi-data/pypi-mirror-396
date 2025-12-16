"""
Account Package

This package provides account management functionality split across multiple modules for better organization.

Modules:
    exceptions: Exception classes for account operations
    core: Core account retrieval functions
    oauth: OAuth-specific account functions
    config: Account configuration management
    crud: Create, read, update, delete operations
    sharing: Account sharing and access management
"""

# Import all exception classes
# Import configuration functions
from .config import (
    get_account_config,
    get_oauth_account_config,
    update_account_config,
    update_oauth_account_config,
)

# Import core functions
from .core import get_account_by_id, get_accounts, get_available_data_providers

# Import CRUD functions
from .crud import (
    create_account,
    create_oauth_account,
    delete_account,
    delete_oauth_account,
    generate_create_account_body,
    generate_create_oauth_account_body,
    update_account_name,
    update_oauth_account_name,
)
from .exceptions import (
    Account_Config_Error,
    Account_CreateParams_Error,
    Account_CRUD_Error,
    Account_GET_Error,
    AccountNoMatchError,
    AccountSharing_Error,
    SearchAccountNotFoundError,
)

# Import OAuth functions
from .oauth import get_oauth_account_by_id, get_oauth_accounts

# Import sharing functions and classes
from .sharing import (
    ShareAccount,
    ShareAccount_AccessLevel,
    ShareAccount_V1_AccessLevel,
    generate_share_account_payload,
    generate_share_account_v1_payload,
    generate_share_account_v2_payload,
    get_account_accesslist,
    get_oauth_account_accesslist,
    share_account,
    share_account_v1,
    share_oauth_account,
)

__all__ = [
    # Exception classes
    "Account_GET_Error",
    "SearchAccountNotFoundError",
    "Account_CRUD_Error",
    "AccountSharing_Error",
    "Account_Config_Error",
    "AccountNoMatchError",
    "Account_CreateParams_Error",
    # Core functions
    "get_available_data_providers",
    "get_accounts",
    "get_account_by_id",
    # OAuth functions
    "get_oauth_accounts",
    "get_oauth_account_by_id",
    # Configuration functions
    "get_account_config",
    "get_oauth_account_config",
    "update_account_config",
    "update_oauth_account_config",
    # CRUD functions
    "generate_create_account_body",
    "create_account",
    "delete_account",
    "generate_create_oauth_account_body",
    "create_oauth_account",
    "delete_oauth_account",
    "update_account_name",
    "update_oauth_account_name",
    # Sharing functions and classes
    "ShareAccount",
    "ShareAccount_V1_AccessLevel",
    "ShareAccount_AccessLevel",
    "generate_share_account_payload",
    "generate_share_account_v1_payload",
    "generate_share_account_v2_payload",
    "get_account_accesslist",
    "get_oauth_account_accesslist",
    "share_account",
    "share_oauth_account",
    "share_account_v1",
]
