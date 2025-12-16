__all__ = ["MFAConfig_InstantiationError", "MFA_Config"]

from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import exceptions as dmde
from ...client.context import RouteContext
from ...routes.instance_config import mfa as mfa_routes


class MFAConfig_InstantiationError(dmde.ClassError):
    def __init__(self, message, auth: DomoAuth, cls):
        super().__init__(domo_instance=auth.domo_instance, message=message, cls=cls)


@dataclass
class MFA_Config:
    auth: DomoAuth = field(repr=False)
    is_multifactor_required: bool = None
    max_code_attempts: int = None
    num_days_valid: int = None

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        return cls(
            auth=auth,
            is_multifactor_required=obj.get("is_multifactor_required"),
            num_days_valid=obj.get("num_days_valid"),
            max_code_attempts=obj.get("max_code_attempts"),
        )

    @classmethod
    async def get_instance_config(
        cls,
        auth: DomoAuth,
        incl_is_multifactor_required: bool = True,
        incl_num_days_valid: bool = True,
        incl_max_code_attempts: bool = True,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await mfa_routes.get_mfa_config(
            auth=auth,
            incl_is_multifactor_required=incl_is_multifactor_required,
            incl_num_days_valid=incl_num_days_valid,
            incl_max_code_attempts=incl_max_code_attempts,
            return_raw=return_raw,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    async def get(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
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

        res = await mfa_routes.get_mfa_config(
            auth=self.auth,
            incl_is_multifactor_required=True,
            incl_num_days_valid=True,
            incl_max_code_attempts=True,
            context=context,
        )

        if return_raw:
            return res

        self.num_days_valid = res.response.get("num_days_valid")
        self.max_code_attempts = res.response.get("max_code_attempts")
        self.is_multifactor_required = res.response.get("is_multifactor_required")

        return self

    def _test_need_update_config(
        self,
        attr_name,
        new_value,
        is_ignore_test: bool = False,
        debug_prn: bool = False,
    ):
        current_value = getattr(self, attr_name)

        if new_value is None:
            return False

        if new_value == current_value and not is_ignore_test:
            if debug_prn:
                print(
                    f"No change necessary -- {current_value} is the same as {new_value}"
                )
            return False

        return True

    async def toggle_mfa(
        self,
        is_enable_MFA: bool,
        is_ignore_test: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        suppress_update_self: bool = False,
        debug_prn: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        need_update_config = self._test_need_update_config(
            attr_name="is_multifactor_required",
            new_value=is_enable_MFA,
            is_ignore_test=is_ignore_test,
            debug_prn=debug_prn,
        )

        if not need_update_config:
            return self

        await mfa_routes.toggle_enable_mfa(
            auth=self.auth,
            is_enable_MFA=is_enable_MFA,
            context=context,
        )

        if suppress_update_self:
            return self

        return await self.get(context=context)

    async def enable(
        self,
        is_ignore_test: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """will have enable_value=True and will enable mfa in the instance"""
        return await self.toggle_mfa(
            is_ignore_test=is_ignore_test,
            context=context,
            is_enable_MFA=True,
            **context_kwargs,
        )

    async def disable(
        self,
        is_ignore_test: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """will have enable_value=False and will disable mfa in the instance"""
        return await self.toggle_mfa(
            is_ignore_test=is_ignore_test,
            context=context,
            is_enable_MFA=False,
            **context_kwargs,
        )

    async def set_max_code_attempts(
        self,
        max_code_attempts: int,
        is_ignore_test: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        suppress_update_self: bool = False,
        debug_prn: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        need_update_config = self._test_need_update_config(
            attr_name="max_code_attempts",
            new_value=max_code_attempts,
            is_ignore_test=is_ignore_test,
            debug_prn=debug_prn,
        )

        if not need_update_config:
            return self

        await mfa_routes.set_mfa_max_code_attempts(
            auth=self.auth,
            max_code_attempts=max_code_attempts,
            context=context,
        )

        if suppress_update_self:
            return self

        return await self.get(context=context)

    async def set_num_days_valid(
        self,
        num_days_valid: int,
        is_ignore_test: bool = False,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        suppress_update_self: bool = False,
        debug_prn: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        need_update_config = self._test_need_update_config(
            attr_name="num_days_valid",
            new_value=num_days_valid,
            is_ignore_test=is_ignore_test,
            debug_prn=debug_prn,
        )

        if not need_update_config:
            return self

        await mfa_routes.set_mfa_num_days_valid(
            auth=self.auth,
            num_days_valid=num_days_valid,
            context=context,
        )
        if not suppress_update_self:
            return self

        return await self.get(context=context)

    async def update(
        self,
        is_enable_MFA: bool = None,
        max_code_attempts: int = None,
        num_days_valid: int = None,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        debug_prn: bool = False,
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

        await self.toggle_mfa(
            is_enable_MFA=is_enable_MFA,
            context=context,
            suppress_update_self=True,
            debug_prn=debug_prn,
        )

        await self.set_max_code_attempts(
            max_code_attempts=max_code_attempts,
            context=context,
            suppress_update_self=True,
            debug_prn=debug_prn,
        )

        await self.set_num_days_valid(
            num_days_valid=num_days_valid,
            context=context,
            suppress_update_self=True,
            debug_prn=debug_prn,
        )

        return await self.get(context=context, return_raw=return_raw)
