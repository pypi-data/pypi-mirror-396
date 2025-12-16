"""Snowflake stream configuration mappings."""

from dataclasses import dataclass, field

from ._base import (
    StreamConfig_Base,
    StreamConfig_Mapping,
    register_mapping,
    register_stream_config,
)

__all__ = [
    # Old pattern (mappings - deprecated but kept for compatibility)
    "SnowflakeMapping",
    "SnowflakeFederatedMapping",
    "SnowflakeInternalUnloadMapping",
    "SnowflakeKeypairAuthMapping",
    "SnowflakeKeypairInternalManagedUnloadMapping",
    "SnowflakeUnloadV2Mapping",
    "SnowflakeWritebackMapping",
    # New pattern (typed configs - recommended)
    "Snowflake_StreamConfig",
    "SnowflakeKeyPairAuth_StreamConfig",
]


@register_mapping("snowflake")
@dataclass
class SnowflakeMapping(StreamConfig_Mapping):
    """Snowflake data provider mapping."""

    data_provider_type: str = "snowflake"
    sql: str = "query"
    warehouse: str = "warehouseName"
    database_name: str = "databaseName"


@register_mapping("snowflake_federated")
@dataclass
class SnowflakeFederatedMapping(StreamConfig_Mapping):
    """Snowflake federated data provider mapping."""

    data_provider_type: str = "snowflake_federated"


@register_mapping("snowflake-internal-unload")
@dataclass
class SnowflakeInternalUnloadMapping(StreamConfig_Mapping):
    """Snowflake internal unload data provider mapping."""

    data_provider_type: str = "snowflake-internal-unload"
    sql: str = "customQuery"
    database_name: str = "databaseName"
    warehouse: str = "warehouseName"


@register_mapping("snowflakekeypairauthentication")
@dataclass
class SnowflakeKeypairAuthMapping(StreamConfig_Mapping):
    """Snowflake keypair authentication data provider mapping."""

    data_provider_type: str = "snowflakekeypairauthentication"
    sql: str = "query"
    database_name: str = "databaseName"
    schema_name: str = "schemaName"
    warehouse: str = "warehouseName"
    report_type: str = "reportType"
    query_tag: str = "queryTag"
    fetch_size: str = "fetchSize"
    update_mode: str = "updatemode.mode"
    convert_timezone: str = "convertTimeZone"
    cloud: str = "cloud"


@register_mapping("snowflake-keypair-internal-managed-unload")
@dataclass
class SnowflakeKeypairInternalManagedUnloadMapping(StreamConfig_Mapping):
    """Snowflake keypair internal managed unload data provider mapping."""

    data_provider_type: str = "snowflake-keypair-internal-managed-unload"
    sql: str = "customQuery"
    database_name: str = "databaseName"
    warehouse: str = "warehouseName"


@register_mapping("snowflake_unload_v2")
@dataclass
class SnowflakeUnloadV2Mapping(StreamConfig_Mapping):
    """Snowflake unload v2 data provider mapping."""

    data_provider_type: str = "snowflake_unload_v2"
    sql: str = "query"
    warehouse: str = "warehouseName"
    database_name: str = "databaseName"


@register_mapping("snowflake-writeback")
@dataclass
class SnowflakeWritebackMapping(StreamConfig_Mapping):
    """Snowflake writeback data provider mapping."""

    data_provider_type: str = "snowflake-writeback"
    table_name: str = "enterTableName"
    database_name: str = "databaseName"
    warehouse: str = "warehouseName"


# ============================================================================
# NEW PATTERN: Typed Stream Config Classes (Recommended)
# ============================================================================


@register_stream_config("snowflake")
@dataclass
class Snowflake_StreamConfig(StreamConfig_Base):
    """Snowflake stream configuration (typed, follows AccountConfig pattern).

    Provides type-safe access to Snowflake stream parameters.

    Example:
        >>> config = Snowflake_StreamConfig.from_dict({
        ...     "query": "SELECT * FROM table",
        ...     "databaseName": "SA_PRD",
        ...     "warehouseName": "COMPUTE_WH"
        ... })
        >>> config.query  # Type-safe attribute access
        "SELECT * FROM table"
        >>> config.database_name
        "SA_PRD"
    """

    data_provider_type: str = "snowflake"

    # Stream configuration parameters
    query: str = None
    database_name: str = None
    warehouse_name: str = None
    schema_name: str = None

    _field_map: dict = field(
        default_factory=lambda: {},
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: [
            "query",
            "database_name",
            "warehouse",
            "schema_name",
        ],
        repr=False,
        init=False,
    )


@register_stream_config("snowflakekeypairauthentication")
@dataclass
class SnowflakeKeyPairAuth_StreamConfig(StreamConfig_Base):
    """Snowflake keypair authentication stream configuration.

    Includes additional fields for keypair auth (query tags, fetch size, etc.).

    Example:
        >>> config = SnowflakeKeyPairAuth_StreamConfig.from_dict({
        ...     "query": "SELECT * FROM table",
        ...     "databaseName": "SA_PRD",
        ...     "queryTag": "domoD2C123",
        ...     "fetchSize": "1000"
        ... })
        >>> config.query_tag
        "domoD2C123"
    """

    data_provider_type: str = "snowflakekeypairauthentication"

    # Stream configuration parameters
    query: str = None
    database_name: str = None
    schema_name: str = None
    warehouse_name: str = None
    report_type: str = None
    query_tag: str = None
    fetch_size: str = None
    update_mode: str = None
    convert_timezone: str = None
    cloud: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "updatemode.mode": "update_mode",  # Special case with dot notation
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: [
            "query",
            "database_name",
            "schema_name",
            "warehouse",
            "report_type",
            "query_tag",
            "fetch_size",
            "update_mode",
            "convert_timezone",
            "cloud",
        ],
        repr=False,
        init=False,
    )


@register_stream_config("snowflake-internal-unload")
@dataclass
class SnowflakeInternalUnload_StreamConfig(StreamConfig_Base):
    """Snowflake internal unload stream configuration.

    Used for Snowflake managed unload operations with custom queries.
    """

    data_provider_type: str = "snowflake-internal-unload"

    # Stream configuration parameters
    custom_query: str = None
    database_name: str = None
    schema_name: str = None
    warehouse_name: str = None
    query_tag: str = None
    query_type: str = None
    database_objects: str = None
    view_name: str = None
    cloud: str = None
    bypass_data_upload: str = None
    update_mode: str = None
    partition_criteria: str = None
    date_format: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "customQuery": "custom_query",
            "updatemode.mode": "update_mode",
        },
        repr=False,
        init=False,
    )


@register_stream_config("snowflake-keypair-internal-managed-unload")
@dataclass
class SnowflakeKeypairInternalManagedUnload_StreamConfig(StreamConfig_Base):
    """Snowflake keypair internal managed unload stream configuration.

    Used for Snowflake keypair-authenticated managed unload operations.
    """

    data_provider_type: str = "snowflake-keypair-internal-managed-unload"

    # Stream configuration parameters
    custom_query: str = None
    database_name: str = None
    schema_name: str = None
    warehouse_name: str = None
    query_tag: str = None
    query_type: str = None
    database_objects: str = None
    cloud: str = None
    bypass_data_upload: str = None
    update_mode: str = None
    partition_criteria: str = None
    date_format: str = None
    partition_column_dropdown_format: str = None
    include_partition: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "customQuery": "custom_query",
            "updatemode.mode": "update_mode",
        },
        repr=False,
        init=False,
    )


@register_stream_config("snowflake-writeback")
@dataclass
class SnowflakeWriteback_StreamConfig(StreamConfig_Base):
    """Snowflake writeback stream configuration.

    Used for writing data from Domo back to Snowflake tables.
    """

    data_provider_type: str = "snowflake-writeback"

    # Stream configuration parameters
    table_name: str = None
    database_name: str = None
    schema_name: str = None
    warehouse_name: str = None
    queried_dataset_id: str = None
    update_mode: str = None
    update_table_options: str = None
    escape_character: str = None
    use_caps: str = None
    validate_table_name: str = None
    use_icebox: str = None
    tablename_dropdown: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "enterTableName": "table_name",
            "updatemode.mode": "update_mode",
        },
        repr=False,
        init=False,
    )


@register_stream_config("snowflake-key-pair-writeback")
@dataclass
class SnowflakeKeyPairWriteback_StreamConfig(StreamConfig_Base):
    """Snowflake key pair authentication writeback stream configuration.

    Used for keypair-authenticated writes from Domo to Snowflake tables.
    """

    data_provider_type: str = "snowflake-key-pair-writeback"

    # Stream configuration parameters
    database_name: str = None
    schema_name: str = None
    warehouse_name: str = None
    queried_dataset_id: str = None
    update_mode: str = None
    update_table_options: str = None
    escape_character: str = None
    use_caps: str = None
    validate_table_name: str = None
    use_icebox: str = None
    tablename_dropdown: str = None
    cloud: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "updatemode.mode": "update_mode",
        },
        repr=False,
        init=False,
    )


@register_stream_config("snowflake-key-pair-unload-v2")
@dataclass
class SnowflakeKeyPairUnloadV2_StreamConfig(StreamConfig_Base):
    """Snowflake key pair unload v2 stream configuration.

    Used for v2 keypair-authenticated unload operations.
    """

    data_provider_type: str = "snowflake-key-pair-unload-v2"

    # Stream configuration parameters
    database_name: str = None
    schema_name: str = None
    warehouse_name: str = None
    table_name: str = None
    generated_query: str = None
    column_names: str = None
    query_type: str = None
    database_objects: str = None
    import_data_method: str = None
    partition_criteria: str = None
    partition_column_name: str = None
    date_format: str = None
    relative_days: str = None
    upsert_key_columns: str = None
    update_mode: str = None
    bypass_data_upload: str = None
    cloud: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "generatedQuery": "generated_query",
            "updatemode.mode": "update_mode",
        },
        repr=False,
        init=False,
    )


@register_stream_config("snowflake_unload_v2")
@register_stream_config("snowflake-unload-v2")
@dataclass
class SnowflakeUnloadV2_StreamConfig(StreamConfig_Base):
    """Snowflake unload v2 stream configuration.

    Used for v2 unload operations (both underscore and hyphen variants).
    """

    data_provider_type: str = "snowflake_unload_v2"

    # Stream configuration parameters
    database_name: str = None
    schema_name: str = None
    warehouse_name: str = None
    table_name: str = None
    generated_query: str = None
    column_names: str = None
    query_type: str = None
    database_objects: str = None
    import_data_method: str = None
    partition_criteria: str = None
    date_format: str = None
    update_mode: str = None
    bypass_data_upload: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "generatedQuery": "generated_query",
            "updatemode.mode": "update_mode",
        },
        repr=False,
        init=False,
    )


@register_stream_config("snowflake-federated")
@dataclass
class SnowflakeFederated_StreamConfig(StreamConfig_Base):
    """Snowflake federated stream configuration.

    Used for federated Snowflake data sources.
    """

    data_provider_type: str = "snowflake-federated"

    # Stream configuration parameters
    source_name: str = None
    source_type: str = None
