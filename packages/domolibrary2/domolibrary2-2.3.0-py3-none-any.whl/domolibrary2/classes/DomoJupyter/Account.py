from __future__ import annotations

__all__ = [
    "DJW_PermissionToAccountDeniedError",
    "DJW_AccountInvalid_NotAddedToWorkspaceError",
    "read_domo_jupyter_account",
    "DomoJupyter_Account",
    "DJW_InvalidClassError",
]


import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import exceptions as dmde
from ...base.exceptions import ClassError, DomoError
from ...routes.account.exceptions import AccountNoMatchError
from ...utils import xkcd_password as dmxkcd
from ...utils.logging import get_colored_logger
from .. import DomoAccount as dmac

logger = get_colored_logger()


class DJW_PermissionToAccountDeniedError(ClassError):
    def __init__(self, message, account_name, cls_instance=None):
        super().__init__(
            message=message, entity_id=account_name, cls_instance=cls_instance
        )


class DJW_AccountInvalid_NotAddedToWorkspaceError(ClassError):
    def __init__(self, message, account_name, cls_instance=None):
        super().__init__(
            message=message, entity_id=account_name, cls_instance=cls_instance
        )


def read_domo_jupyter_account(
    account_name,
    domojupyter_fn: Callable,
    is_abstract: bool = False,
    is_dict: bool = True,
):
    try:
        account_properties = domojupyter_fn.get_account_property_keys(account_name)

    except DomoError as e:
        if str(e).startswith("Permissions denied for workspace"):
            raise DJW_PermissionToAccountDeniedError(
                message=f"share account with user - {e}", account_name=account_name
            ) from e

        if str(e).startswith(
            "Failed to obtain workspace account properties for workspace"
        ):
            raise DJW_AccountInvalid_NotAddedToWorkspaceError(
                message=f"add account to workspace - {e}", account_name=account_name
            ) from e

        raise

    creds = {
        prop: domojupyter_fn.get_account_property_value(account_name, prop)
        for prop in account_properties
    }

    if not is_abstract:
        return creds

    creds = creds["credentials"]

    if not is_dict:
        return creds.strip()

    return json.loads(creds)


@dataclass
class DomoJupyter_Account:
    dj_workspace: Any = field(repr=False)
    account_id: int
    alias: str

    is_exists: bool = False
    domo_account: dmac.DomoAccount = None
    creds: str | dict = field(default=None, repr=False)

    def __post_init__(self):
        self.account_id = int(self.account_id)

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.account_id == other.account_id

    def __lt__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.alias < other.alias

    async def get_account(
        self,
        is_use_default_account_class: bool = True,
        is_suppress_errors: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
    ):
        try:
            self.domo_account = await dmac.DomoAccount.get_by_id(
                auth=self.dj_workspace.auth,
                account_id=self.account_id,
                is_use_default_account_class=is_use_default_account_class,
                is_suppress_no_config=is_suppress_errors,
                session=session,
                debug_api=debug_api,
            )
            self.is_exists = True

            return self.domo_account

        except (AccountNoMatchError, DomoError) as e:
            self.is_exists = False
            await logger.warning(
                f"account id {self.account_id} not found - {e} - is it shared with you?"
            )

            if not is_suppress_errors:
                raise e from e

    @classmethod
    def from_dict(
        cls,
        obj,
        dj_workspace,
        domo_account: dmac.DomoAccount | None = None,
    ):
        account_id = obj["account_id"]
        alias = obj["alias"]

        da = cls(account_id=account_id, alias=alias, dj_workspace=dj_workspace)

        if domo_account is not None:
            da.domo_account = domo_account
            da.is_exists = True

        return da

    @classmethod
    async def _from_account(
        cls,
        dj_workspace,
        domo_account,
        debug_api: bool = False,
        is_use_default_account_class: bool = False,
        is_suppress_errors: bool = False,
        session: httpx.AsyncClient = None,
    ):
        da = cls(
            dj_workspace=dj_workspace,
            account_id=domo_account.id,
            alias=domo_account.name,
        )

        await da.get_account(
            session=session,
            debug_api=debug_api,
            is_use_default_account_class=is_use_default_account_class,
            is_suppress_errors=is_suppress_errors,
        )

        return da

    def to_dict(self):
        return {
            "account_id": str(self.account_id),
            "alias": self.alias,
            "creds": self.creds,
        }

    def to_api(self):
        return {
            "account_id": str(self.account_id),
            "alias": self.alias,
        }

    async def share_with_workspace(
        self,
        dj_workspace: Any = None,
        is_update_config: bool = True,
        debug_api: bool = False,
    ):
        dj_workspace = dj_workspace or self.dj_workspace

        await self.dj_workspace.add_account(
            dja_account=self,
            is_update_config=is_update_config,
            debug_api=debug_api,
        )

    def read_creds(
        self, domojupyter_fn: Callable, is_abstract: bool = None, is_dict: bool = True
    ):
        is_abstract = (
            True
            if self.domo_account
            and self.domo_account.data_provider_type == "abstract-credential-store"
            else False
        )

        creds = read_domo_jupyter_account(
            account_name=self.alias,
            domojupyter_fn=domojupyter_fn,
            is_abstract=is_abstract,
            is_dict=is_dict,
        )

        self.creds = creds

        if not (
            self.domo_account
            and isinstance(self.domo_account, dmac.DomoAccount_Credential)
        ):
            return self.creds

        self.creds = {
            "access_token": (
                creds.get("DOMO_ACCESS_TOKEN")
                if is_abstract
                else creds.get("domoAccessToken")
            ),
            "password": (
                creds.get("DOMO_PASSWORD") if is_abstract else creds.get("password")
            ),
            "username": (
                creds.get("DOMO_USERNAME") if is_abstract else creds.get("username")
            ),
        }

        self.domo_account.set_password(self.creds.get("password"))
        self.domo_account.set_access_token(self.creds.get("access_token"))

        return self.creds

    async def regenerate_failed_password(
        self,
        domojupyter_fn: Callable,
        debug_api: bool = False,
        debug_prn: bool = False,
        new_password: str = None,  # only used if current password does not validate will autogenerate if no passwordd provided
        target_account_name: str = None,
        target_auth: DomoAuth = None,
        is_deploy_account_to_target_instance: bool = True,
        is_force_reset: bool = False,
    ) -> dmac.DomoAccount:
        """
        tests credentials for target_user -- will reset password or access token
        """

        creds = self.read_creds(domojupyter_fn=domojupyter_fn)

        if target_auth:
            self.domo_account.target_auth = target_auth
            self.domo_account.target_instance = target_auth.domo_instance

        if not self.domo_account.target_auth:
            await self.domo_account.test_auths()

        if debug_prn:
            print(
                f"\n\n🛢️ Phase 0: read creds - {json.dumps(creds)} and test against {self.domo_account.target_auth.domo_instance}\n\n"
            )

        if not self.domo_account.target_user:
            await self.domo_account.get_target_user()

            if debug_prn:
                print(
                    f"\n\n🛢️ Phase 0.5: get_target_user {self.domo_account.target_user.display_name} from {self.domo_account.target_user.auth.domo_instance}"
                )

        if not self.domo_account.target_user:
            raise dmac.DAC_NoTargetUser(self.domo_account)

        await self.domo_account.test_full_auth()

        if self.domo_account.is_valid_full_auth and not is_force_reset:
            return self.domo_account

        new_password = new_password or dmxkcd.generate_domo_password()

        if debug_prn:
            print(
                f"\n\n🛢️🛢️ Phase 1: Password Invalid on {self.alias} - for user {self.domo_account.target_user.display_name} - reseting password {new_password}\n\n"
            )

        await self.domo_account.set_target_user_password(
            new_password=new_password, debug_api=debug_api
        )

        if is_deploy_account_to_target_instance:
            await self.domo_account.upsert_target_account(
                account_name=target_account_name or self.domo_account.name,
                debug_api=debug_api,
            )

        return self.domo_account

    async def regenerate_failed_token(
        self,
        domojupyter_fn: Callable,
        debug_api: bool = False,
        debug_prn: bool = False,
        target_account_name: str = None,
        target_auth: DomoAuth = None,
        is_deploy_account_to_target_instance: bool = True,
        is_force_reset: bool = False,
    ) -> dict:
        """
        tests credentials for target_user -- will reset password or access token
        """

        creds = self.read_creds(domojupyter_fn=domojupyter_fn)

        if target_auth:
            self.domo_account.target_auth = target_auth
            self.domo_account.target_instance = target_auth.domo_instance

        if not self.domo_account.target_auth:
            await self.domo_account.test_auths()

        if debug_prn:
            print(
                f"\n\n🛢️ Phase 0: read creds - {json.dumps(creds)} and test against {self.domo_account.target_auth.domo_instance}\n\n"
            )

        await self.domo_account.test_token_auth()

        if self.domo_account.is_valid_token_auth and not is_force_reset:
            return self.domo_account

        if debug_prn:
            print(
                f"\n\n🛢️🛢️ Phase 1: Invalid token on {self.alias} - regenerating token\n\n"
            )

        await self.domo_account.reset_access_token(
            token_name=target_account_name or self.domo_account.name,
            debug_api=debug_api,
        )

        if is_deploy_account_to_target_instance:
            await self.domo_account.upsert_target_account(
                account_name=target_account_name or self.domo_account.name,
                debug_api=debug_api,
            )

        return self.domo_account


class DJW_InvalidClassError(dmde.ClassError):
    def __init__(self, cls_instance, message):
        super().__init__(cls_instance=cls_instance, message=message)
