"""Default DomoCard implementation"""

from __future__ import annotations

__all__ = ["DomoCard_Default", "CardDatasets", "Card_DownloadSourceCodeError"]

import json
import os
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity_w_Lineage, DomoManager, DomoPublishEntity
from ...base.exceptions import ClassError, DomoError
from ...client.context import RouteContext
from ...routes import card as card_routes
from ...utils import (
    chunk_execution as dmce,
    files as dmfi,
)
from ...utils.logging import (
    DomoEntityObjectProcessor,
    LogDecoratorConfig,
    log_call,
)
from ..DomoGroup.core import (
    DomoGroup,
    DomoGroup as dmgr,
)
from ..DomoUser import DomoUser
from ..subentity.lineage import DomoLineage, register_lineage_type


@register_lineage_type("DomoCard_Default", lineage_type="CARD")
@dataclass
class DomoCard_Default(DomoEntity_w_Lineage):
    """Base DomoCard implementation with core functionality"""

    id: str
    auth: DomoAuth = field(repr=False)
    Lineage: DomoLineage | None = field(repr=False, default=None)
    Datasets: CardDatasets | None = field(repr=False, default=None)

    title: str | None = None
    description: str | None = None
    type: str | None = None
    urn: str | None = None
    chart_type: str | None = None
    dataset_id: str | None = None

    datastore_id: str | None = None

    domo_collections: list[Any] = field(default_factory=list)
    domo_source_code: Any = None

    certification: dict | None = None
    owners: list[Any] = field(default_factory=list)

    @property
    def datasets(self) -> list[Any]:  # DomoDataset
        """Legacy property access - prefer using Datasets.get() for async operations"""
        # This property can't be async, so it returns empty list if not already fetched
        # Users should call await card.Datasets.get() to populate datasets
        return []

    @property
    def entity_type(self):
        return "CARD"

    @property
    def entity_name(self) -> str:
        """Get the display name for this card.

        Cards use the 'title' field as their display name.

        Returns:
            Card title, or card ID as fallback
        """
        return str(self.title) if self.title else self.id

    def __post_init__(self):
        super().__post_init__()
        self.enable_publish_support()
        self.Datasets = CardDatasets(auth=self.auth, parent=self)

    @property
    def display_url(self) -> str:
        return f"https://{self.auth.domo_instance}.domo.com/kpis/details/{self.id}"

    @staticmethod
    def _is_federated(obj: dict[str, Any]) -> bool:
        """
        Returns True if the card metadata indicates federation.

        Checks for an explicit 'isFederated' flag, then scans all datasources for federation indicators
        in 'displayType', 'dataType', or 'providerType'.

        See docs/domo_concepts/federated_and_published_entities.md for details.
        """
        # First check explicit flag
        if obj.get("isFederated") is True:
            return True

        # Then check datasources for federation indicators
        datasources = obj.get("datasources", [])
        if not datasources:
            return False

        for ds in datasources:
            display_type = ds.get("displayType", "").upper()
            data_type = ds.get("dataType", "").upper()
            provider_type = ds.get("providerType", "").upper()

            has_federate = any(
                [
                    "FEDERAT" in display_type,
                    "FEDERAT" in data_type,
                    "FEDERAT" in provider_type,
                ]
            )

            if has_federate:
                return True

        return False

    @property
    def is_federated(self) -> bool:
        """Check if this card is federated"""
        return self._is_federated(self.raw)

    @classmethod
    def from_dict(
        cls, auth: DomoAuth, obj: dict[str, Any], owners: list[Any] | None = None
    ):
        """Synchronous factory method for dict → Card construction.

        Build a DomoCard_Default instance from a metadata dictionary and owners list.

        This method does not invoke any other class methods or perform additional API calls.
        All required data must be provided in the arguments.

        Args:
            auth: DomoAuth instance for authentication
            obj: Card metadata dictionary (from API)
            owners: List of owner entities (DomoUser/DomoGroup), optional

        Returns:
            DomoCard_Default instance
        """
        owners = owners or []

        card = cls(
            auth=auth,
            id=obj.get("id"),
            raw=obj,
            title=obj.get("title"),
            description=obj.get("description"),
            type=obj.get("type"),
            urn=obj.get("urn"),
            certification=obj.get("certification"),
            chart_type=obj.get("metadata", {}).get("chartType"),
            dataset_id=(
                obj.get("datasources", [])[0].get("dataSourceId")
                if obj.get("datasources")
                else None
            ),
            owners=owners,
            datastore_id=obj.get("domoapp", {}).get("id"),
        )

        return card

    @staticmethod
    async def get_owners(
        auth: DomoAuth,
        owners: list[dict[str, Any]],
        is_suppress_errors: bool = True,
        *,
        context: RouteContext | None = None,
    ) -> list[Any]:
        """
        Resolve owner entities (DomoUser/DomoGroup) from a list of owner dicts.

        Args:
            auth: DomoAuth instance
            owners: List of owner dicts (each with 'id' and 'type')
            is_suppress_errors: If True, suppress errors and continue; else raise
            context: Optional RouteContext to preserve session across calls

        Returns:
            List of resolved DomoUser or DomoGroup entities

        Processing steps:
            - For each owner dict, dispatch async get_by_id for USER or GROUP
            - Uses gather_with_concurrency for parallel resolution
            - Suppresses errors if requested, logs suppressed errors
        """
        from .. import (
            DomoUser as dmdu,
        )

        print(owners)
        tasks = []
        for ele in owners:
            try:
                if ele["type"] == "USER":
                    tasks.append(
                        dmdu.DomoUser.get_by_id(
                            auth=auth, user_id=ele["id"], context=context
                        )
                    )
                if ele["type"] == "GROUP":
                    tasks.append(
                        dmgr.DomoGroup.get_by_id(
                            group_id=ele["id"], auth=auth, context=context
                        )
                    )

            except DomoError as e:
                if not is_suppress_errors:
                    raise e from e
                else:
                    print(f"Suppressed error getting owner {ele['id']} - {e}")

        return await dmce.gather_with_concurrency(n=60, *tasks)

    @classmethod
    async def _check_if_published(
        cls,
        auth: DomoAuth,
        card_id: str,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
    ) -> bool:
        """Check if a card is part of a publish/subscribe relationship.

        Simplified approach: If the instance has subscriptions and the card is federated,
        it's likely published. Detailed content checking is expensive and error-prone.

        Args:
            auth: Authentication object
            card_id: Card ID to check
            session: Optional HTTP session
            debug_api: Enable debug logging

        Returns:
            True if card is likely published (instance has subscriptions), False otherwise
        """
        from ...classes.DomoEverywhere import DomoEverywhere

        try:
            # Get all subscriptions for this instance
            domo_everywhere = DomoEverywhere(auth=auth)
            await domo_everywhere.get_subscriptions()

            # If this instance has any subscriptions, federated cards are likely published
            # More detailed checking requires publication entity matching which is expensive
            return len(domo_everywhere.subscriptions) > 0

        except Exception:
            # If check fails completely, default to not published
            return False

    @classmethod
    @log_call(
        level_name="entity",
        config=LogDecoratorConfig(result_processor=DomoEntityObjectProcessor()),
    )
    async def get_by_id(
        cls,
        auth: DomoAuth,
        card_id: str,
        optional_parts: str = "certification,datasources,drillPath,owners,properties,domoapp",
        check_if_published: bool = True,
        parent_auth_retrieval_fn: Callable | None = None,
        max_subscriptions_to_check: int | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        is_suppress_errors: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """
        Retrieve a DomoCard by ID, including owners and publication/certification status.

        Args:
            auth: DomoAuth instance
            card_id: Card ID to retrieve
            optional_parts: Comma-separated metadata parts to include (owners, certification, etc.)
            check_if_published: If True, checks if card is published (federated + subscriptions)
            parent_auth_retrieval_fn: Callable returning publisher auth when given publisher domain
            max_subscriptions_to_check: Optional limit when scanning subscriptions
            debug_api: Enable API debug logging
            session: Optional httpx session
            return_raw: If True, return raw API response
            is_suppress_errors: If True, suppress errors during owner resolution
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoCard_Default instance (or raw response if return_raw)

        Processing steps:
            1. Fetch card metadata from API (includes owners, certification, datasources, etc.)
            2. If return_raw, return API response directly
            3. Resolve owners to DomoUser/DomoGroup entities via get_owners (runs separate API calls)
            4. If card is federated and check_if_published is True, run additional check for publication status
            5. Build DomoCard_Default instance with all resolved fields
        """
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

        res = await card_routes.get_card_metadata(
            auth=auth,
            card_id=card_id,
            optional_parts=optional_parts,
            context=context,
        )

        if return_raw:
            return res

        owners = await cls.get_owners(
            auth=auth,
            owners=res.response.get("owners", []),
            is_suppress_errors=is_suppress_errors,
            context=context,
        )

        # Check if published (if federated and check enabled)
        is_published = False
        subscription = None
        if check_if_published and cls._is_federated(res.response):
            if not parent_auth_retrieval_fn:
                raise ValueError(
                    "parent_auth_retrieval_fn is required to determine publish state "
                    "for federated cards."
                )
            probe = DomoPublishEntity.from_probe(
                auth=auth,
                entity_id=str(card_id),
                entity_type="CARD",
            )
            is_published = await probe.check_if_published(
                retrieve_parent_auth_fn=parent_auth_retrieval_fn,
                entity_type="CARD",
                entity_id=str(card_id),
                session=session,
                debug_api=debug_api,
                max_subscriptions_to_check=max_subscriptions_to_check,
            )
            if is_published:
                subscription = probe.subscription

        domo_card = cls.from_dict(
            auth=auth,
            obj=res.response,
            owners=owners,
            is_published=is_published,
        )

        if is_published and subscription:
            helper = domo_card.enable_publish_support()
            helper.hydrate_from_existing(
                subscription=subscription,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                content_type="CARD",
                entity_id=str(card_id),
            )

        return domo_card

    @classmethod
    async def get_entity_by_id(
        cls, auth: DomoAuth, entity_id: str, is_suppress_errors: bool = False, **kwargs
    ):
        return await cls.get_by_id(
            auth=auth,
            card_id=entity_id,
            is_suppress_errors=is_suppress_errors,
            **kwargs,
        )

    async def share(
        self,
        auth: DomoAuth | None = None,
        domo_users: list[DomoUser] | None = None,
        domo_groups: list[DomoGroup] | None = None,
        message: str | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
    ):
        from ...routes import datacenter as datacenter_routes

        if domo_groups:
            domo_groups = (
                domo_groups if isinstance(domo_groups, list) else [domo_groups]
            )
        if domo_users:
            domo_users = domo_users if isinstance(domo_users, list) else [domo_users]

        if context is None:
            context = self._build_route_context(
                session=session,
                debug_api=debug_api,
                debug_num_stacks_to_drop=1,
            )

        res = await datacenter_routes.share_resource(
            auth=auth or self.auth,
            resource_ids=[self.id],
            resource_type=datacenter_routes.ShareResource_Enum.CARD,
            group_ids=[group.id for group in domo_groups] if domo_groups else None,
            user_ids=[user.id for user in domo_users] if domo_users else None,
            message=message,
            context=context,
        )

        return res

    async def get_collections(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        debug_num_stacks_to_drop: int = 2,
        *,
        context: RouteContext | None = None,
    ):
        from .. import DomoAppDb as dmdb

        context = self._build_route_context(
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        )

        domo_collections = await dmdb.AppDbCollections.get_collections(
            datastore_id=self.datastore_id,
            auth=self.auth,
            context=context,
            return_raw=return_raw,
        )

        if return_raw:
            return domo_collections

        self.domo_collections = await dmce.gather_with_concurrency(
            *[
                dmdb.AppDbCollection.get_by_id(
                    collection_id=domo_collection.id,
                    auth=self.auth,
                    debug_api=debug_api,
                )
                for domo_collection in domo_collections
            ],
            n=60,
        )

        return self.domo_collections

    async def get_source_code(
        self, debug_api: bool = False, try_auto_share: bool = False
    ):
        await self.get_collections()

        collection_name = "ddx_app_client_code"
        code_collection = next(
            (
                domo_collection
                for domo_collection in self.domo_collections
                if domo_collection.name == collection_name
            ),
            None,
        )

        if not code_collection:
            raise Card_DownloadSourceCodeError(
                card=deepcopy(self),
                auth=self.auth,
                message=f"collection - {collection_name} not found for {self.title} - {self.id}",
            )

        documents = await code_collection.query_documents(
            debug_api=debug_api, try_auto_share=try_auto_share
        )

        if not documents:
            raise Card_DownloadSourceCodeError(
                card=deepcopy(self),
                auth=self.auth,
                message=f"collection - {collection_name} - {code_collection.id} - unable to retrieve documents for {self.title} - {self.id}",
            )

        self.domo_source_code = documents[0]

        return self.domo_source_code

    async def download_source_code(
        self,
        download_folder="./EXPORT/",
        file_name=None,
        debug_api: bool = False,
        try_auto_share: bool = False,
    ):
        doc = await self.get_source_code(
            debug_api=debug_api, try_auto_share=try_auto_share
        )

        if file_name:
            download_path = os.path.join(
                download_folder, dmfi.change_extension(file_name, new_extension=".json")
            )
            dmfi.upsert_folder(download_path)

            with open(download_path, "w+", encoding="utf-8") as f:
                f.write(json.dumps(doc.content))
                return doc

        ddx_type = next(iter(doc.content))

        for key, value in doc.content[ddx_type].items():
            if key == "js":
                file_name = "app.js"
            elif key == "html":
                file_name = "index.html"
            elif key == "css":
                file_name = "styles.css"
            else:
                file_name = f"{key}.txt"

            download_path = os.path.join(
                download_folder, f"{ddx_type}/{self.id}/{file_name}"
            )
            dmfi.upsert_folder(download_path)

            with open(download_path, "w+", encoding="utf-8") as f:
                f.write(value)

        return doc


@dataclass
class CardDatasets(DomoManager):
    """Manager for datasets associated with a DomoCard

    Provides access to all datasets used by a card through its datasources.
    Inherits from DomoManager to follow standard entity manager patterns.
    """

    auth: DomoAuth = field(repr=False)
    parent: DomoCard_Default = field(repr=False, default=None)

    async def get(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        parent_auth_retrieval_fn: Callable[[str], Any] | None = None,
    ) -> list[Any]:  # Returns list[DomoDataset]
        """Get all datasets associated with this card

        This retrieves datasets from the card's datasources and returns
        DomoDataset instances for each one.

        Args:
            debug_api: Enable API debugging
            session: Optional httpx session for request reuse

        Returns:
            list[DomoDataset]: List of dataset objects associated with the card
        """
        from ..DomoDataset import DomoDataset

        # Get datasources from card metadata if not already loaded
        if not self.parent.raw.get("datasources"):
            if context is None:
                context = self.parent._build_route_context(
                    session=session,
                    debug_api=debug_api,
                    debug_num_stacks_to_drop=1,
                )

            # Reload card with datasources
            res = await card_routes.get_card_metadata(
                auth=self.auth,
                card_id=self.parent.id,
                optional_parts="datasources",
                context=context,
            )
            self.parent.raw = res.response

        datasources = self.parent.raw.get("datasources", [])

        if not datasources:
            return []

        # Get dataset IDs from datasources
        dataset_ids = [
            ds.get("dataSourceId") for ds in datasources if ds.get("dataSourceId")
        ]

        if not dataset_ids:
            return []

        # Fetch all datasets concurrently
        datasets = await dmce.gather_with_concurrency(
            *[
                DomoDataset.get_by_id(
                    auth=self.auth,
                    dataset_id=dataset_id,
                    debug_api=debug_api,
                    session=session,
                    check_if_published=False,
                    parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                )
                for dataset_id in dataset_ids
            ],
            n=60,
        )

        return datasets


class Card_DownloadSourceCodeError(ClassError):
    def __init__(self, card: DomoCard_Default, auth: DomoAuth, message: str):
        super().__init__(cls_instance=card, message=message)
