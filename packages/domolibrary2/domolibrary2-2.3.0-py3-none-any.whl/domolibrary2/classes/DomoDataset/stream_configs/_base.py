"""Base classes and utilities for stream configuration mappings.

This module contains:
- StreamConfig_Mapping: Base class for all provider-specific mappings (OLD - deprecated)
- StreamConfig_Base: New base class for typed stream configs (NEW - follows AccountConfig pattern)
- StreamConfig: Individual stream configuration item (OLD - for list-based configs)
- StreamConfig_Mappings: Enum for accessing registered mappings
- register_mapping: Decorator for registering new mappings
- register_stream_config: Decorator for registering new typed config classes (NEW)
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from sqlglot import exp, parse_one

from ....base.base import DomoBase, DomoEnumMixin
from ....base.exceptions import DomoError
from ....routes.dataset.stream import Stream_CRUD_Error, Stream_GET_Error

__all__ = [
    # New pattern (AccountConfig-style)
    "StreamConfig_Base",
    "register_stream_config",
    # Old pattern (deprecated but kept for compatibility)
    "StreamConfig_Mapping",
    "StreamConfig_Mappings",
    "StreamConfig",
    "register_mapping",
    # Route exceptions
    "Stream_GET_Error",
    "Stream_CRUD_Error",
]

# ============================================================================
# OLD PATTERN: Mapping Registry (deprecated but kept for compatibility)
# ============================================================================

# Registry to store mapping classes (OLD)
_MAPPING_REGISTRY: dict[str, type[StreamConfig_Mapping]] = {}


def register_mapping(data_provider_type: str):
    """Decorator to register a StreamConfig_Mapping subclass (OLD pattern).

    DEPRECATED: Use register_stream_config() for new config classes.

    Args:
        data_provider_type: The data provider type identifier (e.g., 'snowflake')

    Example:
        @register_mapping('snowflake')
        @dataclass
        class SnowflakeMapping(StreamConfig_Mapping):
            sql: str = "query"
            warehouse: str = "warehouseName"
            database_name: str = "databaseName"
    """

    def decorator(cls: type[StreamConfig_Mapping]) -> type[StreamConfig_Mapping]:
        _MAPPING_REGISTRY[data_provider_type] = cls
        return cls

    return decorator


# ============================================================================
# NEW PATTERN: Config Registry (follows AccountConfig pattern)
# ============================================================================

# Registry to store typed config classes (NEW)
_CONFIG_REGISTRY: dict[str, type[StreamConfig_Base]] = {}


def register_stream_config(data_provider_type: str):
    """Decorator to register a StreamConfig_Base subclass (NEW pattern).

    Args:
        data_provider_type: The data provider type identifier (e.g., 'snowflake')

    Example:
        @register_stream_config('snowflake')
        @dataclass
        class Snowflake_StreamConfig(StreamConfig_Base):
            data_provider_type: str = "snowflake"
            query: str = None
            database_name: str = None
    """

    def decorator(cls: type[StreamConfig_Base]) -> type[StreamConfig_Base]:
        _CONFIG_REGISTRY[data_provider_type] = cls
        return cls

    return decorator


# ============================================================================
# Utility Functions (for new pattern)
# ============================================================================


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case.

    Args:
        name: camelCase string

    Returns:
        snake_case string

    Example:
        >>> _camel_to_snake("databaseName")
        "database_name"
        >>> _camel_to_snake("warehouseName")
        "warehouse_name"
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        name: snake_case string

    Returns:
        camelCase string

    Example:
        >>> _snake_to_camel("database_name")
        "databaseName"
        >>> _snake_to_camel("warehouse_name")
        "warehouseName"
    """
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


# ============================================================================
# NEW: StreamConfig_Base (follows AccountConfig pattern)
# ============================================================================


@dataclass
class StreamConfig_Base(DomoBase):
    """Base class for typed stream configurations (NEW pattern).

    Similar to DomoAccount_Config, this provides a consistent interface
    for handling stream execution parameters across different data providers.

    This is the NEW pattern that provides:
    - Type-safe attribute access (stream_config.query)
    - IDE autocomplete
    - Single config object instead of list of configs
    - Validation and computed properties

    Example:
        @register_stream_config("snowflake")
        @dataclass
        class Snowflake_StreamConfig(StreamConfig_Base):
            data_provider_type: str = "snowflake"
            query: str = None
            database_name: str = None
            warehouse: str = None
    """

    data_provider_type: str = None
    parent: Any = field(repr=False, default=None)
    raw: dict = field(default_factory=dict, repr=False)

    # Internal fields
    _field_map: dict = field(default_factory=dict, repr=False, init=False)
    _fields_for_export: list[str] = field(default_factory=list, repr=False, init=False)

    @classmethod
    def from_dict(cls, obj: dict[str, Any], parent: Any = None):
        """Create StreamConfig from dictionary of config parameters.

        Args:
            obj: Dict with config parameter names as keys (e.g., {"query": "SELECT...", "databaseName": "mydb"})
            parent: Parent stream object

        Returns:
            StreamConfig instance with typed attributes

        Example:
            >>> config_dict = {"query": "SELECT *", "databaseName": "SA_PRD"}
            >>> config = Snowflake_StreamConfig.from_dict(config_dict)
            >>> config.query  # "SELECT *"
            >>> config.database_name  # "SA_PRD"
        """
        # Get field map from class definition
        field_map = {}
        if "_field_map" in cls.__dataclass_fields__:
            field_map_field = cls.__dataclass_fields__["_field_map"]
            if (
                hasattr(field_map_field, "default_factory")
                and field_map_field.default_factory
            ):
                field_map = field_map_field.default_factory()

        # Convert keys using field_map or auto-convert camelCase to snake_case
        init_kwargs = {}
        for api_key, api_value in obj.items():
            # Check if there's a custom mapping
            python_attr = field_map.get(api_key)
            if not python_attr:
                # Auto-convert camelCase to snake_case
                python_attr = _camel_to_snake(api_key)

            # Only set if it's a field on the class
            if python_attr in cls.__dataclass_fields__:
                init_kwargs[python_attr] = api_value

        return cls(parent=parent, raw=obj, **init_kwargs)

    def to_dict(self) -> list[dict]:
        """Convert to list of config dictionaries for API submission.

        Returns:
            List of dicts with 'name', 'type', 'value' keys

        Example:
            >>> config = Snowflake_StreamConfig(query="SELECT *", database_name="SA_PRD")
            >>> config.to_dict()
            [{"name": "query", "type": "string", "value": "SELECT *"},
             {"name": "databaseName", "type": "string", "value": "SA_PRD"}]
        """
        result = []

        # Get reverse field map (python_attr -> api_key)
        reverse_map = {v: k for k, v in self._field_map.items()}

        # Get fields to export
        export_fields = self._fields_for_export or [
            f
            for f in self.__dataclass_fields__.keys()
            if not f.startswith("_")
            and f not in ["data_provider_type", "parent", "raw"]
        ]

        for attr_name in export_fields:
            value = getattr(self, attr_name, None)
            if value is not None:
                # Get API key name (reverse mapping or convert snake_case to camelCase)
                api_key = reverse_map.get(attr_name, _snake_to_camel(attr_name))
                result.append({"name": api_key, "type": "string", "value": str(value)})

        return result


# ============================================================================
# OLD: StreamConfig_Mapping (deprecated but kept for compatibility)
# ============================================================================


@dataclass
class StreamConfig_Mapping(DomoBase):
    """Base class for stream configuration mappings.

    Maps Python attribute names to stream configuration parameter names.
    Subclass this for each data provider type.
    """

    data_provider_type: str | None = None

    sql: str = None
    warehouse: str = None
    database_name: str = None
    s3_bucket_category: str = None

    is_default: bool = False

    table_name: str = None
    src_url: str = None
    google_sheets_file_name: str = None
    adobe_report_suite_id: str = None
    qualtrics_survey_id: str = None

    def search_keys_by_value(
        self,
        value_to_search: str,
    ) -> StreamConfig_Mapping | None:
        """Search for Python attribute name by stream config parameter name.

        Args:
            value_to_search: Stream config parameter name to search for

        Returns:
            Python attribute name if found, None otherwise
        """
        if self.is_default:
            if value_to_search in ["enteredCustomQuery", "query", "customQuery"]:
                return "sql"

        return next(
            (key for key, value in asdict(self).items() if value == value_to_search),
            None,
        )


# ============================================================================
# StreamConfig and StreamConfig_Mappings must be defined before platform imports
# ============================================================================


@dataclass
class StreamConfig:
    """Individual stream configuration parameter.

    Represents a single configuration parameter in a stream execution,
    such as a SQL query, database name, warehouse, etc.
    """

    stream_category: str
    name: str
    type: str
    value: str
    value_clean: str = None
    parent: Any = field(repr=False, default=None)

    def __post_init__(self):
        # self.value_clean = self.value.replace("\n", " ")
        # sc.value_clean = re.sub(" +", " ", sc.value_clean)

        if self.stream_category == "sql" and self.parent:
            self.process_sql()

    def process_sql(self):
        """Extract table names from SQL query using sqlglot parser."""
        if not self.parent:
            return None

        self.parent.configuration_query = self.value

        try:
            for table in parse_one(self.value).find_all(exp.Table):
                self.parent.configuration_tables.append(table.name.lower())
                self.parent.configuration_tables = sorted(
                    list(set(self.parent.configuration_tables))
                )
        except DomoError:
            return None

        return self.parent.configuration_tables

    @classmethod
    def from_json(cls, obj: dict, data_provider_type: str, parent_stream: Any = None):
        """Create StreamConfig from API JSON response.
        Args:
            obj: JSON object with 'name', 'type', 'value' keys
            data_provider_type: Data provider type (e.g., 'snowflake')
            parent_stream: Parent stream object
        Returns:
            StreamConfig instance
        """
        config_name = obj["name"]

        # Use standard enum access - triggers _missing_ if not found
        mapping_enum = StreamConfig_Mappings.get(data_provider_type)

        stream_category = "default"
        if mapping_enum and mapping_enum.value:
            stream_category = mapping_enum.value.search_keys_by_value(config_name)

            if parent_stream:
                parent_stream.has_mapping = True

        return cls(
            stream_category=stream_category,
            name=config_name,
            type=obj["type"],
            value=obj["value"],
            parent=parent_stream,
        )

    def to_dict(self):
        """Convert to dictionary for API submission.
        Returns:
            Dict with 'field', 'key', 'value' keys
        """
        return {"field": self.stream_category, "key": self.name, "value": self.value}


# ============================================================================
# Import platform-specific mappings to trigger registration
# ============================================================================

# Import all mappings from the stream_configs submodules
# This triggers the @register_mapping decorators and populates _MAPPING_REGISTRY
from . import _default, aws, domo, google, other, snowflake  # noqa: E402, F401

# ============================================================================
# StreamConfig_Mappings Enum (Auto-generated from registry)
# ============================================================================


class StreamConfig_Mappings(DomoEnumMixin, Enum):
    """Enum of all registered stream config mappings.

    This enum is automatically populated from the registry created by
    @register_mapping decorators. To add a new mapping, simply create a
    new subclass with the @register_mapping decorator in the appropriate
    platform file.
    Usage:
        mapping = StreamConfig_Mappings.get('snowflake')
        sql_param = mapping.value.sql  # "query"
    """

    # Explicit default member to prevent AttributeError
    default = None  # Will be set dynamically via _missing_

    @classmethod
    def _missing_(cls, value):
        """Handle missing enum values by searching the registry."""
        alt_search = value.lower().replace("-", "_")

        # Try direct registry lookup
        if value in _MAPPING_REGISTRY:
            mapping_cls = _MAPPING_REGISTRY[value]
            return cls._create_pseudo_member(value, mapping_cls())

        # Try normalized search
        for key, mapping_cls in _MAPPING_REGISTRY.items():
            if key.lower().replace("-", "_") == alt_search:
                return cls._create_pseudo_member(key, mapping_cls())

        # Return default
        return cls.default
