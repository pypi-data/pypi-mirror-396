__all__ = ["UserAttribute", "UserAttributes"]

import datetime as dt
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import DomoEntity, DomoManager
from ...client.context import RouteContext
from ...routes.instance_config import user_attributes as user_attribute_routes
from ...routes.instance_config.user_attributes import (
    UserAttributes_CRUD_Error,
    UserAttributes_GET_Error,
)


@dataclass(eq=False)
class UserAttribute(DomoEntity):
    """utility class that absorbs many of the domo instance configuration methods"""

    auth: DomoAuth = field(repr=False)
    id: str
    name: str
    description: str

    issuer_type: user_attribute_routes.UserAttributes_IssuerType
    customer_id: str
    value_type: str

    validator: str
    validator_configuration: None

    security_voter: str
    custom: bool

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/governance/attribute-management"

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        return cls(
            auth=auth,
            id=obj["key"],
            name=obj["title"],
            description=obj["description"],
            issuer_type=user_attribute_routes.UserAttributes_IssuerType(
                obj["keyspace"]
            ),
            customer_id=obj["context"],
            value_type=obj["valueType"],
            validator=obj["validator"],
            validator_configuration=obj["validatorConfiguration"],
            security_voter=obj["securityVoter"],
            custom=obj["custom"],
            raw=obj,
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        entity_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await user_attribute_routes.get_user_attribute_by_id(
            auth=auth,
            entity_id=entity_id,
            context=context,
        )

        if return_raw:
            return res
        return cls.from_dict(obj=res.response, auth=auth)

    async def update(
        self,
        name=None,
        description=None,
        issuer_type: user_attribute_routes.UserAttributes_IssuerType | None = None,
        data_type: str | None = None,
        security_voter=None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
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

        await user_attribute_routes.update_user_attribute(
            auth=self.auth,
            attribute_id=self.id,
            name=name,
            description=description,
            issuer_type=issuer_type,
            data_type=data_type,
            security_voter=security_voter,
            context=context,
        )

        new = await UserAttribute.get_by_id(
            entity_id=self.id, auth=self.auth, context=context
        )

        [setattr(self, key, value) for key, value in new.__dict__.items()]

        return self


async def update(
    self: UserAttribute,
    name=None,
    description=None,
    issuer_type: user_attribute_routes.UserAttributes_IssuerType | None = None,
    data_type: str | None = None,
    security_voter=None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
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

    await user_attribute_routes.update_user_attribute(
        auth=self.auth,
        attribute_id=self.id,
        name=name,
        description=description,
        issuer_type=issuer_type,
        data_type=data_type,
        security_voter=security_voter,
        context=context,
    )

    new = await UserAttribute.get_by_id(
        entity_id=self.id, auth=self.auth, context=context
    )

    [setattr(self, key, value) for key, value in new.__dict__.items()]

    return self


@dataclass
class UserAttributes(DomoManager):
    auth: DomoAuth = field(repr=False)

    attributes: list[UserAttribute] = field(default_factory=list)

    async def get(
        self,
        issuer_type_ls: list[
            user_attribute_routes.UserAttributes_IssuerType
        ] = [],  # use `UserAttributes_IssuerType` enum
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
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

        auth = self.auth

        res = await user_attribute_routes.get_user_attributes(
            auth=auth,
            issuer_type_ls=issuer_type_ls,
            context=context,
        )

        if return_raw:
            return res

        self.attributes = [
            UserAttribute.from_dict(obj=obj, auth=auth) for obj in res.response
        ]
        return self.attributes

    async def create(
        self,
        attribute_id: str,
        name=None,
        description=f"updated via domolibrary {dt.datetime.now().strftime('%Y-%m-%d - %H:%M')}",
        data_type: str = "ANY_VALUE",
        security_voter="FULL_VIS_ADMIN_IDP",
        issuer_type: (
            user_attribute_routes.UserAttributes_IssuerType | None
        ) = user_attribute_routes.UserAttributes_IssuerType.CUSTOM,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        return_raw: bool = False,
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

        auth = self.auth
        attribute_id = user_attribute_routes.clean_attribute_id(attribute_id)

        res = await user_attribute_routes.create_user_attribute(
            auth=auth,
            issuer_type=issuer_type,
            name=name,
            attribute_id=attribute_id,
            description=description,
            data_type=data_type,
            security_voter=security_voter,
            context=context,
        )

        await self.get(context=context)

        if return_raw:
            return res

        return await UserAttribute.get_by_id(
            auth=auth, entity_id=attribute_id, context=context
        )


async def create(
    self: UserAttributes,
    attribute_id: str,
    name=None,
    description=f"updated via domolibrary {dt.datetime.now().strftime('%Y-%m-%d - %H:%M')}",
    data_type: str = "ANY_VALUE",
    security_voter="FULL_VIS_ADMIN_IDP",
    issuer_type: (
        user_attribute_routes.UserAttributes_IssuerType | None
    ) = user_attribute_routes.UserAttributes_IssuerType.CUSTOM,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    return_raw: bool = False,
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

    auth = self.auth
    attribute_id = user_attribute_routes.clean_attribute_id(attribute_id)

    res = await user_attribute_routes.create_user_attribute(
        auth=auth,
        issuer_type=issuer_type,
        name=name,
        attribute_id=attribute_id,
        description=description,
        data_type=data_type,
        security_voter=security_voter,
        context=context,
    )

    await self.get(context=context)

    if return_raw:
        return res

    return await UserAttribute.get_by_id(
        auth=auth, entity_id=attribute_id, context=context
    )


async def upsert(
    self: UserAttributes,
    attribute_id,
    name=None,
    description=None,
    issuer_type: user_attribute_routes.UserAttributes_IssuerType | None = None,
    data_type: str | None = None,
    security_voter=None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    debug_prn: bool = False,
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

    auth = self.auth
    attribute_id = user_attribute_routes.clean_attribute_id(attribute_id)

    user_attribute = None

    try:
        user_attribute = await UserAttribute.get_by_id(
            entity_id=attribute_id,
            auth=auth,
            context=context,
        )

        if user_attribute:
            if debug_prn:
                print(f"upserting {attribute_id} in {auth.domo_instance}")

            await user_attribute.update(
                name=name,
                description=description,
                issuer_type=issuer_type,
                data_type=data_type,
                security_voter=security_voter,
                context=context,
            )

        return user_attribute

    except (UserAttributes_CRUD_Error, UserAttributes_GET_Error):
        if debug_prn:
            print(f"creating {attribute_id} in {auth.domo_instance}")

        return await self.create(
            attribute_id=attribute_id,
            name=name,
            description=description or "",
            issuer_type=issuer_type
            or user_attribute_routes.UserAttributes_IssuerType.CUSTOM,
            data_type=data_type or "",
            security_voter=security_voter or "",
            context=context,
        )

    finally:
        await self.get(context=context)


async def delete(
    self: UserAttributes,
    attribute_id: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    return_raw: bool = False,
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

    auth = self.auth

    res = await user_attribute_routes.delete_user_attribute(
        auth=auth,
        attribute_id=attribute_id,
        context=context,
    )

    await self.get(context=context)

    return res
