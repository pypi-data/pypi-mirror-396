"""a class based approach for interacting with Domo Datasets"""

__all__ = [
    "DomoDataset_Data",
]


import asyncio
import io
from dataclasses import dataclass

import httpx
import pandas as pd

from ...base.entities import DomoSubEntity
from ...base.exceptions import DomoError
from ...client.context import RouteContext
from ...routes import dataset as dataset_routes
from ...routes.dataset import (
    DatasetNotFoundError,
    QueryRequestError,
)
from ...utils import chunk_execution as dmce


@dataclass
class DomoDataset_Data(DomoSubEntity):
    "interacts with domo datasets"

    async def query(
        self,
        sql: str,
        session: httpx.AsyncClient | None = None,
        filter_pdp_policy_id_ls: list[int] = None,  # filter by pdp policy
        loop_until_end: bool = False,  # retrieve all available rows
        limit=100,  # maximum rows to return per request.  refers to PAGINATION
        skip=0,
        maximum=100,  # equivalent to the LIMIT or TOP clause in SQL, the number of rows to return total
        return_raw: bool = False,
        debug_api: bool = False,
        debug_loop: bool = False,
        debug_num_stacks_to_drop: int = 2,
        timeout=10,  # larger API requests may require a longer response time
        maximum_retry: int = 5,
        is_return_dataframe: bool = True,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> pd.DataFrame:
        auth = self.parent.auth
        dataset_id = self.parent.id

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = None
        retry = 1

        if filter_pdp_policy_id_ls and not isinstance(filter_pdp_policy_id_ls, list):
            filter_pdp_policy_id_ls = [int(filter_pdp_policy_id_ls)]

        while (not res or not res.is_success) and retry <= maximum_retry:
            try:
                res = await dataset_routes.query_dataset_private(
                    auth=auth,
                    dataset_id=dataset_id,
                    sql=sql,
                    maximum=maximum,
                    filter_pdp_policy_id_ls=filter_pdp_policy_id_ls,
                    skip=skip,
                    limit=limit,
                    loop_until_end=loop_until_end,
                    return_raw=return_raw,
                    debug_loop=debug_loop,
                    timeout=timeout,
                    context=context,
                )

                if return_raw:
                    return res

            except DomoError as e:
                if isinstance(e, DatasetNotFoundError | QueryRequestError):
                    raise e from e

                if retry <= maximum_retry and e:
                    print(
                        f"⚠️ Error.  Attempt {retry} / {maximum_retry} - {e} - while query dataset {self.id} in {self.auth.domo_instance} with {sql}"
                    )

                if retry == maximum_retry:
                    raise e from e

                retry += 1

        if not is_return_dataframe:
            return res.response

        return pd.DataFrame(res.response)

    async def index(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = self.parent.auth
        dataset_id = self.parent.id

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        return await dataset_routes.index_dataset(
            auth=auth, dataset_id=dataset_id, context=context
        )

    async def upload_data(
        self,
        upload_df: pd.DataFrame = None,
        upload_df_ls: list[pd.DataFrame] = None,
        upload_file: io.TextIOWrapper = None,
        upload_method: str = "REPLACE",  # APPEND or REPLACE
        partition_key: str = None,
        is_index: bool = True,
        dataset_upload_id=None,
        session: httpx.AsyncClient = None,
        debug_api: bool = False,
        debug_prn: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = self.parent.auth
        dataset_id = self.parent.id

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        upload_df_ls = upload_df_ls or [upload_df]

        status_message = f"{dataset_id} {partition_key} | {auth.domo_instance}"

        # stage 1 get uploadId
        retry = 1
        while dataset_upload_id is None and retry < 5:
            try:
                if debug_prn:
                    print(f"\n\n🎭 starting Stage 1 - {status_message}")

                res = await dataset_routes.upload_dataset_stage_1(
                    auth=auth,
                    dataset_id=dataset_id,
                    partition_tag=partition_key,
                    context=context,
                )
                if debug_prn:
                    print(
                        f"\n\n🎭 Stage 1 response -- {res.status} for {status_message}"
                    )

                dataset_upload_id = res.response

            except dataset_routes.UploadDataError as e:
                print(f"{e} - attempt{retry}")
                retry += 1

                if retry == 5:
                    print(
                        f"failed to upload data for {dataset_id} in {auth.domo_instance}"
                    )
                    raise e
                    return

                await asyncio.sleep(5)

        # stage 2 upload_dataset
        if upload_file:
            if debug_prn:
                print(f"\n\n🎭 starting Stage 2 - upload file for {status_message}")

            res = await dmce.gather_with_concurrency(
                n=60,
                *[
                    dataset_routes.upload_dataset_stage_2_file(
                        auth=auth,
                        dataset_id=dataset_id,
                        upload_id=dataset_upload_id,
                        part_id=1,
                        data_file=upload_file,
                        context=context,
                    )
                ],
            )

        else:
            if debug_prn:
                print(
                    f"\n\n🎭 starting Stage 2 - {len(upload_df_ls)} - number of parts for {status_message}"
                )

            res = await dmce.gather_with_concurrency(
                n=60,
                *[
                    dataset_routes.upload_dataset_stage_2_df(
                        auth=auth,
                        dataset_id=dataset_id,
                        upload_id=dataset_upload_id,
                        part_id=index + 1,
                        upload_df=df,
                        context=context,
                    )
                    for index, df in enumerate(upload_df_ls)
                ],
            )

        if debug_prn:
            print(f"🎭 Stage 2 - upload data: complete for {status_message}")

        # stage 3 commit_data
        if debug_prn:
            print(
                f"\n\n🎭 starting Stage 3 - commit dataset_upload_id for {status_message}"
            )

        await asyncio.sleep(5)  # wait for uploads to finish

        res = await dataset_routes.upload_dataset_stage_3(
            auth=auth,
            dataset_id=dataset_id,
            upload_id=dataset_upload_id,
            update_method=upload_method,
            partition_tag=partition_key,
            is_index=False,
            context=context,
        )

        if debug_prn:
            print(f"\n🎭 stage 3 - commit dataset: complete for {status_message} ")

        if is_index:
            await asyncio.sleep(3)
            return await self.index(context=context)

        return res

    async def list_partitions(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = self.parent.auth
        dataset_id = self.parent.id

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await dataset_routes.list_partitions(
            auth=auth, dataset_id=dataset_id, context=context
        )
        return res.response

    async def delete_partition(
        self,
        dataset_partition_id: str,
        empty_df: pd.DataFrame = None,
        is_index: bool = True,
        debug_api: bool = False,
        debug_prn: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        auth = self.parent.auth
        dataset_id = self.parent.id

        base_context = self._build_route_context(
            session=None,  # Preserve original behavior
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        if empty_df is None:
            empty_df = await self.query(
                sql="SELECT * from table limit 1",
                context=context,
            )

            await self.upload_data(
                upload_df=empty_df.head(0),
                upload_method="REPLACE",
                is_index=is_index,
                partition_key=dataset_partition_id,
                context=context,
            )

        if debug_prn:
            print("\n\n🎭 starting Stage 1")

        res = await dataset_routes.delete_partition_stage_1(
            auth=auth,
            dataset_id=dataset_id,
            dataset_partition_id=dataset_partition_id,
            context=context,
        )
        if debug_prn:
            print(f"\n\n🎭 Stage 1 response -- {res.status}")
            print(res)

        if debug_prn:
            print("starting Stage 2")

        res = await dataset_routes.delete_partition_stage_2(
            auth=auth,
            dataset_id=dataset_id,
            dataset_partition_id=dataset_partition_id,
            context=context,
        )

        if debug_prn:
            print(f"\n\n🎭 Stage 2 response -- {res.status}")

        if debug_prn:
            print("starting Stage 3")

        res = await dataset_routes.index_dataset(
            auth=auth, dataset_id=dataset_id, context=context
        )
        if debug_prn:
            print(f"\n\n🎭 Stage 3 response -- {res.status}")

        if return_raw:
            return res

        return res.response

    async def truncate(
        self,
        is_index: bool = True,
        empty_df: pd.DataFrame = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        execute_reset = input(
            "This function will delete all rows.  Type BLOW_ME_AWAY to execute:"
        )

        if execute_reset != "BLOW_ME_AWAY":
            print("You didn't type BLOW_ME_AWAY, moving on.")
            return None

        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        # create empty dataset to retain schema
        if not isinstance(empty_df, pd.DataFrame):
            empty_df = await self.query(
                sql="SELECT * from table limit 1",
                context=context,
            )

        empty_df = pd.DataFrame(columns=empty_df.columns)

        res = await self.upload_data(
            upload_df=empty_df,
            upload_method="REPLACE",
            is_index=is_index,
            context=context,
        )

        # get partition list
        partition_list = await self.list_partitions(context=context)
        if len(partition_list) == 0:
            return res

        partition_list = dmce.chunk_list(partition_list, 100)

        for index, pl in enumerate(partition_list):
            print(f"🥫 starting chunk {index + 1} of {len(partition_list)}")

            await asyncio.gather(
                *[
                    self.delete_partition(
                        dataset_partition_id=partition.get("partitionId"),
                        empty_df=empty_df,
                        context=context,
                    )
                    for partition in pl
                ]
            )
            if is_index:
                await self.index(context=context)

        return res
