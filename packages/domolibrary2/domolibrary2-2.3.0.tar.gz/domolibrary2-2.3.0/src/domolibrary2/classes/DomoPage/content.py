"""Page content and data operations."""

__all__ = ["get_cards", "get_datasets", "update_layout", "add_owner"]

import datetime as dt
from collections.abc import Callable
from typing import Any

import httpx

from ...auth import DomoAuth
from ...client.context import RouteContext
from ...routes import page as page_routes
from ...utils import (
    chunk_execution as dmce,
    convert as dmcv,
)


async def get_cards(
    self,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    parent_auth_retrieval_fn: Callable[[str], Any] | None = None,
    check_if_published: bool | None = None,
    **context_kwargs,
):
    from .. import DomoCard as dc

    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    res = await page_routes.get_page_definition(
        auth=self.auth, page_id=self.id, context=context
    )

    if return_raw:
        return res

    if len(res.response.get("cards")) == 0:
        return []

    check_publish = True if check_if_published is None else check_if_published

    self.domo_cards = await dmce.gather_with_concurrency(
        n=60,
        *[
            dc.DomoCard.get_by_id(
                card_id=card["id"],
                auth=self.auth,
                parent_auth_retrieval_fn=parent_auth_retrieval_fn,
                check_if_published=check_publish,
            )
            for card in res.response.get("cards")
        ],
    )

    return self.domo_cards


async def get_datasets(
    self,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    res = await page_routes.get_page_definition(
        auth=self.auth, page_id=self.id, context=context
    )

    if return_raw:
        return res

    cards = await self.get_cards(context=context)

    card_datasets = await dmce.gather_with_concurrency(
        *[card.get_datasets(debug_api=debug_api, session=session) for card in cards],
        n=10,
    )

    self.datasets = [ds for ds_ls in card_datasets for ds in ds_ls if ds is not None]

    return self.datasets


async def update_layout(
    cls,
    auth: DomoAuth,
    body: dict,
    layout_id: str,
    debug_api: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    context = RouteContext.build_context(
        context=context,
        debug_api=debug_api,
        parent_class=getattr(cls, "__name__", "DomoPage"),
        **context_kwargs,
    )

    datetime_now = dt.datetime.now()
    start_time_epoch = dmcv.convert_datetime_to_epoch_millisecond(datetime_now)

    res_writelock = await page_routes.put_writelock(
        auth=auth,
        layout_id=layout_id,
        user_id=auth.user_id,
        epoch_time=start_time_epoch,
        context=context,
    )
    if res_writelock.status == 200:
        res = await page_routes.update_page_layout(
            auth=auth, body=body, layout_id=layout_id, context=context
        )

        if not res.is_success:
            return False

        res_writelock = await page_routes.delete_writelock(
            auth=auth, layout_id=layout_id, context=context
        )
        if res_writelock.status != 200:
            return False

    else:
        return False

    return True


async def add_owner(
    self,
    group_id_ls: list[int],  # DomoGroup IDs to share page with
    user_id_ls: list[int],  # DomoUser IDs to share page with
    note: str = None,  # message for automated email
    send_email: bool = False,  # send or not email to the new owners
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    base_context = self._build_route_context(
        session=session,
        debug_api=debug_api,
        **context_kwargs,
    )
    context = RouteContext.build_context(context=context or base_context)

    res = await page_routes.add_page_owner(
        auth=self.auth,
        page_id_ls=[self.id],
        group_id_ls=group_id_ls,
        user_id_ls=user_id_ls,
        note=note,
        send_email=send_email,
        context=context,
    )

    return res
