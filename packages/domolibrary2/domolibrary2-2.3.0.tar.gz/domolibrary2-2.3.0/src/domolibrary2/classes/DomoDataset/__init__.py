"""
DomoDataset Package

This package provides comprehensive dataset management functionality for Domo instances,
including dataset operations, schema management, PDP policies, streaming capabilities,
and connector management.

Classes:
    DomoDataset_Default: Core dataset operations and management
    DomoDatasets: Manager class for searching and listing datasets
    FederatedDomoDataset: Federated dataset functionality
    DomoPublishDataset: Published dataset operations
    DomoDataset_Schema: Dataset schema management
    DomoDataset_Schema_Column: Individual column management
    PDP_Policy: PDP policy management
    DomoStream: Dataset streaming operations
    DomoConnector: Dataset connector management

Exceptions:
    DatasetNotFoundError: Raised when dataset cannot be found
    QueryRequestError: Raised when dataset query fails
    DatasetSchema_InvalidSchemaError: Raised when schema validation fails
    SearchPDP_NotFound: Raised when PDP policy search returns no results

Enums:
    DatasetSchema_Types: Available dataset schema types
    ShareDataset_AccessLevelEnum: Dataset sharing access levels
    StreamConfig_Mapping_snowflake: Snowflake stream mapping types
"""

# Import all classes and functionality from the package modules
from .ai_readiness import (
    AI_Readiness_Column,
    DomoDataset_AI_Readiness,
)
from .connector import DomoConnector, DomoConnectors
from .core import (
    DomoDataset,
    DomoDataset_Default,
    DomoDatasetView,
    DomoPublishDataset,
    FederatedDomoDataset,
)
from .manager import DomoDatasets
from .pdp import DatasetPdpPolicies, PdpParameter, PDPPolicy
from .schema import (
    DatasetSchema_InvalidSchemaError,
    DatasetSchema_Types,
    DomoDataset_Schema,
    DomoDataset_Schema_Column,
)
from .stream import (
    DomoStream,
    DomoStreams,
)
from .stream_configs import (
    CONFORMED_PROPERTIES,
    ConformedProperty,
    StreamConfig,
    StreamConfig_Mappings,
)

# Import route-level exceptions that are commonly used
try:
    from ...routes.dataset import (
        DatasetNotFoundError,
        QueryRequestError,
        ShareDataset_AccessLevelEnum,
    )
except ImportError:
    # Fallback if route exceptions aren't available
    pass

__all__ = [
    # Main dataset classes
    "DomoDataset",
    "DomoDataset_Default",
    "DomoDatasetView",
    "DomoDatasets",
    "DomoPublishDataset",
    "FederatedDomoDataset",
    # AI Readiness
    "DomoDataset_AI_Readiness",
    "AI_Readiness_Column",
    # Schema management
    "DomoDataset_Schema",
    "DomoDataset_Schema_Column",
    "DatasetSchema_Types",
    "DatasetSchema_InvalidSchemaError",
    # PDP functionality
    "PDPPolicy",
    "PdpParameter",
    "DatasetPdpPolicies",
    # Streaming
    "DomoStream",
    "DomoStreams",
    "StreamConfig",
    "StreamConfig_Mappings",
    # Conformed properties (NEW)
    "ConformedProperty",
    "CONFORMED_PROPERTIES",
    # Connectors
    "DomoConnector",
    "DomoConnectors",
    # Route exceptions (if available)
    "DatasetNotFoundError",
    "QueryRequestError",
    "ShareDataset_AccessLevelEnum",
]
