"""
Cloud Amplifier Route Functions

This module provides functions for managing Domo Cloud Amplifier integrations,
including integration management, warehouse configuration, and database operations.

The module is organized into functional areas:
- core: Core integration management (get, create, update, delete)
- metadata: Metadata and schema operations (databases, schemas, tables, federated metadata)
- utils: Utility functions for request body generation
- exceptions: All Cloud Amplifier-related exception classes

Functions:
    get_integrations: Retrieve all Cloud Amplifier integrations
    get_integration_by_id: Retrieve a specific integration by ID
    get_integration_permissions: Get permissions for integrations
    check_for_colliding_datasources: Check for dataset collisions
    get_federated_source_metadata: Retrieve federated source metadata
    get_integration_warehouses: list available compute warehouses
    get_databases: list databases for an integration
    get_schemas: list schemas for a database
    get_tables: list tables for a schema
    convert_federated_to_cloud_amplifier: Convert federated dataset to Cloud Amplifier
    create_integration: Create a new Cloud Amplifier integration
    update_integration_warehouses: Update compute warehouses
    update_integration: Update an existing integration
    delete_integration: Delete a Cloud Amplifier integration

Utility Functions:
    create_integration_body: Generate request body for integration creation

Exception Classes:
    CloudAmplifier_GET_Error: Raised when integration retrieval fails
    SearchCloudAmplifierNotFoundError: Raised when integration search returns no results
    CloudAmplifier_CRUD_Error: Raised when integration create/update/delete operations fail
    Cloud_Amplifier_Error: Legacy error class (deprecated)
"""

# Import core functions
from .core import (
    convert_federated_to_cloud_amplifier,
    create_integration,
    delete_integration,
    get_integration_by_id,
    get_integration_permissions,
    get_integration_warehouses,
    get_integrations,
    update_integration,
    update_integration_warehouses,
)

# Import all exception classes
from .exceptions import (
    Cloud_Amplifier_Error,
    CloudAmplifier_CRUD_Error,
    CloudAmplifier_GET_Error,
    SearchCloudAmplifierNotFoundError,
)

# Import metadata functions
from .metadata import (
    check_for_colliding_datasources,
    get_databases,
    get_federated_source_metadata,
    get_schemas,
    get_tables,
)

# Import utility functions
from .utils import ENGINES, create_integration_body

__all__ = [
    # Type definitions
    "ENGINES",
    # Exception classes
    "CloudAmplifier_GET_Error",
    "SearchCloudAmplifierNotFoundError",
    "CloudAmplifier_CRUD_Error",
    "Cloud_Amplifier_Error",  # Deprecated, kept for backward compatibility
    # Core functions
    "get_integrations",
    "get_integration_by_id",
    "get_integration_permissions",
    "get_integration_warehouses",
    "create_integration",
    "update_integration",
    "update_integration_warehouses",
    "delete_integration",
    "convert_federated_to_cloud_amplifier",
    # Metadata functions
    "check_for_colliding_datasources",
    "get_federated_source_metadata",
    "get_databases",
    "get_schemas",
    "get_tables",
    # Utility functions
    "create_integration_body",
]
