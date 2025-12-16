"""Google stream configuration mappings."""

from dataclasses import dataclass, field

from ._base import (
    StreamConfig_Base,
    StreamConfig_Mapping,
    register_mapping,
    register_stream_config,
)

__all__ = [
    # Old pattern (deprecated)
    "GoogleSheetsMapping",
    "GoogleSpreadsheetsMapping",
    # New pattern (typed configs)
    "GoogleSheets_StreamConfig",
    "GoogleSpreadsheets_StreamConfig",
]


@register_mapping("google-sheets")
@dataclass
class GoogleSheetsMapping(StreamConfig_Mapping):
    """Google Sheets data provider mapping."""

    data_provider_type: str = "google-sheets"
    google_sheets_file_name: str = "spreadsheetIDFileName"


@register_mapping("google-spreadsheets")
@dataclass
class GoogleSpreadsheetsMapping(StreamConfig_Mapping):
    """Google Spreadsheets data provider mapping."""

    data_provider_type: str = "google-spreadsheets"
    google_sheets_file_name: str = "spreadsheetIDFileName"


# ============================================================================
# NEW PATTERN: Typed Stream Config Classes
# ============================================================================


@register_stream_config("google-sheets")
@dataclass
class GoogleSheets_StreamConfig(StreamConfig_Base):
    """Google Sheets stream configuration (typed)."""

    data_provider_type: str = "google-sheets"

    spreadsheet_id_file_name: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "spreadsheetIDFileName": "spreadsheet_id_file_name",
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["spreadsheet_id_file_name"],
        repr=False,
        init=False,
    )


@register_stream_config("google-spreadsheets")
@dataclass
class GoogleSpreadsheets_StreamConfig(StreamConfig_Base):
    """Google Spreadsheets stream configuration (typed)."""

    data_provider_type: str = "google-spreadsheets"

    spreadsheet_id_file_name: str = None

    _field_map: dict = field(
        default_factory=lambda: {
            "spreadsheetIDFileName": "spreadsheet_id_file_name",
        },
        repr=False,
        init=False,
    )

    _fields_for_export: list[str] = field(
        default_factory=lambda: ["spreadsheet_id_file_name"],
        repr=False,
        init=False,
    )
