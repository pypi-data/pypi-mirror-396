from typing import Literal

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
    "Fileset_GET_Error",
    "Fileset_CRUD_Error",
    "EmbedData_Type",
    "create_filesets_index",
    "embed_image",
    "get_fileset_by_id",
    "search_fileset_files",
    "get_data_file_by_id",
]


class Fileset_GET_Error(RouteError):
    """Raised when fileset retrieval operations fail."""

    def __init__(
        self,
        fileset_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or "Fileset retrieval failed",
            entity_id=fileset_id,
            res=res,
            **kwargs,
        )


class Fileset_CRUD_Error(RouteError):
    """Raised when fileset create, update, or delete operations fail."""

    def __init__(
        self,
        operation: str,
        fileset_id: str | None = None,
        message: str | None = None,
        res=None,
        **kwargs,
    ):
        super().__init__(
            message=message or f"Fileset {operation} operation failed",
            entity_id=fileset_id,
            res=res,
            **kwargs,
        )


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_filesets_index(
    auth: DomoAuth,
    index_id: str,
    embedding_model: str = "domo.domo_ai.domo-embed-text-multilingual-v1:cohere",
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Creates a new vectorDB index."""

    url = f"{auth.domo_instance}.domo.com/api/recall/v1/indexes"

    payload = {
        "indexId": index_id,
        "embeddingModel": embedding_model,
    }
    res = await gd.get_data(
        url,
        method="POST",
        body=payload,
        auth=auth,
        context=context,
    )

    if not res.is_success:
        raise Fileset_CRUD_Error(operation="create index", res=res)

    return res


EmbedData_Type = Literal["base64"]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def embed_image(
    auth: DomoAuth,
    body: dict | None = None,
    image_data: str | None = None,
    media_type: str | None = None,
    data_type: EmbedData_Type = "base64",
    model: str = "domo.domo_ai",
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Create an embedding for a base64 encoded image using Domo's AI services.
    """
    # Utility function is_valid_base64_image should be called by the orchestrator before this.
    # This route function assumes valid base64 data.

    api_url = f"https://{auth.domo_instance}.domo.com/api/ai/v1/embedding/image"

    body = body or {
        "input": [{"type": "", "mediaType": "", "data": ""}],
        "model": "",
    }
    if image_data:
        body["input"][0].update({"data": image_data})

    if media_type:
        body["input"][0].update({"mediaType": media_type})

    if data_type:
        body["input"][0].update({"type": data_type})

    if model:
        body.update({"model": model})

    res = await gd.get_data(
        auth=auth,
        url=api_url,
        method="POST",
        body=body,
        context=context,
    )
    if not res.is_success:
        raise Fileset_CRUD_Error(operation="embed image", res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_fileset_by_id(
    auth: DomoAuth,
    fileset_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/files/v1/filesets/{fileset_id}"
    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        context=context,
    )

    if not res.is_success:
        raise Fileset_GET_Error(fileset_id=fileset_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def search_fileset_files(
    auth: DomoAuth,
    domo_fileset_id: str,
    body: dict | None = None,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/files/v1/filesets/{domo_fileset_id}/files/search?directoryPath=&immediateChildren=true"

    if not body:
        # default body will pull all files within the given fileset_id
        body = {
            "fieldSort": [{"field": "created", "order": "DESC"}],
            "filters": [],
            "dateFilters": [],
        }

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        context=context,
    )
    if not res.is_success:
        raise Fileset_GET_Error(fileset_id=domo_fileset_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_data_file_by_id(
    auth: DomoAuth,
    file_id: str,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """
    Retrieves the content of a data file from Domo.
    """

    url = f"https://{auth.domo_instance}.domo.com/data/v1/data-files/{file_id}"
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        context=context,
    )
    if not res.is_success:
        raise Fileset_GET_Error(fileset_id=file_id, res=res)
    return res
