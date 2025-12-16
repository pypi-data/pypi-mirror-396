"""Authentication routes and error handling for Domo API access.

This module provides authentication functions and custom exception classes
for various Domo authentication methods including username/password,
developer tokens, and access tokens.
"""

from typing import Any

from ..base.exceptions import AuthError, RouteError
from ..client import response as rgd
from ..client.context import RouteContext
from ..utils.logging import LogDecoratorConfig, ResponseGetDataProcessor, log_call

__all__ = [
    "AuthError",
    "InvalidCredentialsError",
    "AccountLockedError",
    "InvalidAuthTypeError",
    "InvalidInstanceError",
    "NoAccessTokenReturnedError",
    "get_full_auth",
    "get_developer_auth",
    "who_am_i",
    "elevate_user_otp",
]


class InvalidCredentialsError(RouteError):
    """Raised when invalid credentials are provided to the API."""

    def __init__(self, res=None, **kwargs):
        super().__init__(
            res=res,
            message="Invalid credentials provided",
            **kwargs,
        )


class AccountLockedError(RouteError):
    """Raised when the user account is locked."""

    def __init__(self, res=None, **kwargs):
        super().__init__(
            res=res,
            message="User account is locked",
            **kwargs,
        )


class InvalidAuthTypeError(RouteError):
    """Raised when an invalid authentication type is used for an API call."""

    def __init__(
        self,
        res=None,
        required_auth_type: Any | None = None,
        required_auth_type_ls: list[Any] | None = None,
        **kwargs,
    ):
        # Convert class types to strings
        if required_auth_type:
            required_types = [required_auth_type.__name__]
        elif required_auth_type_ls:
            required_types = [auth_type.__name__ for auth_type in required_auth_type_ls]
        else:
            required_types = ["Unknown"]

        # Build message
        auth_list = ", ".join(required_types)
        message = f"This API requires: {auth_list}"

        super().__init__(
            res=res,
            message=message,
            **kwargs,
        )


class InvalidInstanceError(RouteError):
    """Raised when an invalid Domo instance is provided."""

    def __init__(self, res=None, domo_instance: str | None = None, **kwargs):
        message = (
            f"Invalid Domo instance: {domo_instance}"
            if domo_instance
            else "Invalid Domo instance"
        )

        super().__init__(
            res=res,
            message=message,
            **kwargs,
        )


class NoAccessTokenReturnedError(RouteError):
    """Raised when no access token is returned from the authentication API."""

    def __init__(self, res=None, **kwargs):
        super().__init__(
            res=res,
            message="No access token returned from authentication API",
            **kwargs,
        )


@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_full_auth(
    domo_instance: str,  # domo_instance.domo.com
    domo_username: str,  # email address
    domo_password: str,
    auth: Any | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Authenticate using username and password to retrieve a full_auth access token.

    This function uses Domo's standard username/password authentication to obtain
    a session token that can be used for subsequent API calls.

    Args:
        domo_instance (str): The Domo instance identifier
        domo_username (str): User's email address
        domo_password (str): User's password
        auth (Any | None): Existing auth object (optional)
        return_raw (bool): Whether to return raw response without processing
        context (RouteContext | None): Route context for request configuration
        **context_kwargs: Additional context parameters (debug_api, session, parent_class, etc.)

    Returns:
        rgd.ResponseGetData: Response containing session token or error information

    Raises:
        InvalidInstanceError: If the Domo instance is invalid
        InvalidCredentialsError: If credentials are invalid or missing session token
        AccountLockedError: If the user account is locked
        NoAccessTokenReturned: If no access token is returned from the API
    """

    from ..client import get_data as gd
    from ..client.context import RouteContext

    domo_instance = domo_instance or (auth.domo_instance if auth else "")

    url = f"https://{domo_instance}.domo.com/api/content/v2/authentication"

    body = {
        "method": "password",
        "emailAddress": domo_username,
        "password": domo_password,
    }

    context = RouteContext.build_context(context, **context_kwargs)

    res = await gd.get_data(
        auth=auth,  # type: ignore  # Auth can be None for authentication endpoints
        method="POST",
        url=url,
        body=body,
        context=context,
        return_raw=return_raw,
    )

    if return_raw:
        # Type assertion for raw return
        return res  # type: ignore

    # Validate response type
    if not isinstance(res, rgd.ResponseGetData):
        raise TypeError(f"Expected ResponseGetData, got {type(res)}")

    # Handle specific error cases
    if res.status == 403 and res.response == "Forbidden":
        raise InvalidInstanceError(res=res, domo_instance=domo_instance)

    if res.is_success and isinstance(res.response, dict):
        reason = res.response.get("reason")

        if reason == "INVALID_CREDENTIALS":
            res.is_success = False
            raise InvalidCredentialsError(res=res)

        if reason == "ACCOUNT_LOCKED":
            res.is_success = False
            raise AccountLockedError(res=res)

        # Check for empty response
        if res.response == {} or res.response == "":
            res.is_success = False
            raise NoAccessTokenReturnedError(res=res)

    # Validate session token presence
    if isinstance(res.response, dict) and not res.response.get("sessionToken"):
        res.is_success = False
        raise InvalidCredentialsError(res=res)

    return res


@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def get_developer_auth(
    domo_client_id: str,
    domo_client_secret: str,
    auth: Any | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Authenticate using OAuth2 client credentials for developer APIs.

    This function is specifically for authenticating against APIs documented
    under developer.domo.com using OAuth2 client credentials flow.

    Args:
        domo_client_id (str): OAuth2 client ID from developer app registration
        domo_client_secret (str): OAuth2 client secret
        auth (Any | None): Existing auth object (optional)
        return_raw (bool): Whether to return raw response without processing
        context (RouteContext | None): Route context for request configuration
        **context_kwargs: Additional context parameters (debug_api, session, parent_class, etc.)

    Returns:
        rgd.ResponseGetData: Response containing access token or error information

    Raises:
        InvalidCredentialsError: If the client credentials are invalid
    """

    from ..client import get_data as gd
    from ..client.context import RouteContext

    url = "https://api.domo.com/oauth/token?grant_type=client_credentials"

    context = RouteContext.build_context(context, **context_kwargs)

    url = "https://api.domo.com/oauth/token?grant_type=client_credentials"

    res = await gd.get_data(
        method="GET",
        url=url,
        auth=auth,  # type: ignore  # Auth can be None for authentication endpoints
        context=context,
        return_raw=return_raw,
    )

    if return_raw:
        # Type assertion for raw return
        return res  # type: ignore

    # Validate response type
    if not isinstance(res, rgd.ResponseGetData):
        raise TypeError(f"Expected ResponseGetData, got {type(res)}")

    # Handle authentication errors
    if res.status == 401 and res.response == "Unauthorized":
        res.is_success = False
        raise InvalidCredentialsError(res=res)

    return res


@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
    color="cyan",
)
async def who_am_i(
    auth: Any,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Validate authentication against the 'me' API endpoint.

    This function validates the authentication token by calling Domo's user 'me' API.
    This is the same authentication test the Domo Java CLI uses.

    Args:
        auth (Any): Authentication object containing domo_instance and auth tokens
        return_raw (bool): Whether to return raw response without processing
        context (RouteContext | None): Route context for request configuration
        **context_kwargs: Additional context parameters (debug_api, session, parent_class, etc.)

    Returns:
        rgd.ResponseGetData: Response containing user information or error details

    Raises:
        InvalidInstanceError: If the Domo instance is invalid (403 Forbidden)
        InvalidCredentialsError: If the authentication token is invalid
    """

    from ..client import get_data as gd
    from ..client.context import RouteContext

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/users/me"

    context = RouteContext.build_context(context, **context_kwargs)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
        return_raw=return_raw,
    )

    if not res.is_success:
        # The @log_call decorator will handle error logging automatically
        pass

    if return_raw:
        # Type assertion for raw return
        return res  # type: ignore

    # Validate response type
    if not isinstance(res, rgd.ResponseGetData):
        raise TypeError(f"Expected ResponseGetData, got {type(res)}")

    # Handle specific error cases
    if res.status == 403 and res.response == "Forbidden":
        raise InvalidInstanceError(res=res)

    if res.status == 401 and res.response == "Unauthorized":
        res.is_success = False  # Fix typo: was is_sucess

    if not res.is_success:
        raise InvalidCredentialsError(res=res)

    return res


@log_call(
    level_name="route",
    config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
)
async def elevate_user_otp(
    auth: Any,
    one_time_password: str,
    user_id: str | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Elevate authentication using a one-time password (OTP).

    This function is used when multi-factor authentication is enabled and
    an additional OTP verification step is required.

    Args:
        auth (Any): Authentication object containing domo_instance and tokens
        one_time_password (str): The OTP code for authentication elevation
        user_id (str | None): User ID (will be retrieved from auth if not provided)
        context (RouteContext | None): Route context for request configuration
        **context_kwargs: Additional context parameters (debug_api, session, parent_class, etc.)

    Returns:
        rgd.ResponseGetData: Response from the OTP elevation request

    Raises:
        InvalidCredentialsError: If the OTP is invalid or elevation fails
    """
    from ..client import get_data as gd

    # Get user_id from auth if not provided
    if not auth.user_id and not user_id:
        await auth.who_am_i()

    user_id = user_id or auth.user_id

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/elevations/{user_id}"

    body = {"timeBasedOneTimePassword": one_time_password}

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        context=context,
    )

    # Validate response type
    if not isinstance(res, rgd.ResponseGetData):
        raise TypeError(f"Expected ResponseGetData, got {type(res)}")

    if not res.is_success:
        raise InvalidCredentialsError(res=res)

    return res
