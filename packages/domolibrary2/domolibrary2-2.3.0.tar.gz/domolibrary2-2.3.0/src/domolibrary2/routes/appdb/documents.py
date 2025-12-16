"""
AppDb Document Functions

This module provides functions for managing Domo AppDb documents including
retrieval, creation, and update operations.

Functions:
    get_documents_from_collection: Get documents from a collection
    get_collection_document_by_id: Get a specific document by ID
    create_document: Create a new document in a collection
    update_document: Update an existing document
"""

from typing import Any

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
from .exceptions import AppDb_CRUD_Error, AppDb_GET_Error, SearchAppDbNotFoundError

__all__ = [
    "get_documents_from_collection",
    "get_collection_document_by_id",
    "create_document",
    "update_document",
]


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_documents_from_collection(
    auth: DomoAuth,
    collection_id: str,
    query: dict[str, Any] | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get documents from a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        query: Optional query parameters for document filtering
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing documents information

    Raises:
        AppDb_GET_Error: If documents retrieval fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v2/collections/{collection_id}/documents/query"

    query = query or {}

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=query,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_GET_Error(
            appdb_id=collection_id,
            message=f"unable to query documents in collection - {collection_id}",
            res=res,
        )

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def get_collection_document_by_id(
    auth: DomoAuth,
    collection_id: str,
    document_id: str,
    query: dict[str, Any] | None = None,
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Get a specific document by ID from a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        document_id: Unique identifier for the document
        query: Optional query parameters
        context: Optional RouteContext for request configuration
        return_raw: Return raw API response without processing
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing document information

    Raises:
        AppDb_GET_Error: If document retrieval fails
        SearchAppDbNotFoundError: If document with specified ID doesn't exist
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/collections/{collection_id}/documents/{document_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        body=query,
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchAppDbNotFoundError(
                search_criteria=f"document_id: {document_id} in collection: {collection_id}",
                res=res,
            )
        raise AppDb_GET_Error(appdb_id=document_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def create_document(
    auth: DomoAuth,
    collection_id: str,
    content: dict[str, Any],
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Create a new document in a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        content: Document content to create
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing created document information

    Raises:
        AppDb_CRUD_Error: If document creation fails
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v1/collections/{collection_id}/documents"

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body={"content": content},
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise AppDb_CRUD_Error(operation="create", appdb_id=collection_id, res=res)

    return res


@gd.route_function
@log_call(
    level_name="route",
    config=LogDecoratorConfig(
        entity_extractor=DomoEntityExtractor(),
        result_processor=DomoEntityResultProcessor(),
    ),
)
async def update_document(
    auth: DomoAuth,
    collection_id: str,
    document_id: str,
    content: dict[str, Any],
    return_raw: bool = False,
    *,
    context: RouteContext | None = None,
    **context_kwargs,
) -> rgd.ResponseGetData:
    """Update an existing document in a collection.

    Args:
        auth: Authentication object containing credentials and instance info
        collection_id: Unique identifier for the collection
        document_id: Unique identifier for the document to update
        content: Updated document content
        return_raw: Return raw API response without processing
        context: RouteContext for request configuration
        **context_kwargs: Additional context parameters (session, debug_api, etc.)

    Returns:
        ResponseGetData object containing updated document information

    Raises:
        AppDb_CRUD_Error: If document update fails
        SearchAppDbNotFoundError: If document with specified ID doesn't exist
    """

    url = f"https://{auth.domo_instance}.domo.com/api/datastores/v2/collections/{collection_id}/documents/{document_id}"

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body={"content": content},
        context=context,
    )

    if return_raw:
        return res

    if not res.is_success:
        if res.status == 404:
            raise SearchAppDbNotFoundError(
                search_criteria=f"document_id: {document_id} in collection: {collection_id}",
                res=res,
            )
        raise AppDb_CRUD_Error(operation="update", appdb_id=document_id, res=res)

    return res
