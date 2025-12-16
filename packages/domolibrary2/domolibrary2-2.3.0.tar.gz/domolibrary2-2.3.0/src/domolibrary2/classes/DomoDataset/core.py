"""a class based approach for interacting with Domo Datasets"""

__all__ = [
    "DomoDataset_Default",
    "FederatedDomoDataset",
    "DomoPublishDataset",
    "DomoDatasetView",
    "DomoDataset",
]


from collections.abc import Callable
from dataclasses import dataclass

import httpx

from ...auth import DomoAuth
from ...base.entities_federated import DomoFederatedEntity
from ...utils import chunk_execution as dmce
from ..subentity.lineage import register_lineage_type
from .dataset_default import DomoDataset_Default
from .view import DomoDatasetView


@register_lineage_type("FederatedDomoDataset", lineage_type="DATA_SOURCE")
@dataclass
class FederatedDomoDataset(DomoDataset_Default, DomoFederatedEntity):
    """Federated dataset seen in a parent instance; points to a child instance's native dataset."""

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

            entity_name = getattr(self, "name", "N/A")
            subscriber_instance = getattr(self.auth, "domo_instance", "unknown")
            publisher_instance = (
                getattr(parent_auth, "domo_instance", "unknown")
                if parent_auth
                else "unknown"
            )

            raise ClassError(
                cls_instance=self,
                message=(
                    f"Unable to retrieve federated parent entity for dataset '{entity_name}' (ID: {self.id}). "
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
        dataset_id: str,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
        is_use_default_dataset_class: bool = False,
        parent_class: str | None = None,
        is_suppress_no_account_config: bool = True,
    ):
        """retrieves federated dataset metadata"""
        # Use parent implementation to avoid code duplication
        return await super().get_by_id(
            dataset_id=dataset_id,
            auth=auth,
            debug_api=debug_api,
            return_raw=return_raw,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            is_use_default_dataset_class=is_use_default_dataset_class,
            parent_class=parent_class or cls.__name__,
            is_suppress_no_account_config=is_suppress_no_account_config,
        )


@register_lineage_type("DomoPublishDataset", lineage_type="DATA_SOURCE")
@dataclass
class DomoPublishDataset(FederatedDomoDataset):
    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        return await cls.get_by_id(id=entity_id, auth=auth, **kwargs)

    async def get_subscription(
        self,
        parent_auth_retrieval_fn: Callable | None = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        max_subscriptions_to_check: int | None = None,
    ):
        """Retrieve subscription information for this dataset via PublishResolver.

        Uses the shared resolver to locate the subscription where this dataset
        appears as a DATA_SOURCE in subscriber associations.
        """
        helper = self.enable_publish_support()
        return await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            session=session,
            debug_api=debug_api,
            max_subscriptions_to_check=max_subscriptions_to_check,
            entity_type="DATA_SOURCE",
            entity_id=str(self.id),
        )

    async def get_parent_publication(
        self,
        parent_auth: None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Retrieve the parent publication for this published dataset.

        Args:
            parent_auth: Authentication for publisher instance
            parent_auth_retrieval_fn: Function to retrieve publisher auth

        Returns:
            DomoPublication object
        """
        # Get subscription first if not already loaded
        helper = self.enable_publish_support()

        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="DATA_SOURCE",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)

        parent_publication = await helper.get_parent_publication(
            parent_auth=publisher_auth,
        )

        return parent_publication

    async def get_parent_content_details(
        self,
        parent_auth: None = None,
        parent_auth_retrieval_fn: Callable | None = None,
    ):
        """Retrieve the parent dataset from the publisher instance.

        Args:
            parent_auth: Authentication for publisher instance
            parent_auth_retrieval_fn: Function to retrieve publisher auth

        Returns:
            DomoDataset instance from publisher
        """
        # Get parent publication if not loaded
        helper = self.enable_publish_support()

        await helper.ensure_subscription(
            retrieve_parent_auth_fn=parent_auth_retrieval_fn,
            entity_type="DATA_SOURCE",
            entity_id=str(self.id),
        )

        publisher_auth = await helper.get_publisher_auth(parent_auth=parent_auth)
        await helper.get_parent_publication(parent_auth=publisher_auth)

        parent_dataset = await helper.get_publisher_entity(
            parent_auth=publisher_auth,
        )

        return parent_dataset


@register_lineage_type("DomoDataset", lineage_type="DATA_SOURCE")
@dataclass
class DomoDataset(DomoDataset_Default):
    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict,
        # is_admin_summary: bool = True,
        check_is_published: bool = None,
        is_use_default_dataset_class: bool = False,
        new_cls=None,
        is_published: bool = False,
        **kwargs,
    ) -> "DomoDataset":
        """Factory method that automatically detects the dataset type and returns
        the appropriate class:
        - DomoDatasetView for views (dataset-view)
        - DomoPublishDataset for published federated datasets
        - FederatedDomoDataset for federated datasets
        - DomoDataset for regular datasets
        """

        is_federated = cls._is_federated(obj)
        is_view = cls._is_view(obj)

        new_cls = DomoDataset

        # Check if it's a view first (views can also be federated)
        if is_view and not is_use_default_dataset_class:
            new_cls = DomoDatasetView
        elif is_federated and not is_use_default_dataset_class:
            # If federated AND published, return DomoPublishDataset
            if check_is_published:
                new_cls = DomoPublishDataset
            else:
                new_cls = FederatedDomoDataset

        return super().from_dict(
            auth=auth,
            obj=obj,
            is_use_default_dataset_class=is_use_default_dataset_class,
            new_cls=new_cls,
            **kwargs,
        )

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        dataset_id: str,
        debug_api: bool = False,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_num_stacks_to_drop: int = 2,
        is_use_default_dataset_class: bool = False,
        parent_class: str | None = None,
        is_get_account: bool = True,
        is_suppress_no_account_config: bool = True,
        check_if_published: bool = True,
        parent_auth_retrieval_fn: Callable | None = None,
        max_subscriptions_to_check: int | None = None,
    ):
        """Retrieve dataset metadata by ID.

        This method uses the factory pattern in from_dict() to automatically
        return the appropriate dataset class (DomoDatasetView, FederatedDomoDataset, etc.)
        based on the dataset metadata.
        """
        # Delegate to parent class which has the published check logic
        return await super().get_by_id(
            auth=auth,
            dataset_id=dataset_id,
            debug_api=debug_api,
            return_raw=return_raw,
            session=session,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            is_use_default_dataset_class=is_use_default_dataset_class,
            parent_class=parent_class or cls.__name__,
            is_get_account=is_get_account,
            is_suppress_no_account_config=is_suppress_no_account_config,
            check_if_published=check_if_published,
            parent_auth_retrieval_fn=parent_auth_retrieval_fn,
            max_subscriptions_to_check=max_subscriptions_to_check,
        )
