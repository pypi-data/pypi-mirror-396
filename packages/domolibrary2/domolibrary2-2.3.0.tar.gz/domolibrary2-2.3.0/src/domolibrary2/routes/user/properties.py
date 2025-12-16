"""
User Properties Management Routes

This module provides functionality for managing user properties and property-related
operations in Domo instances. This includes user properties like display name, email,
phone, department, role, as well as property-specific operations like password
management, avatar management, landing page settings, and permission controls.

Functions:
    update_user: Update user properties via identity API
    generate_patch_user_property_body: Generate request body for property updates
    set_user_landing_page: Set user's default landing page
    reset_password: Reset user password
    request_password_reset: Request password reset via email
    download_avatar: Download user avatar image
    upload_avatar: Upload user avatar image
    generate_avatar_bytestr: Generate base64 avatar string for uploads
    user_is_allowed_direct_signon: Manage direct sign-on permissions

Classes:
    UserProperty_Type: Enum of available user property types
    UserProperty: Class representing a user property with type and values

Exception Classes:
    ResetPasswordPasswordUsedErrorError: Raised when password was previously used
    DownloadAvatar_Error: Raised when avatar download fails
"""

import base64
import os
from enum import Enum

from ...auth import DomoAuth
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils import images
from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)
from .exceptions import (
    DownloadAvatar_Error,
    ResetPasswordPasswordUsedError,
    User_CRUD_Error,
)

__all__ = [
    "UserProperty_Type",
    "UserProperty",
    "generate_patch_user_property_body",
    "update_user",
    "set_user_landing_page",
    "reset_password",
    "request_password_reset",
    "download_avatar",
    "generate_avatar_bytestr",
    "upload_avatar",
    "user_is_allowed_direct_signon",
]


class UserProperty_Type(DomoEnumMixin, Enum):
    """Enumeration of available user property types."""

    display_name = "displayName"
    email_address = "emailAddress"
    phone_number = "phoneNumber"
    title = "title"
    department = "department"
    web_landing_page = "webLandingPage"
    web_mobile_landing_page = "webMobileLandingPage"
    role_id = "roleId"
    employee_id = "employeeId"
    employee_number = "employeeNumber"
    hire_date = "hireDate"
    reports_to = "reportsTo"


class UserProperty:
    """Represents a user property with its type and values."""

    def __init__(self, property_type: UserProperty_Type, values: str | list[str]):
        """Initialize a user property.

        Args:
            property_type: The type of property from UserProperty_Type enum
            values: The value(s) for the property (can be single value or list)
        """
        self.property_type = property_type
        self.values = self._value_to_list(values)

    @staticmethod
    def _value_to_list(values: str | list[str]) -> list[str]:
        """Convert values to list format if not already.

        Args:
            values: Single value or list of values

        Returns:
            list: Values as a list
        """
        return values if isinstance(values, list) else [values]

    def to_dict(self):
        """Convert the property to dictionary format for API requests.

        Returns:
            dict: Property in API format with key and values
        """
        return {
            "key": self.property_type.value,
            "values": self._value_to_list(self.values),
        }


def generate_patch_user_property_body(user_property_ls: list[UserProperty]) -> dict:
    """Generate request body for user property updates.

    Args:
        user_property_ls: list of UserProperty objects to update

    Returns:
        dict: Request body with attributes array for PATCH request
    """
    return {
        "attributes": [user_property.to_dict() for user_property in user_property_ls]
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_user(
    auth: DomoAuth,
    user_id: str,
    user_property_ls: list[UserProperty],
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """Update user properties via the identity API.

    Args:
        user_id: ID of the user to update
        user_property_ls: list of UserProperty objects with updates
        auth: Authentication object
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object confirming property updates

    Raises:
        User_CRUD_Error: If property update fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/users/{user_id}"

    body = {}

    if isinstance(user_property_ls, list):
        if isinstance(user_property_ls[0], UserProperty):
            body = generate_patch_user_property_body(user_property_ls)

        if isinstance(user_property_ls[0], dict):
            body = {"attributes": user_property_ls}

    if not body:
        raise ValueError(f"Invalid user_property_ls format {user_property_ls}")

    res = await gd.get_data(
        url=url,
        method="PATCH",
        auth=auth,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_CRUD_Error(operation="update_properties", user_id=user_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def set_user_landing_page(
    auth: DomoAuth,
    user_id: str,
    page_id: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """Set a user's landing page.

    Args:
        auth: Authentication object
        user_id: ID of the user to update
        page_id: ID of the page to set as landing page
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object confirming the update

    Raises:
        User_CRUD_Error: If landing page update fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/landings/target/DESKTOP/entity/PAGE/id/{page_id}/{user_id}"

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_CRUD_Error(
            operation="set_landing_page",
            user_id=user_id,
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def reset_password(
    auth: DomoAuth,
    user_id: str,
    new_password: str,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Reset a user's password.

    Args:
        auth: Authentication object
        user_id: ID of the user whose password to reset
        new_password: New password for the user
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object confirming password reset

    Raises:
        User_CRUD_Error: If password reset fails
        ResetPasswordPasswordUsedError: If password was previously used
    """

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/password"

    body = {"domoUserId": user_id, "password": new_password}

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_CRUD_Error(
            operation="reset_password",
            user_id=user_id,
            res=res,
            message="unable to change password",
        )

    if (
        res.status == 200
        and res.response.get("description", None)
        == "Password has been used previously."
    ):
        raise ResetPasswordPasswordUsedError(
            user_id=user_id,
            res=res,
            message=res.response["description"].replace(".", ""),
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def request_password_reset(
    domo_instance: str,
    email: str,
    locale: str = "en-us",
    *,
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
):
    """Request a password reset for a user via email.

    Args:
        domo_instance: Name of the Domo instance
        email: Email address of the user requesting password reset
        locale: Locale for the reset email (default: "en-us")
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object confirming password reset request

    Raises:
        User_CRUD_Error: If password reset request fails
    """
    url = f"https://{domo_instance}.domo.com/api/domoweb/auth/sendReset"

    params = {"email": email, "locale": locale}

    res = await gd.get_data(
        url=url,
        method="GET",
        params=params,
        auth=None,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_CRUD_Error(
            operation="request_password_reset",
            res=res,
            message=f"unable to request password reset {res.response}",
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def download_avatar(
    auth: DomoAuth,
    user_id: str,
    pixels: int = 300,
    folder_path="./images",
    img_name=None,
    is_download_image: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """Download a user's avatar image.

    Args:
        user_id: ID of the user whose avatar to download
        auth: Authentication object
        pixels: Size of the avatar in pixels (default: 300)
        folder_path: Path to save the avatar image (default: "./images")
        img_name: Custom name for the image file (optional)
        is_download_image: Whether to save image to disk (default: True)
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing avatar data

    Raises:
        DownloadAvatar_Error: If avatar download fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/avatar/USER/{user_id}?size={pixels}"

    res = await gd.get_data_stream(
        url=url,
        method="GET",
        auth=auth,
        headers={"accept": "image/png;charset=utf-8"},
        context=context,
    )

    if return_raw:
        return res

    if res.status != 200:
        raise DownloadAvatar_Error(user_id=user_id, res=res)

    if is_download_image is True:
        img_name = f"{user_id}.png" if img_name is None else img_name

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(f"{folder_path}/{img_name}", "wb") as file:
            file.write(res.response)

    return res


def generate_avatar_bytestr(img_bytestr: bytes | str, img_type: str) -> str:
    """Generate base64 encoded avatar byte string for upload.

    Args:
        img_bytestr: Image data as bytes or base64 string
        img_type: Image type ('jpg' or 'png')

    Returns:
        str: Base64 encoded image string with data URI prefix
    """
    if isinstance(img_bytestr, str):
        img_bytestr = img_bytestr.encode("utf-8")

    if not images.isBase64(img_bytestr):
        img_bytestr = base64.b64encode(img_bytestr)

    img_bytestr = img_bytestr.decode("utf-8")

    html_encoding = f"data:image/{img_type};base64,"

    if not img_bytestr.startswith(html_encoding):
        img_bytestr = html_encoding + img_bytestr

    return img_bytestr


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def upload_avatar(
    auth: DomoAuth,
    user_id: int,
    img_bytestr: bytes,
    img_type: str,  #'jpg or png'
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """Upload an avatar image for a user.

    Args:
        auth: Authentication object
        user_id: ID of the user to update avatar for
        img_bytestr: Image data as bytes
        img_type: Image type ('jpg' or 'png')
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object confirming avatar upload

    Raises:
        User_CRUD_Error: If avatar upload fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/avatar/bulk"

    body = {
        "base64Image": generate_avatar_bytestr(img_bytestr, img_type),
        "encodedImage": generate_avatar_bytestr(img_bytestr, img_type),
        "isOpen": False,
        "entityIds": [user_id],
        "entityType": "USER",
    }

    res = await gd.get_data(
        url=url,
        method="POST",
        body=body,
        auth=auth,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_CRUD_Error(
            operation="upload_avatar",
            user_id=str(user_id),
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def user_is_allowed_direct_signon(
    auth: DomoAuth,
    user_ids: list[str],
    is_allow_dso: bool = True,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Manage direct sign-on permissions for users.

    Args:
        auth: Authentication object
        user_ids: list of user IDs to modify
        is_allow_dso: Whether to allow direct sign-on (default: True)
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object confirming permission changes

    Raises:
        User_CRUD_Error: If direct sign-on permission update fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users/directSignOn"
    params = {"value": is_allow_dso}

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        params=params,
        body=user_ids if isinstance(user_ids, list) else [user_ids],
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise User_CRUD_Error(
            operation="set_direct_signon",
            res=res,
        )

    return res
