"""Stream configuration mappings organized by platform.

This package contains stream configuration classes organized by major platform
(Snowflake, AWS, Domo, Google, etc.).

TWO PATTERNS AVAILABLE:

1. NEW PATTERN (Recommended): Typed Config Classes
   - Follows AccountConfig pattern
   - Type-safe attribute access: config.query
   - IDE autocomplete works
   - Single config object per stream

   Example:
       from domolibrary2.classes.DomoDataset.stream_configs import StreamConfig_Base
       from domolibrary2.classes.DomoDataset.stream_configs.snowflake import Snowflake_StreamConfig

       config = Snowflake_StreamConfig.from_dict({"query": "SELECT *", "databaseName": "SA_PRD"})
       query = config.query  # Type-safe, autocomplete works!

2. OLD PATTERN (Deprecated): Mapping Classes
   - Maps field names to config parameters
   - Search through list of StreamConfig objects
   - Kept for backward compatibility

   Example:
       from domolibrary2.classes.DomoDataset.stream_configs import StreamConfig_Mapping

       mapping = StreamConfig_Mappings('snowflake')
       sql_param = mapping.value.sql  # "query"
"""

# Import and re-export base classes and utilities
from ._base import (
    _MAPPING_REGISTRY,
    Stream_CRUD_Error,
    Stream_GET_Error,
    StreamConfig,
    StreamConfig_Base,
    StreamConfig_Mapping,
    StreamConfig_Mappings,
    register_mapping,
    register_stream_config,
)
from ._conformed import CONFORMED_PROPERTIES, ConformedProperty

# Import new typed config classes
from ._default import Default_StreamConfig
from ._repr import (
    ConformedPropertyReprMixin,
    create_stream_repr,
    get_available_config_keys,
    get_conformed_properties_for_repr,
    get_missing_mappings,
)
from .aws import (
    AmazonAthenaHighBandwidth_StreamConfig,
    AmazonS3AssumeRole_StreamConfig,
    AWSAthena_StreamConfig,
)
from .domo import DatasetCopy_StreamConfig, DomoCSV_StreamConfig
from .google import GoogleSheets_StreamConfig, GoogleSpreadsheets_StreamConfig
from .other import (
    AdobeAnalyticsV2_StreamConfig,
    PostgreSQL_StreamConfig,
    Qualtrics_StreamConfig,
    SharePointOnline_StreamConfig,
)
from .snowflake import (
    Snowflake_StreamConfig,
    SnowflakeKeyPairAuth_StreamConfig,
)

__all__ = [
    # NEW PATTERN (Recommended)
    "StreamConfig_Base",
    "register_stream_config",
    # Conformed properties (semantic layer)
    "ConformedProperty",
    "CONFORMED_PROPERTIES",
    # Custom repr utilities
    "create_stream_repr",
    "get_conformed_properties_for_repr",
    "get_missing_mappings",
    "get_available_config_keys",
    "ConformedPropertyReprMixin",
    # NEW: Snowflake configs
    "Snowflake_StreamConfig",
    "SnowflakeKeyPairAuth_StreamConfig",
    # NEW: AWS configs
    "AWSAthena_StreamConfig",
    "AmazonAthenaHighBandwidth_StreamConfig",
    "AmazonS3AssumeRole_StreamConfig",
    # NEW: Domo configs
    "DatasetCopy_StreamConfig",
    "DomoCSV_StreamConfig",
    # NEW: Google configs
    "GoogleSheets_StreamConfig",
    "GoogleSpreadsheets_StreamConfig",
    # NEW: Other configs
    "AdobeAnalyticsV2_StreamConfig",
    "PostgreSQL_StreamConfig",
    "Qualtrics_StreamConfig",
    "SharePointOnline_StreamConfig",
    # NEW: Default config
    "Default_StreamConfig",
    # OLD PATTERN (Deprecated but kept for compatibility)
    "StreamConfig_Mapping",
    "StreamConfig_Mappings",
    "StreamConfig",
    "_MAPPING_REGISTRY",
    "register_mapping",
    # Route exceptions
    "Stream_GET_Error",
    "Stream_CRUD_Error",
]
