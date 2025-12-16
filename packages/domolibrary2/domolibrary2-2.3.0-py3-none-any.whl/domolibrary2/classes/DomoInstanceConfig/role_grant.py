__all__ = ["DomoGrant", "DomoGrants"]

from dataclasses import dataclass, field

import httpx

from domolibrary2.base.entities import DomoBase, DomoManager

from ...auth import DomoAuth as dmda
from ...client.context import RouteContext
from ...routes import grant as grant_routes
from ...utils import DictDot as util_dd


@dataclass
class DomoGrant(DomoBase):
    id: str
    display_group: str | None = None
    title: str | None = None
    depends_on_ls: list[str] | None = None
    description: str | None = None
    role_membership_ls: list[str] | None = field(default=None)

    def __post_init__(self):
        self.id = str(self.id)

    def __eq__(self, other):
        if not isinstance(other, DomoGrant):
            return False

        return self.id == other.id

    @classmethod
    def from_dict(cls, obj):
        dd = obj
        if not isinstance(dd, util_dd.DictDot):
            dd = util_dd.DictDot(obj)

        return cls(
            id=dd.authority,
            display_group=dd.authorityUIGroup,
            depends_on_ls=dd.dependsOnAuthorities,
            title=dd.title,
            description=dd.description,
            role_membership_ls=[str(role) for role in dd.roleIds],
        )


@dataclass
class DomoGrants(DomoManager):
    auth: dmda = field(repr=False)

    grants: list[DomoGrant] | None = field(default=None)

    async def get(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await grant_routes.get_grants(
            auth=self.auth,
            context=context,
        )

        if return_raw or not res.is_success:
            return res

        self.grants = [DomoGrant.from_dict(obj) for obj in res.response]

        return self.grants
