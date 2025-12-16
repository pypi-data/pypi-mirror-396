"""Token-based authentication classes for Domo (access tokens)."""

from dataclasses import dataclass, field

from ..base.exceptions import AuthError
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)
from .base import _DomoAuth_Optional, _DomoAuth_Required


class _DomoTokenAuth_Required(_DomoAuth_Required, _DomoAuth_Optional):  # noqa: N801
    """Mixin for required parameters for DomoTokenAuth.

    This class provides token-based authentication functionality using pre-generated
    access tokens from Domo's admin panel. This is useful in environments where
    direct username/password authentication is not permitted.

    Attributes:
        domo_access_token (str): Pre-generated access token from Domo admin panel
    """

    def __init__(
        self,
        domo_access_token: str,
        domo_instance: str,
        token_name: str | None = None,
        token: str | None = None,
        user_id: str | None = None,
        is_valid_token: bool = False,
    ):
        """Initialize token authentication with pre-generated access token.

        Args:
            domo_access_token (str): Pre-generated access token from Domo admin panel
            domo_instance (str): The Domo instance identifier
            token_name (str | None): Name identifier for the token
            token (str | None): The authentication token (will be set to access token)
            user_id (str | None): The authenticated user's ID
            is_valid_token (bool): Whether the current token is valid

        Raises:
            InvalidCredentialsError: If domo_access_token is empty
        """
        if not domo_access_token:
            raise AuthError(message="Domo access token is required.")
        self.domo_access_token = domo_access_token

        _DomoAuth_Required.__init__(self, domo_instance)
        _DomoAuth_Optional.__init__(
            self, domo_instance, token_name, token, user_id, is_valid_token
        )

    @property
    def auth_header(self) -> dict:
        """Generate the authentication header for access token based authentication.

        Returns:
            dict: HTTP headers with 'x-domo-developer-token' containing the access token
        """
        return {"x-domo-developer-token": self.token or self.domo_access_token}

    @log_call(
        level_name="auth",
        config=LogDecoratorConfig(
            entity_extractor=DomoEntityExtractor(),
            result_processor=DomoEntityResultProcessor(),
        ),
    )
    async def get_auth_token(
        self,
        token_name: str | None = None,
        **context_kwargs,
    ) -> str:
        """Retrieve the access token, updating internal attributes as necessary.

        For token authentication, this method validates the token by calling who_am_i
        if no user_id is set, then returns the access token.

        Args:
            token_name (str | None): Override token name for display purposes
            **context_kwargs: Context parameters (session, debug_api, debug_num_stacks_to_drop, etc.)

        Returns:
            str: The access token
        """

        if not self.user_id:
            await self.who_am_i(**context_kwargs)

        self.token = self.domo_access_token
        self.is_valid_token = True

        if token_name:
            self.token_name = token_name

        return self.token


@dataclass
class DomoTokenAuth(_DomoTokenAuth_Required):
    """Token-based authentication using pre-generated access tokens.

    This authentication method uses access tokens generated from Domo's admin panel
    (Admin > Access Tokens). This is particularly useful in environments where
    direct username/password authentication is not permitted or for automated systems.

    Attributes:
        domo_access_token (str): Pre-generated access token (not shown in repr)
        domo_instance (str): The Domo instance identifier
        token_name (str | None): Name identifier for the token
        token (str | None): The authentication token (not shown in repr)
        user_id (str | None): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid
        use_cache (bool): Enable HTTP response caching (default: True)
        cache_size (int): Maximum number of cache entries (default: 1000)
        cache_default_ttl (int): Default cache TTL in seconds (default: 300)
        cache_strategy (str | None): Cache invalidation strategy (default: None, uses SMART)
        custom_cache_rules (dict | None): Custom cache invalidation rules (default: None)

    Example:
        >>> auth = DomoTokenAuth(
        ...     domo_access_token="your-access-token-here",
        ...     domo_instance="mycompany"
        ... )
        >>> token = await auth.get_auth_token()
    """

    domo_access_token: str = field(repr=False)
    domo_instance: str

    token_name: str | None = None
    token: str | None = field(default=None, repr=False)
    user_id: str | None = None
    is_valid_token: bool = False

    # Phase 3: Cache configuration
    use_cache: bool = True  # Default enabled for optimization
    cache_size: int = 1000
    cache_default_ttl: int = 300  # 5 minutes default TTL
    cache_strategy: str | None = None  # None = use default (SMART)
    custom_cache_rules: dict[str, list[str]] | None = None

    def __post_init__(self):
        """Initialize the authentication after dataclass creation."""
        self.token = self.domo_access_token

        if not self.token:
            raise AuthError(message="Domo access token is required.")

        _DomoTokenAuth_Required.__init__(
            self,
            domo_access_token=self.domo_access_token,
            domo_instance=self.domo_instance,
            token_name=self.token_name,
            token=self.token,
            user_id=self.user_id,
            is_valid_token=self.is_valid_token,
        )

        # Store cache config for session creation
        self._cache_config = {
            "use_cache": self.use_cache,
            "cache_size": self.cache_size,
            "default_ttl": self.cache_default_ttl,
            "cache_strategy": self.cache_strategy,
            "custom_cache_rules": self.custom_cache_rules,
        }
        self._cached_session = None  # Will be created on first use
