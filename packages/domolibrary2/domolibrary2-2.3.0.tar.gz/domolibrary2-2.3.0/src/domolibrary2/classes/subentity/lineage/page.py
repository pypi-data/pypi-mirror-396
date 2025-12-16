"""Lineage handler for Page entities."""

from __future__ import annotations

__all__ = ["DomoLineage_Page"]

from dataclasses import dataclass, field
from typing import Any

import httpx

from ....base.exceptions import ClassError
from ....client.context import RouteContext
from .base import DomoLineage, register_lineage
from .link import DomoLineage_Link, DomoLineageLink_Card


@register_lineage(
    "DomoPage", "DomoPage_Default", "FederatedDomoPage", "DomoPublishPage"
)
@dataclass
class DomoLineage_Page(DomoLineage):
    """Lineage handler for page entities.

    The parent is the page entity this lineage is based off of (not a dependency).
    Pages have cards as their immediate dependencies.
    """

    cards: list[Any] = field(repr=False, default=None)

    async def _get_entity_lineage(
        self,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        return_raw: bool = False,
        max_depth: int | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoLineage_Link]:
        """Get the page's immediate dependencies (cards).

        The parent is the page entity this lineage is based off of (not a dependency).
        This method fetches the cards that belong to the page.
        """
        if not self.parent:
            raise ClassError(
                message="Parent must be set. Use from_parent() to create lineage with a parent.",
                cls_instance=self,
            )

        parent_auth_retrieval_fn = context_kwargs.pop("parent_auth_retrieval_fn", None)
        check_if_published_override = context_kwargs.pop("check_if_published", None)

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

        # If lineage was already set, return a copy to avoid external mutations
        if self.lineage:
            return list(self.lineage)

        check_publish = (
            parent_auth_retrieval_fn is not None
            if check_if_published_override is None
            else check_if_published_override
        )

        cards = await self.parent.get_cards(
            context=context,
            parent_auth_retrieval_fn=parent_auth_retrieval_fn,
            check_if_published=check_publish,
        )

        lineage: list[DomoLineage_Link] = []
        for card in cards:
            card_link = DomoLineageLink_Card(
                id=str(card.id),
                auth=self.auth,
                entity=card,
                _type=None,  # Type derived from entity
                dependents=[],
                dependencies=[],
            )
            lineage.append(card_link)

        self.cards = cards
        # Return lineage without mutating self.lineage (will be cached by get() at the end)
        return lineage
