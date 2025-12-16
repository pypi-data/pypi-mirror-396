"""Developer authentication classes for Domo (OAuth2 client credentials)."""

from dataclasses import dataclass, field

from ..base.exceptions import AuthError
from ..client.response import ResponseGetData
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)
from .base import _DomoAuth_Optional, _DomoAuth_Required


@dataclass
class DomoDeveloperAuth(_DomoAuth_Optional, _DomoAuth_Required):
    """Developer authentication using client credentials.

    This authentication method uses OAuth2 client credentials (client ID and secret)
    to obtain bearer tokens. This is typically used for applications built on
    Domo's developer platform and requires developer app registration.

    Attributes:
        domo_client_id (str): OAuth2 client ID from developer app registration
        domo_client_secret (str): OAuth2 client secret (not shown in repr)
        domo_instance (str): The Domo instance identifier
        token_name (str | None): Name identifier for the token
        token (str | None): The bearer token (not shown in repr)
        user_id (str | None): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid
        use_cache (bool): Enable HTTP response caching (default: True)
        cache_size (int): Maximum number of cache entries (default: 1000)
        cache_default_ttl (int): Default cache TTL in seconds (default: 300)
        cache_strategy (str | None): Cache invalidation strategy (default: None, uses SMART)
        custom_cache_rules (dict | None): Custom cache invalidation rules (default: None)

    Example:
        >>> auth = DomoDeveloperAuth(
        ...     domo_client_id="your-client-id",
        ...     domo_client_secret="your-client-secret",
        ...     domo_instance="mycompany"
        ... )
        >>> token = await auth.get_auth_token()
    """

    domo_client_id: str
    domo_client_secret: str = field(repr=False)
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
        _DomoAuth_Optional.__init__(
            self,
            domo_instance=self.domo_instance,
            token_name=self.token_name,
            token=self.token,
            user_id=self.user_id,
            is_valid_token=self.is_valid_token,
        )
        _DomoAuth_Required.__init__(self, domo_instance=self.domo_instance)

        # Store cache config for session creation
        self._cache_config = {
            "use_cache": self.use_cache,
            "cache_size": self.cache_size,
            "default_ttl": self.cache_default_ttl,
            "cache_strategy": self.cache_strategy,
            "custom_cache_rules": self.custom_cache_rules,
        }
        self._cached_session = None  # Will be created on first use

    @property
    def auth_header(self) -> dict:
        """Generate the authentication header for developer token authentication.

        Returns:
            dict: HTTP headers with 'Authorization' bearer token, or empty dict if no token
        """
        if self.token:
            return {"Authorization": f"bearer {self.token}"}
        return {}

    @log_call(
        level_name="auth",
        config=LogDecoratorConfig(
            entity_extractor=DomoEntityExtractor(),
            result_processor=DomoEntityResultProcessor(),
        ),
    )
    async def get_auth_token(
        self,
        **context_kwargs,
    ) -> str:
        """Retrieve the developer token using client credentials and update internal attributes.

        This method uses OAuth2 client credentials flow to obtain a bearer token
        from Domo's developer authentication endpoint.

        Args:
            **context_kwargs: Context parameters (session, debug_api, debug_num_stacks_to_drop, etc.)

        Returns:
            str: The bearer token for API authentication

        Raises:
            InvalidCredentialsError: If authentication fails or no token is returned
        """

        from ...routes import auth as auth_routes

        res = await auth_routes.get_developer_auth(
            auth=None,
            domo_client_id=self.domo_client_id,
            domo_client_secret=self.domo_client_secret,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )

        if isinstance(res, ResponseGetData) and res.is_success and res.response:
            self.is_valid_token = True
            self.token = str(
                res.response.get("access_token", "")
                if isinstance(res.response, dict)
                else ""
            )
            self.user_id = (
                res.response.get("userId") if isinstance(res.response, dict) else ""
            )
            self.domo_instance = (
                res.response.get("domain", self.domo_instance)
                if isinstance(res.response, dict)
                else ""
            )
            self.token_name = self.token_name or "developer_auth"
            return self.token

        raise AuthError(message="Failed to retrieve developer token")
