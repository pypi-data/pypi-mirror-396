"""
Dataset Tools for Domo MCP Server

Provides tools for managing datasets in Domo including querying data,
retrieving metadata, and managing dataset sharing.
"""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp
from domolibrary2.routes import dataset as dataset_routes


class DatasetInfo(BaseModel):
    """Structured output for dataset metadata."""

    id: str = Field(description="Dataset ID")
    name: str = Field(description="Dataset name")
    description: str | None = Field(default=None, description="Dataset description")
    owner_id: str | None = Field(default=None, description="Owner user ID")
    owner_name: str | None = Field(default=None, description="Owner display name")
    row_count: int | None = Field(default=None, description="Number of rows")
    column_count: int | None = Field(default=None, description="Number of columns")
    created_at: str | None = Field(default=None, description="Creation timestamp")
    updated_at: str | None = Field(default=None, description="Last update timestamp")
    pdp_enabled: bool | None = Field(default=None, description="Whether PDP is enabled")


class QueryResult(BaseModel):
    """Structured output for dataset query results."""

    columns: list[str] = Field(description="Column names")
    rows: list[list] = Field(description="Query result rows")
    row_count: int = Field(description="Number of rows returned")
    datasource: str | None = Field(default=None, description="Datasource name")


class DatasetColumn(BaseModel):
    """Schema information for a dataset column."""

    name: str = Field(description="Column name")
    type: str = Field(description="Column data type")
    description: str | None = Field(default=None, description="Column description")


class DatasetSchema(BaseModel):
    """Structured output for dataset schema."""

    dataset_id: str = Field(description="Dataset ID")
    columns: list[DatasetColumn] = Field(description="List of columns in the dataset")


def _parse_dataset(data: dict) -> DatasetInfo:
    """Parse dataset data from API response."""
    owner = data.get("owner", {}) or {}
    return DatasetInfo(
        id=str(data.get("id", "")),
        name=data.get("name", ""),
        description=data.get("description"),
        owner_id=str(owner.get("id", "")) if owner.get("id") else None,
        owner_name=owner.get("name"),
        row_count=data.get("rows"),
        column_count=data.get("columns"),
        created_at=data.get("createdAt"),
        updated_at=data.get("updatedAt"),
        pdp_enabled=data.get("pdpEnabled"),
    )


@mcp.tool()
async def get_dataset(
    dataset_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> DatasetInfo:
    """Get metadata for a specific dataset.

    Args:
        dataset_id: The unique identifier of the dataset
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching dataset {dataset_id}")

    try:
        res = await dataset_routes.get_dataset_by_id(auth=auth, dataset_id=dataset_id)
        return _parse_dataset(res.response)

    except dataset_routes.Dataset_GET_Error as e:
        await ctx.error(f"Failed to get dataset {dataset_id}: {e}")
        raise


@mcp.tool()
async def query_dataset(
    dataset_id: str,
    sql: str,
    ctx: Context[ServerSession, DomoContext],
) -> QueryResult:
    """Execute a SQL query against a Domo dataset.

    Args:
        dataset_id: The ID of the dataset to query
        sql: SQL query to execute (e.g., "SELECT * FROM table LIMIT 100")
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Querying dataset {dataset_id}")

    try:
        res = await dataset_routes.query_dataset_private(
            auth=auth,
            dataset_id=dataset_id,
            sql=sql,
        )
        data = res.response or {}

        columns = data.get("columns", [])
        rows = data.get("rows", [])

        await ctx.info(f"Query returned {len(rows)} rows")
        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            datasource=data.get("datasource"),
        )

    except dataset_routes.QueryRequestError as e:
        await ctx.error(f"Query failed: {e}")
        raise


@mcp.tool()
async def get_dataset_schema(
    dataset_id: str,
    ctx: Context[ServerSession, DomoContext],
) -> DatasetSchema:
    """Get the schema (columns and types) for a dataset.

    Args:
        dataset_id: The ID of the dataset
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching schema for dataset {dataset_id}")

    try:
        res = await dataset_routes.get_schema(auth=auth, dataset_id=dataset_id)
        schema_data = res.response or {}

        columns = []
        for col in schema_data.get("columns", []):
            columns.append(
                DatasetColumn(
                    name=col.get("name", ""),
                    type=col.get("type", ""),
                    description=col.get("description"),
                )
            )

        return DatasetSchema(dataset_id=dataset_id, columns=columns)

    except dataset_routes.Dataset_GET_Error as e:
        await ctx.error(f"Failed to get schema: {e}")
        raise


@mcp.tool()
async def share_dataset(
    dataset_id: str,
    user_ids: list[str],
    access_level: str,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Share a dataset with specified users.

    Args:
        dataset_id: The ID of the dataset to share
        user_ids: List of user IDs to share with
        access_level: Access level - "READ", "WRITE", or "OWNER"
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Sharing dataset {dataset_id} with {len(user_ids)} users")

    try:
        # Map access level string to enum
        access_enum = dataset_routes.ShareDataset_AccessLevelEnum[access_level.upper()]

        await dataset_routes.share_dataset(
            auth=auth,
            dataset_id=dataset_id,
            user_ids=user_ids,
            access_level=access_enum,
        )

        await ctx.info(f"Dataset {dataset_id} shared successfully")
        return f"Successfully shared dataset {dataset_id} with {len(user_ids)} users at {access_level} level"

    except dataset_routes.ShareDataset_Error as e:
        await ctx.error(f"Failed to share dataset: {e}")
        raise


class DatasetSearchResult(BaseModel):
    """Structured output for dataset search result."""

    id: str = Field(description="Dataset ID")
    name: str = Field(description="Dataset name")
    description: str | None = Field(default=None, description="Dataset description")
    owner_name: str | None = Field(default=None, description="Owner display name")
    row_count: int | None = Field(default=None, description="Number of rows")


class DatasetSearchResults(BaseModel):
    """Structured output for list of dataset search results."""

    datasets: list[DatasetSearchResult] = Field(description="List of matching datasets")
    total_count: int = Field(description="Total number of datasets returned")


def _parse_search_result(data: dict) -> DatasetSearchResult:
    """Parse dataset search result from API response.

    The datacenter search API returns results with different field names than
    the dataset metadata API. This handles both formats:
    - Datacenter: id/databaseId, name/title, ownerName, rowCount
    - Dataset API: id, name, owner.name, rows
    """
    return DatasetSearchResult(
        id=str(data.get("id", data.get("databaseId", ""))),
        name=data.get("name", data.get("title", "")),
        description=data.get("description"),
        owner_name=data.get("ownerName") or data.get("owner", {}).get("name"),
        row_count=data.get("rowCount") or data.get("rows"),
    )


@mcp.tool()
async def search_datasets(
    ctx: Context[ServerSession, DomoContext],
    search_text: str = Field(
        default="", description="Text to search for in dataset names (optional)"
    ),
    maximum: int = Field(
        default=100, description="Maximum number of datasets to return"
    ),
) -> DatasetSearchResults:
    """Search for datasets by name.

    Searches the datacenter for datasets matching the specified criteria.
    If no search_text is provided, returns all datasets up to the maximum limit.

    Args:
        search_text: Text to search for in dataset names (wildcards supported)
        maximum: Maximum number of datasets to return (default: 100)
    """
    auth = ctx.request_context.lifespan_context.auth
    search_desc = f"'{search_text}'" if search_text else "all datasets"
    await ctx.info(f"Searching datasets: {search_desc}")

    try:
        res = await dataset_routes.search_datasets(
            auth=auth,
            search_text=search_text if search_text else None,
            maximum=maximum,
        )

        datasets_data = res.response or []
        datasets = [_parse_search_result(d) for d in datasets_data]

        await ctx.info(f"Found {len(datasets)} datasets")
        return DatasetSearchResults(datasets=datasets, total_count=len(datasets))

    except dataset_routes.Dataset_GET_Error as e:
        await ctx.error(f"Failed to search datasets: {e}")
        raise
