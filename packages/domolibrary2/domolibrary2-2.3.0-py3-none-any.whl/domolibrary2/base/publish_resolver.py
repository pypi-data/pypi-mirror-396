from __future__ import annotations

"""Shared utilities for resolving publish/subscription relationships.

This module centralizes the common pattern used by published entities:

1. On a **subscriber** instance, retrieve subscription summaries.
2. For each subscription, call the PUBLISH associations API on the **publisher**
   instance to fetch subscriber content details.
3. Match a given subscriber-side entity (card, dataset, page, app) to the
   corresponding subscription based on content type and subscriber object id.
"""

import inspect  # noqa: E402
from collections.abc import Awaitable, Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from typing import Any  # noqa: E402

import httpx  # noqa: E402

from ..auth import DomoAuth  # noqa: E402
from ..client.context import RouteContext  # noqa: E402
from ..routes import publish as publish_routes  # noqa: E402
from ..utils.logging import get_colored_logger  # noqa: E402

ContentType = str  # e.g. "CARD", "DATA_SOURCE", "PAGE", "DATA_APP"

logger = get_colored_logger()


@dataclass
class PublishResolver:
    """Resolve subscriptions for subscriber-side entities."""

    subscriber_auth: DomoAuth
    parent_auth_retrieval_fn: Callable[[str], Any | Awaitable[Any]]
    session: httpx.AsyncClient | None = None
    debug_api: bool = False
    max_subscriptions_to_check: int | None = None

    async def _get_publisher_auth(self, publisher_domain: str) -> DomoAuth:
        """Get auth for the publisher instance, supporting sync or async callbacks."""
        auth_or_coro = self.parent_auth_retrieval_fn(publisher_domain)
        if inspect.isawaitable(auth_or_coro):
            return await auth_or_coro  # type: ignore[return-value]
        return auth_or_coro  # type: ignore[return-value]

    async def get_subscription_for_entity(
        self,
        *,
        entity_type: ContentType,
        subscriber_entity_id: str,
    ):
        """Find the subscription that contains the given subscriber entity."""
        # Local import to avoid cycles at module import time
        from ..classes.DomoEverywhere.core import DomoSubscription

        if not self.parent_auth_retrieval_fn:
            raise ValueError(
                "parent_auth_retrieval_fn is required to resolve subscriptions. "
                "This function should accept a publisher_domain and return DomoAuth "
                "for that instance (sync or async)."
            )

        context = RouteContext(
            session=self.session,
            debug_api=self.debug_api,
            debug_num_stacks_to_drop=2,
            parent_class=self.__class__.__name__,
        )

        summaries_res = await publish_routes.get_subscription_summaries(
            auth=self.subscriber_auth,
            context=context,
        )

        if not summaries_res.is_success or not summaries_res.response:
            raise ValueError(
                f"Failed to retrieve subscriptions for instance "
                f"{self.subscriber_auth.domo_instance}"
            )

        subscriptions_checked = 0
        total_subscriptions = len(summaries_res.response)
        target_id = str(subscriber_entity_id)

        await logger.debug(
            f"Found {total_subscriptions} subscriptions",
            extra={
                "entity_type": entity_type,
                "subscriber_entity_id": subscriber_entity_id,
                "subscriber_instance": self.subscriber_auth.domo_instance,
                "total_subscriptions": total_subscriptions,
            },
        )

        for summary in summaries_res.response:
            if (
                self.max_subscriptions_to_check is not None
                and subscriptions_checked >= self.max_subscriptions_to_check
            ):
                await logger.debug(
                    f"Reached max subscriptions limit ({self.max_subscriptions_to_check}), stopping search",
                    extra={"max_subscriptions": self.max_subscriptions_to_check},
                )
                break

            subscription_id = summary.get("subscriptionId")
            publication_id = summary.get("publicationId")
            subscriber_domain = summary.get("subscriberDomain")
            publisher_domain = summary.get("publisherDomain")

            if (
                not subscription_id
                or not publication_id
                or not subscriber_domain
                or not publisher_domain
            ):
                continue

            subscriptions_checked += 1

            sub_idx = (
                self.max_subscriptions_to_check
                if self.max_subscriptions_to_check
                else total_subscriptions
            )
            await logger.debug(
                f"Checking subscription {subscriptions_checked}/{sub_idx}: {subscription_id}",
                extra={
                    "subscription_id": subscription_id,
                    "publisher_domain": publisher_domain,
                    "publication_id": publication_id,
                    "subscription_number": subscriptions_checked,
                },
            )

            try:
                publisher_auth = await self._get_publisher_auth(publisher_domain)
            except Exception as exc:  # pragma: no cover - best effort logging
                await logger.warning(
                    f"Unable to fetch auth for publisher {publisher_domain}: {exc}",
                    extra={
                        "publisher_domain": publisher_domain,
                        "error": str(exc),
                    },
                )
                continue

            try:
                content_res = await publish_routes.get_subscriber_content_details(
                    auth=publisher_auth,
                    publication_id=publication_id,
                    subscriber_instance=subscriber_domain,
                    context=context,
                )
            except Exception as exc:  # pragma: no cover - best effort logging
                await logger.warning(
                    f"Unable to fetch subscriber content details for {subscription_id}: {exc}",
                    extra={
                        "subscription_id": subscription_id,
                        "error": str(exc),
                    },
                )
                continue

            if not (content_res.is_success and content_res.response):
                await logger.debug(
                    f"No subscriber content details for subscription {subscription_id}",
                    extra={"subscription_id": subscription_id},
                )
                continue

            for item in content_res.response:
                if (
                    item.get("contentType") == entity_type
                    and str(item.get("subscriberObjectId")) == target_id
                ):
                    await logger.info(
                        f"✅ Found {entity_type} {target_id} in subscription {subscription_id}",
                        extra={
                            "entity_type": entity_type,
                            "entity_id": target_id,
                            "subscription_id": subscription_id,
                            "publisher_domain": publisher_domain,
                        },
                    )
                    return DomoSubscription.from_dict(
                        auth=self.subscriber_auth,
                        parent_publication=None,
                        obj=summary,
                    )

        # No subscription found
        if self.max_subscriptions_to_check:
            raise ValueError(
                f"Entity {subscriber_entity_id} (type {entity_type}) is not part of "
                f"any subscription after checking {subscriptions_checked} "
                f"subscriptions. Try increasing max_subscriptions_to_check "
                f"(currently {self.max_subscriptions_to_check})."
            )

        raise ValueError(
            f"Entity {subscriber_entity_id} (type {entity_type}) is not part of any "
            f"subscription after checking all {subscriptions_checked} subscriptions."
        )
