"""Core DomoCard classes including federated and published support"""

__all__ = [
    "FederatedDomoCard",
    "DomoPublishCard",
    "DomoCard",
]

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base.entities_federated import DomoFederatedEntity
from ...utils import chunk_execution as dmce
from ..subentity.lineage import register_lineage_type
from .card_default import DomoCard_Default


@register_lineage_type("FederatedDomoCard", lineage_type="CARD")
@dataclass
class FederatedDomoCard(DomoCard_Default, DomoFederatedEntity):
    """Federated card seen in a parent instance; points to a child instance's native card."""

    @property
    def entity_type(self):
        return "CARD"

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
                    f"Unable to retrieve federated parent entity for card '{entity_name}' (ID: {self.id}). "
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
        auth: DomoAuth,
        card_id: str,
        optional_parts: str = "certification,datasources,drillPath,owners,properties,domoapp",
        check_if_published: bool = True,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        is_suppress_errors: bool = False,
    ):
        """Retrieve federated card metadata"""
        # Use parent implementation to avoid code duplication
        return await super().get_by_id(
            auth=auth,
            card_id=card_id,
            optional_parts=optional_parts,
            check_if_published=check_if_published,
            debug_api=debug_api,
            session=session,
            return_raw=return_raw,
            is_suppress_errors=is_suppress_errors,
        )


@register_lineage_type("DomoPublishCard", lineage_type="CARD")
@dataclass
class DomoPublishCard(FederatedDomoCard):
    """Published card that supports publish/subscribe across instances"""

    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        return await cls.get_by_id(auth=auth, card_id=entity_id, **kwargs)

    async def get_subscription(
        self,
        parent_auth_retrieval_fn: Callable | None = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        max_subscriptions_to_check: int | None = None,
    ):
        """Retrieve subscription information for this card via PublishResolver.

        This uses a shared resolver to scan subscription summaries and PUBLISH
        associations on publisher instances, avoiding duplicated logic across
        published entity types.
        """
        helper = self.enable_publish_support()
        return await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            session=session,
            debug_api=debug_api,
            max_subscriptions_to_check=max_subscriptions_to_check,
            entity_type="CARD",
            entity_id=str(self.id),
        )

    async def get_parent_publication(
        self,
        parent_auth: DomoAuth | None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Retrieve parent publication information.

        Args:
            parent_auth: Authentication for publisher instance
            parent_auth_retrieval_fn: Function to retrieve publisher auth

        Returns:
            DomoPublication object from publisher

        Raises:
            ValueError: If parent_auth cannot be determined
        """
        # Get subscription if not already loaded
        helper = self.enable_publish_support()
        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="CARD",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)

        parent_publication = await helper.get_parent_publication(
            parent_auth=publisher_auth
        )

        return parent_publication

    async def get_parent_content_details(
        self,
        parent_auth: DomoAuth | None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Retrieve the parent card from the publisher instance.

        Args:
            parent_auth: Authentication for publisher instance
            parent_auth_retrieval_fn: Function to retrieve publisher auth

        Returns:
            DomoCard instance from publisher
        """
        # Get parent publication if not loaded
        helper = self.enable_publish_support()

        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="CARD",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)
        await helper.get_parent_publication(parent_auth=publisher_auth)

        parent_card = await helper.get_publisher_entity(
            parent_auth=publisher_auth,
        )

        return parent_card


@register_lineage_type("DomoCard", lineage_type="CARD")
@dataclass
class DomoCard(DomoCard_Default):
    """Smart factory class that returns appropriate card type based on metadata"""

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict,
        owners: list[Any] = None,
        is_published: bool = False,
        **kwargs,
    ) -> "DomoCard":
        """Convert API response dictionary to appropriate card class instance"""

        is_federated = cls._is_federated(obj)

        new_cls = DomoCard

        if is_federated:
            # If federated AND published, return DomoPublishCard
            if is_published:
                new_cls = DomoPublishCard
            else:
                new_cls = FederatedDomoCard

        # Build the card instance with the appropriate class
        card = new_cls(
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
            owners=owners or [],
            datastore_id=obj.get("domoapp", {}).get("id"),
        )

        return card
