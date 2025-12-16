"""Dataset core CRUD operations."""

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
from .exceptions import Dataset_CRUD_Error, Dataset_GET_Error, DatasetNotFoundError


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataset_by_id(
    dataset_id: str,  # dataset id from URL
    auth: DomoAuth | None = None,  # requires full authentication
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:  # returns metadata about a dataset
    """retrieve dataset metadata"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}"  # type: ignore

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if res.status == 404 and res.response == "Not Found":
        raise DatasetNotFoundError(dataset_id=dataset_id, res=res)

    if not res.is_success:
        raise Dataset_GET_Error(dataset_id=dataset_id, res=res)

    return res


def generate_create_dataset_body(
    dataset_name: str, dataset_type: str = "API", schema: dict | None = None
) -> dict:
    schema = schema or {
        "columns": [
            {"type": "STRING", "name": "Friend"},
            {"type": "STRING", "name": "Attending"},
        ]
    }

    return {
        "userDefinedType": dataset_type,
        "dataSourceName": dataset_name,
        "schema": schema,
    }


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create(
    auth: DomoAuth,
    dataset_name: str,
    dataset_type: str = "api",
    schema: dict | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    body = generate_create_dataset_body(
        dataset_name=dataset_name, dataset_type=dataset_type, schema=schema
    )

    url = f"https://{auth.domo_instance}.domo.com/api/data/v2/datasources"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        context=context,
    )

    if not res.is_success:
        raise Dataset_CRUD_Error(res=res)

    return res


def generate_enterprise_toolkit_body(
    dataset_name: str,
    dataset_description: str,
    datasource_type: str,
    columns_schema: list[dict],
) -> dict:
    return {
        "dataSourceName": dataset_name,
        "dataSourceDescription": dataset_description,
        "dataSourceType": datasource_type,
        "schema": {"columns": columns_schema},
    }


def generate_remote_domostats_body(
    dataset_name: str,
    dataset_description: str,
    columns_schema: list[dict] | None = None,
) -> dict:
    return generate_enterprise_toolkit_body(
        dataset_name=dataset_name,
        dataset_description=dataset_description,
        columns_schema=columns_schema
        or [{"type": "STRING", "name": "Remote Domo Stats"}],
        datasource_type="ObservabilityMetrics",
    )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_dataset_enterprise_tookit(
    auth: DomoAuth,
    payload: dict,  # call generate_enterprise_toolkit_body
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/executor/v1/datasets"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=payload,
        context=context,
    )

    if not res.is_success:
        raise Dataset_CRUD_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def delete_partition_stage_1(
    auth: DomoAuth,
    dataset_id: str,
    dataset_partition_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """Delete partition has 3 stages
    # Stage 1. This marks the data version associated with the partition tag as deleted.
    It does not delete the partition tag or remove the association between the partition tag and data version.
    There should be no need to upload an empty file – step #3 will remove the data from Adrenaline.
    # update on 9/9/2022 based on the conversation with Greg Swensen"""

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/tag/{dataset_partition_id}/data"

    res = await gd.get_data(
        auth=auth,
        method="DELETE",
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
async def delete_partition_stage_2(
    auth: DomoAuth,
    dataset_id: str,
    dataset_partition_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    """This will remove the partition association so that it doesn't show up in the list call.
    Technically, this is not required as a partition against a deleted data version will not count against the 400 partition limit
    but as the current partitions api doesn't make that clear, cleaning these up will make it much easier for you to manage.
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/partition/{dataset_partition_id}"

    res = await gd.get_data(
        auth=auth,
        method="DELETE",
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
async def delete(
    auth: DomoAuth,
    dataset_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}?deleteMethod=hard"

    res = await gd.get_data(
        auth=auth,
        method="DELETE",
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
async def search_datasets(
    auth: DomoAuth,
    search_text: str | None = None,
    maximum: int | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Search for datasets by name.

    Uses the datacenter search API to find datasets matching the search criteria.

    Args:
        auth: Authentication object
        search_text: Optional text to search for in dataset names (wildcards supported)
        maximum: Maximum number of results to return
        return_raw: Return raw response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing list of matching datasets

    Raises:
        Dataset_GET_Error: If search operation fails
    """

    from ..datacenter import Datacenter_Enum, search_datacenter
    from ..datacenter.exceptions import SearchDatacenterNoResultsFoundError

    try:
        res = await search_datacenter(
            auth=auth,
            search_text=search_text,
            entity_type=Datacenter_Enum.DATASET,
            maximum=maximum,
            context=context,
        )
    except SearchDatacenterNoResultsFoundError:
        # No results is valid - return empty list
        res = rgd.ResponseGetData(
            status=200,
            response=[],
            is_success=True,
        )

    if return_raw:
        return res

    if not res.is_success:
        raise Dataset_GET_Error(res=res)

    return res
