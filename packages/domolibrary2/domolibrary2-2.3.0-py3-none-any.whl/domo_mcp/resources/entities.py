"""
Domo Entity Resources for MCP Server

Provides URI-based resources for accessing Domo entities.
Resources follow the domo:// URI scheme for consistent access.
"""

import json

from domo_mcp.auth_context import get_auth_from_env
from domo_mcp.server import mcp
from domolibrary2.routes import (
    dataset as dataset_routes,
    user as user_routes,
)


@mcp.resource("domo://instance")
async def get_instance_info() -> str:
    """Get information about the connected Domo instance."""
    auth = get_auth_from_env()
    return json.dumps(
        {
            "domo_instance": auth.domo_instance,
            "instance_url": f"https://{auth.domo_instance}.domo.com",
        }
    )


@mcp.resource("domo://users/{user_id}")
async def get_user_resource(user_id: str) -> str:
    """Get a Domo user by ID as a resource.

    Args:
        user_id: The unique identifier of the user
    """
    auth = get_auth_from_env()

    try:
        res = await user_routes.get_by_id(auth=auth, user_id=user_id)
        return json.dumps(res.response)
    except user_routes.User_GET_Error as e:
        return json.dumps({"error": str(e), "user_id": user_id})


@mcp.resource("domo://datasets/{dataset_id}")
async def get_dataset_resource(dataset_id: str) -> str:
    """Get a Domo dataset by ID as a resource.

    Args:
        dataset_id: The unique identifier of the dataset
    """
    auth = get_auth_from_env()

    try:
        res = await dataset_routes.get_dataset_by_id(auth=auth, dataset_id=dataset_id)
        return json.dumps(res.response)
    except dataset_routes.Dataset_GET_Error as e:
        return json.dumps({"error": str(e), "dataset_id": dataset_id})


@mcp.resource("domo://datasets/{dataset_id}/schema")
async def get_dataset_schema_resource(dataset_id: str) -> str:
    """Get the schema for a Domo dataset as a resource.

    Args:
        dataset_id: The unique identifier of the dataset
    """
    auth = get_auth_from_env()

    try:
        res = await dataset_routes.get_schema(auth=auth, dataset_id=dataset_id)
        return json.dumps(res.response)
    except dataset_routes.Dataset_GET_Error as e:
        return json.dumps({"error": str(e), "dataset_id": dataset_id})
