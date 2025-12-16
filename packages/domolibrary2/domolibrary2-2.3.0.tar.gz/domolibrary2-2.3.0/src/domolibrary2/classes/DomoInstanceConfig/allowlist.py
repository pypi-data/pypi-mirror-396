__all__ = [
    "validate_ip_or_cidr",
    "DomoAllowlist",
]

import ipaddress
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...client.context import RouteContext
from ...routes.instance_config import allowlist as allowlist_routes


def validate_ip_or_cidr(ip: str):
    try:
        # Try IPv4 address
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        try:
            # Try IPv4 network (CIDR)
            ipaddress.IPv4Network(ip, strict=False)
            return True
        except ValueError as e:
            raise ValueError(f"Invalid IP/CIDR entry: {ip}") from e


@dataclass
class DomoAllowlist:
    """A class for managing the Domo instance IP allowlist configuration.

    This class provides methods to get, set, add, and remove IP addresses/CIDR ranges
    from the instance allowlist, as well as manage the filter all traffic setting.

    Note: Unlike most Domo entities, the allowlist is a singleton configuration per instance
    and does not have an 'id' field.
    """

    auth: DomoAuth = field(repr=False)
    allowlist: list[str] = field(default_factory=list)
    is_filter_all_traffic_enabled: bool | None = None
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def display_url(self) -> str:
        """Return the URL to the allowlist configuration page in Domo."""
        return f"https://{self.auth.domo_instance}.domo.com/admin/security/settings"

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]) -> "DomoAllowlist":
        """Create a DomoAllowlist instance from a dictionary representation.

        Args:
            auth: Authentication object for API requests
            obj: Dictionary containing allowlist data

        Returns:
            DomoAllowlist instance
        """
        return cls(
            auth=auth,
            allowlist=obj.get("allowlist") or obj.get("addresses", []),
            is_filter_all_traffic_enabled=obj.get("is_filter_all_traffic_enabled"),
            raw=obj,
        )

    async def get(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:
        """
        retrieves the allowlist for an instance
        """
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await allowlist_routes.get_allowlist(
            auth=self.auth,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        self.allowlist = [str(s) for s in res.response]

        return self.allowlist

    async def set(
        self,
        ip_address_ls: list[str],
        is_suppress_errors: bool = False,
        debug_api: bool = False,
        debug_prn: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        for ip in ip_address_ls:
            try:
                validate_ip_or_cidr(ip)
            except ValueError as ve:
                if not is_suppress_errors:
                    raise ve

                print(f"skipping invalid entry: {ip}")
                ip_address_ls.remove(ip)
                continue

        # get current allowlist
        await self.get(context=context)

        if sorted(ip_address_ls) == sorted(self.allowlist):
            if debug_prn:
                print("no changes to allowlist detected, skipping update")
            return self.allowlist

        await allowlist_routes.set_allowlist(
            ip_address_ls=ip_address_ls,
            auth=self.auth,
            context=context,
        )

        return await self.get(
            context=context,
        )

    async def add_ips(
        self,
        ip_address_ls: str,
        is_suppress_errors: bool = False,
        debug_api: bool = False,
        debug_prn: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:
        """
        adds an IP or CIDR to the allowlist
        """
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        new_allowlist = await self.get(context=context)

        for ip in ip_address_ls:
            if ip in new_allowlist:
                continue

            new_allowlist.append(ip)

        return await self.set(
            ip_address_ls=new_allowlist,
            context=context,
            is_suppress_errors=is_suppress_errors,
            debug_prn=debug_prn,
        )

    async def remove_ips(
        self,
        ip_address_ls: str,
        debug_prn: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        is_suppress_errors: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:
        """
        removes an IP or CIDR to the allowlist
        """
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        allowlist = await self.get(context=context)

        for ip in ip_address_ls:
            if ip not in allowlist:
                continue

            allowlist.remove(ip)

        return await self.set(
            ip_address_ls=allowlist,
            context=context,
            is_suppress_errors=is_suppress_errors,
            debug_prn=debug_prn,
        )

    async def get_is_filter_all_traffic_enabled(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> bool:
        """
        retrieves whether the "filter all traffic" setting is enabled
        """
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await allowlist_routes.get_allowlist_is_filter_all_traffic_enabled(
            auth=self.auth,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        self.is_filter_all_traffic_enabled = bool(res.response["is_enabled"])

        return self.is_filter_all_traffic_enabled

    async def toggle_is_filter_all_traffic_enabled(
        self,
        is_enabled: bool,
        debug_api: bool = False,
        debug_prn: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> bool:
        """
        retrieves whether the "filter all traffic" setting is enabled
        """
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        await self.get_is_filter_all_traffic_enabled(context=context)

        if self.is_filter_all_traffic_enabled == is_enabled:
            if debug_prn:
                print("no action required")

            return bool(self.is_filter_all_traffic_enabled)

        res = await allowlist_routes.toggle_allowlist_is_filter_all_traffic_enabled(
            auth=self.auth,
            is_enabled=is_enabled,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        self.is_filter_all_traffic_enabled = res.response["is_enabled"]

        return bool(self.is_filter_all_traffic_enabled)

        return bool(self.is_filter_all_traffic_enabled)
