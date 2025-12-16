"""
Datacenter Package

This package provides datacenter management functionality for searching, lineage, and sharing.

Modules:
    exceptions: Exception classes for datacenter operations
    core: Core datacenter functions, enums, and utilities
"""

# Import route functions, utility functions, TypedDict, and all enums
from .core import (
    Datacenter_Enum,
    Datacenter_Filter_Field_Certification_Enum,
    Datacenter_Filter_Field_Enum,
    Dataflow_Type_Filter_Enum,
    LineageNode,
    ShareResource_Enum,
    generate_search_datacenter_account_body,
    generate_search_datacenter_body,
    generate_search_datacenter_filter,
    generate_search_datacenter_filter_search_term,
    get_connectors,
    get_lineage_upstream,
    search_datacenter,
    share_resource,
)

# Import all exception classes
from .exceptions import (
    DatacenterGetError,
    SearchDatacenterNoResultsFoundError,
    ShareResourceError,
)

# Backward compatibility alias
SearchDatacenter_GET_Error = DatacenterGetError

__all__ = [
    # Exception classes
    "DatacenterGetError",
    "SearchDatacenterNoResultsFoundError",
    "ShareResourceError",
    "SearchDatacenter_GET_Error",  # Backward compatibility alias
    # Enums
    "Datacenter_Enum",
    "Dataflow_Type_Filter_Enum",
    "Datacenter_Filter_Field_Enum",
    "Datacenter_Filter_Field_Certification_Enum",
    "ShareResource_Enum",
    # TypedDict
    "LineageNode",
    # Utility functions
    "generate_search_datacenter_filter",
    "generate_search_datacenter_filter_search_term",
    "generate_search_datacenter_body",
    "generate_search_datacenter_account_body",
    # Route functions
    "search_datacenter",
    "get_connectors",
    "get_lineage_upstream",
    "share_resource",
]
