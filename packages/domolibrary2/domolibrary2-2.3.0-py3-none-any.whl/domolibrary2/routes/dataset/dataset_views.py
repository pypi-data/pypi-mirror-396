"""Dataset view operations."""

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
from .exceptions import Dataset_GET_Error


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_dataset_view_schema_indexed(
    auth: DomoAuth,
    dataset_id: str,
    include_data_control_column_details: bool = True,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get the indexed schema for a dataset view with optional data control column details.

    This endpoint returns the schema structure for a dataset view, including:
    - Column definitions with types and visibility
    - SELECT query structure
    - View template information
    - Data control column details (if requested)

    Args:
        auth: Authentication object
        dataset_id: The dataset view ID
        include_data_control_column_details: If True, includes data control column details
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing:
        - name: View name
        - tables: Array of tables with column definitions
        - select: SELECT query structure
        - dataSourceId: Dataset ID
        - versionId: Version ID
        - viewTemplate: Template information with select string and fromItemInfo
        - dataControlDetails: Data control column details (if requested)

    Raises:
        Dataset_GET_Error: If schema retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/schema/indexed"

    params = {}
    if include_data_control_column_details:
        params["options"] = "INCLUDE_DATA_CONTROL_COLUMN_DETAILS"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        params=params,
        context=context,
    )

    if not res.is_success:
        raise Dataset_GET_Error(dataset_id=dataset_id, res=res)

    return res
