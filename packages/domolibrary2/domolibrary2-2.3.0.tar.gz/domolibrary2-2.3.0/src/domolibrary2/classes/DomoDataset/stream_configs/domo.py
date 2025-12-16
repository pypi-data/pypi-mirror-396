"""Domo stream configuration mappings."""

from dataclasses import dataclass, field

from ._base import (
    StreamConfig_Base,
    StreamConfig_Mapping,
    register_mapping,
    register_stream_config,
)

__all__ = [
    # Old pattern (deprecated)
    "DatasetCopyMapping",
    "DomoCSVMapping",
    # New pattern (typed configs)
    "DatasetCopy_StreamConfig",
    "DomoCSV_StreamConfig",
]


@register_mapping("dataset-copy")
@dataclass
class DatasetCopyMapping(StreamConfig_Mapping):
    """Dataset copy data provider mapping."""

    data_provider_type: str = "dataset-copy"
    src_url: str = "datasourceUrl"


@register_mapping("domo-csv")
@dataclass
class DomoCSVMapping(StreamConfig_Mapping):
    """Domo CSV data provider mapping."""

    data_provider_type: str = "domo-csv"
    src_url: str = "datasourceUrl"


# ============================================================================
# NEW PATTERN: Typed Stream Config Classes
# ============================================================================


@register_stream_config("dataset-copy")
@dataclass
class DatasetCopy_StreamConfig(StreamConfig_Base):
    """Dataset copy stream configuration (typed)."""

    data_provider_type: str = "dataset-copy"

    datasource_url: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "datasourceUrl": "datasource_url",
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["datasource_url"],
        repr=False,
        init=False,
    )


@register_stream_config("domo-csv")
@dataclass
class DomoCSV_StreamConfig(StreamConfig_Base):
    """Domo CSV stream configuration (typed)."""

    data_provider_type: str = "domo-csv"

    datasource_url: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "datasourceUrl": "datasource_url",
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["datasource_url"],
        repr=False,
        init=False,
    )
