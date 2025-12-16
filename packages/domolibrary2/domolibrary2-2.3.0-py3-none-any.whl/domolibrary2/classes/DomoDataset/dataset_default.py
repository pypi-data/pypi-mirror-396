"""a class based approach for interacting with Domo Datasets"""

__all__ = [
    "DomoDataset_Default",
]


import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, ClassVar

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity_w_Lineage
from ...base.exceptions import ClassError
from ...client.context import RouteContext
from ...routes import dataset as dataset_routes
from ...routes.dataset import (
    ShareDataset_AccessLevelEnum,
)
from ...utils import convert as dmcv
from ...utils.logging import get_colored_logger
from ..subentity import (
    certification as dmdc,
    tags as dmtg,
)
from ..subentity.lineage import register_lineage_type
from ..subentity.schedule import DomoSchedule
from . import (
    ai_readiness as dmdai,
    pdp as dmpdp,
    schema as dmdsc,
    stream as dmdst,
)
from .dataset_data import DomoDataset_Data

logger = get_colored_logger()


class DomoDataset_NoTransportType_Error(ClassError):
    """Raised when unable to determine the transport type of a dataset."""

    def __init__(self, cls_instance=None, message: str = None, **kwargs):
        if not message:
            message = "Unable to determine the transport type of the dataset."

        super().__init__(cls_instance=cls_instance, message=message, **kwargs)


@register_lineage_type("DomoDataset_Default", lineage_type="DATA_SOURCE")
@dataclass
class DomoDataset_Default(DomoEntity_w_Lineage):  # noqa: N801
    "interacts with domo datasets"

    id: str
    auth: DomoAuth = field(repr=False)

    display_type: str = ""
    data_provider_type: str = ""
    name: str = ""
    description: str = ""
    row_count: int | None = None
    column_count: int | None = None

    stream_id: int | None = None
    cloud_id: str | None = None

    last_touched_dt: dt.datetime | None = None
    last_updated_dt: dt.datetime | None = None
    created_dt: dt.datetime | None = None

    owner: dict = field(default_factory=dict)
    formulas: dict = field(default_factory=dict)

    Data: DomoDataset_Data | None = field(default=None, repr=False)
    Schema: dmdsc.DomoDataset_Schema | None = field(default=None, repr=False)
    Stream: dmdst.DomoStream | None = field(default=None, repr=False)
    Tags: dmtg.DomoTags | None = field(default=None, repr=False)
    PDP: dmpdp.DatasetPdpPolicies | None = field(default=None, repr=False)

    Certification: dmdc.DomoCertification = field(default=None, repr=False)
    AI_Readiness: dmdai.DomoDataset_AI_Readiness = field(default=None, repr=False)

    # Lineage: dmdl.DomoLineage = field(default=None, repr=False)

    # Include selected computed properties in generic to_dict serialization
    __serialize_properties__: ClassVar[tuple] = ("display_url", "transport_type")

    @property
    def entity_type(self):
        return "DATASET"

    @property
    def Account(self):
        if self.Stream and self.Stream.Account:
            return self.Stream.Account
        return None

    @staticmethod
    def _is_federated(obj: dict[str, Any]) -> bool:
        """Heuristic: decide if a dataset JSON represents a federated (proxy) dataset."""

        dpt = obj.get("dataProviderType", "").upper()
        disp = obj.get("displayType", "").upper()

        has_hint = any(
            [
                bool(obj.get("federation")),
                bool(obj.get("federationData")),
                bool(obj.get("federatedDatasetId")),
                bool(obj.get("publisherDomain")),
                obj.get("isFederated") is True,
            ]
        )

        has_federate = any(["FEDERAT" in dpt, "FEDERAT" in disp])
        return has_hint or has_federate

    @property
    def transport_type(self) -> str | None:
        """Get the transport type of the dataset if available.

        Returns None if transport type cannot be determined rather than raising an exception.
        This allows the property to be safely included in serialization.
        """
        if self.raw.get("transportType"):
            return self.raw.get("transportType").upper()

        if self.Stream and self.Stream.transport_type:
            return self.Stream.transport_type.upper()

        # Return None instead of raising to allow safe serialization
        return None

    @property
    def is_federated(self) -> bool:
        """Heuristic: decide if a dataset JSON represents a federated (proxy) dataset."""

        return self._is_federated(self.raw)

    @staticmethod
    def _is_view(obj: dict[str, Any]) -> bool:
        """Check if a dataset JSON represents a view (dataset-view).

        Args:
            obj: Dataset metadata dictionary

        Returns:
            True if the dataset is a view, False otherwise
        """
        from .view import DomoDatasetView

        return DomoDatasetView._is_view(obj)

    @property
    def is_view(self) -> bool:
        """Check if this dataset is a view."""
        return self._is_view(self.raw) if self.raw else False

    @property
    def Schedule(self) -> "DomoSchedule":
        return self.Stream.Schedule if self.Stream and self.Stream.Schedule else None

    def __post_init__(self):
        super().__post_init__()
        self.enable_publish_support()

        # Lineage implemented by parent post init
        self.Data = DomoDataset_Data.from_parent(parent=self)
        self.Schema = dmdsc.DomoDataset_Schema.from_parent(parent=self)
        self.Tags = dmtg.DomoTags.from_parent(parent=self)

        # Only instantiate Stream if dataset has a stream_id
        if self.stream_id:
            self.Stream = self.Stream or dmdst.DomoStream.from_parent(
                parent=self, stream_id=self.stream_id
            )

        self.PDP = dmpdp.DatasetPdpPolicies.from_parent(parent=self)

        self.Certification = dmdc.DomoCertification.from_parent(parent=self)

        self.AI_Readiness = dmdai.DomoDataset_AI_Readiness.from_parent(parent=self)

        self.Relations = None

    @property
    def display_url(self) -> str:
        return f"https://{self.auth.domo_instance}.domo.com/datasources/{self.id}/details/overview"

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict[str, Any],
        is_use_default_dataset_class: bool = True,
        new_cls=None,
        **kwargs,
    ) -> "DomoDataset_Default":
        if not is_use_default_dataset_class:
            if not new_cls:
                raise NotImplementedError(
                    "Must provide new_cls if not using default dataset class"
                )
            cls = new_cls

        formulas = obj.get("properties", {}).get("formulas", {}).get("formulas", {})

        ds = cls(
            auth=auth,
            id=obj.get("id") or obj.get("databaseId"),
            raw=obj,
            display_type=obj.get("displayType", ""),
            data_provider_type=obj.get("dataProviderType", ""),
            name=obj.get("name", ""),
            description=obj.get("description", ""),
            owner=obj.get("owner", {}),
            stream_id=obj.get("streamId", None),
            cloud_id=obj.get("cloudId", None),
            last_touched_dt=dmcv.convert_epoch_millisecond_to_datetime(
                obj.get("lastTouched")
            ),
            last_updated_dt=dmcv.convert_epoch_millisecond_to_datetime(
                obj.get("lastUpdated")
            ),
            created_dt=dmcv.convert_epoch_millisecond_to_datetime(obj.get("created")),
            row_count=int(obj.get("rowCount") or 0),
            column_count=int(obj.get("columnCount") or 0),
            formulas=formulas,
            **kwargs,
        )

        return ds

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
        check_if_published: bool = None,
        parent_auth_retrieval_fn: Callable | None = None,
        max_subscriptions_to_check: int | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """retrieves dataset metadata

        Args:
            auth: Authentication object for API requests
            dataset_id: Dataset identifier to fetch
            debug_api: Enable verbose API logging
            return_raw: If True return the raw response object
            check_if_published: When True attempt to resolve publish subscriptions
            parent_auth_retrieval_fn: Callable used to obtain publisher auth for publish checks
            max_subscriptions_to_check: Optional limit passed to the PublishResolver
        """

        context = RouteContext.build_context(
            context=context,
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        # Override parent_class if explicitly provided
        if parent_class:
            context.parent_class = parent_class

        res = await dataset_routes.get_dataset_by_id(
            auth=auth,
            dataset_id=dataset_id,
            context=context,
        )

        if return_raw:
            return res

        obj = res.response

        # Validate response is a dict
        if not isinstance(obj, dict):
            raise ValueError(
                f"Expected dict response from API, got {type(obj).__name__}: {obj}"
            )

        # Check if published (for federated datasets)
        is_published = False
        subscription = None
        if check_if_published and cls._is_federated(obj):
            await logger.debug(
                f"Checking if federated dataset {dataset_id} is published",
                extra={
                    "dataset_id": dataset_id,
                    "is_federated": True,
                    "check_if_published": check_if_published,
                },
            )
            # TODO: Future enhancement - use lineage-based class selection
            # Instead of checking here, we could:
            # 1. Create dataset with from_dict
            # 2. Call: lineage = await DomoLineage.get_lineage_from_entity(
            #       entity=ds, check_is_published=True, parent_auth_retrieval_fn=...)
            # 3. If lineage.is_published: return DomoPublishDataset
            # 4. Elif lineage.is_federated: return FederatedDomoDataset
            # For now, keep existing probe pattern
            probe = await cls.probe_is_published(
                entity_id=dataset_id,
                subscriber_auth=auth,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                session=session,
                debug_api=debug_api,
                max_subscriptions_to_check=max_subscriptions_to_check,
                context=context,
            )
            is_published = probe.is_published
            subscription = probe.subscription

            await logger.debug(
                f"Probe results: is_published={is_published}, has_subscription={subscription is not None}",
                extra={
                    "dataset_id": dataset_id,
                    "is_published": is_published,
                    "has_subscription": subscription is not None,
                    "subscription_id": subscription.id if subscription else None,
                },
            )

        ds = cls.from_dict(
            obj=obj,
            auth=auth,
            new_cls=cls,
            is_use_default_dataset_class=is_use_default_dataset_class,
            check_is_published=is_published,  # Used for class selection only
        )

        if is_published and subscription:
            await logger.debug(
                f"Hydrating publish helper for dataset {dataset_id}",
                extra={
                    "dataset_id": dataset_id,
                    "subscription_id": subscription.id,
                },
            )
            helper = ds.enable_publish_support()
            helper.hydrate_from_existing(
                subscription=subscription,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                content_type="DATA_SOURCE",
                entity_id=str(dataset_id),
            )
            # Update Lineage.Publish so publish info is accessible via ds.Lineage.Publish
            if ds.Lineage:
                ds.Lineage.Publish = helper
                await logger.info(
                    f"✅ Lineage.Publish assigned for dataset {dataset_id}",
                    extra={
                        "dataset_id": dataset_id,
                        "subscription_id": subscription.id,
                    },
                )
            else:
                await logger.warning(
                    f"⚠️ Lineage is None, cannot assign Publish for dataset {dataset_id}",
                    extra={"dataset_id": dataset_id},
                )
        elif check_if_published and cls._is_federated(obj):
            await logger.debug(
                f"Skipping publish helper hydration: is_published={is_published}, has_subscription={subscription is not None}",
                extra={
                    "dataset_id": dataset_id,
                    "is_published": is_published,
                    "has_subscription": subscription is not None,
                },
            )

        if ds.Stream:
            await ds.Stream.refresh(
                is_get_account=is_get_account,
                is_suppress_no_account_config=is_suppress_no_account_config,
                context=context,
            )

        return ds

    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        return await cls.get_by_id(dataset_id=entity_id, auth=auth, **kwargs)

    async def delete(
        self,
        dataset_id: str | None = None,
        auth: DomoAuth | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        dataset_id = dataset_id or self.id
        auth = auth or self.auth

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await dataset_routes.delete(
            auth=auth, dataset_id=dataset_id, context=context
        )

        return res

    async def share(
        self,
        member,  # DomoUser or DomoGroup
        auth: DomoAuth | None = None,
        share_type: ShareDataset_AccessLevelEnum = ShareDataset_AccessLevelEnum.CAN_SHARE,
        is_send_email=False,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Import DomoGroup here to avoid circular imports
        from ..DomoGroup.core import DomoGroup

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        body = dataset_routes.generate_share_dataset_payload(
            entity_type="GROUP" if isinstance(member, DomoGroup) else "USER",
            entity_id=int(member.id),
            access_level=share_type,
            is_send_email=is_send_email,
        )

        res = await dataset_routes.share_dataset(
            auth=auth or self.auth,
            dataset_id=self.id,
            body=body,
            context=context,
        )

        return res

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        dataset_name: str,
        dataset_type: str = "api",
        schema: dict | None = None,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> "DomoDataset_Default":
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        schema = schema or {
            "columns": [
                {"name": "col1", "type": "LONG", "upsertKey": False},
                {"name": "col2", "type": "STRING", "upsertKey": False},
            ]
        }

        res = await dataset_routes.create(
            dataset_name=dataset_name,
            dataset_type=dataset_type,
            schema=schema,
            auth=auth,
            context=context,
        )

        if return_raw:
            return res

        dataset_id = res.response.get("dataSource").get("dataSourceId")

        return await cls.get_by_id(
            dataset_id=dataset_id,
            auth=auth,
            context=context,
        )
