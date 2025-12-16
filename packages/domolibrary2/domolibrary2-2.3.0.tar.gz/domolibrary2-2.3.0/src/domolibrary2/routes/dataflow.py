from ..auth import DomoAuth
from ..base.exceptions import RouteError
from ..client import (
    get_data as gd,
    response as rgd,
)
from ..client.context import RouteContext
from ..utils.logging import (
    DomoEntityExtractor,
    DomoEntityResultProcessor,
    LogDecoratorConfig,
    log_call,
)

__all__ = [
    "GET_Dataflow_Error",
    "CRUD_Dataflow_Error",
    "get_dataflows",
    "get_dataflow_by_id",
    "update_dataflow_definition",
    "get_dataflow_tags_by_id",
    "generate_tag_body",
    "put_dataflow_tags_by_id",
    "get_dataflow_versions",
    "get_dataflow_by_id_and_version",
    "get_dataflow_execution_history",
    "get_dataflow_execution_by_id",
    "execute_dataflow",
    "generate_search_dataflows_to_jupyter_workspaces_body",
    "search_dataflows_to_jupyter_workspaces",
]


class GET_Dataflow_Error(RouteError):
    def __init__(self, res: rgd.ResponseGetData):
        super().__init__(res=res)


class CRUD_Dataflow_Error(RouteError):
    def __init__(self, res: rgd.ResponseGetData):
        super().__init__(res=res)


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataflows(
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    domo_instance = auth.domo_instance

    url = f"https://{domo_instance}.domo.com/api/dataprocessing/v1/dataflows"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise GET_Dataflow_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataflow_by_id(
    dataflow_id: int,
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    domo_instance = auth.domo_instance

    url = f"https://{domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise GET_Dataflow_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_dataflow_definition(
    auth: DomoAuth,
    dataflow_id: int,
    dataflow_definition: dict,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    # Construct the URL
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}"

    # Make the API call
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=dataflow_definition,
        context=context,
    )

    # Check for successful response
    if not res.is_success:
        raise RouteError(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataflow_tags_by_id(
    auth: DomoAuth,
    dataflow_id: int,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    # Construct the URL for the GET request
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}/tags"

    # Make the GET request
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    # Check if the request was successful
    if not res.is_success:
        raise RouteError(res=res)

    return res


def generate_tag_body(dataflow_id: str, tag_ls: list[str]) -> dict:
    return {"flowId": dataflow_id, "tags": tag_ls}


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def put_dataflow_tags_by_id(
    auth: DomoAuth,
    dataflow_id: int,
    tag_ls: list[str],
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    # Construct the URL
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}/tags"

    # Generate the request body
    body = generate_tag_body(dataflow_id=dataflow_id, tag_ls=tag_ls)

    # Make the API call
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        context=context,
    )

    # Check for successful response
    if not res.is_success:
        raise RouteError(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataflow_versions(
    dataflow_id: int,
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}/versions"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise GET_Dataflow_Error(res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataflow_by_id_and_version(
    dataflow_id: int,
    version_id: int,
    auth: DomoAuth,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v2/dataflows/{dataflow_id}/versions/{version_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise GET_Dataflow_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataflow_execution_history(
    dataflow_id: int,
    auth: DomoAuth,
    maximum: int | None = None,
    debug_loop: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}/executions"

    def arr_fn(res):
        return res.response

    res = await gd.looper(
        auth=auth,
        url=url,
        loop_until_end=True if not maximum else False,
        method="GET",
        offset_params_in_body=False,
        offset_params={"offset": "offset", "limit": "limit"},
        arr_fn=arr_fn,
        maximum=maximum,
        limit=100,
        debug_loop=debug_loop,
        context=context,
    )

    if not res.is_success:
        raise GET_Dataflow_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataflow_execution_by_id(
    auth: DomoAuth,
    dataflow_id: int,
    execution_id: int,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}/executions/{execution_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )

    if not res.is_success:
        raise GET_Dataflow_Error(res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def execute_dataflow(
    auth: DomoAuth,
    dataflow_id: int,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}/executions"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        context=context,
    )
    if not res.is_success:
        raise CRUD_Dataflow_Error(res)

    return res


def generate_search_dataflows_to_jupyter_workspaces_body(
    filter_body: dict | None = None, dataflow_id: int | None = None
) -> dict:
    """
    Ensure the DATA_FLOW_ID filter exists in filter_body and append the given dataflow_id to it
    (only if it’s not already present).

    Args:
        filter_body (dict): e.g. {"filters":[{"type":"DATA_FLOW_ID","values":[116]}]}
        dataflow_id (int): ID to add under the DATA_FLOW_ID filter
    """

    filter_body = filter_body or {}

    if not dataflow_id:
        return filter_body

    # 1. Make sure there's a filters list
    filters = filter_body.setdefault("filters", [])

    # 2. Try to find an existing DATA_FLOW_ID filter
    for f in filters:
        if f.get("type") == "DATA_FLOW_ID":
            # append if it's new
            if dataflow_id not in f["values"]:
                f["values"].append(dataflow_id)
            break
    else:
        # 3. If we never broke out, no filter existed—create it
        filters.append({"type": "DATA_FLOW_ID", "values": [dataflow_id]})

    return filter_body


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_dataflows_to_jupyter_workspaces(
    auth: DomoAuth,
    dataflow_id: int | None = None,
    return_raw: bool = False,
    filter_body: dict | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
):
    filter_body = generate_search_dataflows_to_jupyter_workspaces_body(
        filter_body=filter_body, dataflow_id=dataflow_id
    )

    res = await gd.get_data(
        url=f"https://{auth.domo_instance}.domo.com/api/datascience/v1/search/notebooks",
        auth=auth,
        method="POST",
        body=filter_body,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise RouteError(res=res)

    res.response = res.response["notebooks"]

    if dataflow_id:
        if not res.response:
            raise RouteError(
                res=res,
                entity_id=dataflow_id,
                message="unable to retrieve jupyter notebook data for dataflow",
            )

        res.response = res.response[-1]

    return res
