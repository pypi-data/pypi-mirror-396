from dataclasses import dataclass, field
from typing import Any

import httpx
import pandas as pd

from domolibrary2.base.base import DomoBase

from ...auth import DomoAuth
from ...client.context import RouteContext
from ...routes import (
    application as application_routes,
)
from ...routes.instance_config import (
    authorized_domains as domains_routes,
)
from .access_token import DomoAccessTokens
from .allowlist import DomoAllowlist
from .api_client import ApiClients
from .bootstrap import DomoBootstrap
from .instance_switcher import InstanceSwitcher
from .mfa import MFA_Config
from .role import DomoRoles
from .role_grant import DomoGrants
from .sso import SSO as SSO_Class
from .toggle import DomoToggle
from .user_attributes import UserAttributes

__all__ = ["DomoInstanceConfig"]


@dataclass
class DomoInstanceConfig(DomoBase):
    """utility class that absorbs many of the domo instance configuration methods"""

    auth: DomoAuth = field(repr=False)

    Accounts: Any = field(default=None)
    AccessTokens: DomoAccessTokens = field(default=None)
    Allowlist: DomoAllowlist = field(default=None)
    ApiClients: "ApiClients" = field(default=None)
    Bootstrap: DomoBootstrap = field(default=None)

    Connectors: Any = field(default=None)  # DomoConnectors
    InstanceSwitcher: "InstanceSwitcher" = field(default=None)

    Grants: DomoGrants = field(default=None)

    MFA: MFA_Config = field(default=None)
    Roles: DomoRoles = field(default=None)

    SSO: SSO_Class = field(default=None)
    Everywhere: Any = field(
        default=None
    )  # DomoEverywhere - imported lazily to avoid circular import
    UserAttributes: "UserAttributes" = field(default=None)
    Toggle: DomoToggle = field(default=None)

    def __post_init__(self):
        from ..DomoAccount import DomoAccounts
        from ..DomoDataset import DomoConnectors
        from ..DomoEverywhere import DomoEverywhere

        self.Accounts = DomoAccounts(auth=self.auth)
        self.AccessTokens = DomoAccessTokens(auth=self.auth)
        self.ApiClients = ApiClients(auth=self.auth)
        self.Allowlist = DomoAllowlist(auth=self.auth)
        self.Bootstrap = DomoBootstrap(auth=self.auth)

        self.Connectors = DomoConnectors(auth=self.auth)
        self.Grants = DomoGrants(auth=self.auth)
        self.InstanceSwitcher = InstanceSwitcher(auth=self.auth)
        self.MFA = MFA_Config(auth=self.auth)
        self.Everywhere = DomoEverywhere(auth=self.auth)
        self.UserAttributes = UserAttributes(auth=self.auth)
        self.Roles = DomoRoles(auth=self.auth)
        self.SSO = SSO_Class(auth=self.auth)
        self.Toggle = DomoToggle(auth=self.auth)

    async def get_applications(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        from ..DomoApplication.Application import DomoApplication

        res = await application_routes.get_applications(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        return [
            DomoApplication.from_dict(auth=self.auth, obj=job) for job in res.response
        ]

    async def generate_applications_report(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )

        context = RouteContext.build_context(context=context or base_context)

        domo_apps = await self.get_applications(
            context=context,
            return_raw=return_raw,
        )

        if return_raw:
            return domo_apps

        df = pd.DataFrame([app.__dict__ for app in domo_apps])
        df["domo_instance"] = self.auth.domo_instance

        df.drop(columns=["auth"], inplace=True)
        df.rename(
            columns={
                "id": "application_id",
                "name": "application_name",
                "description": "application_description",
                "version": "application_version",
            },
            inplace=True,
        )

        return df.sort_index(axis=1)

    async def get_authorized_domains(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        debug_num_stacks_to_drop: int = 1,
        **context_kwargs,
    ) -> list[str]:
        """returns a list of authorized domains (str) does not update instance_config"""
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )

        context = RouteContext.build_context(context=context or base_context)

        res = await domains_routes.get_authorized_domains(
            auth=self.auth, return_raw=return_raw, context=context
        )

        if return_raw:
            return res

        return res.response

    async def set_authorized_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        debug_num_stacks_to_drop=1,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )

        context = RouteContext.build_context(context=context or base_context)

        res = await domains_routes.set_authorized_domains(
            auth=self.auth,
            authorized_domain_ls=authorized_domains,
            context=context,
        )

        return res

    async def upsert_authorized_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )

        context = RouteContext.build_context(context=context or base_context)

        existing_domains = await self.get_authorized_domains(
            context=context,
        )

        authorized_domains += existing_domains

        return await self.set_authorized_domains(
            authorized_domains=authorized_domains,
            context=context,
        )

    async def get_authorized_custom_app_domains(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop=2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )

        context = RouteContext.build_context(context=context or base_context)

        res = await domains_routes.get_authorized_custom_app_domains(
            auth=self.auth,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        return res.response

        # | exporti

    async def set_authorized_custom_app_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )

        context = RouteContext.build_context(context=context or base_context)

        res = await domains_routes.set_authorized_custom_app_domains(
            auth=self.auth,
            authorized_custom_app_domain_ls=authorized_domains,
            context=context,
        )

        return res

    async def upsert_authorized_custom_app_domains(
        self,
        authorized_domains: list[str],
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )

        context = RouteContext.build_context(context=context or base_context)

        existing_domains = await self.get_authorized_custom_app_domains(
            context=context,
        )

        authorized_domains += existing_domains

        return await self.set_authorized_custom_app_domains(
            authorized_domains=authorized_domains,
            context=context,
        )
