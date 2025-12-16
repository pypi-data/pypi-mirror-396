__all__ = ["DomoAppStudio", "DomoAppStudios"]


from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..auth import DomoAuth
from ..base.entities import DomoEntity_w_Lineage, DomoPublishEntity
from ..client.context import RouteContext
from ..routes import appstudio as appstudio_routes
from ..utils import (
    DictDot as util_dd,
    chunk_execution as dmce,
)
from . import DomoUser as dmdu
from .subentity.lineage import DomoLineage, register_lineage_type


@register_lineage_type("DomoAppStudio", lineage_type="DATA_APP")
@dataclass
class DomoAppStudio(DomoEntity_w_Lineage):
    id: int
    auth: DomoAuth = field(repr=False)

    title: str = None
    is_locked: bool = None

    owners: list = field(default_factory=list)

    custom_attributes: dict = field(default_factory=dict)

    Lineage: DomoLineage = None

    def __post_init__(self):
        super().__post_init__()
        self.enable_publish_support()

    @classmethod
    async def _from_content_stacks_v3(cls, page_obj, auth: DomoAuth = None):
        dd = page_obj
        if isinstance(page_obj, dict):
            dd = util_dd.DictDot(page_obj)

        aps = cls(
            id=int(dd.dataAppId),
            title=dd.title or dd.Title,
            is_locked=dd.locked,
            auth=auth,
            raw=page_obj,
        )

        if dd.owners and len(dd.owners) > 0:
            aps.owners = await aps._get_domo_owners_from_dd(dd.owners)

        return aps

    @classmethod
    async def get_by_id(
        cls,
        appstudio_id: str,
        auth: DomoAuth,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop: int = 2,
        check_if_published: bool = False,
        parent_auth_retrieval_fn: Callable | None = None,
        max_subscriptions_to_check: int | None = None,
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

        res = await appstudio_routes.get_appstudio_by_id(
            auth=auth,
            appstudio_id=appstudio_id,
            context=context,
        )

        if return_raw:
            return res

        is_published = False
        subscription = None
        if check_if_published:
            if not parent_auth_retrieval_fn:
                raise ValueError(
                    "parent_auth_retrieval_fn is required to determine publish state "
                    "for AppStudio apps."
                )
            probe = DomoPublishEntity.from_probe(
                auth=auth,
                entity_id=str(appstudio_id),
                entity_type="DATA_APP",
            )
            is_published = await probe.check_if_published(
                retrieve_parent_auth_fn=parent_auth_retrieval_fn,
                entity_type="DATA_APP",
                entity_id=str(appstudio_id),
                session=session,
                debug_api=debug_api,
                max_subscriptions_to_check=max_subscriptions_to_check,
            )
            if is_published:
                subscription = probe.subscription

        target_cls = cls
        if is_published:
            from .DomoAppStudio_publish import DomoPublishAppStudio as PublishApp

            target_cls = PublishApp

        app = await target_cls._from_content_stacks_v3(
            page_obj=res.response,
            auth=auth,
        )

        if is_published and subscription:
            helper = app.enable_publish_support()
            helper.hydrate_from_existing(
                subscription=subscription,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                content_type="DATA_APP",
                entity_id=str(appstudio_id),
            )

        return app

    @classmethod
    async def get_entity_by_id(cls, entity_id: str, auth: DomoAuth, **kwargs):
        return await cls.get_by_id(auth=auth, appstudio_id=entity_id, **kwargs)

    @property
    def entity_type(self):
        return "DATA_APP"

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/app-studio/{self.id}"

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        """Create a DomoAppStudio instance from a dictionary representation."""
        return cls._from_content_stacks_v3(page_obj=obj, auth=auth)

    async def _get_domo_owners_from_dd(self, owners: util_dd.DictDot):
        if not owners or len(owners) == 0:
            return []

        from .DomoGroup import core as dmg

        domo_groups = []
        domo_users = []

        owner_group_ls = [
            owner.id for owner in owners if owner.type == "GROUP" and owner.id
        ]

        if len(owner_group_ls) > 0:
            domo_groups = await dmce.gather_with_concurrency(
                n=60,
                *[
                    dmg.DomoGroup.get_by_id(group_id=group_id, auth=self.auth)
                    for group_id in owner_group_ls
                ],
            )

        owner_user_ls = [
            owner.id for owner in owners if owner.type == "USER" and owner.id
        ]

        if len(owner_user_ls) > 0:
            domo_users_manager = dmdu.DomoUsers(auth=self.auth)
            domo_users = await domo_users_manager.search_by_id(
                user_ids=owner_user_ls,
                only_allow_one=False,
                suppress_no_results_error=True,
            )

        owner_ce = (domo_groups or []) + (domo_users or [])

        res = []
        for owner in owner_ce:
            if isinstance(owner, list):
                [res.append(member) for member in owner]
            else:
                res.append(owner)

        return res

    @classmethod
    async def _from_adminsummary(cls, appstudio_obj, auth: DomoAuth):
        dd = appstudio_obj

        if isinstance(appstudio_obj, dict):
            dd = util_dd.DictDot(appstudio_obj)

        aps = cls(
            id=int(dd.id or dd.dataAppId),
            title=dd.title or dd.Title,
            is_locked=dd.locked,
            auth=auth,
            raw=appstudio_obj,
        )

        if dd.owners and len(dd.owners) > 0:
            aps.owners = await aps._get_domo_owners_from_dd(dd.owners)

        return aps

    async def get_accesslist(
        self,
        auth: DomoAuth = None,
        return_raw: bool = False,
        debug_api: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = auth or self.auth

        base_context = self._build_route_context(
            debug_api=debug_api,
            debug_num_stacks_to_drop=2,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await appstudio_routes.get_appstudio_access(
            auth=auth,
            appstudio_id=self.id,
            context=context,
        )

        if return_raw:
            return res

        if not res.is_success:
            raise Exception("error getting access list")

        from .DomoGroup import core as dmg

        s = {
            # "explicit_shared_user_count": res.response.get("explicitSharedUserCount"),
            "total_user_count": res.response.get("totalUserCount"),
        }

        user_ls = res.response.get("users", None)
        domo_users = []
        if user_ls and isinstance(user_ls, list) and len(user_ls) > 0:
            domo_users_manager = dmdu.DomoUsers(auth=auth)
            domo_users = await domo_users_manager.search_by_id(
                user_ids=[user.get("id") for user in user_ls],
                only_allow_one=False,
                suppress_no_results_error=True,
            )

        group_ls = res.response.get("groups", None)
        domo_groups = []
        if group_ls and isinstance(group_ls, list) and len(group_ls) > 0:
            domo_groups = await dmce.gather_with_concurrency(
                n=60,
                *[
                    dmg.DomoGroup.get_by_id(group_id=group.get("id"), auth=auth)
                    for group in group_ls
                ],
            )

        return {
            **s,
            "domo_users": domo_users,
            "domo_groups": domo_groups,
        }

    async def share(
        self,
        auth: DomoAuth = None,
        domo_users: list = None,  # DomoUsers to share page with,
        domo_groups: list = None,  # DomoGroups to share page with
        message: str = None,  # message for automated email
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        if domo_groups:
            domo_groups = (
                domo_groups if isinstance(domo_groups, list) else [domo_groups]
            )
        if domo_users:
            domo_users = domo_users if isinstance(domo_users, list) else [domo_users]

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await appstudio_routes.share(
            auth=auth or self.auth,
            appstudio_ids=[self.id],
            group_ids=[group.id for group in domo_groups] if domo_groups else None,
            user_ids=[user.id for user in domo_users] if domo_users else None,
            message=message,
            context=context,
        )

        return res

    @classmethod
    async def add_appstudio_owner(
        cls,
        auth: DomoAuth,
        appstudio_id_ls: list[int],  # AppStudio IDs to be updated by owner,
        group_id_ls: list[int],  # DomoGroup IDs to share page with
        user_id_ls: list[int],  # DomoUser IDs to share page with
        note: str = None,  # message for automated email
        send_email: bool = False,  # send or not email to the new owners
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await appstudio_routes.add_page_owner(
            auth=auth,
            appstudio_id_ls=appstudio_id_ls,
            group_id_ls=group_id_ls,
            user_id_ls=user_id_ls,
            note=note,
            send_email=send_email,
            context=context,
        )

        return res


@dataclass
class DomoAppStudios:
    @classmethod
    async def get_appstudios(
        cls,
        auth=DomoAuth,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_loop: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """use admin_summary to retrieve all appstudios in an instance -- regardless of user access
        NOTE: some appstudios APIs will not return results if appstudio access isn't explicitly shared
        """
        is_close_session = False if session else True

        session = session or httpx.AsyncClient()

        try:
            base_context = RouteContext.build_context(
                session=session,
                debug_api=debug_api,
                parent_class=cls.__name__,
                **context_kwargs,
            )
            context = RouteContext.build_context(context=context or base_context)

            res = await appstudio_routes.get_appstudios_adminsummary(
                auth=auth, debug_loop=debug_loop, context=context
            )

            if return_raw:
                return res

            if not res.is_success:
                raise Exception("unable to retrieve appstudios")

            return await dmce.gather_with_concurrency(
                n=60,
                *[
                    DomoAppStudio._from_adminsummary(page_obj, auth=auth)
                    for page_obj in res.response
                ],
            )

        finally:
            if is_close_session:
                await session.aclose()
