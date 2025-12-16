"""AWS stream configuration mappings."""

from dataclasses import dataclass, field

from ._base import (
    StreamConfig_Base,
    StreamConfig_Mapping,
    register_mapping,
    register_stream_config,
)

__all__ = [
    # Old pattern (deprecated)
    "AWSAthenaMapping",
    "AmazonAthenaHighBandwidthMapping",
    "AmazonS3AssumeRoleMapping",
    # New pattern (typed configs)
    "AWSAthena_StreamConfig",
    "AmazonAthenaHighBandwidth_StreamConfig",
    "AmazonS3AssumeRole_StreamConfig",
]


@register_mapping("aws-athena")
@dataclass
class AWSAthenaMapping(StreamConfig_Mapping):
    """AWS Athena data provider mapping."""

    data_provider_type: str = "aws-athena"
    sql: str = "query"
    database_name: str = "databaseName"
    table_name: str = "tableName"


@register_mapping("amazon-athena-high-bandwidth")
@dataclass
class AmazonAthenaHighBandwidthMapping(StreamConfig_Mapping):
    """Amazon Athena high bandwidth data provider mapping."""

    data_provider_type: str = "amazon-athena-high-bandwidth"
    sql: str = "enteredCustomQuery"
    database_name: str = "databaseName"


@register_mapping("amazon_s3_assumerole")
@dataclass
class AmazonS3AssumeRoleMapping(StreamConfig_Mapping):
    """Amazon S3 assume role data provider mapping."""

    data_provider_type: str = "amazon_s3_assumerole"
    s3_bucket_category: str = "filesDiscovery"


# ============================================================================
# NEW PATTERN: Typed Stream Config Classes
# ============================================================================


@register_stream_config("aws-athena")
@dataclass
class AWSAthena_StreamConfig(StreamConfig_Base):
    """AWS Athena stream configuration (typed)."""

    data_provider_type: str = "aws-athena"

    query: str = None
    database_name: str = None
    table_name: str = None

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["query", "database_name", "table_name"],
        repr=False,
        init=False,
    )


@register_stream_config("amazon-athena-high-bandwidth")
@dataclass
class AmazonAthenaHighBandwidth_StreamConfig(StreamConfig_Base):
    """Amazon Athena high bandwidth stream configuration (typed)."""

    data_provider_type: str = "amazon-athena-high-bandwidth"

    query: str = None
    database_name: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "enteredCustomQuery": "query",
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["query", "database_name"],
        repr=False,
        init=False,
    )


@register_stream_config("amazon_s3_assumerole")
@dataclass
class AmazonS3AssumeRole_StreamConfig(StreamConfig_Base):
    """Amazon S3 assume role stream configuration (typed)."""

    data_provider_type: str = "amazon_s3_assumerole"

    files_discovery: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "filesDiscovery": "files_discovery",
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["files_discovery"],
        repr=False,
        init=False,
    )
