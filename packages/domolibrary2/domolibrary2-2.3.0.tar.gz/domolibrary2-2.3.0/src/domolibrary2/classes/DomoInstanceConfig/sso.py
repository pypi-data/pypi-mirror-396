__all__ = [
    "SSOConfig_InstantiationError",
    "SSOConfig_UpdateError",
    "SSO_Config",
    "SSO_OIDC_Config",
    "SSO_SAML_Config",
    "SSO",
]


import json
from collections.abc import Callable
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from functools import partial
from pprint import pprint  # pprint from_dict
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import (
    DomoBase,
    DomoManager,
    exceptions as dmde,
)
from ...client import (
    response as rgd,
)
from ...client.context import RouteContext
from ...routes.instance_config import sso as sso_routes
from ...utils import convert as dmcv


class SSOConfig_InstantiationError(dmde.ClassError):
    def __init__(self, message, auth, cls_instance=None):
        super().__init__(auth=auth, message=message, cls_instance=cls_instance)


class SSOConfig_UpdateError(dmde.ClassError):
    def __init__(
        self, errors_obj, res: rgd.ResponseGetData, cls_instance, domo_instance
    ):
        message = json.dumps(errors_obj)
        super().__init__(
            res=res, message=message, cls_instance=cls_instance, entity_id=domo_instance
        )


@dataclass
class SSO_Config(DomoBase):
    """base class for SAML and OIDC Config"""

    auth: DomoAuth
    idp_enabled: bool  # False
    enforce_allowlist: bool
    idp_certificate: str

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/security/sso?tab=configuration"

    def set_attribute(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise SSOConfig_InstantiationError(
                    message=f"key {key} not part of class", auth=self.auth
                )
            if value is not None:
                setattr(self, key, value)

        return self

    @classmethod
    async def get(cls, auth: DomoAuth):
        raise NotImplementedError()

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict,
        debug_prn: bool = False,
        **kwargs: dict,  # parameters that will be passed to the class object (must be attributes of the class)
    ):
        new_obj = {
            dmcv.convert_str_to_snake_case(key, is_pascal=True): value
            for key, value in obj.items()
        }

        idp_enabled = new_obj.pop("idp_enabled")

        if isinstance(idp_enabled, str):
            idp_enabled = dmcv.convert_string_to_bool(idp_enabled)

        enforce_allowlist = new_obj.pop("enforce_whitelist")

        if debug_prn:
            pprint(
                {
                    "new_obj": new_obj,
                    "idp_enabled": idp_enabled,
                    "enforce_allowlist": enforce_allowlist,
                    "kwargs": kwargs,
                }
            )

        sso_cls = cls(
            auth=auth,
            enforce_allowlist=enforce_allowlist,
            idp_enabled=idp_enabled,
            raw=obj,
            **kwargs,
            **new_obj,
        )

        sso_cls.set_attribute(**new_obj)

        return sso_cls

    async def update(
        self,
        update_config_route_fn: Callable,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        debug_is_test: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )
        context = RouteContext.build_context(context=context or base_context)

        self.set_attribute(**kwargs)

        body_sso = self.to_dict()

        if debug_is_test:
            print("⚗️⚠️ This is a test, SSO Config will not be updated")
            return body_sso

        res = await update_config_route_fn(
            auth=self.auth,
            body_sso=body_sso,
            context=context,
        )

        if return_raw:
            return res

        new_config = await self.get(auth=self.auth)

        errors_obj = {}
        for n_key, current_value in asdict(new_config).items():
            if n_key in ["auth"]:
                continue

            expected_value = getattr(self, n_key)

            if expected_value != current_value:
                errors_obj.update(
                    {
                        "key": n_key,
                        "expected_value": expected_value,
                        "current_value": current_value,
                    }
                )

            self.set_attribute(**{n_key: current_value})

        if errors_obj:
            raise SSOConfig_UpdateError(
                res=res,
                errors_obj=errors_obj,
                cls_instance=self,
                domo_instance=self.auth.domo_instance,
            )

        return self


@dataclass
class SSO_OIDC_Config(SSO_Config):
    login_enabled: bool
    import_groups: bool
    require_invitation: bool
    skip_to_idp: bool
    redirect_url: str  # url
    override_sso: bool
    override_embed: bool
    well_known_config: str

    auth_request_endpoint: str = None  # url
    token_endpoint: str = None
    user_info_endpoint: str = None
    public_key: str = None

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any], debug_prn: bool = False):
        raw = deepcopy(obj)

        override_sso = obj.pop("overrideSSO")

        idp_certificate = (
            obj.pop("certificate") if hasattr(obj, "certificate") else None
        )

        return super().from_dict(
            auth=auth,
            obj=obj,
            raw=raw,
            debug_prn=debug_prn,
            override_sso=override_sso,
            idp_certificate=idp_certificate,
        )

    def to_dict(self, override_fn: Callable = None, is_include_undefined: bool = False):
        return super().to_dict(
            override_fn=partial(
                sso_routes.generate_sso_oidc_body,
                is_include_undefined=is_include_undefined,
            )
        )

    @classmethod
    async def get(
        cls,
        auth: DomoAuth,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_prn: bool = False,
        return_raw: bool = False,
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
            debug_num_stacks_to_drop=2,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await sso_routes.get_sso_oidc_config(
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response, debug_prn=debug_prn)

    async def update(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        debug_is_test: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **kwargs,
    ):
        return await super().update(
            update_config_route_fn=sso_routes.update_sso_oidc_config,
            context=context,
            debug_is_test=debug_is_test,
            return_raw=return_raw,
            **kwargs,
        )


@dataclass
class SSO_SAML_Config(SSO_Config):
    is_enabled: bool
    import_groups: bool  # False
    require_invitation: bool
    redirect_url: str

    auth_request_endpoint: str = None
    issuer: str = None
    relay_state: bool = None
    redirect_url: str = None
    sign_auth_request: Any = None

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any], debug_prn: bool = False):
        raw = deepcopy(obj)

        is_enabled = obj.pop("enabled")

        relay_state = (
            dmcv.convert_string_to_bool(obj.pop("relayState"))
            if obj.get("relayState")
            else None
        )

        idp_certificate = (
            obj.pop("idpCertificate") if obj.get("idpCertificate") else None
        )

        return super().from_dict(
            auth=auth,
            obj=obj,
            is_enabled=is_enabled,
            idp_certificate=idp_certificate,
            relay_state=relay_state,
            raw=raw,
            debug_prn=debug_prn,
        )

    def to_dict(self, is_include_undefined: bool = False):
        return super().to_dict(
            override_fn=partial(
                sso_routes.generate_sso_saml_body,
                is_include_undefined=is_include_undefined,
            )
        )

    @classmethod
    async def get(
        cls,
        auth: DomoAuth,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_prn: bool = False,
        return_raw: bool = False,
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
            debug_num_stacks_to_drop=1,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await sso_routes.get_sso_saml_config(
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

        return SSO_SAML_Config.from_dict(
            auth=auth, obj=res.response, debug_prn=debug_prn
        )

    async def update(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        debug_is_test: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **kwargs,
    ):
        return await super().update(
            update_config_route_fn=sso_routes.update_sso_saml_config,
            context=context,
            debug_is_test=debug_is_test,
            return_raw=return_raw,
            **kwargs,
        )


@dataclass
class SSO(DomoManager):
    """
    class for managing SSO Config.
    Includes both OIDC aand SAML
    """

    OIDC: SSO_OIDC_Config = field(default=None)  # OIDDC config class
    SAML: SSO_SAML_Config = field(default=None)  # SAML config class

    async def get_oidc(
        self,
        debug_api: bool = False,
        debug_prn: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        OIDC = await SSO_OIDC_Config.get(
            auth=self.auth,
            debug_prn=debug_prn,
            return_raw=return_raw,
            context=context,
            **context_kwargs,
        )

        if return_raw:
            return OIDC

        self.OIDC = OIDC

        return self.OIDC

    async def get_saml(
        self,
        debug_api: bool = False,
        debug_prn: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        SAML = await SSO_SAML_Config.get(
            auth=self.auth,
            debug_prn=debug_prn,
            return_raw=return_raw,
            context=context,
            **context_kwargs,
        )

        if return_raw:
            return SAML

        self.SAML = SAML

        return self.SAML

    async def get(
        self,
        debug_api: bool = False,
        debug_prn: bool = False,
        *,
        context: RouteContext | None = None,
    ):
        await self.get_oidc(debug_prn=debug_prn, context=context)
        await self.get_saml(debug_prn=debug_prn, context=context)

        return self
