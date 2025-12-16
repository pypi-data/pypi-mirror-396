"""
AppDb Route Functions

This module provides functions for managing Domo AppDb datastores, collections, and documents.
The functionality is organized into logical submodules while maintaining backward compatibility.

Submodules:
    exceptions: Exception classes for AppDb operations
    datastores: Datastore management functions
    collections: Collection management functions
    documents: Document management functions

Exception Classes:
    AppDb_GET_Error: Raised when AppDb retrieval operations fail
    SearchAppDbNotFoundError: Raised when AppDb search returns no results
    AppDb_CRUD_Error: Raised when AppDb create/update/delete operations fail

Datastore Functions:
    get_datastores: Retrieve all datastores
    get_datastore_by_id: Retrieve a specific datastore by ID
    get_collections_from_datastore: Get collections from a specific datastore
    create_datastore: Create a new datastore

Collection Functions:
    create_collection: Create a new collection in a datastore
    get_collections: Retrieve all collections
    get_collection_by_id: Retrieve a specific collection by ID
    modify_collection_permissions: Modify collection permissions

Document Functions:
    get_documents_from_collection: Get documents from a collection
    get_collection_document_by_id: Get a specific document by ID
    create_document: Create a new document in a collection
    update_document: Update an existing document

Enums:
    Collection_Permission_Enum: Permissions for collection access
"""

# Import all functions and classes for backward compatibility
from .collections import (
    Collection_Permission_Enum,
    create_collection,
    get_collection_by_id,
    get_collections,
    modify_collection_permissions,
)
from .datastores import (
    create_datastore,
    get_collections_from_datastore,
    get_datastore_by_id,
    get_datastores,
)
from .documents import (
    create_document,
    get_collection_document_by_id,
    get_documents_from_collection,
    update_document,
)
from .exceptions import (
    AppDb_CRUD_Error,
    AppDb_GET_Error,
    SearchAppDbNotFoundError,
)

__all__ = [
    # Exception classes
    "AppDb_GET_Error",
    "SearchAppDbNotFoundError",
    "AppDb_CRUD_Error",
    # Datastore functions
    "get_datastores",
    "get_datastore_by_id",
    "get_collections_from_datastore",
    "create_datastore",
    # Collection functions
    "create_collection",
    "get_collections",
    "get_collection_by_id",
    "modify_collection_permissions",
    "Collection_Permission_Enum",
    # Document functions
    "get_documents_from_collection",
    "get_collection_document_by_id",
    "create_document",
    "update_document",
]
