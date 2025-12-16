from __future__ import annotations

__all__ = ["DomoJupyter_DataSource"]


from dataclasses import dataclass, field
from typing import Any

import httpx

from .. import DomoDataset as dmds


@dataclass
class DomoJupyter_DataSource:
    dj_workspace: Any = field(repr=False)

    dataset_id: str
    alias: str

    is_exists: bool = False
    domo_dataset: dmds.DomoDataset = None

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.dataset_id == other.dataset_id

    def __lt__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.alias < other.alias

    async def get_dataset(
        self,
        is_suppress_no_account_config: bool = False,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
    ):
        import domolibrary2.routes.dataset as dataset_route

        try:
            self.domo_dataset = await dmds.DomoDataset.get_by_id(
                auth=self.dj_workspace.auth,
                dataset_id=self.dataset_id,
                is_suppress_no_config=is_suppress_no_account_config,
                session=session,
                debug_api=debug_api,
            )
            self.is_exists = True

            return self.domo_dataset

        except dataset_route.DatasetNotFoundError:
            self.is_exists = False

    @classmethod
    def from_dict(
        cls,
        obj,
        dj_workspace,
        domo_dataset: dmds.DomoDataset | None = None,
    ):
        dataset_id = obj["dataSourceId"]

        ds = cls(
            dataset_id=dataset_id,
            alias=obj["alias"],
            dj_workspace=dj_workspace,
        )

        if domo_dataset is not None:
            ds.domo_dataset = domo_dataset
            ds.is_exists = True

        return ds

    def to_dict(self):
        return {"dataSourceId": self.dataset_id, "alias": self.alias}

    async def share_with_workspace_as_input_datasource(
        self,
        dj_workspace: Any = None,
        is_update_config: bool = True,
        debug_api: bool = False,
    ):
        dj_workspace = dj_workspace or self.dj_workspace

        await self.dj_workspace.add_config_input_datasource(
            dja_input_datasource=self,
            is_update_config=is_update_config,
            debug_api=debug_api,
        )

    async def share_with_workspace_as_output_datasource(
        self,
        dj_workspace: Any = None,
        is_update_config: bool = True,
        debug_api: bool = False,
    ):
        dj_workspace = dj_workspace or self.dj_workspace

        await self.dj_workspace.add_config_output_datasource(
            dja_datasource=self,
            is_update_config=is_update_config,
            debug_api=debug_api,
        )
