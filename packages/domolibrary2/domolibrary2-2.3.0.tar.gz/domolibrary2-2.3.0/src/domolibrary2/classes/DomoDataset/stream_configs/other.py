"""Other/miscellaneous stream configuration mappings."""

from dataclasses import dataclass, field

from ._base import (
    StreamConfig_Base,
    StreamConfig_Mapping,
    register_mapping,
    register_stream_config,
)

__all__ = [
    # Old pattern (deprecated)
    "AdobeAnalyticsV2Mapping",
    "PostgreSQLMapping",
    "QualtricsMapping",
    "SharePointOnlineMapping",
    # New pattern (typed configs)
    "AdobeAnalyticsV2_StreamConfig",
    "PostgreSQL_StreamConfig",
    "Qualtrics_StreamConfig",
    "SharePointOnline_StreamConfig",
]


@register_mapping("adobe-analytics-v2")
@dataclass
class AdobeAnalyticsV2Mapping(StreamConfig_Mapping):
    """Adobe Analytics v2 data provider mapping."""

    data_provider_type: str = "adobe-analytics-v2"
    sql: str = "query"
    adobe_report_suite_id: str = "report_suite_id"


@register_mapping("postgresql")
@dataclass
class PostgreSQLMapping(StreamConfig_Mapping):
    """PostgreSQL data provider mapping."""

    data_provider_type: str = "postgresql"
    sql: str = "query"


@register_mapping("qualtrics")
@dataclass
class QualtricsMapping(StreamConfig_Mapping):
    """Qualtrics data provider mapping."""

    data_provider_type: str = "qualtrics"
    qualtrics_survey_id: str = "survey_id"


@register_mapping("sharepointonline")
@dataclass
class SharePointOnlineMapping(StreamConfig_Mapping):
    """SharePoint Online data provider mapping."""

    data_provider_type: str = "sharepointonline"
    src_url: str = "relativeURL"


# ============================================================================
# NEW PATTERN: Typed Stream Config Classes
# ============================================================================


@register_stream_config("adobe-analytics-v2")
@dataclass
class AdobeAnalyticsV2_StreamConfig(StreamConfig_Base):
    """Adobe Analytics v2 stream configuration (typed)."""

    data_provider_type: str = "adobe-analytics-v2"

    query: str = None
    report_suite_id: str = None

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["query", "report_suite_id"],
        repr=False,
        init=False,
    )


@register_stream_config("postgresql")
@dataclass
class PostgreSQL_StreamConfig(StreamConfig_Base):
    """PostgreSQL stream configuration (typed)."""

    data_provider_type: str = "postgresql"

    query: str = None

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["query"],
        repr=False,
        init=False,
    )


@register_stream_config("qualtrics")
@dataclass
class Qualtrics_StreamConfig(StreamConfig_Base):
    """Qualtrics stream configuration (typed)."""

    data_provider_type: str = "qualtrics"

    survey_id: str = None

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["survey_id"],
        repr=False,
        init=False,
    )


@register_stream_config("sharepointonline")
@dataclass
class SharePointOnline_StreamConfig(StreamConfig_Base):
    """SharePoint Online stream configuration (typed)."""

    data_provider_type: str = "sharepointonline"

    relative_url: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "relativeURL": "relative_url",
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["relative_url"],
        repr=False,
        init=False,
    )
