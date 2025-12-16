__all__ = ["DomoPublishAppStudio"]

from collections.abc import Callable
from dataclasses import dataclass

import httpx

from ..auth import DomoAuth
from .DomoAppStudio import DomoAppStudio
from .subentity.lineage import register_lineage_type


@register_lineage_type("DomoPublishAppStudio", lineage_type="DATA_APP")
@dataclass
class DomoPublishAppStudio(DomoAppStudio):
    """Published AppStudio app that supports publish/subscribe across instances.

    This closely mirrors the behavior of DomoPublishCard/DomoPublishPage/
    DomoPublishDataset, but for AppStudio DATA_APP content.
    """

    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        """Factory used by DomoPublication to resolve publisher-side entities."""
        return await cls.get_by_id(auth=auth, appstudio_id=entity_id, **kwargs)

    async def get_subscription(
        self,
        parent_auth_retrieval_fn: Callable | None = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        max_subscriptions_to_check: int | None = None,
    ):
        """Retrieve subscription information for this AppStudio app via PublishResolver.

        Uses the shared resolver to locate the subscription where this app
        appears as DATA_APP content in subscriber associations.
        """
        helper = self.enable_publish_support()
        return await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            session=session,
            debug_api=debug_api,
            max_subscriptions_to_check=max_subscriptions_to_check,
            entity_type="DATA_APP",
            entity_id=str(self.id),
        )

    async def get_parent_publication(
        self,
        parent_auth: DomoAuth | None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Retrieve the parent publication for this published AppStudio app."""
        helper = self.enable_publish_support()

        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="DATA_APP",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)

        return await helper.get_parent_publication(parent_auth=publisher_auth)

    async def get_parent_content_details(
        self,
        parent_auth: DomoAuth | None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Retrieve the parent AppStudio app from the publisher instance."""
        helper = self.enable_publish_support()

        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="DATA_APP",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)
        await helper.get_parent_publication(parent_auth=publisher_auth)

        return await helper.get_publisher_entity(parent_auth=publisher_auth)
