__all__ = [
    "Account_CanIModifyError",
    "UpsertAccount_MatchCriteriaError",
    "DomoAccounConfig_MissingFieldsError",
    "DomoAccount_Default",
    "AccountClass_CRUDError",
]
import asyncio
import datetime as dt
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity
from ...base.exceptions import ClassError, DomoError
from ...client.context import RouteContext
from ...routes import account as account_routes
from ...utils import convert as cd
from ...utils.logging import (
    LogDecoratorConfig,
    ResponseGetDataProcessor,
    get_colored_logger,
    log_call,
)
from .access import DomoAccess_Account
from .config import AccountConfig, DomoAccount_Config

logger = get_colored_logger()


class Account_CanIModifyError(ClassError):
    def __init__(self, account_id, domo_instance):
        super().__init__(
            message="`DomoAccount.is_admin_summary` must be `False` to proceed.  Either set the value explicity, or retrieve the account instance using `DomoAccount.get_by_id()`",
            domo_instance=domo_instance,
            entity_id=account_id,
        )


class UpsertAccount_MatchCriteriaError(ClassError):
    def __init__(self, domo_instance):
        super().__init__(
            message="must pass an account_id or account_name to UPSERT",
            domo_instance=domo_instance,
        )


class DomoAccounConfig_MissingFieldsError(ClassError):
    def __init__(self, domo_instance, missing_keys, account_id):
        super().__init__(
            domo_instance=domo_instance,
            message=f"{account_id} config class definition is missing the following keys - {', '.join(missing_keys)} extend the AccountConfig",
        )


class AccountClass_CRUDError(ClassError):
    def __init__(self, cls_instance, message):
        super().__init__(cls_instance=cls_instance, message=message)


@dataclass
class DomoAccount_Default(DomoEntity):
    id: int
    auth: DomoAuth = field(repr=False)

    name: str = None  # Internal name field
    display_name: str = None  # User-friendly display name
    data_provider_type: str = None

    created_dt: dt.datetime = None
    modified_dt: dt.datetime = None

    owners: list[Any] = None  # DomoUser or DomoGroup

    is_admin_summary: bool = True
    dataset_count: int = None

    Config: DomoAccount_Config = field(repr=False, default=None, compare=False)
    Access: DomoAccess_Account = field(repr=False, default=None, compare=False)

    def __eq__(self, other):
        if not isinstance(other, DomoAccount_Default):
            return False

        return (
            self.id == other.id and self.auth.domo_instance == other.auth.domo_instance
        )

    @property
    def entity_type(self):
        return "ACCOUNT"

    @property
    def display_url(self):
        """returns the URL to the account in Domo"""
        return f"{self.auth.domo_instance}/datacenter/accounts"

    def __post_init__(self):
        self.id = int(self.id)

        self.Access = DomoAccess_Account.from_parent(
            parent=self,
        )

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict[str, Any],
        is_admin_summary: bool = True,
        new_cls: Any = None,
        **kwargs,
    ):
        """converts data_v1_accounts API response into an accounts class object"""

        return new_cls(
            id=obj.get("id") or obj.get("databaseId"),
            name=obj.get("name"),
            display_name=obj.get("displayName"),
            data_provider_type=obj.get("dataProviderId") or obj.get("dataProviderType"),
            created_dt=cd.convert_epoch_millisecond_to_datetime(
                obj.get("createdAt") or obj.get("createDate")
            ),
            modified_dt=cd.convert_epoch_millisecond_to_datetime(
                obj.get("modifiedAt") or obj.get("lastModified")
            ),
            auth=auth,
            is_admin_summary=is_admin_summary,
            owners=obj.get("owners"),
            dataset_count=obj.get("datasetCount"),
            raw=obj,
            **kwargs,
        )

    def _update_self(self, new_class, skip_props: list[str] | None = None) -> bool:
        for key, value in new_class.__dict__.items():
            if key in skip_props:
                continue

            setattr(self, key, value)

        return True

    def _test_missing_keys(
        self, res_obj: dict[str, Any], config_obj: dict[str, Any]
    ) -> list[str]:
        return [r_key for r_key in res_obj.keys() if r_key not in config_obj.keys()]

    async def refresh(
        self,
        is_suppress_no_config: bool = False,
        debug_api: bool = False,
        session: httpx.Client = None,
    ):
        """synchronous wrapper for _get_config"""

        await super().refresh(
            is_suppress_no_config=is_suppress_no_config,
            debug_api=debug_api,
            session=session,
        )

        await self._get_config(
            is_suppress_no_config=is_suppress_no_config,
            debug_api=debug_api,
            session=session,
        )

        return self

    @log_call(
        level_name="class",
        config=LogDecoratorConfig(result_processor=ResponseGetDataProcessor()),
        logger=logger,
    )
    async def _get_config(
        self,
        session=None,
        return_raw: bool = False,
        debug_api: bool = None,
        auth: DomoAuth = None,
        debug_num_stacks_to_drop=2,
        is_unmask: bool = True,
        is_suppress_no_config: bool = False,  # can be used to suppress cases where the config is not defined, either because the account_config is OAuth, and therefore not stored in Domo OR because the AccountConfig class doesn't cover the data_type
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        await logger.debug(f"Getting config for {self.__class__.__name__} id {self.id}")

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if not self.data_provider_type:
            res = await account_routes.get_account_by_id(
                auth=self.auth,
                account_id=self.id,
                context=context,
            )

            self.data_provider_type = res.response["dataProviderType"]

        res = await account_routes.get_account_config(
            auth=auth or self.auth,
            account_id=self.id,
            is_unmask=is_unmask,
            data_provider_type=self.data_provider_type,
            context=context,
        )

        if return_raw:
            return res

        try:
            config_fn = AccountConfig(self.data_provider_type).value
            self.Config = config_fn.from_dict(
                obj=res.response, data_provider_type=self.data_provider_type
            )

        except (DomoError, ValueError, TypeError) as e:
            message = f"unable to parse account config for {self.__class__.__name__} id {self.id} - {e}"

            if not is_suppress_no_config:
                await logger.error(message, color="red")
                raise e from e

            await logger.warning(
                message,
                color="yellow",
            )

        if self.Config and self.Config.to_dict() != {}:
            self._test_missing_keys(
                res_obj=res.response, config_obj=self.Config.to_dict()
            )

        return self.Config

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        account_id: int,
        is_suppress_no_config: bool = True,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        is_use_default_account_class=False,
        is_unmask=True,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """retrieves account metadata and attempts to retrieve config"""
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.get_account_by_id(
            auth=auth,
            account_id=account_id,
            is_unmask=is_unmask,
            context=context,
        )

        if return_raw:
            return res

        obj = res.response

        acc = cls.from_dict(
            obj=obj,
            auth=auth,
            is_admin_summary=False,
            is_use_default_class=is_use_default_account_class,
            new_cls=cls,
        )

        await acc._get_config(
            context=context,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            is_suppress_no_config=is_suppress_no_config,
        )

        return acc

    @classmethod
    async def get_entity_by_id(cls, entity_id, **kwargs):
        """Alias for get_by_id"""
        return await cls.get_by_id(account_id=entity_id, **kwargs)

    @classmethod
    async def create_account(
        cls,
        account_name: str,
        config: DomoAccount_Config,
        auth: DomoAuth,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop: int = 2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.create_account(
            account_name=account_name,
            data_provider_type=config.data_provider_type,
            auth=auth,
            config_body=config.to_dict(),
            context=context,
        )

        if return_raw:
            return res

        acc = await cls.get_by_id(
            auth=auth, account_id=res.response.get("id"), context=context
        )
        acc.Config = config
        return acc

    async def update_name(
        self,
        account_name: str = None,
        auth: DomoAuth = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = auth or self.auth

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.update_account_name(
            auth=auth,
            account_id=self.id,
            account_name=account_name or self.display_name or self.name,
            context=context,
        )

        if return_raw:
            return res

        if not res.is_success and self.is_admin_summary:
            raise Account_CanIModifyError(
                account_id=self.id, domo_instance=auth.domo_instance
            )

        new_acc = await DomoAccount_Default.get_by_id(
            auth=auth, account_id=self.id, context=context
        )

        self._update_self(new_class=new_acc, skip_props=["Config"])

        return self

        return self

    async def delete_account(
        self,
        auth: DomoAuth = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop=2,
        parent_class=None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = auth or self.auth

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await account_routes.delete_account(
            auth=auth,
            account_id=self.id,
            context=context,
        )

        if not res.is_success and self.is_admin_summary:
            raise Account_CanIModifyError(
                account_id=self.id, domo_instance=auth.domo_instance
            )

        return res

    async def update_config(
        self,
        auth: DomoAuth = None,
        debug_api: bool = False,
        config: DomoAccount_Config = None,
        is_suppress_no_config=False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        return_raw: bool = False,
        is_update_config: bool = False,  # if calling the Api, Domo will send encrypted values (astericks) in most cases it's best not to try to retrieve updated values from the API
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = auth or self.auth

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if config:
            self.Config = config

        if not self.Config:
            raise AccountClass_CRUDError(
                cls_instance=self,
                message="unable to update account - no domo_account.Config not provided",
            )

        res = await account_routes.update_account_config(
            auth=auth,
            account_id=self.id,
            config_body=self.Config.to_dict(),
            context=context,
        )

        # await asyncio.sleep(3)

        # new_acc = await DomoAccount_Default.get_by_id(auth=auth, account_id=self.id)

        # self._update_self(new_class = new_acc, skip_props = ['Config'])

        if return_raw:
            return res

        if not res.is_success and self.is_admin_summary:
            raise Account_CanIModifyError(
                account_id=self.id, domo_instance=auth.domo_instance
            )

        if not is_update_config:
            return self.Config

        await asyncio.sleep(3)

        await self._get_config(
            context=context,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            is_suppress_no_config=is_suppress_no_config,
        )

        return self.Config

    async def upsert_target_account(
        self,
        target_auth: DomoAuth,  # valid auth for target destination
        account_name: str = None,  # defaults to self.display_name or self.name
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """
        upsert an account in a target instance with self.Config
        """
        from copy import deepcopy

        # Import here to avoid circular import
        from . import core

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        return await core.DomoAccounts.upsert_account(
            auth=target_auth,
            account_name=account_name or self.display_name or self.name,
            account_config=deepcopy(self.Config),
            data_provider_type=self.data_provider_type,
            context=context,
        )

    async def get_access(
        self,
        force_refresh: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Retrieve the access list for this account.

        This method retrieves all users and groups that have access to this account
        along with their access levels.

        Args:
            force_refresh: If True, refresh even if Access relationships are already loaded
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            List of Access_Relation objects representing users/groups with access

        Example:
            >>> account = await DomoAccount.get_by_id(auth=auth, account_id="123")
            >>> access_list = await account.get_access()
            >>> for access in access_list:
            ...     print(f"{access.entity.name}: {access.relationship_type}")
        """
        if not force_refresh and self.Access.relationships:
            return self.Access.relationships

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        return await self.Access.get(
            context=context,
        )

    async def share(
        self,
        user_id: int = None,
        group_id: int = None,
        access_level=None,  # ShareAccount_AccessLevel
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Share this account with a user or group.

        Args:
            user_id: User ID to share with (mutually exclusive with group_id)
            group_id: Group ID to share with (mutually exclusive with user_id)
            access_level: Access level (ShareAccount_AccessLevel enum)
            session: HTTP client session (optional)
            debug_api: Enable API debugging
            return_raw: Return raw response without processing
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            ResponseGetData if return_raw=True, else the updated account

        Raises:
            ValueError: If neither user_id nor group_id is provided
            Account_Share_Error: If sharing operation fails

        Example:
            >>> from domolibrary2.routes.account import ShareAccount_AccessLevel
            >>> account = await DomoAccount.get_by_id(auth=auth, account_id="123")
            >>> await account.share(
            ...     user_id=456,
            ...     access_level=ShareAccount_AccessLevel.CAN_EDIT
            ... )
        """
        if not user_id and not group_id:
            raise ValueError("Must provide either user_id or group_id")

        if not access_level:
            from ...routes.account import ShareAccount_AccessLevel

            access_level = ShareAccount_AccessLevel.CAN_VIEW

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        # Generate share payload
        share_payload = access_level.generate_payload(
            user_id=user_id, group_id=group_id
        )

        res = await account_routes.share_account(
            auth=self.auth,
            account_id=self.id,
            share_payload=share_payload,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        # Refresh access list after sharing
        if self.Access:
            await self.get_access(force_refresh=True, context=context)

        return self
