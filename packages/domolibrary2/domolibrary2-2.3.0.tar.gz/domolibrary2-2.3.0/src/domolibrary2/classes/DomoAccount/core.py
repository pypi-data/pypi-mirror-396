__all__ = ["DomoAccount", "DomoAccounts_NoAccount", "DomoAccounts"]


from dataclasses import dataclass
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import exceptions as dmde
from ...base.entities import DomoManager
from ...client.context import RouteContext
from ...routes import (
    account as account_routes,
    datacenter as datacenter_routes,
)
from ...routes.datacenter.exceptions import SearchDatacenterNoResultsFoundError
from ...utils import chunk_execution as dmce
from .account_credential import DomoAccountCredential
from .account_default import (
    DomoAccount_Default,
    UpsertAccount_MatchCriteriaError,
)
from .account_oauth import DomoAccount_OAuth
from .config import AccountConfig


class DomoAccounts_NoAccount(dmde.ClassError):
    def __init__(self, cls=None, cls_instance=None, message=None, domo_instance=None):
        super().__init__(
            cls=cls, cls_instance=cls_instance, message=message, entity_id=domo_instance
        )


@dataclass
class DomoAccount(DomoAccount_Default):
    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict[str, Any],
        is_admin_summary: bool = True,
        is_use_default_class: bool = False,
        new_cls: Any = None,  # Keep for compatibility with parent signature
        **kwargs,
    ):
        """converts data_v1_accounts API response into an accounts class object"""

        # If new_cls is explicitly provided, use it; otherwise determine from is_use_default_class
        if new_cls is None:
            if is_use_default_class:
                new_cls = cls
            elif obj.get("credentialsType") == "oauth":
                new_cls = DomoAccount_OAuth
            else:
                new_cls = DomoAccountCredential

        return super().from_dict(
            auth=auth,
            obj=obj,
            is_admin_summary=is_admin_summary,
            new_cls=new_cls,
            **kwargs,
        )


@dataclass
class DomoAccounts(DomoManager):
    accounts: list[DomoAccount] = None
    oauths: list[DomoAccount_OAuth] = None

    async def get_accounts_accountsapi(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        is_use_default_account_class: bool = True,
        debug_num_stacks_to_drop: int = 2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop - 1,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.get_accounts(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        if len(res.response) == 0:
            self.accounts = []
            return self.accounts

        self.accounts = await dmce.gather_with_concurrency(
            n=60,
            *[
                DomoAccount.get_by_id(
                    account_id=obj.get("id"),
                    auth=self.auth,
                    context=context,
                    is_use_default_account_class=is_use_default_account_class,
                )
                for obj in res.response
            ],
        )

        return self.accounts

    async def get_accounts_queryapi(
        self,
        additional_filters_ls=None,
        is_use_default_account_class: bool = False,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """v2 api for works with group_account_v2 beta"""
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop - 1,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await datacenter_routes.search_datacenter(
            auth=self.auth,
            entity_type=datacenter_routes.Datacenter_Enum.ACCOUNT.value,
            additional_filters_ls=additional_filters_ls,
            context=context,
        )

        if return_raw:
            return res

        if len(res.response) == 0:
            self.accounts = []
            return self.accounts

        self.accounts = [
            DomoAccount.from_dict(
                auth=self.auth,
                obj=account_obj,
                is_use_default_class=is_use_default_account_class,
            )
            for account_obj in res.response
        ]
        return self.accounts

    async def get(
        self,
        *args: Any,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        is_use_default_account_class: bool = False,
        debug_num_stacks_to_drop: int = 3,
        context: RouteContext | None = None,
        **kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        domo_accounts = None
        try:
            domo_accounts = await self.get_accounts_queryapi(
                context=context,
                is_use_default_account_class=is_use_default_account_class,
                return_raw=return_raw,
            )

        except SearchDatacenterNoResultsFoundError as e:
            print(e)

        if not domo_accounts:
            domo_accounts = await self.get_accounts_accountsapi(
                context=context,
                is_use_default_account_class=is_use_default_account_class,
                return_raw=return_raw,
            )

        if return_raw:
            return domo_accounts

        return self.accounts

    async def get_oauths(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_num_stacks_to_drop: int = 2,
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

        res = await account_routes.get_oauth_accounts(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        self.oauths = [
            DomoAccount_OAuth.from_dict(
                obj=obj, auth=self.auth, is_use_default_account_class=True
            )
            for obj in res.response
        ]

        return self.oauths

    async def search_by_name(
        self,
        account_name: str,
        data_provider_type: str = None,
        is_use_default_account_class: bool = True,
        is_suppress_not_found_exception: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoAccount | None:
        """Search for an account by name (matches display_name or name).

        Args:
            account_name: Account name to search for (case-insensitive)
            data_provider_type: Optional filter by data provider type
            is_use_default_account_class: Use default account class
            is_suppress_not_found_exception: Suppress not found exceptions
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (session, debug_api, etc.)

        Returns:
            Matching DomoAccount or None if not found

        Raises:
            DomoError: If account retrieval fails
        """
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        await self.get(
            context=context,
            is_use_default_account_class=is_use_default_account_class,
        )

        for account in self.accounts:
            # Check both name and display_name for matching
            name_match = False
            if (
                account.display_name
                and account.display_name.lower() == account_name.lower()
            ):
                name_match = True
            elif account.name and account.name.lower() == account_name.lower():
                name_match = True

            if not name_match:
                continue

            # If data_provider_type specified, must match
            if data_provider_type and data_provider_type != account.data_provider_type:
                continue

            return account

        if is_suppress_not_found_exception:
            return None

        raise DomoAccounts_NoAccount(
            cls=self.__class__,
            message=f"No account found with name '{account_name}'",
            domo_instance=self.auth.domo_instance,
        )

    @classmethod
    async def upsert_account(
        cls,
        auth: DomoAuth,
        account_id: str = None,
        account_name: str = None,
        account_config: AccountConfig = None,
        data_provider_type: str = None,
        debug_api: bool = False,
        debug_prn: bool = False,
        return_raw: bool = False,
        return_search: bool = False,
        is_use_default_account_class: bool = True,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """search for an account and upsert it"""
        # For classmethods, create a temporary instance to use _build_route_context
        temp_instance = cls(auth=auth)
        base_context = temp_instance._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if not account_name and not account_id:
            raise UpsertAccount_MatchCriteriaError(domo_instance=auth.domo_instance)

        data_provider_type = (
            data_provider_type or account_config and account_config.data_provider_type
        )
        acc = None

        if account_id:
            try:
                acc = await DomoAccount.get_by_id(
                    auth=auth,
                    account_id=account_id,
                    context=context,
                    is_use_default_account_class=is_use_default_account_class,
                    **context_kwargs,
                )
            except dmde.DomoError:
                pass

        if account_name and not acc:
            try:
                domo_accounts = DomoAccounts(auth=auth)
                acc = await domo_accounts.search_by_name(
                    account_name=account_name,
                    data_provider_type=data_provider_type,
                    is_use_default_account_class=is_use_default_account_class,
                    context=context,
                    **context_kwargs,
                )
            except dmde.DomoError:
                pass

        if return_search:
            return acc

        if not isinstance(
            acc, DomoAccount_Default | DomoAccount | DomoAccountCredential
        ):
            if debug_prn:
                print(f"creating {account_name} in {auth.domo_instance}")

            return await DomoAccount.create_account(
                account_name=account_name,
                config=account_config,
                auth=auth,
                context=context,
                return_raw=return_raw,
            )

        if account_name and account_id:
            if debug_prn:
                print(
                    f"upsert-ing {acc.id} - {acc.display_name or acc.name} in {auth.domo_instance}"
                )

            await acc.update_name(
                account_name=account_name,
                context=context,
                return_raw=return_raw,
            )

        if account_config:  # upsert account
            acc.Config = account_config

            if debug_prn:
                print(f"upsertting {acc.id}:  updating config")

            await acc.update_config(context=context, return_raw=return_raw)

        return acc
