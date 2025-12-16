from __future__ import annotations

import datetime as dt
import inspect
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base import (
    DomoEntity_w_Lineage,
    DomoEnumMixin,
    exceptions as dmde,
)
from ...client.context import RouteContext
from ...routes import publish as publish_routes
from ...utils import chunk_execution as dmce
from ..subentity import lineage as dmdl
from ..subentity.lineage import register_lineage_type

__all__ = [
    "DomoPublication_Content_Enum",
    "DomoPublication_Content",
    "DomoPublication_UnexpectedContentType",
    "DomoPublication",
    "DomoSubscription_NoParentAuth",
    "DomoSubscription_NoParent",
    "DomoSubscription",
    "DomoEverywhere",
]


class DomoSubscription_NoParentAuth(dmde.ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            cls_instance=cls_instance,
            entity_id="subscription_id",
            message="must pass parent_auth or parent_auth_retrieval_fn which returns an instance of auth given self",
        )


class DomoSubscription_NoParent(dmde.ClassError):
    def __init__(self, cls_instance):
        super().__init__(
            cls_instance=cls_instance,
            entity_id="subscription_id",
            message="unable to retrieve parent publication",
        )


class DomoPublication_Content_Enum(DomoEnumMixin, Enum):
    from .. import (
        DomoAppStudio as dmas,
        DomoCard as dmac,
        DomoDataset as dmds,
        DomoPage as dmpg,
    )

    CARD = dmac.DomoCard
    DATASET = dmds.DomoDataset
    DATA_APP = dmas.DomoAppStudio
    PAGE = dmpg.DomoPage


@dataclass
class DomoPublication_Content:
    auth: DomoAuth

    content_id: str
    entity_type: str
    entity_id: str
    entity_domain: str
    is_v2: bool
    is_direct_content: bool

    created_dt: dt.datetime
    updated_dt: dt.datetime = None

    subscriber_content_id: str = None
    subscriber_insance: str = None

    entity: Any = field(repr=False, default=None)
    parent: Any = field(repr=False, default=None)

    """the publication content is the content from the publisher instance that is being distributed to subscribers"""

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any], parent: Any = None):
        entity_type = obj.get("content").get("type")
        return cls(
            auth=auth,
            content_id=obj["id"],
            entity_id=obj.get("content").get("domoObjectId"),
            entity_domain=obj.get("content").get("domain"),
            is_v2=obj.get("isV2"),
            created_dt=(
                dt.datetime.fromtimestamp(obj["created"] / 1000)
                if obj["created"]
                else None
            ),
            updated_dt=(
                dt.datetime.fromtimestamp(obj.get("content").get("updated") / 1000)
                if obj.get("content").get("updated")
                else None
            ),
            is_direct_content=obj.get("useDirectContent"),
            parent=parent,
            entity_type=entity_type,
            entity=DomoPublication_Content_Enum[entity_type].value,
        )

    async def get_entity(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """get the entity from the publication content"""
        if not self.entity:
            self.entity = DomoPublication_Content_Enum[self.entity_type].value

        base_context = RouteContext.build_context(
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        self.entity = await self.entity.get_entity_by_id(
            auth=self.auth,
            entity_id=self.entity_id,
            context=context,
        )

        return self.entity

    def to_api_json(self) -> dict[str, Any]:
        return {
            "domain": self.entity_domain,
            "domoObjectId": self.entity_id,
            "customerId": self.entity_domain,
            "type": self.entity_type,
        }


class DomoPublication_UnexpectedContentType(dmde.ClassError):
    def __init__(self, cls_instance, content_type):
        super().__init__(
            cls_instance=cls_instance,
            message=f"DomoPublication_Instantiation: Unexpected content type {content_type}",
        )


@register_lineage_type("DomoPublication", lineage_type="PUBLICATION")
@dataclass
class DomoPublication(DomoEntity_w_Lineage):
    name: str
    description: str
    is_v2: bool
    created_dt: dt.datetime

    updated_dt: dt.datetime = None

    subscriptions: list[DomoSubscription] = None

    content: list[DomoPublication_Content] = None

    @property
    def entity_type(self):
        return "PUBLICATION"

    def __post_init__(self):
        self.Lineage = dmdl.DomoLineage_Publication.from_parent(
            parent=self, auth=self.auth
        )

    def _generate_subscriptions(self, subscription_authorizations_ls, auth):
        self.subscriptions = [
            DomoSubscription.from_dict(auth=auth, obj=sub, parent_publication=self)
            for sub in subscription_authorizations_ls
        ]

    def _generate_content(self, children_ls):
        self.content = [
            DomoPublication_Content.from_dict(auth=self.auth, obj=child, parent=self)
            for child in children_ls
        ]

        return self.content

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        domo_pub = cls(
            id=obj["id"],
            name=obj["name"],
            description=obj["description"],
            created_dt=(
                dt.datetime.fromtimestamp(obj["created"] / 1000)
                if obj["created"]
                else None
            ),
            updated_dt=(
                dt.datetime.fromtimestamp(obj.get("content").get("updated") / 1000)
                if obj.get("content").get("updated")
                else None
            ),
            is_v2=obj["isV2"],
            auth=auth,
            raw=obj,
        )

        if (
            obj.get("subscriptionAuthorizations")
            and len(obj.get("subscriptionAuthorizations")) > 0
        ):
            domo_pub._generate_subscriptions(
                subscription_authorizations_ls=obj["subscriptionAuthorizations"],
                auth=auth,
            )

        if obj.get("children") and len(obj.get("children")) > 0:
            domo_pub._generate_content(obj["children"])

        return domo_pub

    @classmethod
    async def get_by_id(
        cls,
        publication_id,
        auth: DomoAuth,
        return_raw: bool = False,
        timeout=10,
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
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

        res = await publish_routes.get_publication_by_id(
            auth=auth,
            publication_id=publication_id,
            timeout=timeout,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    @classmethod
    async def get_entity_by_id(cls, entity_id, **kwargs):
        return await cls.get_by_id(publication_id=entity_id, **kwargs)

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/domo-everywhere/publications/details?id={self.id}"

    async def get_content_details(
        self,
        subscriber_domain: str,  # must include .domo.com
        debug_api: bool = False,
        debug_num_stacks_to_drop=2,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        if not subscriber_domain.lower().endswith(".domo.com"):
            subscriber_domain = f"{subscriber_domain}.domo.com"

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.get_subscriber_content_details(
            auth=self.auth,
            publication_id=self.id,
            subscriber_instance=subscriber_domain,
            context=context,
        )

        publication_content = self.content

        for content in publication_content:
            subscriber_obj = next(
                (
                    subscriber_obj
                    for subscriber_obj in res.response
                    if subscriber_obj["publisherObjectId"] == content.entity_id
                    and subscriber_obj["contentType"] == content.entity_type
                ),
                None,
            )
            if subscriber_obj is not None:
                content.subscriber_content_id = subscriber_obj["subscriberObjectId"]
                content.subscriber_insance = subscriber_obj["subscriberDomain"]

        self.content = publication_content

        return res

    async def get_publication_entity_by_subscriber_entity(
        self,
        subscriber_domain: str,
        subscriber: Any,  # DomoPage, DomoCard, DomoDataset
        _is_suppress_errors: bool = False,  # Unused but kept for API compatibility
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> Any:  # DomoCard, DomoDataset, DomoPage
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await self.get_content_details(
            subscriber_domain=subscriber_domain,
            context=context,
        )

        obj = next(
            (row for row in res.response if row["subscriberObjectId"] == subscriber.id),
            None,
        )

        if not obj:
            return None

        # Resolve publisher entity. If the provided 'subscriber' is a FederatedDomoDataset
        # we should fetch the publisher-side dataset as the default dataset class (not the federated wrapper).
        publisher_obj_id = obj["publisherObjectId"]

        # Lazy import to avoid circular imports
        if subscriber.__class__.__name__ == "FederatedDomoDataset":
            try:
                from ..DomoDataset.core import DomoDataset as PublisherDataset

                return await PublisherDataset.get_by_id(
                    dataset_id=publisher_obj_id,
                    auth=self.auth,
                    is_use_default_dataset_class=True,
                )
            except dmde.DomoError:
                # Fall back to calling the subscriber's resolver if publisher fetch fails
                return await subscriber.get_entity_by_id(
                    entity_id=publisher_obj_id, auth=self.auth
                )

        # Default behavior: delegate to subscriber's get_entity_by_id
        return await subscriber.get_entity_by_id(
            entity_id=publisher_obj_id, auth=self.auth
        )

    @classmethod
    async def create_publication(
        cls,
        auth: DomoAuth,
        name: str,
        content_ls: list[DomoPublication_Content],
        subscription_ls: list[DomoSubscription],
        unique_id: str = None,
        description: str = None,
        debug_api: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        if not isinstance(subscription_ls, list):
            subscription_ls = [subscription_ls]

        domain_ls = []
        content_json_ls = []
        for sub in subscription_ls:
            domain_ls.append(sub.subscriber_domain)
        for content_item in content_ls:
            content_json_ls.append(content_item.to_api_json())

        unique_id = unique_id or str(uuid.uuid4())

        body = publish_routes.generate_publish_body(
            url=f"{auth.domo_instance}.domo.com",
            sub_domain_ls=domain_ls,
            content_ls=content_json_ls,
            name=name,
            unique_id=unique_id,
            description=description or "",
            is_new=True,
        )

        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.create_publish_job(
            auth=auth,
            body=body,
            context=context,
        )

        return cls.from_dict(auth=auth, obj=res.response)

    async def revoke_subscription_auth(
        self,
        auth: DomoAuth = None,
        subscription_id: str = None,
        subscription: DomoSubscription = None,
        _debug_api: bool = False,  # Unused but kept for API compatibility
        _session: httpx.AsyncClient = None,  # Unused but kept for API compatibility
        _debug_num_stacks_to_drop: int = 2,  # Unused but kept for API compatibility
    ):
        # Note: This function may not have a direct route implementation
        # It would need to be implemented based on the available API endpoints
        auth = auth or self.auth
        subscription_id = subscription_id or subscription.id

        # This is a placeholder implementation - would need actual API route
        raise NotImplementedError("revoke_subscription_auth route not yet implemented")

    async def update_publication(
        self,
        auth: DomoAuth = None,
        content_ls: list[DomoPublication_Content] = None,
        description: str = None,
        name: str = None,
        subscription_ls: list[DomoSubscription] = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = auth or self.auth

        # Use the actual available route
        if not isinstance(subscription_ls, list) and subscription_ls:
            subscription_ls = [subscription_ls]

        domain_ls = []
        content_json_ls = []

        if subscription_ls:
            for sub in subscription_ls:
                domain_ls.append(sub.subscriber_domain)

        if content_ls:
            for content_item in content_ls:
                content_json_ls.append(content_item.to_api_json())

        body = publish_routes.generate_publish_body(
            url=f"{auth.domo_instance}.domo.com",
            sub_domain_ls=domain_ls,
            content_ls=content_json_ls,
            name=name or self.name,
            unique_id=self.id,
            description=description or self.description,
            is_new=False,
        )

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.update_publish_job(
            auth=auth,
            publication_id=self.id,
            body=body,
            context=context,
        )

        return res


@register_lineage_type("DomoSubscription", lineage_type="SUBSCRIPTION")
@dataclass
class DomoSubscription(DomoEntity_w_Lineage):
    """the subscriber represents a location a publication is sent to"""

    id: str
    publication_id: str
    subscriber_domain: str
    publisher_domain: str
    parent_publication: DomoPublication = field(repr=False, default=None)
    created_dt: dt.datetime | None = None

    def __post_init__(self):
        super().__post_init__()

    @classmethod
    def from_dict(
        cls, auth: DomoAuth, obj: dict[str, Any], parent_publication: Any = None
    ):
        return cls(
            auth=auth,
            id=obj.get("id") or obj.get("subscriptionId"),
            publication_id=obj["publicationId"],
            subscriber_domain=obj.get("domain") or obj.get("subscriberDomain"),
            publisher_domain=obj.get("publisherDomain"),
            created_dt=(
                (dt.datetime.fromtimestamp(obj.get("created") / 1000))
                if obj.get("created")
                else None
            ),
            raw=obj,
            parent_publication=parent_publication,
        )

    @property
    def entity_type(self):
        return "SUBSCRIPTION"

    @property
    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/admin/domo-everywhere/subscriptions"

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        subscription_id: str,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.get_subscription_by_id(
            auth=auth,
            subscription_id=subscription_id,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    @classmethod
    async def get_entity_by_id(cls, entity_id: str, auth: DomoAuth, **kwargs):
        return await cls.get_by_id(subscription_id=entity_id, auth=auth, **kwargs)

    async def get_parent_publication(
        self,
        parent_auth: DomoAuth = None,
        parent_auth_retrieval_fn: Callable = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        if not parent_auth and parent_auth_retrieval_fn:
            auth_or_coro = parent_auth_retrieval_fn(self.publisher_domain)
            if inspect.isawaitable(auth_or_coro):
                parent_auth = await auth_or_coro  # type: ignore[assignment]
            else:
                parent_auth = auth_or_coro

        if not parent_auth:
            raise DomoSubscription_NoParentAuth(self)

        self.parent_publication = await DomoPublication.get_by_id(
            publication_id=self.publication_id,
            auth=parent_auth,
            context=context,
        )

        return self.parent_publication

    async def get_content_details(
        self,
        parent_auth: DomoAuth = None,
        parent_auth_retrieval_fn: Callable = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        if not self.parent_publication:
            await self.get_parent_publication(
                parent_auth=parent_auth,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                context=context,
            )

        if not self.parent_publication:
            raise DomoSubscription_NoParent(self)

        publication_content = self.parent_publication.content

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.get_subscriber_content_details(
            auth=self.parent_publication.auth,
            publication_id=self.publication_id,
            subscriber_instance=self.subscriber_domain,
            context=context,
        )

        for content in publication_content:
            subscriber_obj = next(
                (
                    subscriber_obj
                    for subscriber_obj in res.response
                    if subscriber_obj["publisherObjectId"] == content.entity_id
                    and subscriber_obj["contentType"] == content.entity_type
                ),
                None,
            )
            if subscriber_obj is not None:
                content.subscriber_content_id = subscriber_obj["subscriberObjectId"]
                content.subscriber_insance = subscriber_obj["subscriberDomain"]

        # Return the updated publication content
        return publication_content


@dataclass
class DomoEverywhere:
    auth: DomoAuth = field(repr=False)

    publications: list[DomoPublication] = field(default=None)

    subscriptions: list[DomoSubscription] = field(default=None)

    invitations: list[dict[str, Any]] = field(default=None)

    async def get_publications(
        self,
        search_term: str = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.search_publications(
            auth=self.auth,
            search_term=search_term,
            context=context,
        )

        if return_raw:
            return res

        self.publications = await dmce.gather_with_concurrency(
            n=60,
            *[
                DomoPublication.get_by_id(
                    publication_id=obj.get("id"), auth=self.auth, context=context
                )
                for obj in res.response
            ],
        )
        return self.publications

    async def search_publications(
        self,
        search_term: str = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await self.get_publications(
            search_term=search_term,
            return_raw=return_raw,
            context=context,
        )

        return res

    async def get_subscriptions(
        self,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """get instances subscription summaries"""

        self.subscriptions = []

        base_context = RouteContext.build_context(
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.get_subscription_summaries(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        for sub in res.response:
            domo_sub = DomoSubscription.from_dict(auth=self.auth, obj=sub)

            if sub in self.subscriptions:
                continue
            self.subscriptions.append(domo_sub)

        return self.subscriptions

    async def get_subscription_invitations(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.get_subscription_invitations(
            auth=self.auth,
            context=context,
        )

        self.invitations = res.response

        return res

    async def accept_invite_by_id(
        self,
        subscription_id: str,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        base_context = RouteContext.build_context(
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await publish_routes.accept_invite_by_id(
            auth=self.auth,
            subscription_id=subscription_id,
            context=context,
        )

        if res.status == 200:
            return res.response
        else:
            return None
