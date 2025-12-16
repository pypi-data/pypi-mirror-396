"""Jupyter authentication classes for Domo."""

from dataclasses import dataclass, field

from .base import _DomoAuth_Optional, _DomoAuth_Required
from .full import DomoFullAuth, _DomoFullAuth_Required
from .token import DomoTokenAuth, _DomoTokenAuth_Required


class _DomoJupyter_Required:  # noqa: N801
    """Required parameters and setup for Domo Jupyter authentication.

    This class provides the foundational authentication components needed for
    Domo Jupyter environments, including token validation and environment setup.

    Attributes:
        jupyter_token (str): Authorization token from Domo Jupyter network traffic
        service_location (str): Service location from Domo Jupyter environment
        service_prefix (str): Service prefix from Domo Jupyter environment
    """

    def __init__(
        self,
        jupyter_token: str | None = None,
        service_location: str | None = None,
        service_prefix: str | None = None,
    ):
        """Initialize Jupyter authentication parameters.

        If parameters are not provided, the user will be prompted to enter them
        interactively. These values are typically obtained by monitoring Domo
        Jupyter network traffic.

        Args:
            jupyter_token (str | None): Authorization token from network traffic
            service_location (str | None): Service location from environment
            service_prefix (str | None): Service prefix from environment

        Raises:
            ValueError: If any required parameters are missing after initialization
        """

        self.jupyter_token = jupyter_token or input(
            "jupyter token: # retrieve this by monitoring Domo Jupyter network traffic. It is the Authorization header\n> "
        )
        self.service_location = service_location or input(
            "service_location: # retrieve from Domo Jupyter environment\n> "
        )
        self.service_prefix = service_prefix or input(
            "service_prefix: # retrieve from Domo Jupyter environment\n> "
        )

        self._test_prereq()

    def get_jupyter_token_flow(self):
        """Stub method for initiating a Jupyter token retrieval flow.

        This method is a placeholder for future implementation of automated
        Jupyter token retrieval.
        """
        print("hello world, I am a jupyter_token")

    def _test_prereq(self):
        """Validate that required attributes are present.

        Raises:
            ValueError: If any required Jupyter parameters are missing
        """
        missing = []
        if not self.jupyter_token:
            missing.append("jupyter_token")
        if not self.service_location:
            missing.append("service_location")
        if not self.service_prefix:
            missing.append("service_prefix")

        if missing:
            raise ValueError(f"DomoJupyterAuth objects must have: {', '.join(missing)}")


@dataclass
class DomoJupyterAuth(_DomoAuth_Optional, _DomoJupyter_Required, _DomoAuth_Required):
    """Base class for Domo Jupyter authentication.

    This class combines the core authentication functionality with Jupyter-specific
    requirements. It serves as a foundation for specific Jupyter authentication types.
    """


@dataclass
class DomoJupyterFullAuth(
    _DomoJupyter_Required,
    _DomoFullAuth_Required,
):
    """Jupyter authentication using full credentials (username/password).

    This class combines full Domo authentication with Jupyter environment support.
    It's used when working within Domo Jupyter environments and requires both
    standard Domo credentials and Jupyter-specific authentication tokens.

    Attributes:
        jupyter_token (str): Authorization token from Domo Jupyter (not shown in repr)
        service_location (str): Service location from Jupyter environment
        service_prefix (str): Service prefix from Jupyter environment
        domo_instance (str): The Domo instance identifier
        domo_username (str): Domo username for authentication
        domo_password (str): Domo password for authentication (not shown in repr)
        token_name (str | None): Name identifier for the token
        token (str | None): The authentication token (not shown in repr)
        user_id (str | None): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid

    Example:
        >>> auth = DomoJupyterFullAuth(
        ...     jupyter_token="jupyter-auth-token",
        ...     service_location="service-location",
        ...     service_prefix="service-prefix",
        ...     domo_instance="mycompany",
        ...     domo_username="user@company.com",
        ...     domo_password="secure_password"
        ... )
    """

    jupyter_token: str = field(repr=False)
    service_location: str
    service_prefix: str

    domo_instance: str
    domo_username: str
    domo_password: str = field(repr=False)

    token_name: str | None = None
    token: str | None = field(default=None, repr=False)
    user_id: str | None = None
    is_valid_token: bool = False

    def __post_init__(self):
        """Initialize the Jupyter and full authentication mixins."""
        _DomoJupyter_Required.__init__(
            self,
            jupyter_token=self.jupyter_token,
            service_location=self.service_location,
            service_prefix=self.service_prefix,
        )
        _DomoFullAuth_Required.__init__(
            self,
            domo_username=self.domo_username,
            domo_password=self.domo_password,
            domo_instance=self.domo_instance,
            token_name=self.token_name,
            token=self.token,
            user_id=self.user_id,
            is_valid_token=self.is_valid_token,
        )

    @property
    def auth_header(self) -> dict:
        """Generate authentication headers combining Domo and Jupyter tokens.

        Returns:
            dict: Combined authentication headers for both Domo and Jupyter APIs
        """
        return {
            **super().auth_header,
            "authorization": f"Token {self.jupyter_token}",
        }

    @classmethod
    def convert_auth(
        cls, auth: DomoFullAuth, jupyter_token, service_location, service_prefix
    ):
        """Convert DomoFullAuth to DomoJupyterFullAuth.

        This factory method creates a Jupyter-enabled authentication object from
        an existing full authentication object by adding the necessary Jupyter
        environment parameters.

        Args:
            auth (DomoFullAuth): Existing full authentication object
            jupyter_token (str): Authorization token from Domo Jupyter
            service_location (str): Service location from Jupyter environment
            service_prefix (str): Service prefix from Jupyter environment

        Returns:
            DomoJupyterFullAuth: New Jupyter-enabled authentication object
        """
        return cls(
            domo_instance=auth.domo_instance,
            domo_username=auth.domo_username,
            domo_password=auth.domo_password,
            jupyter_token=jupyter_token,
            service_location=service_location,
            service_prefix=service_prefix,
            token_name=auth.token_name,
            token=auth.token,
            user_id=auth.user_id,
            is_valid_token=auth.is_valid_token,
        )


@dataclass
class DomoJupyterTokenAuth(
    _DomoJupyter_Required,
    _DomoTokenAuth_Required,
):
    """Jupyter authentication using access tokens.

    This class combines token-based Domo authentication with Jupyter environment support.
    It's used when working within Domo Jupyter environments with pre-generated access
    tokens instead of username/password credentials.

    Attributes:
        jupyter_token (str): Authorization token from Domo Jupyter (not shown in repr)
        service_location (str): Service location from Jupyter environment
        service_prefix (str): Service prefix from Jupyter environment
        domo_instance (str): The Domo instance identifier
        domo_access_token (str): Pre-generated access token (not shown in repr)
        token_name (str | None): Name identifier for the token
        token (str | None): The authentication token (not shown in repr)
        user_id (str | None): The authenticated user's ID
        is_valid_token (bool): Whether the current token is valid

    Example:
        >>> auth = DomoJupyterTokenAuth(
        ...     jupyter_token="jupyter-auth-token",
        ...     service_location="service-location",
        ...     service_prefix="service-prefix",
        ...     domo_instance="mycompany",
        ...     domo_access_token="your-access-token"
        ... )
    """

    jupyter_token: str = field(repr=False)
    service_location: str
    service_prefix: str

    domo_instance: str

    domo_access_token: str = field(repr=False)

    token_name: str | None = None
    token: str | None = field(default=None, repr=False)
    user_id: str | None = None
    is_valid_token: bool = False

    def __post_init__(self):
        """Initialize the Jupyter and token authentication mixins."""
        _DomoJupyter_Required.__init__(
            self,
            jupyter_token=self.jupyter_token,
            service_location=self.service_location,
            service_prefix=self.service_prefix,
        )
        _DomoTokenAuth_Required.__init__(
            self,
            domo_access_token=self.domo_access_token,
            domo_instance=self.domo_instance,
            token_name=self.token_name,
            token=self.token,
            user_id=self.user_id,
            is_valid_token=self.is_valid_token,
        )

    @property
    def auth_header(self) -> dict:
        """Generate authentication headers combining Domo and Jupyter tokens.

        Returns:
            dict: Combined authentication headers for both Domo and Jupyter APIs
        """
        return {
            **super().auth_header,
            "authorization": f"Token {self.jupyter_token}",
        }

    @classmethod
    def convert_auth(
        cls, auth: DomoTokenAuth, jupyter_token, service_location, service_prefix
    ):
        """Convert DomoTokenAuth to DomoJupyterTokenAuth.

        This factory method creates a Jupyter-enabled authentication object from
        an existing token authentication object by adding the necessary Jupyter
        environment parameters.

        Args:
            auth (DomoTokenAuth): Existing token authentication object
            jupyter_token (str): Authorization token from Domo Jupyter
            service_location (str): Service location from Jupyter environment
            service_prefix (str): Service prefix from Jupyter environment

        Returns:
            DomoJupyterTokenAuth: New Jupyter-enabled authentication object
        """
        return cls(
            domo_instance=auth.domo_instance,
            domo_access_token=auth.domo_access_token,
            jupyter_token=jupyter_token,
            service_location=service_location,
            service_prefix=service_prefix,
            token_name=auth.token_name,
            token=auth.token,
            user_id=auth.user_id,
            is_valid_token=auth.is_valid_token,
        )
