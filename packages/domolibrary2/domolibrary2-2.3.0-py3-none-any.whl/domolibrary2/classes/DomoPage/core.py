"""Core DomoPage entity class and basic operations."""

__all__ = ["DomoPage", "FederatedDomoPage", "DomoPublishPage"]

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, ClassVar

import httpx

from ...auth import DomoAuth
from ...base import exceptions as dmde
from ...base.entities import DomoEntity_w_Lineage, DomoPublishEntity
from ...base.entities_federated import DomoFederatedEntity
from ...client.context import RouteContext
from ...routes import page as page_routes
from ...utils import (
    DictDot as util_dd,
    chunk_execution as dmce,
)
from .. import (
    DomoUser as dmu,
)
from ..subentity.lineage import DomoLineage, register_lineage_type
from . import page_content as dmpg_c
from .pages import DomoPages


@register_lineage_type("DomoPage_Default", lineage_type="PAGE")
@dataclass
class DomoPage_Default(DomoEntity_w_Lineage):
    id: int
    auth: DomoAuth = field(repr=False)
    Lineage: DomoLineage | None = field(repr=False, default=None)

    title: str = None
    top_page_id: int = None
    parent_page_id: int = None
    is_locked: bool = None

    collections: list = field(default_factory=list)

    owners: list = field(default_factory=list)
    cards: list = field(default_factory=list)

    custom_attributes: dict = field(default_factory=dict)

    parent_page: dict = None  # DomoPage
    top_page: dict = None  # DomoPage
    children: list = field(default_factory=list)

    # parent_hierarchy: [dict] = None
    # flat_children: list = None

    layout: dmpg_c.PageLayout = field(default_factory=dict)

    cards: list[Any] = None  # DomoCard
    datasets: list[Any] = None  # DomoDataset

    # Include computed properties in serialization
    __serialize_properties__: ClassVar[tuple] = ("display_url",)

    def __post_init__(self):
        super().__post_init__()
        self.enable_publish_support()

    @property
    def entity_type(self):
        return "PAGE"

    @property
    def entity_name(self) -> str:
        """Get the display name for this page.

        Pages use the 'title' field as their display name.

        Returns:
            Page title, or page ID as fallback
        """
        return str(self.title) if self.title else str(self.id)

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/page/{self.id}"

    async def _get_domo_owners_from_dd(
        self,
        owners: util_dd.DictDot,
        suppress_no_results_error: bool = True,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        debug_num_stacks_to_drop: int = 3,
    ):
        if not owners or len(owners) == 0:
            return []

        from ..DomoGroup import core as dmg

        domo_groups = []
        domo_users = []

        owner_group_ls = [
            owner.id for owner in owners if owner.type == "GROUP" and owner.id
        ]

        if len(owner_group_ls) > 0:
            domo_groups = await dmce.gather_with_concurrency(
                n=60,
                *[
                    dmg.DomoGroup.get_by_id(
                        group_id=group_id,
                        auth=self.auth,
                        debug_api=debug_api,
                        session=session,
                        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                    )
                    for group_id in owner_group_ls
                ],
            )

        owner_user_ls = [
            owner.id for owner in owners if owner.type == "USER" and owner.id
        ]

        if len(owner_user_ls) > 0:
            domo_users_manager = dmu.DomoUsers(auth=self.auth)
            domo_users = await domo_users_manager.search_by_id(
                user_ids=owner_user_ls,
                only_allow_one=False,
                suppress_no_results_error=suppress_no_results_error,
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
    def _from_content_stacks_v3(
        cls,
        page_obj,
        auth: DomoAuth = None,
        owners: list[Any] = None,
    ):
        # from . import DomoCard as dc

        dd = page_obj
        if isinstance(page_obj, dict):
            dd = util_dd.DictDot(page_obj)

        pg = cls(
            id=int(dd.id),
            title=dd.title,
            raw=page_obj,
            parent_page_id=int(dd.page.parentPageId) if dd.page.parentPageId else None,
            collections=dd.collections,
            auth=auth,
        )

        if hasattr(dd, "pageLayoutV4") and dd.pageLayoutV4 is not None:
            pg.layout = dmpg_c.PageLayout.from_dict(dd=dd.pageLayoutV4)

        if owners is not None:
            pg.owners = owners

        return pg

    @classmethod
    async def get_by_id(
        cls,
        page_id: str,
        auth: DomoAuth,
        suppress_no_results_error: bool = True,
        return_raw: bool = False,
        debug_api: bool = False,
        include_layout: bool = False,
        # if True, will drill down to all the Children.  Set to False to prevent calculating children
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        id=None,
        *,
        context: RouteContext | None = None,
    ):
        page_id = page_id or id

        context = RouteContext.build_context(
            context=context,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
        )

        res = await page_routes.get_page_by_id(
            auth=auth,
            page_id=page_id,
            include_layout=include_layout,
            context=context,
        )

        if return_raw:
            return res

        # Fetch owners if present in response
        owners = None
        dd = (
            util_dd.DictDot(res.response)
            if isinstance(res.response, dict)
            else res.response
        )
        if hasattr(dd, "page") and dd.page.owners and len(dd.page.owners) > 0:
            pg_temp = cls(
                id=int(dd.id),
                title=dd.title,
                raw=res.response,
                parent_page_id=(
                    int(dd.page.parentPageId) if dd.page.parentPageId else None
                ),
                collections=dd.collections,
                auth=auth,
            )
            owners = await pg_temp._get_domo_owners_from_dd(
                dd.page.owners,
                suppress_no_results_error=suppress_no_results_error,
                debug_api=debug_api,
                session=session,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            )

        pg = cls._from_content_stacks_v3(
            page_obj=res.response,
            auth=auth,
            owners=owners,
        )

        pg.custom_attributes["parent_page"] = None
        pg.custom_attributes["top_page"] = None

        return pg

    @classmethod
    async def get_entity_by_id(cls, entity_id: str, **kwargs):
        return await cls.get_by_id(page_id=entity_id, **kwargs)

    @classmethod
    def from_dict(cls, **kwargs):
        return cls._from_content_stacks_v3(**kwargs)

    @classmethod
    async def _from_adminsummary(
        cls,
        page_obj,
        auth: DomoAuth,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
    ):
        from .. import DomoCard as dmc

        dd = page_obj

        if isinstance(page_obj, dict):
            dd = util_dd.DictDot(page_obj)

        page_id = int(dd.id or dd.pageId)

        parent_page_id = int(dd.parentPageId) if dd.parentPageId else page_id

        top_page_id = int(dd.topPageId) if dd.topPageId else parent_page_id

        pg = cls(
            id=page_id,
            title=dd.title or dd.pageTitle,
            raw=page_obj,
            parent_page_id=parent_page_id,
            top_page_id=top_page_id,
            collections=dd.collections,
            is_locked=dd.locked,
            auth=auth,
        )

        if dd.page and dd.page.owners and len(dd.page.owners) > 0:
            pg.owners = await pg._get_domo_owners_from_dd(
                dd.page.owners, debug_api=debug_api, session=session
            )

        if dd.cards and len(dd.cards) > 0:
            pg.cards = await dmce.gather_with_concurrency(
                n=60,
                *[
                    dmc.DomoCard.get_by_id(
                        id=card.id, auth=auth, session=session, debug_api=debug_api
                    )
                    for card in dd.cards
                ],
            )

        return pg

    @classmethod
    async def _from_bootstrap(
        cls,
        page_obj,
        auth: DomoAuth = None,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
    ):
        dd = page_obj
        if isinstance(page_obj, dict):
            dd = util_dd.DictDot(page_obj)

        pg = cls(
            id=int(dd.id),
            title=dd.title,
            raw=page_obj,
            auth=auth,
        )

        if isinstance(dd.owners, list) and len(dd.owners) > 0:
            pg.owners = await pg._get_domo_owners_from_dd(
                dd.owners, debug_api=debug_api, session=session
            )

        if isinstance(dd.children, list) and len(dd.children) > 0:
            pg.children = await dmce.gather_with_concurrency(
                n=60,
                *[
                    cls._from_bootstrap(
                        page_obj=child_dd,
                        auth=auth,
                        debug_api=debug_api,
                        session=session,
                    )
                    for child_dd in dd.children
                    if child_dd.type == "page"
                ],
            )

            [print(other_dd) for other_dd in dd.children if other_dd.type != "page"]

        return pg

    async def get_parents(self):
        if not self.parent_page_id:
            return self.custom_attributes

        if not self.top_page_id:
            page_as = next(
                pg
                for pg in (await DomoPages(auth=self.auth).get(search_title=self.id))
                if pg.id == self.id
            )
            self.top_page_id = page_as.top_page_id
            self.top_page = page_as

        if self.id == self.top_page_id:
            self.custom_attributes["top_page"] = self.top_page

        parent_page_as = next(
            pg
            for pg in (
                await DomoPages(auth=self.auth).get(search_title=self.parent_page_id)
            )
            if pg.id == self.parent_page_id
        )

        if self.parent_page_id == parent_page_as.id:
            self.parent_page = parent_page_as

        self.custom_attributes["parent_page"] = parent_page_as

        if not self.custom_attributes.get("path"):
            self.custom_attributes["path"] = []

        self.custom_attributes["path"].append(parent_page_as)

        if self.id != self.top_page_id:
            await self.get_parents(page=parent_page_as)

        return self.custom_attributes

    async def get_children(self, is_suppress_errors: bool = False):
        async def _get_children_recur(parent_page, is_suppress_errors: bool = False):
            parent_page.children = parent_page.children or []

            try:
                child_pages = await DomoPages(auth=parent_page.auth).get(
                    parent_page_id=parent_page.id,
                    # is_suppress_errors=is_suppress_errors
                )

                parent_page.children = [
                    child
                    for child in child_pages
                    if child is not None and child.parent_page_id == parent_page.id
                ]

                await dmce.gather_with_concurrency(
                    n=10,
                    *[
                        _get_children_recur(
                            parent_page=cp,
                            is_suppress_errors=is_suppress_errors,
                        )
                        for cp in parent_page.children
                    ],
                )

                return self.children

            except dmde.DomoError as e:
                print(
                    f"cannot access child page -- https://{parent_page.auth.domo_instance}.domo.com/page/{parent_page.id} -- is it shared\nwith you?"
                )
                if not is_suppress_errors:
                    raise e from e

        self.children = await _get_children_recur(
            parent_page=self,
            is_suppress_errors=is_suppress_errors,
        )

        return self.children

    def flatten_children(self, path=None, hierarchy=0, results=None):
        results = results or []

        path = f"{path} > {self.title}" if path else self.title

        results.append({"hierarchy": hierarchy, "path": path, "page": self})

        if self.children:
            [
                child.flatten_children(path, hierarchy + 1, results)
                for child in self.children
            ]

        return results


@register_lineage_type("FederatedDomoPage", lineage_type="PAGE")
@dataclass
class FederatedDomoPage(DomoPage_Default, DomoFederatedEntity):
    """Federated page seen in a parent instance; points to a child instance's native page."""

    @property
    def entity_type(self):
        return "PAGE"

    async def get_federated_parent(
        self,
        parent_auth: None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        from ...classes.DomoEverywhere import DomoEverywhere

        domo_everywhere = DomoEverywhere(
            auth=self.auth,
        )

        await domo_everywhere.get_subscriptions()

        await dmce.gather_with_concurrency(
            *[
                sub.get_parent_publication(
                    parent_auth_retrieval_fn=parent_auth_retrieval_fn,  # type: ignore
                    parent_auth=parent_auth,  # type: ignore
                )
                for sub in domo_everywhere.subscriptions
            ],
            n=20,
        )

        all = await dmce.gather_with_concurrency(
            *[
                sub.parent_publication.get_publication_entity_by_subscriber_entity(
                    subscriber_domain=sub.subscriber_domain,
                    subscriber=self,
                )
                for sub in domo_everywhere.subscriptions
            ],
            n=20,
        )

        self.parent_entity = next(
            (entity for entity in all if entity is not None), None
        )
        if not self.parent_entity:
            from ...base.exceptions import ClassError

            entity_name = getattr(self, "title", "N/A")
            subscriber_instance = getattr(self.auth, "domo_instance", "unknown")
            publisher_instance = (
                getattr(parent_auth, "domo_instance", "unknown")
                if parent_auth
                else "unknown"
            )

            raise ClassError(
                cls_instance=self,
                message=(
                    f"Unable to retrieve federated parent entity for page '{entity_name}' (ID: {self.id}). "
                    f"The most likely cause is that the publisher entity has not been shared with the user "
                    f"authenticated on the subscriber instance '{subscriber_instance}'. "
                    f"Please verify that:\n"
                    f"  1. The entity is published from publisher instance '{publisher_instance}'\n"
                    f"  2. The entity is included in a publication that is subscribed to by '{subscriber_instance}'\n"
                    f"  3. The user authenticated with '{subscriber_instance}' has access to the published entity"
                ),
            )

        return self.parent_entity

    @classmethod
    async def get_by_id(
        cls,
        page_id: str,
        auth: DomoAuth,
        suppress_no_results_error: bool = True,
        return_raw: bool = False,
        debug_api: bool = False,
        include_layout: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        id=None,
        check_if_published: bool = True,
    ):
        """Retrieve federated page metadata"""
        # Use parent implementation to avoid code duplication
        return await super().get_by_id(
            page_id=page_id,
            auth=auth,
            suppress_no_results_error=suppress_no_results_error,
            return_raw=return_raw,
            debug_api=debug_api,
            include_layout=include_layout,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            session=session,
            id=id,
        )


@register_lineage_type("DomoPublishPage", lineage_type="PAGE")
@dataclass
class DomoPublishPage(FederatedDomoPage):
    """Published page that supports publish/subscribe across instances"""

    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        return await cls.get_by_id(auth=auth, page_id=entity_id, **kwargs)

    async def get_subscription(
        self,
        parent_auth_retrieval_fn: Callable | None = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        max_subscriptions_to_check: int | None = None,
    ):
        """Retrieve subscription information for this page via PublishResolver.

        Uses the shared resolver to locate the subscription where this page
        appears as PAGE content in subscriber associations.
        """
        helper = self.enable_publish_support()
        return await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            session=session,
            debug_api=debug_api,
            max_subscriptions_to_check=max_subscriptions_to_check,
            entity_type="PAGE",
            entity_id=str(self.id),
        )

    async def get_parent_publication(
        self,
        parent_auth: DomoAuth | None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Get parent publication and publisher page from subscription metadata"""
        helper = self.enable_publish_support()

        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="PAGE",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)

        return await helper.get_parent_publication(parent_auth=publisher_auth)

    async def get_parent_content_details(
        self,
        parent_auth: DomoAuth | None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Retrieve the parent page from the publisher instance.

        Args:
            parent_auth: Authentication for publisher instance
            parent_auth_retrieval_fn: Function to retrieve publisher auth

        Returns:
            DomoPage instance from publisher
        """
        helper = self.enable_publish_support()

        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="PAGE",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)
        await helper.get_parent_publication(parent_auth=publisher_auth)

        return await helper.get_publisher_entity(parent_auth=publisher_auth)


# Factory function to determine correct page class
class DomoPage:
    """Factory class that returns the appropriate page type based on federation status"""

    @classmethod
    async def get_by_id(
        cls,
        page_id: str,
        auth: DomoAuth,
        suppress_no_results_error: bool = True,
        return_raw: bool = False,
        debug_api: bool = False,
        include_layout: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        id=None,
        check_if_published: bool = False,
        parent_auth_retrieval_fn: Callable | None = None,
        max_subscriptions_to_check: int | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Retrieve page and return appropriate type (DomoPage_Default, FederatedDomoPage, or DomoPublishPage).

        Args:
            page_id: Page identifier
            auth: Authentication object
            suppress_no_results_error: Suppress errors when no results found
            return_raw: Return raw API response
            debug_api: Enable debug logging
            include_layout: Include page layout in response
            debug_num_stacks_to_drop: Stack frames to drop in debug output
            session: Optional HTTP session
            id: Alternative parameter for page_id
            check_if_published: Check if page is published (requires subscription check)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoPage_Default, FederatedDomoPage, or DomoPublishPage instance
        """
        page_id = page_id or id

        context = RouteContext.build_context(
            context=context,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=cls.__name__,
            **context_kwargs,
        )

        # Get page data
        res = await page_routes.get_page_by_id(
            auth=auth,
            page_id=page_id,
            include_layout=include_layout,
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
                    "for pages."
                )
            probe = DomoPublishEntity.from_probe(
                auth=auth,
                entity_id=str(page_id),
                entity_type="PAGE",
            )
            is_published = await probe.check_if_published(
                retrieve_parent_auth_fn=parent_auth_retrieval_fn,
                entity_type="PAGE",
                entity_id=str(page_id),
                session=session,
                debug_api=debug_api,
                max_subscriptions_to_check=max_subscriptions_to_check,
            )
            if is_published:
                subscription = probe.subscription

        # Fetch owners if present in response
        owners = None
        dd = (
            util_dd.DictDot(res.response)
            if isinstance(res.response, dict)
            else res.response
        )
        if hasattr(dd, "page") and dd.page.owners and len(dd.page.owners) > 0:
            pg_temp = DomoPage_Default(
                id=int(dd.id),
                title=dd.title,
                raw=res.response,
                parent_page_id=(
                    int(dd.page.parentPageId) if dd.page.parentPageId else None
                ),
                collections=dd.collections,
                auth=auth,
            )
            owners = await pg_temp._get_domo_owners_from_dd(
                dd.page.owners,
                suppress_no_results_error=suppress_no_results_error,
                debug_api=debug_api,
                session=session,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            )

        # Create appropriate page instance
        page_cls = DomoPublishPage if is_published else DomoPage_Default
        pg = await page_cls._from_content_stacks_v3(
            page_obj=res.response,
            auth=auth,
            owners=owners,
        )

        if is_published and subscription:
            helper = pg.enable_publish_support()
            helper.hydrate_from_existing(
                subscription=subscription,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                content_type="PAGE",
                entity_id=str(page_id),
            )

        pg.custom_attributes["parent_page"] = None
        pg.custom_attributes["top_page"] = None

        return pg
