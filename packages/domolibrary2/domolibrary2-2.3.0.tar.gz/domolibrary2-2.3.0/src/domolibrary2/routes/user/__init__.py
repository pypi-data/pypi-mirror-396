"""
User Management Routes

This module provides comprehensive user management functionality for Domo instances,
organized into three main categories:

- user: Core user operations (get, search, create, update, delete)
- attributes: User attribute management
- properties: User property management and updates

All user-related functionality is accessible through this unified interface.
"""

from ..instance_config.user_attributes import (  # Attribute functions
    UserAttributes_IssuerType,
    clean_attribute_id,
    create_user_attribute,
    delete_user_attribute,
    generate_create_user_attribute_body,
    get_user_attribute_by_id,
    get_user_attributes,
    update_user_attribute,
)
from .core import (  # Core user functions
    create_user,
    delete_user,
    get_all_users,
    get_by_id,
    process_v1_search_users,
    search_users,
    search_users_by_email,
    search_users_by_id,
    search_virtual_user_by_subscriber_instance,
)
from .exceptions import (
    DeleteUserError,
    DownloadAvatar_Error,
    ResetPasswordPasswordUsedError,
    SearchUserNotFoundError,
    User_CRUD_Error,
    User_GET_Error,
    UserAttributes_CRUD_Error,
    UserAttributes_GET_Error,
    UserSharing_Error,
)
from .properties import (  # Property-related classes and functions; Property functions
    UserProperty,
    UserProperty_Type,
    download_avatar,
    generate_avatar_bytestr,
    generate_patch_user_property_body,
    request_password_reset,
    reset_password,
    set_user_landing_page,
    update_user,
    upload_avatar,
    user_is_allowed_direct_signon,
)

__all__ = [
    # Exception classes
    "User_GET_Error",
    "User_CRUD_Error",
    "SearchUserNotFoundError",
    "UserSharing_Error",
    "ResetPasswordPasswordUsedError",
    "DownloadAvatar_Error",
    "DeleteUserError",
    # Core user functions
    "get_all_users",
    "search_users",
    "search_users_by_id",
    "search_users_by_email",
    "get_by_id",
    "search_virtual_user_by_subscriber_instance",
    "create_user",
    "set_user_landing_page",
    "reset_password",
    "request_password_reset",
    "delete_user",
    "user_is_allowed_direct_signon",
    "download_avatar",
    "generate_avatar_bytestr",
    "upload_avatar",
    "process_v1_search_users",
    # User attributes
    "UserAttributes_IssuerType",
    "UserAttributes_GET_Error",
    "UserAttributes_CRUD_Error",
    "get_user_attributes",
    "get_user_attribute_by_id",
    "clean_attribute_id",
    "generate_create_user_attribute_body",
    "create_user_attribute",
    "update_user_attribute",
    "delete_user_attribute",
    # User properties
    "UserProperty_Type",
    "UserProperty",
    "generate_patch_user_property_body",
    "update_user",
]
