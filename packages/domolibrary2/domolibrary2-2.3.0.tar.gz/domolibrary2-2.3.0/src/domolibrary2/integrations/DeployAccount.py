from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, fields
from typing import Any

from dc_logger.client.base import get_global_logger

from ..auth import DomoAuth
from ..classes.DomoAccount import DomoAccount, DomoAccounts
from ..classes.DomoAccount.config import AccountConfig, DomoAccount_Config
from ..client.context import RouteContext
from ..utils.logging import log_call

__all__ = ["DeployAccount"]


ConfigTypeSpecifier = AccountConfig | type[DomoAccount_Config] | str

logger = get_global_logger()


@dataclass
class DeployAccount:
    """Deploy multiple `DomoAccount` objects that share a credential bundle.

    Attributes:
        auth: Auth used to create / upsert the accounts.
        creds: Shared credential dictionary.  Keys should match the
            dataclass field names on the target `DomoAccount_Config`
            subclasses (e.g. ``account``, ``username``, ``private_key``,
            ``access_key``).
        config_types: Collection of config type specifiers.  Each entry may
            be:

              - an `AccountConfig` enum member
              - a concrete `DomoAccount_Config` subclass
              - a data_provider_type string (e.g. ``"snowflake-key-pair-unload-v2"``)

        account_name: Base account name to use.  A short provider suffix
            is appended to make each account name unique per config type.
        description: Optional human friendly description of the bundle.
            Not sent to the Domo APIs; intended for logging / debugging.
        is_available_as_unencrypted: Controls the `allow_external_use`
            flag on each generated config.  When ``False`` we still build
            configs normally, but mark them as not available for external
            unencrypted use.
    """

    auth: DomoAuth
    creds: dict[str, Any]
    config_types: Sequence[ConfigTypeSpecifier]

    account_name: str
    description: str | None = None
    is_available_as_unencrypted: bool = True
    context: RouteContext | None = None

    @log_call(level_name="integration", color="cyan", log_level="info")
    async def deploy(
        self,
        *,
        debug_api: bool = False,
        debug_prn: bool = False,
        dry_run: bool = False,
    ) -> list[DomoAccount]:
        """Create or update one `DomoAccount` per config type.

        Returns:
            List of created / upserted `DomoAccount` instances in the same
            order as `config_types`.
        """

        # Build effective route context (merge existing context + overrides)
        ctx = RouteContext.build_context(
            self.context,
            debug_api=debug_api,
            dry_run=dry_run,
        )
        # If either flag says dry_run, treat it as a dry run
        dry_run = dry_run or ctx.dry_run

        accounts: list[DomoAccount] = []

        await logger.info(
            "Starting DeployAccount deployment",
            method="COMMENT",
            account_name=self.account_name,
            description=self.description,
            is_available_as_unencrypted=self.is_available_as_unencrypted,
            num_config_types=len(self.config_types),
            dry_run=dry_run,
            context_has_session=ctx.session is not None,
            context_debug_api=ctx.debug_api,
        )

        for spec in self.config_types:
            config_cls, provider_type = self._resolve_config_class(spec)
            config = self._build_config(config_cls)

            # Mirror the per-config allow_external_use flag against the
            # DeployAccount's high‑level `is_available_as_unencrypted` flag.
            config.allow_external_use = self.is_available_as_unencrypted

            account_display_name = self._build_account_name(
                self.account_name, provider_type
            )

            if dry_run:
                await logger.info(
                    "[DRY RUN] Would deploy DomoAccount",
                    method="COMMENT",
                    account_name=account_display_name,
                    provider_type=provider_type,
                    config_class=config_cls.__name__,
                    creds_keys=sorted(self.creds.keys()),
                    session_has=ctx.session is not None,
                    context_debug_api=ctx.debug_api,
                )
                continue

            acc = await DomoAccounts.upsert_account(
                auth=self.auth,
                account_name=account_display_name,
                account_config=config,
                data_provider_type=provider_type,
                debug_api=ctx.debug_api,
                debug_prn=debug_prn,
                session=ctx.session,
            )

            accounts.append(acc)

            await logger.info(
                "Deployed DomoAccount",
                method="COMMENT",
                account_id=getattr(acc, "id", None),
                account_name=account_display_name,
                provider_type=provider_type,
            )

        return accounts

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #

    @staticmethod
    def _build_account_name(base_name: str, _provider_type: str) -> str:
        """Return the base account name without modification.

        Callers that need per-provider suffixes can incorporate them into
        `base_name` before invoking this helper.  Keeping the name stable
        here avoids surprising changes for simple single-config deploys.
        """
        return base_name

    @staticmethod
    def _resolve_config_class(
        spec: ConfigTypeSpecifier,
    ) -> tuple[type[DomoAccount_Config], str]:
        """Normalize a config type specifier into (config_cls, provider_type)."""

        # Enum member – use its value (the config class)
        if isinstance(spec, AccountConfig):
            config_cls: type[DomoAccount_Config] = spec.value
            provider_type = config_cls.data_provider_type  # type: ignore[attr-defined]
            return config_cls, provider_type

        # Direct config subclass
        if isinstance(spec, type) and issubclass(spec, DomoAccount_Config):
            config_cls = spec
            provider_type = getattr(config_cls, "data_provider_type", None)
            if not provider_type:
                raise ValueError(
                    f"{config_cls.__name__} is missing a 'data_provider_type' attribute"
                )
            return config_cls, provider_type

        # String – interpret as data_provider_type and resolve via AccountConfig
        if isinstance(spec, str):
            enum_member = AccountConfig(spec)
            if enum_member is None or enum_member.value is None:
                raise ValueError(
                    f"Unknown or unsupported account config provider_type: {spec!r}"
                )

            config_cls = enum_member.value
            provider_type = getattr(config_cls, "data_provider_type", spec)
            return config_cls, provider_type

        raise TypeError(
            "Unsupported config type specifier. Expected AccountConfig, "
            "DomoAccount_Config subclass, or provider_type string."
        )

    def _build_config(self, config_cls: type[DomoAccount_Config]) -> DomoAccount_Config:
        """Instantiate a config class using the shared `creds` bundle.

        Only fields that both:

          - are part of the dataclass' init fields, and
          - are present in `self.creds`

        are forwarded into the constructor.  Any additional validation of
        required fields is delegated to the config class' own
        ``__post_init__`` implementation.
        """

        init_kwargs: dict[str, Any] = {}

        for f in fields(config_cls):
            if not f.init:
                continue

            # Skip base/meta properties that are handled internally
            if f.name in {
                "data_provider_type",
                "is_oauth",
                "parent",
                "raw",
                "_field_map",
                "_fields_for_serialization",
                "allow_external_use",
            }:
                continue

            if f.name in self.creds:
                init_kwargs[f.name] = self.creds[f.name]

        return config_cls(**init_kwargs)  # type: ignore[arg-type]
