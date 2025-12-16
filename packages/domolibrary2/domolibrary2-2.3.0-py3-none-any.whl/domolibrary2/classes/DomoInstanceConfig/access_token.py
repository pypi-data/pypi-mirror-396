__all__ = ["DomoAccessToken", "DomoAccessTokens"]

import asyncio
import datetime as dt
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity, DomoManager
from ...client.context import RouteContext
from ...routes import access_token as access_token_routes
from ...utils import (
    chunk_execution as dmce,
    convert as dmcv,
)


@dataclass(eq=False)
class DomoAccessToken(DomoEntity):
    auth: DomoAuth = field(repr=False)
    id: str
    raw: dict = field(repr=False)
    name: str = ""
    owner: Any = None  # DomoUser
    expiration_date: dt.datetime | None = None
    token: str = field(repr=False, default="")

    def __post_init__(self):
        if not isinstance(self.expiration_date, dt.datetime):
            self.expiration_date = dmcv.convert_epoch_millisecond_to_datetime(
                self.expiration_date  # type: ignore
            )

    @property
    def days_till_expiration(self):
        return (self.expiration_date - dt.datetime.now()).days

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/security/accesstokens"

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict[str, Any],
        owner: Any = None,
    ):
        return cls(
            id=obj["id"],
            name=obj["name"],
            owner=owner,
            expiration_date=obj["expires"],
            auth=auth,
            token=obj.get("token") or "",
            raw=obj,
        )

    @staticmethod
    async def _get_owner(owner_id, auth: DomoAuth):
        from ..DomoUser import DomoUser

        return await DomoUser.get_by_id(auth=auth, id=owner_id)

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
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
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await access_token_routes.get_access_token_by_id(
            auth=auth,
            id=id,
            context=context,
        )

        if return_raw:
            return res

        obj = res.response

        owner = await cls._get_owner(owner_id=obj["ownerId"], auth=auth)

        return cls.from_dict(obj=obj, auth=auth, owner=owner)

    @classmethod
    async def generate(
        cls,
        duration_in_days: int,
        token_name: str,
        auth: DomoAuth,
        owner,  # DomoUser
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
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
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await access_token_routes.generate_access_token(
            user_id=owner.id,
            token_name=token_name,
            duration_in_days=duration_in_days,
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(obj=res.response, auth=auth, owner=owner)

    async def revoke(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
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

        return await access_token_routes.revoke_access_token(
            auth=self.auth,
            access_token_id=self.id,
            context=context,
        )

    async def regenerate(
        self,
        session: httpx.AsyncClient | None = None,
        duration_in_days: int = 90,
        debug_api: bool = False,
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

        await self.revoke(context=context)

        await asyncio.sleep(3)

        new_token = await self.generate(
            duration_in_days=duration_in_days,
            token_name=self.name,
            auth=self.auth,
            owner=self.owner,
            context=context,
            return_raw=return_raw,
        )

        self.id = new_token.id
        self.token = new_token.token
        self.expiration_date = new_token.expiration_date

        return self


@dataclass
class DomoAccessTokens(DomoManager):
    auth: DomoAuth = field(repr=False)

    domo_access_tokens: list[DomoAccessToken] = field(default_factory=list)

    async def get(
        self,
        return_raw: bool = False,
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

        res = await access_token_routes.get_access_tokens(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        return await dmce.gather_with_concurrency(
            *[
                DomoAccessToken.get_by_id(
                    id=obj["id"],
                    auth=self.auth,
                    context=context,
                )
                for obj in res.response
            ],
            n=10,
        )

    async def generate(
        self,
        duration_in_days: int,
        token_name: str,
        owner,  # DomoUser
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop: int = 2,
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

        domo_access_token = await DomoAccessToken.generate(
            owner=owner,
            token_name=token_name,
            duration_in_days=duration_in_days,
            auth=self.auth,
            context=context,
            return_raw=return_raw,
        )

        await self.get(
            context=context,
        )

        return domo_access_token
