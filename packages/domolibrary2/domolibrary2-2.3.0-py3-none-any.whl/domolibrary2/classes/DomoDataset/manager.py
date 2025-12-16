"""DomoDatasets Manager Class for collection operations on datasets."""

from dataclasses import dataclass, field

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoManager
from ...client.context import RouteContext
from ...routes import dataset as dataset_routes
from .core import DomoDataset


@dataclass
class DomoDatasets(DomoManager):
    """Manager class for searching and retrieving multiple datasets.

    Provides methods for listing and searching datasets in a Domo instance.
    """

    auth: DomoAuth = field(repr=False)
    datasets: list[DomoDataset] = field(default_factory=list)

    @classmethod
    def _to_domo_dataset(cls, dataset_ls: list, auth: DomoAuth) -> list[DomoDataset]:
        """Convert API response list to DomoDataset objects."""
        return [DomoDataset.from_dict(auth=auth, obj=obj) for obj in dataset_ls]

    async def get(
        self,
        search_text: str | None = None,
        maximum: int | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoDataset]:
        """Retrieve datasets from Domo, optionally filtering by search text.

        Args:
            search_text: Optional text to search for in dataset names
            maximum: Maximum number of datasets to return
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)
            return_raw: Return raw API response
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            List of DomoDataset objects matching the criteria
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await dataset_routes.search_datasets(
            auth=self.auth,
            search_text=search_text,
            maximum=maximum,
            context=context,
        )

        if return_raw:
            return res

        self.datasets = self._to_domo_dataset(
            dataset_ls=res.response or [], auth=self.auth
        )
        return self.datasets

    async def search(
        self,
        search_text: str,
        maximum: int | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoDataset]:
        """Search for datasets by name.

        Args:
            search_text: Text to search for in dataset names (wildcards supported)
            maximum: Maximum number of datasets to return
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop for debugging
            session: HTTP client session (optional)
            return_raw: Return raw API response
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            List of DomoDataset objects matching the search criteria
        """
        return await self.get(
            search_text=search_text,
            maximum=maximum,
            return_raw=return_raw,
            context=context,
            **context_kwargs,
        )
