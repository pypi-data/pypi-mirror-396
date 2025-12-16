"""Base authentication classes for Domo authentication."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from ..client.response import ResponseGetData
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)


class _DomoAuth_Required(ABC):  # noqa: N801
    """Abstract base class for required Domo authentication parameters.

    This class provides the minimal required functionality for Domo authentication,
    including instance validation and manual login URL generation.

    Attributes:
        domo_instance (str): The Domo instance identifier (e.g., 'mycompany' or 'mycompany.domo.com')
    """

    def __init__(self, domo_instance: str):
        """Initialize with required Domo instance.

        Args:
            domo_instance (str): The Domo instance identifier

        Raises:
            InvalidInstanceError: If domo_instance is empty or None
        """
        if not domo_instance:
            from ..base.exceptions import AuthError

            raise AuthError(message="Domo instance is required. Example: 'mycompany'")

        self.domo_instance = domo_instance

    @property
    def url_manual_login(self) -> str:
        """Generate the manual login URL for the Domo instance.

        Returns:
            str: The complete URL for manual login to the Domo instance
        """
        return f"https://{self.domo_instance}.domo.com/auth/index?domoManualLogin=true"


class _DomoAuth_Optional(ABC):  # noqa: N801
    """Abstract base class for optional Domo authentication functionality.

    This class provides common authentication methods and token management
    functionality that can be shared across different authentication types.

    Attributes:
        domo_instance (str): The Domo instance identifier
        token_name (str | None): Name identifier for the token
        token (str | None): The authentication token
        user_id (str | None): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid
    """

    def __init__(
        self,
        domo_instance: str,
        token_name: str | None = None,
        token: str | None = None,
        user_id: str | None = None,
        is_valid_token: bool = False,
    ):
        """Initialize optional authentication parameters.

        Args:
            domo_instance (str): The Domo instance identifier
            token_name (str | None): Name identifier for the token
            token (str | None): The authentication token
            user_id (str | None): The authenticated user's ID
            is_valid_token (bool): Whether the current token is valid

        Raises:
            InvalidInstanceError: If domo_instance is empty or None
        """
        self.domo_instance = domo_instance
        self.token_name = token_name
        self.token = token
        self.user_id = user_id
        self.is_valid_token = is_valid_token

        self._set_token_name()

        if not self.domo_instance:
            from ..base.exceptions import AuthError

            raise AuthError(
                message="Domo instance is required. Example: 'mycompany.domo.com' or 'mycompany'"
            )

    def _set_token_name(self):
        """Set default token name to domo_instance if not provided."""
        if not self.token_name:
            self.token_name = self.domo_instance

    @property
    @abstractmethod
    def auth_header(self) -> dict:
        """Generate authentication headers for API requests.

        Returns:
            dict: HTTP headers containing authentication information

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement auth_header property.")

    @log_call(
        level_name="auth",
        config=LogDecoratorConfig(
            entity_extractor=DomoEntityExtractor(),
            result_processor=DomoEntityResultProcessor(),
        ),
        color="cyan",
    )
    async def who_am_i(
        self,
        **context_kwargs,
    ) -> ResponseGetData:
        """Perform an API call to identify the user associated with the token.

        This method validates the authentication token by calling the Domo 'me' API
        endpoint and updates the user_id and token validity status.

        Args:
            **context_kwargs: Context parameters (session, debug_api, debug_num_stacks_to_drop, etc.)

        Returns:
            ResponseGetData: Response containing user information and success status

        Raises:
            TypeError: If the response is not of expected ResponseGetData type
        """
        from ..routes import auth as auth_routes

        res = await auth_routes.who_am_i(
            auth=self,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )

        if res.is_success:
            self.is_valid_token = True

        if res.response and isinstance(res.response, dict):
            self.user_id = res.response.get("id")

        return res

    @log_call(
        level_name="auth",
        config=LogDecoratorConfig(
            entity_extractor=DomoEntityExtractor(),
            result_processor=DomoEntityResultProcessor(),
        ),
    )
    async def elevate_otp(
        self,
        one_time_password: str,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
    ):
        """Elevate the authentication to include OTP (One-Time Password) if required.

        This method is used when multi-factor authentication is enabled and an
        additional OTP verification step is required.

        Args:
            one_time_password (str): The OTP code for authentication elevation
            debug_api (bool): Whether to enable API debugging
            session (httpx.AsyncClient | None): HTTP client session to use
            debug_num_stacks_to_drop (int): Number of stack frames to drop for debugging

        Returns:
            ResponseGetData: Response from the OTP elevation request
        """
        if session is None:
            async with httpx.AsyncClient() as client_session:
                from ..routes import auth as auth_routes

                return await auth_routes.elevate_user_otp(
                    auth=self,
                    debug_api=debug_api,
                    session=client_session,
                    one_time_password=one_time_password,
                    debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                )
        else:
            from ..routes import auth as auth_routes

            return await auth_routes.elevate_user_otp(
                auth=self,
                debug_api=debug_api,
                session=session,
                one_time_password=one_time_password,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            )

    @abstractmethod
    async def get_auth_token(
        self,
        **context_kwargs,
    ) -> str | ResponseGetData:
        """Retrieve or generate an authentication token.

        This abstract method must be implemented by subclasses to handle
        the specific authentication flow for each authentication type.

        Args:
            **context_kwargs: Context parameters (session, debug_api, debug_num_stacks_to_drop, etc.)

        Returns:
            Union[str, ResponseGetData]: The authentication token or raw response data

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement get_auth_token method.")

    async def print_is_token(
        self,
        token_name: str | None = None,
        **context_kwargs,
    ) -> bool:
        """Print token status and return True if token is valid, otherwise False.

        This method performs a complete authentication check including token
        retrieval and validation, then prints a user-friendly status message.

        Args:
            token_name (str | None): Override token name for display purposes
            **context_kwargs: Additional context parameters (debug_api, session, etc.)

        Returns:
            bool: True if token is valid, False otherwise
        """
        self.token_name = token_name or self.token_name

        if not self.token:
            await self.get_auth_token(**context_kwargs)

        if not self.is_valid_token:
            await self.who_am_i(**context_kwargs)

        if not self.is_valid_token:
            print(
                f"🚧 failed to retrieve {self.token_name} token from {self.domo_instance}"
            )
            return False

        try:
            # Try to print with emoji (works on modern terminals)
            print(f"🎉 {self.token_name} token retrieved from {self.domo_instance} ⚙️")
        except UnicodeEncodeError:
            # Fallback for Windows console without emoji support
            print(
                f"[SUCCESS] {self.token_name} token retrieved from {self.domo_instance}"
            )
        return True

    # Cache Management Methods (Phase 3)

    def clear_cache(self):
        """Clear all HTTP caches for this auth instance.

        This clears both request-level and collection-level caches.
        Useful when you want to ensure fresh data from the API.
        """
        if hasattr(self, "_cached_session") and self._cached_session:
            transport = getattr(self._cached_session, "_transport", None)
            if transport and hasattr(transport, "clear_cache"):
                transport.clear_cache()

    def cache_stats(self) -> dict:
        """Get HTTP cache statistics.

        Returns:
            dict: Cache statistics including:
                - request_cache: {total_entries, hits, misses, hit_rate}
                - collection_cache: {total_entries, hits, misses, hit_rate}
        """
        if hasattr(self, "_cached_session") and self._cached_session:
            transport = getattr(self._cached_session, "_transport", None)
            if transport and hasattr(transport, "get_stats"):
                return transport.get_stats()

        # Default empty stats
        return {
            "request_cache": {
                "total_entries": 0,
                "hits": 0,
                "misses": 0,
                "hit_rate": 0.0,
            },
            "collection_cache": {
                "total_entries": 0,
                "hits": 0,
                "misses": 0,
                "hit_rate": 0.0,
            },
        }

    async def invalidate_cache(self, url_pattern: str):
        """Manually invalidate cache entries matching URL pattern.

        Args:
            url_pattern: URL pattern to invalidate (e.g., '/api/content/v2/users/123')
                        Supports wildcards depending on invalidation strategy.
        """
        if hasattr(self, "_cached_session") and self._cached_session:
            transport = getattr(self._cached_session, "_transport", None)
            if transport and hasattr(transport, "_invalidate_by_url"):
                await transport._invalidate_by_url(url_pattern)

    def set_cache_strategy(self, strategy):
        """Change cache invalidation strategy.

        Args:
            strategy: New invalidation strategy (from InvalidationStrategy enum)
        """
        if hasattr(self, "_cached_session") and self._cached_session:
            transport = getattr(self._cached_session, "_transport", None)
            if transport and hasattr(transport, "invalidator"):
                transport.invalidator.strategy = strategy


@dataclass
class DomoAuth(_DomoAuth_Optional, _DomoAuth_Required):
    """Concrete combined DomoAuth base class.

    This is a concrete implementation that combines the required and optional
    authentication functionality. It serves as a base class for specific
    authentication types.
    """
