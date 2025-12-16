"""Lineage handlers for Publication and Subscription entities."""

from __future__ import annotations

__all__ = ["DomoLineage_Publication", "DomoLineage_Subscription"]

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from ....auth import DomoAuth
from ....base.exceptions import ClassError
from ....client.context import RouteContext
from ....utils import chunk_execution as dmce
from .base import DomoLineage, register_lineage
from .link import DomoLineageLink_Publication


@register_lineage("DomoPublication")
@dataclass
class DomoLineage_Publication(DomoLineage):
    """Lineage handler for publication entities.

    The parent is the publication entity this lineage is based off of (not a dependency).
    Publications contain multiple entities (datasets, cards, pages).
    """

    datasets: list[Any] = field(repr=False, default=None)
    cards: list[Any] = field(repr=False, default=None)
    page: list[Any] = field(repr=False, default=None)
    unsorted: list[Any] = field(repr=False, default=None)

    async def _get_content_item_lineage(
        self,
        pc,  # DomoEntity - publication content item
        session: httpx.AsyncClient | None = None,
        is_suppress_errors: bool = False,
        debug_api: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Get lineage for a single publication content item.

        Args:
            pc: Publication content entity
            session: HTTP session for API calls
            is_suppress_errors: If True, skip entities without lineage support
            debug_api: Enable API debugging
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            Lineage list for the content item

        Raises:
            NotImplementedError: If entity type doesn't support lineage and errors aren't suppressed
        """
        # Filter context_kwargs to only include valid _build_route_context parameters
        valid_context_keys = {
            "session",
            "debug_api",
            "log_level",
            "debug_num_stacks_to_drop",
            "use_cache",
            "invalidate_cache",
            "cache_config",
            "is_verify",
            "dry_run",
            "is_follow_redirects",
        }
        filtered_kwargs = {
            k: v for k, v in context_kwargs.items() if k in valid_context_keys
        }

        base_context = self.parent._build_route_context(
            session=session,
            debug_api=debug_api,
            **filtered_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if not pc.entity.Lineage and not is_suppress_errors:
            raise NotImplementedError(
                f"Lineage is not implemented for this entity type - {pc.entity.__class__.__name__}"
            )

        await pc.get_entity_by_id(entity_id=pc.entity_id, auth=pc.auth, context=context)

        return await pc.entity.Lineage.get(context=context)

    def _categorize_lineage_items(self, lineage: list[Any]):
        """Categorize lineage items into datasets, cards, pages, and unsorted.

        Args:
            lineage: List of lineage items to categorize
        """
        for ele in lineage:
            if ele.__class__.__name__ == "DomoDataset":
                if not self.datasets:
                    self.datasets = []
                self.datasets.append(ele)
            elif ele.__class__.__name__ == "DomoCard":
                if not self.cards:
                    self.cards = []
                self.cards.append(ele)
            elif ele.__class__.__name__ == "DomoPage":
                if not self.page:
                    self.page = []
                self.page.append(ele)
            else:
                if not self.unsorted:
                    self.unsorted = []
                self.unsorted.append(ele)

        if self.unsorted:
            print(
                f"Unsorted lineage items: {', '.join([ele.__class__.__name__ for ele in self.unsorted])}"
            )

    async def get(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
        parent_auth: DomoAuth = None,
        parent_auth_retrieval_fn: Callable = None,
        is_recursive: bool = False,
        max_depth: int | None = None,
        is_suppress_errors: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Get lineage for all content items in the publication.

        Orchestrates fetching lineage for each content item and categorizing the results.
        """
        # Filter context_kwargs to only include valid _build_route_context parameters
        valid_context_keys = {
            "session",
            "debug_api",
            "log_level",
            "debug_num_stacks_to_drop",
            "use_cache",
            "invalidate_cache",
            "cache_config",
            "is_verify",
            "dry_run",
            "is_follow_redirects",
        }
        filtered_kwargs = {
            k: v for k, v in context_kwargs.items() if k in valid_context_keys
        }

        base_context = self.parent._build_route_context(
            session=session,
            debug_api=debug_api,
            **filtered_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if not self.parent:
            raise ClassError(
                message="Parent must be set. Use from_parent() to create lineage with a parent.",
                cls_instance=self,
            )

        await self.parent.get_content(context=context)

        if return_raw:
            return self.parent.content

        # Gather lineage for all content items concurrently
        lineage = await dmce.gather_with_concurrency(
            *[
                self._get_content_item_lineage(
                    pc=pc,
                    is_suppress_errors=is_suppress_errors,
                    context=context,
                )
                for pc in self.parent.content
                if pc
            ],
            n=10,
        )

        # Filter out None values
        result = [ele for ele in lineage if ele]

        # Categorize items into datasets, cards, pages, and unsorted
        self._categorize_lineage_items(result)

        # Cache the result for future use (but computation doesn't depend on it)
        self.lineage = result
        return result


@register_lineage("DomoSubscription")
@dataclass
class DomoLineage_Subscription(DomoLineage):
    """Lineage handler for subscription entities."""

    async def get(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
        parent_auth: DomoAuth | None = None,
        parent_auth_retrieval_fn: Callable | None = None,
        is_recursive: bool = False,
        max_depth: int | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        # Filter context_kwargs to only include valid _build_route_context parameters
        valid_context_keys = {
            "session",
            "debug_api",
            "log_level",
            "debug_num_stacks_to_drop",
            "use_cache",
            "invalidate_cache",
            "cache_config",
            "is_verify",
            "dry_run",
            "is_follow_redirects",
        }
        filtered_kwargs = {
            k: v for k, v in context_kwargs.items() if k in valid_context_keys
        }

        base_context = self.parent._build_route_context(
            session=session,
            debug_api=debug_api,
            **filtered_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        publisher_auth = parent_auth
        if not publisher_auth and parent_auth_retrieval_fn:
            auth_or_coro = parent_auth_retrieval_fn(self.parent.publisher_domain)
            if inspect.isawaitable(auth_or_coro):
                publisher_auth = await auth_or_coro
            else:
                publisher_auth = auth_or_coro

        if not publisher_auth:
            raise ClassError(
                cls_instance=self.parent,
                message=(
                    "parent_auth (publisher auth) is required to resolve "
                    "subscription lineage."
                ),
            )

        publication = await self.parent.get_parent_publication(
            parent_auth=publisher_auth,
            parent_auth_retrieval_fn=parent_auth_retrieval_fn,
            context=context,
            **context_kwargs,
        )

        if return_raw:
            return publication.raw

        publication_link = DomoLineageLink_Publication(
            auth=publisher_auth,
            id=str(publication.id),
            entity=publication,
            _type="PUBLICATION",
            dependents=[],
            dependencies=[],
        )

        publication_lineage = await publication.Lineage.get(
            session=session,
            debug_api=debug_api,
            return_raw=False,
            parent_auth=publisher_auth,
            parent_auth_retrieval_fn=parent_auth_retrieval_fn,
            is_recursive=is_recursive,
            max_depth=max_depth,
            context=context,
            **context_kwargs,
        )

        publication_link.dependencies = list(publication_lineage)
        self.lineage = [publication_link] + list(publication_lineage)
        return list(self.lineage)
