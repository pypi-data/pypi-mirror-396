"""Conformed property mappings for stream configurations.

This module defines semantic properties that exist across different stream types
(e.g., "query", "database", "warehouse") and maps them to platform-specific
configuration parameter names.

This allows DomoStream to provide a consistent interface regardless of the
underlying data provider:

    stream.sql          # Works for Snowflake, Athena, PostgreSQL, etc.
    stream.database     # Works across database connectors
    stream.report_id    # Works for Adobe, Qualtrics, Google Sheets
"""

from dataclasses import dataclass

__all__ = [
    "ConformedProperty",
    "CONFORMED_PROPERTIES",
]


@dataclass
class ConformedProperty:
    """Maps semantic property names to platform-specific config keys.

    Defines a "conformed" or "semantic" property that exists conceptually
    across multiple data providers, even though each provider may use a
    different parameter name.

    Attributes:
        name: Semantic name of the property (e.g., "query", "database")
        mappings: Dict mapping provider_type to typed_config attribute name
        description: Human-readable description of what this property represents
        supported_providers: List of provider types that support this property
        is_repr: Whether to include this property in __repr__ output (default: False)

    Example:
        query = ConformedProperty(
            name="query",
            description="SQL query or data selection statement",
            mappings={
                "snowflake": "query",
                "aws-athena": "query",
                "amazon-athena-high-bandwidth": "query",
                "postgresql": "query",
            },
            is_repr=True  # Show in repr
        )
    """

    name: str
    mappings: dict[str, str]
    description: str = None
    is_repr: bool = False

    def get_key_for_provider(self, provider_type: str) -> str | None:
        """Get the typed_config attribute name for a specific provider.

        Args:
            provider_type: Data provider type (e.g., "snowflake", "aws-athena")

        Returns:
            Attribute name on the typed config class, or None if not supported

        Example:
            >>> query_prop.get_key_for_provider("snowflake")
            "query"
            >>> query_prop.get_key_for_provider("unknown-provider")
            None
        """
        return self.mappings.get(provider_type)

    @property
    def supported_providers(self) -> list[str]:
        """List of provider types that support this property."""
        return list(self.mappings.keys())


# ============================================================================
# Conformed Property Registry
# ============================================================================

CONFORMED_PROPERTIES = {
    "query": ConformedProperty(
        is_repr=True,
        name="query",
        description="SQL query or data selection statement",
        mappings={
            # Snowflake variants
            "snowflake": "query",
            "snowflakekeypairauthentication": "query",
            "snowflake_unload_v2": "query",
            "snowflake-unload-v2": "query",
            "snowflake-internal-unload": "custom_query",
            "snowflake-keypair-internal-managed-unload": "custom_query",
            "snowflake-key-pair-unload-v2": "generated_query",
            # AWS
            "aws-athena": "query",
            "amazon-athena-high-bandwidth": "query",
            # PostgreSQL
            "postgresql": "query",
        },
    ),
    "database": ConformedProperty(
        name="database",
        description="Database name or identifier",
        is_repr=True,  # Show in repr - key property
        mappings={
            # Snowflake variants
            "snowflake": "database_name",
            "snowflakekeypairauthentication": "database_name",
            "snowflake-internal-unload": "database_name",
            "snowflake-keypair-internal-managed-unload": "database_name",
            "snowflake_unload_v2": "database_name",
            "snowflake-unload-v2": "database_name",
            "snowflake-writeback": "database_name",
            "snowflake-key-pair-writeback": "database_name",
            "snowflake-key-pair-unload-v2": "database_name",
            # AWS
            "aws-athena": "database_name",
            "amazon-athena-high-bandwidth": "database_name",
            # PostgreSQL
            "postgresql": "database_name",
        },
    ),
    "schema": ConformedProperty(
        name="schema",
        description="Database schema name",
        is_repr=True,  # Show in repr
        mappings={
            "snowflake": "schema_name",
            "snowflakekeypairauthentication": "schema_name",
            "snowflake-keypair-internal-managed-unload": "schema_name",
            "snowflake-internal-unload": "schema_name",
            "snowflake-writeback": "schema_name",
            "snowflake-key-pair-writeback": "schema_name",
            "snowflake-key-pair-unload-v2": "schema_name",
            "snowflake_unload_v2": "schema_name",
            "snowflake-unload-v2": "schema_name",
            "postgresql": "schema_name",
        },
    ),
    "warehouse": ConformedProperty(
        name="warehouse",
        description="Compute warehouse or resource pool",
        is_repr=True,  # Show in repr - important for Snowflake
        mappings={
            # Snowflake variants
            "snowflake-keypair-internal-managed-unload": "warehouse_name",
            "snowflake": "warehouse_name",
            "snowflakekeypairauthentication": "warehouse_name",
            "snowflake-internal-unload": "warehouse_name",
            "snowflake-keypair-internal-unload": "warehouse_name",
            "snowflake_unload_v2": "warehouse_name",
            "snowflake-unload-v2": "warehouse_name",
            "snowflake-writeback": "warehouse_name",
            "snowflake-key-pair-writeback": "warehouse_name",
            "snowflake-key-pair-unload-v2": "warehouse_name",
        },
    ),
    "table": ConformedProperty(
        name="table",
        description="Table name or identifier",
        is_repr=True,  # Show in repr
        mappings={
            "aws-athena": "table_name",
            "snowflake-writeback": "table_name",
            "snowflake-key-pair-writeback": "table_name",
            "snowflake-key-pair-unload-v2": "table_name",
            "snowflake_unload_v2": "table_name",
            "snowflake-unload-v2": "table_name",
        },
    ),
    "report_id": ConformedProperty(
        name="report_id",
        description="Report identifier (Adobe report suite, Qualtrics survey, etc.)",
        is_repr=True,  # Show in repr
        mappings={
            "adobe-analytics-v2": "adobe_report_suite_id",
            "qualtrics": "qualtrics_survey_id",
        },
    ),
    "spreadsheet": ConformedProperty(
        name="spreadsheet",
        description="Spreadsheet identifier or file name",
        is_repr=True,  # Show in repr
        mappings={
            "google-sheets": "spreadsheet_id_file_name",
            "google-spreadsheets": "spreadsheet_id_file_name",
        },
    ),
    "bucket": ConformedProperty(
        name="bucket",
        description="S3 bucket or cloud storage location",
        is_repr=False,  # Don't show in repr by default
        mappings={
            "amazon_s3_assumerole": "s3_bucket_category",
            "amazon-s3-assume-role": "files_discovery",
        },
    ),
    "dataset_id": ConformedProperty(
        name="dataset_id",
        description="Source dataset ID (for Domo-to-Domo connections)",
        is_repr=False,  # Don't show in repr (shown via parent.id anyway)
        mappings={
            "dataset-copy": "dataset_id",
        },
    ),
    "file_url": ConformedProperty(
        name="file_url",
        description="URL or path to data file",
        is_repr=False,  # Don't show in repr (usually too long)
        mappings={
            "domo-csv": "url",
        },
    ),
    "host": ConformedProperty(
        name="host",
        description="Database host or server address",
        is_repr=False,  # Don't show in repr (security)
        mappings={
            "postgresql": "host",
            "sharepoint-online": "site_url",
        },
    ),
    "port": ConformedProperty(
        name="port",
        description="Database port number",
        is_repr=False,  # Don't show in repr (not usually interesting)
        mappings={
            "postgresql": "port",
        },
    ),
    "update_mode": ConformedProperty(
        name="update_mode",
        description="Data update mode (Replace, Upsert, Append)",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflakekeypairauthentication": "update_mode",
            "snowflake": "update_mode",
            "snowflake-internal-unload": "update_mode",
            "snowflake-keypair-internal-managed-unload": "update_mode",
            "snowflake-writeback": "update_mode",
            "snowflake-key-pair-writeback": "update_mode",
            "snowflake-key-pair-unload-v2": "update_mode",
            "snowflake_unload_v2": "update_mode",
            "snowflake-unload-v2": "update_mode",
        },
    ),
    "query_tag": ConformedProperty(
        name="query_tag",
        description="Query tag for tracking and monitoring",
        is_repr=False,  # Don't show in repr (technical detail)
        mappings={
            "snowflakekeypairauthentication": "query_tag",
            "snowflake": "query_tag",
            "snowflake-internal-unload": "query_tag",
            "snowflake-keypair-internal-managed-unload": "query_tag",
        },
    ),
    "fetch_size": ConformedProperty(
        name="fetch_size",
        description="Number of rows to fetch per batch",
        is_repr=False,  # Don't show in repr (technical detail)
        mappings={
            "snowflakekeypairauthentication": "fetch_size",
            "snowflake": "fetch_size",
        },
    ),
    "report_type": ConformedProperty(
        name="report_type",
        description="Type of report or query (tables, views, custom query)",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflakekeypairauthentication": "report_type",
            "snowflake": "report_type",
        },
    ),
    "cloud": ConformedProperty(
        name="cloud",
        description="Cloud provider or environment (domo, aws, azure)",
        is_repr=False,  # Don't show in repr (infrastructure detail)
        mappings={
            "snowflakekeypairauthentication": "cloud",
            "snowflake-internal-unload": "cloud",
            "snowflake-keypair-internal-managed-unload": "cloud",
            "snowflake-key-pair-writeback": "cloud",
            "snowflake-key-pair-unload-v2": "cloud",
        },
    ),
    "bypass_data_upload": ConformedProperty(
        name="bypass_data_upload",
        description="Whether to bypass data upload to Domo",
        is_repr=False,  # Don't show in repr (operational flag)
        mappings={
            "snowflakekeypairauthentication": "bypass_data_upload",
            "snowflake-internal-unload": "bypass_data_upload",
            "snowflake-keypair-internal-managed-unload": "bypass_data_upload",
            "snowflake-key-pair-unload-v2": "bypass_data_upload",
            "snowflake_unload_v2": "bypass_data_upload",
            "snowflake-unload-v2": "bypass_data_upload",
        },
    ),
    "convert_timezone": ConformedProperty(
        name="convert_timezone",
        description="Timezone conversion setting",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflakekeypairauthentication": "convert_timezone",
        },
    ),
    "query_type": ConformedProperty(
        name="query_type",
        description="Query type (customQuery, queryBuilder, tables, views)",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflake-internal-unload": "query_type",
            "snowflake-keypair-internal-managed-unload": "query_type",
            "snowflake-key-pair-unload-v2": "query_type",
            "snowflake_unload_v2": "query_type",
            "snowflake-unload-v2": "query_type",
        },
    ),
    "database_objects": ConformedProperty(
        name="database_objects",
        description="Type of database objects to query (tables, views)",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflake-internal-unload": "database_objects",
            "snowflake-keypair-internal-managed-unload": "database_objects",
            "snowflake-key-pair-unload-v2": "database_objects",
            "snowflake_unload_v2": "database_objects",
            "snowflake-unload-v2": "database_objects",
        },
    ),
    "partition_criteria": ConformedProperty(
        name="partition_criteria",
        description="Partition criteria for incremental data loading",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflake-internal-unload": "partition_criteria",
            "snowflake-keypair-internal-managed-unload": "partition_criteria",
            "snowflake-key-pair-unload-v2": "partition_criteria",
            "snowflake_unload_v2": "partition_criteria",
            "snowflake-unload-v2": "partition_criteria",
        },
    ),
    "date_format": ConformedProperty(
        name="date_format",
        description="Date format string (yyyy-MM-dd, etc.)",
        is_repr=False,  # Don't show in repr (formatting detail)
        mappings={
            "snowflake-internal-unload": "date_format",
            "snowflake-keypair-internal-managed-unload": "date_format",
            "snowflake-key-pair-unload-v2": "date_format",
            "snowflake_unload_v2": "date_format",
            "snowflake-unload-v2": "date_format",
        },
    ),
    "queried_dataset_id": ConformedProperty(
        name="queried_dataset_id",
        description="Source dataset ID for writeback operations",
        is_repr=False,  # Don't show in repr (technical reference)
        mappings={
            "snowflake-writeback": "queried_dataset_id",
            "snowflake-key-pair-writeback": "queried_dataset_id",
        },
    ),
    "view_name": ConformedProperty(
        name="view_name",
        description="Database view name",
        is_repr=False,  # Don't show in repr (specific to views)
        mappings={
            "snowflake-internal-unload": "view_name",
        },
    ),
    "column_names": ConformedProperty(
        name="column_names",
        description="List of column names to include",
        is_repr=False,  # Don't show in repr (too long)
        mappings={
            "snowflake-key-pair-unload-v2": "column_names",
            "snowflake_unload_v2": "column_names",
            "snowflake-unload-v2": "column_names",
        },
    ),
    "import_data_method": ConformedProperty(
        name="import_data_method",
        description="Data import method (partition, noPartitionAndUpsert, etc.)",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflake-key-pair-unload-v2": "import_data_method",
            "snowflake_unload_v2": "import_data_method",
            "snowflake-unload-v2": "import_data_method",
        },
    ),
    "partition_column_name": ConformedProperty(
        name="partition_column_name",
        description="Column name used for partitioning",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflake-key-pair-unload-v2": "partition_column_name",
        },
    ),
    "relative_days": ConformedProperty(
        name="relative_days",
        description="Number of days to look back for incremental loading",
        is_repr=False,  # Don't show in repr (operational detail)
        mappings={
            "snowflake-key-pair-unload-v2": "relative_days",
        },
    ),
}
