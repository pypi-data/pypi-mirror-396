"""Page management and collection operations."""

__all__ = ["DomoPages"]

from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ...client.context import RouteContext
from ...routes import page as page_routes
from ...utils import chunk_execution as dmce


@dataclass
class DomoPages:
    auth: DomoAuth = field(repr=False)
    pages: list[Any] = None  # DomoPage

    async def get(self, **kwargs):
        """calls get_admin_summary to retrieve all pages in an instance"""
        return await self.get_admin_summary(**kwargs)

    async def get_admin_summary(
        self,
        search_title: str = None,
        parent_page_id: int = None,
        return_raw: bool = False,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """use admin_summary to retrieve all pages in an instance -- regardless of user access
        NOTE: some Page APIs will not return results if page access isn't explicitly shared
        """
        from .core import DomoPage

        # DomoPages doesn't extend DomoManager, so use RouteContext.build_context directly
        # but merge with context_kwargs for backward compatibility
        context = RouteContext.build_context(
            context=context,
            session=session,
            debug_api=debug_api,
            parent_class=self.__class__.__name__,
            **context_kwargs,
        )

        res = await page_routes.get_pages_adminsummary(
            auth=self.auth,
            context=context,
            search_title=search_title,
            page_parent_id=parent_page_id,
        )

        if return_raw:
            return res

        self.pages = await dmce.gather_with_concurrency(
            n=60,
            *[
                DomoPage._from_adminsummary(
                    page_obj, auth=self.auth, debug_api=debug_api, session=session
                )
                for page_obj in res.response
            ],
        )

        return self.pages
