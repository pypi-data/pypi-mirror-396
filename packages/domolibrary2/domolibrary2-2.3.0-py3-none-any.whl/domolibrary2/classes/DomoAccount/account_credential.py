__all__ = [
    "DACNoTargetInstanceError",
    "DACNoTargetUserError",
    "DACNoPasswordError",
    "DACNoUserNameError",
    "DACNoAccessTokenNameError",
    "DACNoAccessTokenError",
    "DACValidAuthError",
    "DomoAccountCredential",
]


from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth, DomoFullAuth, DomoTokenAuth
from ...base.exceptions import AuthError, ClassError, DomoError
from ...client.context import RouteContext
from ...utils import convert as dmcv
from ..DomoInstanceConfig.access_token import DomoAccessToken
from ..DomoUser import DomoUser, DomoUsers
from .account_default import DomoAccount_Default


class DACNoTargetInstanceError(ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            message=f"no target_instance on class - {cls_instance.name}",
            cls_instance=cls_instance,
        )


class DACNoTargetUserError(ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            message=f"no target_user on class - {cls_instance.name}",
            cls_instance=cls_instance,
        )


class DACNoPasswordError(ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            message=f"no password stored in account - {cls_instance.name}",
            cls_instance=cls_instance,
        )


class DACNoUserNameError(ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            message=f"no username stored in account - {cls_instance.name}",
            cls_instance=cls_instance,
        )


class DACNoAccessTokenNameError(ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            message="must pass access token name to retrieve",
            cls_instance=cls_instance,
        )


class DACNoAccessTokenError(ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            message=f"no access_token stored in account - {cls_instance.name}",
            cls_instance=cls_instance,
        )


class DACValidAuthError(ClassError):
    def __init__(self, cls_instance, message=None):
        super().__init__(
            message=message
            or f"{cls_instance.name} no valid auth retrieved for domo_instance - {cls_instance.target_instance}",
            cls_instance=cls_instance,
        )


@dataclass
class DomoAccountCredential(DomoAccount_Default):
    """Account credential management class for Domo accounts.

    This class extends DomoAccount_Default to provide credential management
    capabilities including authentication testing, password management, and
    access token operations.

    Attributes:
        target_instance: Target Domo instance for credential operations
        is_valid_full_auth: Whether full authentication is valid
        is_valid_token_auth: Whether token authentication is valid
        target_auth: Active authentication object for target instance
        target_user: DomoUser object for the target user
        target_access_token: Access token for the account
    """

    target_auth: DomoAuth = field(default=None, compare=False)
    target_user: DomoUser = field(default=None, compare=False)
    target_access_token: DomoAccessToken = field(default=None, compare=False)
    target_instance: str = field(default=None)

    is_valid_full_auth: bool = None
    is_valid_token_auth: bool = None

    _token_auth: DomoAuth = field(repr=False, default=None, compare=False)
    _full_auth: DomoAuth = field(repr=False, default=None, compare=False)

    # Note: __post_init__ is inherited from DomoAccount_Default
    # which initializes the Access subentity

    @classmethod
    def from_dict(
        cls,
        obj: dict[str, Any],
        is_admin_summary: bool = True,
        auth: DomoAuth | None = None,
        is_use_default_account_class: bool = False,
        **kwargs,
    ):
        """Create Account_Credential from dictionary representation.

        Args:
            obj: Dictionary containing account data
            is_admin_summary: Whether this is an admin summary view
            auth: Authentication object
            **kwargs: Additional keyword arguments including target_instance

        Returns:
            DomoAccount_Credential instance
        """
        # Note: is_use_default_account_class is consumed here and not passed to parent
        # to avoid TypeError when passed to dataclass __init__
        return super().from_dict(
            obj=obj,
            is_admin_summary=is_admin_summary,
            auth=auth,
            new_cls=cls,
            target_instance=kwargs.get("target_instance"),
        )

    def set_password(self, password: str) -> bool:
        """Set the password in the account configuration.

        Args:
            password: New password to set

        Returns:
            True if successful
        """
        self.Config.password = password
        return True

    def set_username(self, username: str) -> bool:
        """Set the username in the account configuration.

        Args:
            username: New username to set

        Returns:
            True if successful
        """
        self.Config.username = username
        return True

    def set_access_token(self, access_token: str) -> bool:
        """Set the access token in the account configuration.

        Args:
            access_token: New access token to set

        Returns:
            True if successful
        """
        self.Config.domo_access_token = access_token
        return True

    async def test_full_auth(
        self, debug_api: bool = False, session: httpx.AsyncClient | None = None
    ) -> bool:
        """Test full authentication (username/password) for the account.

        Generates a DomoFullAuth object and validates it against the target instance.

        Args:
            debug_api: Enable API debugging
            session: HTTP client session (optional)

        Returns:
            True if authentication is valid, False otherwise

        Raises:
            DAC_NoUserName: If username is not configured
            DAC_NoPassword: If password is not configured
            DAC_NoTargetInstance: If target instance is not set
        """
        self.is_valid_full_auth = False

        if not self.Config.username:
            raise DACNoUserNameError(self)

        if not self.Config.password:
            raise DACNoPasswordError(self)

        if not self.target_instance:
            raise DACNoTargetInstanceError(self)

        self._full_auth = DomoFullAuth(
            domo_instance=self.target_instance,
            domo_username=self.Config.username,
            domo_password=self.Config.password,
        )

        try:
            await self._full_auth.print_is_token(debug_api=debug_api, session=session)
            self.is_valid_full_auth = True

        except AuthError as e:
            dmcv.print_md(f"🤯 test_full_auth for: ***{self.name}*** returned {e}")

            self.is_valid_full_auth = False

        return self.is_valid_full_auth

    async def test_token_auth(
        self, debug_api: bool = False, session: httpx.AsyncClient | None = None
    ) -> bool:
        """Test token authentication for the account.

        Generates a DomoTokenAuth object and validates it against the target instance.

        Args:
            debug_api: Enable API debugging
            session: HTTP client session (optional)

        Returns:
            True if authentication is valid, False otherwise

        Raises:
            DAC_NoAccessToken: If access token is not configured
            DAC_NoTargetInstance: If target instance is not set
        """

        self.is_valid_token_auth = False

        if not self.Config.domo_access_token:
            raise DACNoAccessTokenError(self)

        if not self.target_instance:
            raise DACNoTargetInstanceError(self)

        self._token_auth = DomoTokenAuth(
            domo_instance=self.target_instance,
            domo_access_token=self.Config.domo_access_token,
        )

        try:
            await self._token_auth.print_is_token(debug_api=debug_api, session=session)
            self.is_valid_token_auth = True
            self.target_auth = self._token_auth

        except AuthError as e:
            dmcv.print_md(f"🤯 test_token_auth for: ***{self.name}*** returned {e}")
            self.is_valid_token_auth = False

        return self.is_valid_token_auth

    def _set_target_auth(
        self,
        valid_backup_auth: DomoAuth | None = None,
    ) -> DomoAuth:
        """Set target authentication using best available method.

        Prioritizes authentication methods in order: Token Auth > Full Auth > Backup Auth

        Args:
            valid_backup_auth: Validated backup authentication object to use as fallback

        Returns:
            The selected authentication object

        Raises:
            DACValidAuthError: If no valid authentication method is available
        """

        target_auth = None

        if self.is_valid_token_auth:
            target_auth = self._token_auth

        if self.is_valid_full_auth:
            target_auth = self._full_auth

        if not target_auth and (valid_backup_auth and valid_backup_auth.is_valid_token):
            target_auth = valid_backup_auth

        if not target_auth:
            raise DACValidAuthError(self)

        self.target_auth = target_auth

        return self.target_auth

    async def test_auths(
        self,
        backup_auth: DomoAuth | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
    ) -> dict:
        """Test both token and full authentication methods.

        Attempts to validate both authentication methods and sets the best available
        as the target authentication.

        Args:
            backup_auth: Backup authentication to use if configured auths fail
            debug_api: Enable API debugging
            session: HTTP client session (optional)

        Returns:
            Dictionary with authentication test results
        """
        ## test token auth
        try:
            await self.test_token_auth(debug_api=debug_api, session=session)

        except DomoError as e:
            print(f"testing token: {self.name}: {e}")

        ## test full auth
        try:
            await self.test_full_auth(debug_api=debug_api, session=session)

        except DomoError as e:
            print(f"testing full auth: {self.name}: {e}")

        ## generate target_auth
        try:
            self._set_target_auth(valid_backup_auth=backup_auth)
        except DACValidAuthError as e:
            print(f"{self.name}: unable to generate valid target_auth: {e}")
        return self.to_dict()

    def to_dict(self, return_snake_case: bool = False) -> dict:
        """Convert credential information to dictionary.

        Returns:
            Dictionary containing account ID, alias, instance, and auth validity status
        """

        s = super().to_dict(return_snake_case=return_snake_case)
        s.update(
            {
                "account_id": self.id,
                "alias": self.name,
                "target_instance": self.target_instance,
                "is_valid_full_auth": self.is_valid_full_auth,
                "is_valid_token_auth": self.is_valid_token_auth,
            }
        )
        return s

    async def get_target_user(
        self,
        user_email: str | None = None,
        target_auth: DomoAuth | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoUser:
        """Retrieve the target user for this account.

        Args:
            user_email: Email address of user (defaults to configured username)
            target_auth: Authentication object (defaults to self.target_auth)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            context: Optional RouteContext for API call configuration

        Returns:
            DomoUser object for the target user

        Raises:
            DAC_NoUserName: If user email is not provided or configured
            DACValidAuthError: If target authentication is not available
            DAC_NoTargetUser: If user cannot be found
        """
        user_email = user_email or self.Config.username

        if not user_email:
            raise DACNoUserNameError(self)

        target_auth = target_auth or self.target_auth

        if not target_auth:
            raise DACValidAuthError(
                self,
                message="no target_auth, pass a valid backup_auth",
            )

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        self.target_user = await DomoUsers(auth=target_auth).search_by_email(
            email=[user_email],
            context=context,
        )

        if not self.target_user:
            raise DACNoTargetUserError(self)

        return self.target_user

    async def update_target_user_password(
        self,
        new_password: str,
        user_email: str | None = None,
        is_update_account: bool = True,
        target_auth: DomoAuth | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> "DomoAccountCredential":
        """Update the password for the target user.

        Args:
            new_password: New password to set for the user
            user_email: Email address of user (defaults to configured username)
            is_update_account: Whether to update the account config with new password
            target_auth: Authentication object (defaults to self.target_auth)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            Self for method chaining

        Raises:
            DACValidAuthError: If target authentication is not available
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        target_auth = target_auth or self.target_auth

        if not target_auth:
            raise DACValidAuthError(
                self,
                message="no target_auth, pass a valid backup_auth",
            )

        if not self.target_user:
            await self.get_target_user(
                context=context,
                user_email=user_email,
                target_auth=target_auth,
                **context_kwargs,
            )

        await self.target_user.reset_password(
            new_password=new_password,
            context=context,
            **context_kwargs,
        )

        self.set_password(new_password)

        if is_update_account:
            await self.update_config(context=context, **context_kwargs)

        return self

    async def get_target_access_token(
        self,
        token_name: str | None = None,
        user_email: str | None = None,
        target_auth: DomoAuth | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoAccessToken:
        """Retrieve an access token for the target user.

        Args:
            token_name: Name of the access token (defaults to account name)
            user_email: Email address of user (defaults to configured username)
            target_auth: Authentication object (defaults to self.target_auth)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoAccessToken object if found, None otherwise

        Raises:
            DACValidAuthError: If target authentication is not available
            DAC_NoAccessTokenName: If token name is not provided or available
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        target_auth = target_auth or self.target_auth

        if not target_auth:
            raise DACValidAuthError(
                self,
                message="no target_auth, pass a valid backup_auth",
            )

        if not self.target_user:
            await self.get_target_user(
                context=context,
                user_email=user_email,
                target_auth=target_auth,
            )

        token_name = token_name or self.name

        if not token_name:
            raise DACNoAccessTokenNameError(self)

        domo_access_tokens = await self.target_user.get_access_tokens(
            context=context,
        )

        self.target_access_token = next(
            (
                dat
                for dat in domo_access_tokens
                if dat and (dat.name and dat.name.lower() == token_name.lower())
            ),
            None,
        )

        if not self.target_access_token:
            raise DACNoAccessTokenNameError(self)

        return self.target_access_token

    async def regenerate_target_access_token(
        self,
        token_name: str | None = None,
        duration_in_days: int = 90,
        user_email: str | None = None,
        is_update_account: bool = True,
        target_auth: DomoAuth | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> "DomoAccountCredential":
        """Regenerate or create an access token for the target user.

        If a token with the given name exists, it will be regenerated. Otherwise,
        a new token will be created.

        Args:
            token_name: Name of the access token (defaults to account name)
            duration_in_days: Token validity duration in days (default: 90)
            user_email: Email address of user (defaults to configured username)
            is_update_account: Whether to update the account config with new token
            target_auth: Authentication object (defaults to self.target_auth)
            debug_api: Enable API debugging
            session: HTTP client session (optional)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            Self for method chaining

        Raises:
            DACValidAuthError: If target authentication is not available
            DAC_NoTargetUser: If target user cannot be retrieved
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        target_auth = target_auth or self.target_auth

        if not target_auth:
            raise DACValidAuthError(
                self,
                message="no target_auth, pass a valid backup_auth",
            )

        domo_access_token = await self.get_target_access_token(
            token_name=token_name,
            user_email=user_email,
            target_auth=target_auth,
            context=context,
        )  # handles retrieving target user

        if not self.target_user:
            raise DACNoTargetUserError(self)

        if domo_access_token:
            await domo_access_token.regenerate(
                duration_in_days=duration_in_days, context=context
            )

        else:
            domo_access_token = await DomoAccessToken.generate(
                duration_in_days=duration_in_days,
                token_name=token_name,
                auth=target_auth,
                owner=self.target_user,
                context=context,
            )

            self.target_access_token = domo_access_token

        self.set_access_token(domo_access_token.token)

        if is_update_account:
            await self.update_config(context=context)

        return self
