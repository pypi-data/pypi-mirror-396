from __future__ import annotations

__all__ = [
    "DomoAccount_Config",
    "AccountConfig_UsesOauthError",
    "DomoAccount_NoConfig_OAuthError",
    "AccountConfig_ProviderTypeNotDefinedError",
    "AccountConfig_SerializationMismatchError",
    "DomoAccount_NoConfig",
    "DomoAccount_Config_AbstractCredential",
    "DomoAccount_Config_DatasetCopy",
    "DomoAccount_Config_DomoAccessToken",
    "DomoAccount_Config_Governance",
    "DomoAccount_Config_AmazonS3",
    "DomoAccount_Config_AmazonS3Advanced",
    "DomoAccount_Config_DomoToS3",
    "DomoAccount_Config_AwsAthena",
    "DomoAccount_Config_HighBandwidthConnector",
    "DomoAccount_Config_Snowflake",
    "DomoAccount_Config_SnowflakeUnload_V2",
    "DomoAccount_Config_SnowflakeUnloadAdvancedPartition",
    "DomoAccount_Config_SnowflakeWriteback",
    "DomoAccount_Config_SnowflakeUnload",
    "DomoAccount_Config_SnowflakeFederated",
    "DomoAccount_Config_SnowflakeInternalUnload",
    "DomoAccount_Config_SnowflakeKeyPairAuthentication",
    "DomoAccount_Config_SnowflakeKeyPairWriteback",
    "DomoAccount_Config_SnowflakeKeyPairUnload_V2",
    "DomoAccount_Config_SnowflakeKeyPairInternalManagedUnload",
    "AccountConfig",
    "register_account_config",
]

from dataclasses import dataclass
from enum import Enum

from ...base.base import DomoEnumMixin
from ...base.exceptions import ClassError

# Import base config class and exceptions - must be before registry setup
from .account_configs._base import (  # noqa: E402
    AccountConfig_SerializationMismatchError,
    DomoAccount_Config,
)

# ============================================================================
# Exceptions
# ============================================================================


class AccountConfig_UsesOauthError(ClassError):
    def __init__(self, cls_instance, data_provider_type):
        super().__init__(
            cls_instance=cls_instance,
            message=f"data provider type {data_provider_type} uses OAuth and therefore wouldn't return a Config object",
        )


class AccountConfig_ProviderTypeNotDefinedError(ClassError):
    def __init__(self, cls_instance, data_provider_type):
        super().__init__(
            cls_instance=cls_instance,
            message=f"data provider type {data_provider_type} not defined yet. Extend the AccountConfig class",
        )


# ============================================================================
# Registry and Decorator
# ============================================================================

# Registry to store account config classes
_ACCOUNT_CONFIG_REGISTRY: dict[str, type[DomoAccount_Config]] = {}

# OAuth providers that don't have config classes
_OAUTH_PROVIDERS = {"google-spreadsheets"}


def register_account_config(data_provider_type: str):
    """Decorator to register a DomoAccount_Config subclass.

    Args:
        data_provider_type: The data provider type identifier (e.g., 'snowflake')

    Example:
        @register_account_config('snowflake')
        @dataclass
        class DomoAccount_Config_Snowflake(DomoAccount_Config):
            account: str = None
            username: str = None
            password: str = field(repr=False, default=None)
            role: str = None
    """

    def decorator(cls: type[DomoAccount_Config]) -> type[DomoAccount_Config]:
        _ACCOUNT_CONFIG_REGISTRY[data_provider_type] = cls
        return cls

    return decorator


# ============================================================================
# Base Classes
# ============================================================================


@dataclass
class DomoAccount_NoConfig_OAuthError(DomoAccount_Config):
    is_oauth: bool = True

    def __super_init__(self):
        raise AccountConfig_UsesOauthError(
            cls_instance=self, data_provider_type=self.data_provider_type
        )


@dataclass
class DomoAccount_NoConfig(DomoAccount_Config):
    is_oauth: bool = False

    def __super_init__(self):
        raise AccountConfig_ProviderTypeNotDefinedError(
            cls_instance=self, data_provider_type=self.data_provider_type
        )


# ============================================================================
# Import platform-specific configurations to trigger registration
# ============================================================================

# Import all mappings from the account_configs subfolder
# This triggers the @register_account_config decorators and populates _ACCOUNT_CONFIG_REGISTRY
import domolibrary2.classes.DomoAccount.account_configs  # noqa: E402, F401

# Re-export all config classes for backwards compatibility
from .account_configs.aws import (  # noqa: E402
    DomoAccount_Config_AmazonS3,
    DomoAccount_Config_AmazonS3Advanced,
    DomoAccount_Config_AwsAthena,
    DomoAccount_Config_DomoToS3,
    DomoAccount_Config_HighBandwidthConnector,
)
from .account_configs.domo import (  # noqa: E402
    DomoAccount_Config_AbstractCredential,
    DomoAccount_Config_DatasetCopy,
    DomoAccount_Config_DomoAccessToken,
    DomoAccount_Config_Governance,
)
from .account_configs.snowflake import (  # noqa: E402
    DomoAccount_Config_Snowflake,
    DomoAccount_Config_SnowflakeFederated,
    DomoAccount_Config_SnowflakeInternalUnload,
    DomoAccount_Config_SnowflakeKeyPairAuthentication,
    DomoAccount_Config_SnowflakeKeyPairInternalManagedUnload,
    DomoAccount_Config_SnowflakeKeyPairUnload_V2,
    DomoAccount_Config_SnowflakeKeyPairWriteback,
    DomoAccount_Config_SnowflakeUnload,
    DomoAccount_Config_SnowflakeUnload_V2,
    DomoAccount_Config_SnowflakeUnloadAdvancedPartition,
    DomoAccount_Config_SnowflakeWriteback,
)

# ============================================================================
# AccountConfig Enum (Auto-generated from registry)
# ============================================================================


class AccountConfig(DomoEnumMixin, Enum):
    """Enum of all registered account config classes.

    This enum is automatically populated from the registry created by
    @register_account_config decorators. To add a new config, simply create a
    new subclass with the @register_account_config decorator in the
    account_configs subfolder.

    The enum provides:
    - Static access to config classes via enum members
    - Dynamic lookup of config classes by data_provider_type
    - OAuth provider detection
    - Normalization of provider type strings (hyphens/underscores)
    """

    # Explicit default member to prevent AttributeError
    default = None  # Will be set dynamically via _missing_

    @staticmethod
    def normalize_provider_type(provider_type: str) -> str:
        """Normalize provider type to standard format (lowercase with hyphens)."""
        return provider_type.lower().replace("_", "-")

    @classmethod
    def _missing_(cls, value):
        """Handle missing enum values by searching the registry."""
        normalized = cls.normalize_provider_type(value)

        # Try direct registry lookup
        if normalized in _ACCOUNT_CONFIG_REGISTRY:
            config_class = _ACCOUNT_CONFIG_REGISTRY[normalized]
            return cls._create_pseudo_member(normalized, config_class)

        # Check if it's an OAuth provider
        if normalized in _OAUTH_PROVIDERS:
            print(AccountConfig_UsesOauthError(cls, value))
            return None

        # Unknown provider type
        print(AccountConfig_ProviderTypeNotDefinedError(cls, value))
        return None
