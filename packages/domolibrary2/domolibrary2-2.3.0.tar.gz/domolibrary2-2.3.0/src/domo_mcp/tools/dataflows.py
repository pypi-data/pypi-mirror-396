"""
Dataflow Tools for Domo MCP Server

Provides tools for managing dataflows in Domo including listing,
monitoring execution history, and triggering dataflow runs.
"""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from domo_mcp.auth_context import DomoContext
from domo_mcp.server import mcp
from domolibrary2.routes import dataflow as dataflow_routes


class DataflowInfo(BaseModel):
    """Structured output for dataflow metadata."""

    id: int = Field(description="Dataflow ID")
    name: str = Field(description="Dataflow name")
    description: str | None = Field(default=None, description="Dataflow description")
    dataflow_type: str | None = Field(default=None, description="Type of dataflow")
    owner_id: str | None = Field(default=None, description="Owner user ID")
    owner_name: str | None = Field(default=None, description="Owner display name")
    enabled: bool | None = Field(
        default=None, description="Whether dataflow is enabled"
    )
    last_execution_status: str | None = Field(
        default=None, description="Status of last execution"
    )


class DataflowList(BaseModel):
    """Structured output for list of dataflows."""

    dataflows: list[DataflowInfo] = Field(description="List of dataflows")
    total_count: int = Field(description="Total number of dataflows returned")


class DataflowExecution(BaseModel):
    """Structured output for dataflow execution details."""

    execution_id: str = Field(description="Execution ID")
    dataflow_id: int = Field(description="Dataflow ID")
    status: str = Field(description="Execution status")
    start_time: str | None = Field(default=None, description="Execution start time")
    end_time: str | None = Field(default=None, description="Execution end time")
    duration_seconds: int | None = Field(
        default=None, description="Execution duration in seconds"
    )
    error_message: str | None = Field(
        default=None, description="Error message if failed"
    )


class ExecutionHistory(BaseModel):
    """Structured output for dataflow execution history."""

    dataflow_id: int = Field(description="Dataflow ID")
    executions: list[DataflowExecution] = Field(description="List of executions")
    total_count: int = Field(description="Total number of executions")


def _parse_dataflow(data: dict) -> DataflowInfo:
    """Parse dataflow data from API response."""
    owner = data.get("owner", {}) or {}
    return DataflowInfo(
        id=data.get("id", 0),
        name=data.get("name", ""),
        description=data.get("description"),
        dataflow_type=data.get("dapDataFlowType") or data.get("type"),
        owner_id=str(owner.get("id", "")) if owner.get("id") else None,
        owner_name=owner.get("name") or owner.get("displayName"),
        enabled=data.get("enabled"),
        last_execution_status=(
            data.get("lastExecution", {}).get("state")
            if data.get("lastExecution")
            else None
        ),
    )


def _parse_execution(data: dict, dataflow_id: int) -> DataflowExecution:
    """Parse execution data from API response."""
    return DataflowExecution(
        execution_id=str(data.get("id", "")),
        dataflow_id=dataflow_id,
        status=data.get("state", ""),
        start_time=data.get("startedAt"),
        end_time=data.get("endedAt"),
        duration_seconds=data.get("runTime"),
        error_message=data.get("errorMessage"),
    )


@mcp.tool()
async def get_dataflows(
    ctx: Context[ServerSession, DomoContext],
    limit: int = Field(
        default=100, description="Maximum number of dataflows to return"
    ),
) -> DataflowList:
    """List all dataflows in the Domo instance.

    Returns a list of all dataflows with their metadata including
    name, type, owner, and last execution status.
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching dataflows from {auth.domo_instance}")

    try:
        res = await dataflow_routes.get_dataflows(auth=auth)
        dataflows_data = res.response or []

        # Apply limit
        dataflows_data = dataflows_data[:limit]

        dataflows = [_parse_dataflow(df) for df in dataflows_data]

        await ctx.info(f"Found {len(dataflows)} dataflows")
        return DataflowList(dataflows=dataflows, total_count=len(dataflows))

    except dataflow_routes.GET_Dataflow_Error as e:
        await ctx.error(f"Failed to get dataflows: {e}")
        raise


@mcp.tool()
async def get_dataflow_by_id(
    dataflow_id: int,
    ctx: Context[ServerSession, DomoContext],
) -> DataflowInfo:
    """Get details for a specific dataflow.

    Args:
        dataflow_id: The unique identifier of the dataflow
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching dataflow {dataflow_id}")

    try:
        res = await dataflow_routes.get_dataflow_by_id(
            auth=auth, dataflow_id=dataflow_id
        )
        return _parse_dataflow(res.response)

    except dataflow_routes.GET_Dataflow_Error as e:
        await ctx.error(f"Failed to get dataflow {dataflow_id}: {e}")
        raise


@mcp.tool()
async def get_dataflow_execution_history(
    dataflow_id: int,
    ctx: Context[ServerSession, DomoContext],
    limit: int = Field(
        default=10, description="Maximum number of executions to return"
    ),
) -> ExecutionHistory:
    """Get the execution history for a dataflow.

    Args:
        dataflow_id: The ID of the dataflow
        limit: Maximum number of executions to return (default: 10)
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Fetching execution history for dataflow {dataflow_id}")

    try:
        res = await dataflow_routes.get_dataflow_execution_history(
            auth=auth, dataflow_id=dataflow_id
        )
        executions_data = res.response or []

        # Apply limit
        executions_data = executions_data[:limit]

        executions = [_parse_execution(ex, dataflow_id) for ex in executions_data]

        await ctx.info(f"Found {len(executions)} executions")
        return ExecutionHistory(
            dataflow_id=dataflow_id,
            executions=executions,
            total_count=len(executions),
        )

    except dataflow_routes.GET_Dataflow_Error as e:
        await ctx.error(f"Failed to get execution history: {e}")
        raise


@mcp.tool()
async def execute_dataflow(
    dataflow_id: int,
    ctx: Context[ServerSession, DomoContext],
) -> str:
    """Trigger execution of a dataflow.

    Args:
        dataflow_id: The ID of the dataflow to execute
    """
    auth = ctx.request_context.lifespan_context.auth
    await ctx.info(f"Triggering execution for dataflow {dataflow_id}")

    try:
        await dataflow_routes.execute_dataflow(auth=auth, dataflow_id=dataflow_id)

        await ctx.info(f"Dataflow {dataflow_id} execution triggered successfully")
        return f"Successfully triggered execution for dataflow {dataflow_id}"

    except dataflow_routes.CRUD_Dataflow_Error as e:
        await ctx.error(f"Failed to execute dataflow: {e}")
        raise
