"""
DomoDataflow Manager

Manager class for working with collections of dataflows.
"""

from __future__ import annotations

from dataclasses import field

import httpx

from ...base import DomoManager
from ...client.context import RouteContext
from ...routes import dataflow as dataflow_routes
from ...utils import chunk_execution as dmce
from .core import DomoDataflow
from .exceptions import SearchDataflowNotFoundError

__all__ = [
    "DomoDataflows",
]


class DomoDataflows(DomoManager):
    """Manager class for searching and retrieving multiple dataflows.

    Provides methods for listing, searching, and upserting dataflows in a Domo instance.
    """

    dataflows: list[DomoDataflow] = field(default_factory=list)

    async def get(
        self,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoDataflow]:
        """Retrieve all dataflows from Domo.

        Args:
            return_raw: Return raw API response instead of DomoDataflow objects
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            List of DomoDataflow objects
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await dataflow_routes.get_dataflows(
            auth=self.auth,
            context=context,
        )

        if return_raw:
            return res

        self.dataflows = await dmce.gather_with_concurrency(
            *[
                DomoDataflow.get_by_id(
                    auth=self.auth, dataflow_id=obj["id"], context=context
                )
                for obj in res.response
            ],
            n=10,
        )

        return self.dataflows

    async def search_by_name(
        self,
        name: str,
        exact: bool = False,
        only_allow_one: bool = True,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoDataflow | list[DomoDataflow]:
        """Search for dataflows by name.

        Args:
            name: Dataflow name to search for (case-insensitive)
            exact: If True, require exact name match; if False, partial match
            only_allow_one: If True, return single result; if False, return list
            return_raw: Return raw API response
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoDataflow or list of DomoDataflows matching the search criteria

        Raises:
            SearchDataflowNotFoundError: If no dataflows match the search criteria
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if not self.dataflows:
            await self.get(context=context, return_raw=return_raw)

        if return_raw:
            return self.dataflows

        if exact:
            matches = [
                df
                for df in self.dataflows
                if df.name and df.name.lower() == name.lower()
            ]
        else:
            matches = [
                df
                for df in self.dataflows
                if df.name and name.lower() in df.name.lower()
            ]

        if not matches:
            raise SearchDataflowNotFoundError(cls_instance=self, search_name=name)

        if only_allow_one:
            return matches[0]

        return matches

    async def upsert(
        self,
        name: str,
        dataflow_definition: dict,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoDataflow:
        """Create or update a dataflow by name.

        If a dataflow with the given name exists, updates its definition.
        Otherwise, creates a new dataflow.

        Args:
            name: Dataflow name to match/create
            dataflow_definition: Full dataflow definition dict
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            Created or updated DomoDataflow instance
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        try:
            existing = await self.search_by_name(
                name=name,
                exact=True,
                only_allow_one=True,
                context=context,
            )

            # Update existing dataflow
            return await existing.update_dataflow_definition(
                new_dataflow_definition=dataflow_definition,
                context=context,
            )

        except SearchDataflowNotFoundError:
            # Create new dataflow
            dataflow_definition["name"] = name
            new_dataflow = await DomoDataflow.create(
                auth=self.auth,
                dataflow_definition=dataflow_definition,
                context=context,
            )

            # Refresh the list
            await self.get(context=context)

            return new_dataflow
