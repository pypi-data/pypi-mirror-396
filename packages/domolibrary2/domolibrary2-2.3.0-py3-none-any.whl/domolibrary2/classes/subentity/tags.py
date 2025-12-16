"""a class based approach for interacting with Domo Datasets"""

__all__ = ["DomoTags_SetTagsError", "DomoTags"]

import json
from dataclasses import dataclass, field

import httpx

from ...base.entities import DomoSubEntity
from ...base.exceptions import ClassError as dmde_ClassError
from ...client.context import RouteContext
from ...routes import dataset as dataset_routes


class DomoTags_SetTagsError(dmde_ClassError):
    """return if DatasetTags request is not successfull"""

    def __init__(self, dataset_id, res, cls_instance):
        message = f"failed to set tags on dataset - {dataset_id}"
        super().__init__(message=message, res=res, cls_instance=cls_instance)


@dataclass
class DomoTags(DomoSubEntity):
    """class for interacting with dataset tags"""

    tags: list[str] = field(default_factory=list)

    async def get(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:  # returns a list of tags
        """gets the existing list of dataset_tags"""

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await dataset_routes.get_dataset_by_id(
            dataset_id=self.parent.id,
            auth=self.parent.auth,
            context=context,
        )

        if res.response.get("tags"):
            self.tags = json.loads(res.response.get("tags"))

        return self.tags

    async def update(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:  # returns a list of tags
        """replaces all tags with a new list of dataset_tags"""

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        await dataset_routes.set_dataset_tags(
            auth=self.parent.auth,
            tag_ls=self.tags,
            dataset_id=self.parent.id,
            context=context,
        )

        await self.get(context=context)

        return self.tags

    async def add(
        self,
        add_tags: list[str],
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:  # returns a list of tags
        """appends tags to the list of existing dataset_tags"""

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        await self.get(context=context)

        for tg in add_tags:
            if tg not in self.tags:
                self.tags.append(tg)

        return await self.update(
            context=context,
        )

    async def remove(
        self,
        remove_tags: list[str],
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[str]:  # returns a list of tags
        """removes tags from the existing list of dataset_tags"""

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        await self.get(context=context)

        for tg in remove_tags:
            if tg in self.tags:
                self.tags.remove(tg)

        return await self.update(
            context=context,
        )
