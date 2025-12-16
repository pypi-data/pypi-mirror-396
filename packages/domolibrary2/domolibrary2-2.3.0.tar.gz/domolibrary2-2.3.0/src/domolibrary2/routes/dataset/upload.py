"""Dataset upload and data operations."""

from __future__ import annotations

import io

import pandas as pd

from ...auth import DomoAuth
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...client.context import RouteContext
from ...utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)
from .exceptions import (
    Dataset_CRUD_Error,
    Dataset_GET_Error,
    DatasetNotFoundError,
    UploadDataError,
)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def upload_dataset_stage_1(
    auth: DomoAuth,
    dataset_id: str,
    #  restate_data_tag: str = None, # deprecated
    partition_tag: str | None = None,  # synonymous with data_tag
    *,  # Make following params keyword-only
    context: RouteContext | None = None,
    return_raw: bool = False,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """preps dataset for upload by creating an upload_id (upload session key) pass to stage 2 as a parameter"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads"

    # base body assumes no paritioning
    body = {"action": None, "appendId": None}

    params = None

    if partition_tag:
        # params = {'dataTag': restate_data_tag or data_tag} # deprecated
        params = {"dataTag": partition_tag}
        body.update({"appendId": "latest"})  # type: ignore

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        params=params,
        context=context,
    )

    if not res.is_success:
        raise UploadDataError(stage_num=1, dataset_id=dataset_id, res=res)

    if return_raw:
        return res

    upload_id = res.response.get("uploadId")

    if not upload_id:
        raise UploadDataError(
            stage_num=1,
            dataset_id=dataset_id,
            res=res,
            message="no upload_id",
        )

    res.response = upload_id

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def upload_dataset_stage_2_file(
    auth: DomoAuth,
    dataset_id: str,
    upload_id: str,  # must originate from  a stage_1 upload response
    data_file: io.TextIOWrapper | None = None,
    # only necessary if streaming multiple files into the same partition (multi-part upload)
    part_id: int = 2,
    *,  # Make following params keyword-only
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Upload data file to dataset (stage 2 of upload process)."""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/parts/{part_id}"

    body = data_file

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        content_type="text/csv",
        body=body,
        context=context,
    )

    if not res.is_success:
        raise UploadDataError(stage_num=2, dataset_id=dataset_id, res=res)

    res.upload_id = upload_id
    res.dataset_id = dataset_id
    res.part_id = part_id

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def upload_dataset_stage_2_df(
    auth: DomoAuth,
    dataset_id: str,
    upload_id: str,  # must originate from  a stage_1 upload response
    upload_df: pd.DataFrame,
    part_id: int = 2,  # only necessary if streaming multiple files into the same partition (multi-part upload)
    *,  # Make following params keyword-only
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Upload pandas DataFrame to dataset (stage 2 of upload process)."""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/parts/{part_id}"

    body = upload_df.to_csv(header=False, index=False)

    # if debug:

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        content_type="text/csv",
        body=body,
        context=context,
    )

    if not res.is_success:
        raise UploadDataError(stage_num=2, dataset_id=dataset_id, res=res)

    res.upload_id = upload_id
    res.dataset_id = dataset_id
    res.part_id = part_id

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def upload_dataset_stage_3(
    auth: DomoAuth,
    dataset_id: str,
    upload_id: str,  # must originate from  a stage_1 upload response
    update_method: str = "REPLACE",  # accepts REPLACE or APPEND
    partition_tag: str | None = None,  # synonymous with data_tag
    is_index: bool = False,  # index after uploading
    #  restate_data_tag: str = None, # deprecated
    *,  # Make following params keyword-only
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """commit will close the upload session, upload_id.  this request defines how the data will be loaded into Adrenaline, update_method
    has optional flag for indexing dataset.
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/commit"

    body = {"index": is_index, "action": update_method}

    if partition_tag:
        body.update(
            {
                "action": "APPEND",
                #  'dataTag': restate_data_tag or data_tag,
                #  'appendId': 'latest' if (restate_data_tag or data_tag) else None,
                "dataTag": partition_tag,
                "appendId": "latest" if partition_tag else None,
                "index": is_index,
            }
        )

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        context=context,
    )

    if not res.is_success:
        raise UploadDataError(stage_num=3, dataset_id=dataset_id, res=res)

    res.upload_id = upload_id
    res.dataset_id = dataset_id

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def index_dataset(
    auth: DomoAuth,
    dataset_id: str,
    *,  # Make following params keyword-only
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """manually index a dataset"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/indexes"

    body = {"dataIds": []}

    res = await gd.get_data(
        auth=auth,
        method="POST",
        body=body,
        url=url,
        context=context,
    )

    if not res.is_success:
        raise Dataset_CRUD_Error(dataset_id=dataset_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def index_status(
    auth: DomoAuth,
    dataset_id: str,
    index_id: str,
    *,  # Make following params keyword-only
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """get the completion status of an index"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/indexes/{index_id}/statuses"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if not res.is_success:
        raise Dataset_GET_Error(dataset_id=dataset_id, res=res)

    return res


def generate_list_partitions_body(limit: int = 100, offset: int = 0) -> dict:
    return {
        "paginationFields": [
            {
                "fieldName": "datecompleted",
                "sortOrder": "DESC",
                "filterValues": {"MIN": None, "MAX": None},
            }
        ],
        "limit": limit,
        "offset": offset,
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def list_partitions(
    auth: DomoAuth,
    dataset_id: str,
    body: dict | None = None,
    debug_loop: bool = False,
    *,  # Make following params keyword-only
    context: RouteContext | None = None,
    **context_kwargs,
):
    """List all partitions for a dataset."""

    body = body or generate_list_partitions_body()

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/partition/list"

    offset_params = {
        "offset": "offset",
        "limit": "limit",
    }

    def arr_fn(res) -> list[dict]:
        return res.response

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        body=body,
        offset_params_in_body=True,
        offset_params=offset_params,
        loop_until_end=True,
        debug_loop=debug_loop,
        context=context,
    )

    if res.status == 404 and res.response == "Not Found":
        raise DatasetNotFoundError(dataset_id=dataset_id, res=res)

    if not res.is_success:
        raise Dataset_GET_Error(dataset_id=dataset_id, res=res)

    return res
