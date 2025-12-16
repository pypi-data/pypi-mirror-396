"""Account module providing Domo account management functionality.

This module contains classes for managing Domo accounts, credentials, configurations,
and OAuth settings.

Classes:
    DomoAccount: Main account class
    DomoAccount_Default: Base account functionality
    DomoAccount_Credential: Account credential management
    DomoAccount_OAuth: OAuth account configurations
    AccountConfig: Account configuration classes
    DomoAccounts: Collection class for managing multiple accounts

Example:
    Basic account usage:

        >>> from domolibrary2.classes.Account import DomoAccount
        >>> account = DomoAccount.from_dict(account_data)

    Working with account collections:

        >>> from domolibrary2.classes.Account import DomoAccounts
        >>> accounts = await DomoAccounts(auth=auth).get()
"""

__all__ = [
    "DomoAccount",
    "DomoAccount_Default",
    "DomoAccountCredential",
    "DomoAccount_OAuth",
    "AccountConfig",
    "DomoAccount_Config",
    "DomoAccounts",
    "DomoAccounts_NoAccount",
    "ShareAccount_AccessLevel",
    "AccountConfig_ProviderTypeNotDefinedError",
    "AccountConfig_UsesOauthError",
    "DomoAccount_NoConfig_OAuthError",
]

# Import route enums used by account classes
from ...routes.account import ShareAccount_AccessLevel
from .account_credential import DomoAccountCredential
from .account_default import DomoAccount_Default
from .account_oauth import DomoAccount_OAuth
from .config import (
    AccountConfig,
    AccountConfig_ProviderTypeNotDefinedError,
    AccountConfig_UsesOauthError,
    DomoAccount_Config,
    DomoAccount_NoConfig_OAuthError,
)

# Import main classes
from .core import DomoAccount, DomoAccounts, DomoAccounts_NoAccount
