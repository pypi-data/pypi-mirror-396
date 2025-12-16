"""Custom __repr__ for DomoStream that includes conformed properties.

This module provides a smart __repr__ implementation that:
1. Shows only properties where is_repr=True
2. Truncates long values for readability
3. Prioritizes important properties (sql, database, warehouse)
4. Tracks missing provider mappings via _missing_mappings
"""

from typing import Any

from ....base.exceptions import DomoError


def get_missing_mappings(stream_obj: Any) -> list[str]:
    """Get list of conformed properties that don't have mappings for this provider.

    Args:
        stream_obj: The DomoStream instance

    Returns:
        List of property names that exist in registry but don't support this provider

    Example:
        >>> stream.data_provider_key = "google-sheets"
        >>> get_missing_mappings(stream)
        ['query', 'database', 'warehouse']  # SQL properties not supported
    """
    from ._conformed import CONFORMED_PROPERTIES

    missing = []
    provider_key = getattr(stream_obj, "data_provider_key", None)

    if not provider_key:
        return missing

    for prop_name, conf_prop in CONFORMED_PROPERTIES.items():
        # Skip properties not meant for repr
        if not conf_prop.is_repr:
            continue

        # Check if provider supports this property
        if provider_key not in conf_prop.supported_providers:
            missing.append(prop_name)

    return missing


def get_available_config_keys(stream_obj: Any) -> list[str]:
    """Get list of typed_config keys that are NOT mapped to conformed properties.

    This helps identify gaps in conformed property mappings - keys that exist
    in the typed_config but don't have a corresponding conformed property.

    Args:
        stream_obj: The DomoStream instance

    Returns:
        List of typed_config attribute names that aren't mapped to conformed properties

    Example:
        >>> stream.data_provider_key = "snowflake"
        >>> stream._available_config_keys
        ['role', 'authenticator', 'private_key']  # Keys not yet mapped
    """
    from ._conformed import CONFORMED_PROPERTIES

    typed_config = getattr(stream_obj, "typed_config", None)
    if not typed_config:
        return []

    provider_key = getattr(stream_obj, "data_provider_key", None)
    if not provider_key:
        return []

    # Get all attribute names from typed_config (excluding private/magic)
    all_keys = [
        attr
        for attr in dir(typed_config)
        if not attr.startswith("_") and not callable(getattr(typed_config, attr))
    ]

    # Get all mapped keys for this provider
    mapped_keys = set()
    for conf_prop in CONFORMED_PROPERTIES.values():
        key = conf_prop.get_key_for_provider(provider_key)
        if key:
            mapped_keys.add(key)

    # Return keys that aren't mapped
    unmapped = [key for key in all_keys if key not in mapped_keys]

    # Filter out common base class attributes
    exclude = {
        "data_provider_type",
        "transport_type",
        "data_provider_key",
        "raw",
        "auth",
    }
    return [key for key in unmapped if key not in exclude]


def create_stream_repr(
    stream_obj: Any,
    max_value_length: int = 50,
    max_total_length: int = 200,
    priority_props: list[str] = None,
    include_missing_mappings: bool = False,
) -> str:
    """Create a custom __repr__ string for DomoStream with conformed properties.

    Only includes properties where is_repr=True in CONFORMED_PROPERTIES registry.

    Args:
        stream_obj: The DomoStream instance
        max_value_length: Maximum length for individual property values
        max_total_length: Maximum total length of repr string
        priority_props: List of properties to show first (defaults to common SQL properties)
        include_missing_mappings: If True, append count of missing mappings

    Returns:
        Formatted repr string

    Example:
        >>> stream = DomoStream(id="123", data_provider_key="snowflake")
        >>> print(create_stream_repr(stream))
        DomoStream(id='123', provider='snowflake', sql='SELECT...', database='SA_PRD')
    """
    from ._conformed import CONFORMED_PROPERTIES

    priority_props = priority_props or ["sql", "database", "warehouse", "schema"]

    parts = []

    # Always include ID and provider
    parts.append(f"DomoStream(id='{stream_obj.id}'")

    if hasattr(stream_obj, "data_provider_name") and stream_obj.data_provider_name:
        parts.append(f"provider='{stream_obj.data_provider_name}'")
    elif hasattr(stream_obj, "data_provider_key") and stream_obj.data_provider_key:
        parts.append(f"provider='{stream_obj.data_provider_key}'")

    # Get property name mapping (registry name -> property name)
    property_map = {
        "query": "sql",
        "database": "database",
        "schema": "schema",
        "warehouse": "warehouse",
        "table": "table",
        "report_id": "report_id",
        "spreadsheet": "spreadsheet",
        "bucket": "bucket",
        "dataset_id": "dataset_id",
        "file_url": "file_url",
        "host": "host",
        "port": "port",
    }

    # Collect property values (ONLY where is_repr=True)
    prop_values = []

    # Check priority properties first
    for prop_name in priority_props:
        # Find the registry name for this property
        registry_name = next(
            (k for k, v in property_map.items() if v == prop_name), None
        )
        if not registry_name:
            continue

        # Check if this property is marked for repr
        conf_prop = CONFORMED_PROPERTIES.get(registry_name)
        if not conf_prop or not conf_prop.is_repr:
            continue

        if hasattr(stream_obj, prop_name):
            try:
                value = getattr(stream_obj, prop_name, None)
                if value is not None:
                    prop_values.append((prop_name, value, True))  # True = priority
            except DomoError:
                continue

    # Check other properties (ONLY where is_repr=True)
    for registry_name, conf_prop in CONFORMED_PROPERTIES.items():
        # Skip if not marked for repr
        if not conf_prop.is_repr:
            continue

        prop_name = property_map.get(registry_name)
        if not prop_name or prop_name in priority_props:
            continue

        if hasattr(stream_obj, prop_name):
            try:
                value = getattr(stream_obj, prop_name, None)
                if value is not None:
                    prop_values.append(
                        (prop_name, value, False)
                    )  # False = not priority
            except DomoError:
                continue

    # Format property values
    for prop_name, value, is_priority in prop_values:
        # Truncate long strings
        if isinstance(value, str):
            if len(value) > max_value_length:
                value = value[:max_value_length] + "..."

        parts.append(f"{prop_name}='{value}'")

        # Check if we're getting too long
        current_repr = ", ".join(parts) + ")"
        if len(current_repr) > max_total_length and not is_priority:
            parts.append("...")
            break

    # Optionally include missing mappings count
    if include_missing_mappings:
        missing = get_missing_mappings(stream_obj)
        if missing:
            parts.append(f"_missing_mappings={len(missing)}")

    return ", ".join(parts) + ")"


def get_conformed_properties_for_repr(stream_obj: Any) -> dict[str, Any]:
    """Get dictionary of conformed properties and their values for a stream.

    Args:
        stream_obj: The DomoStream instance

    Returns:
        Dict of {property_name: value} for all non-None conformed properties

    Example:
        >>> props = get_conformed_properties_for_repr(stream)
        >>> props
        {'sql': 'SELECT * FROM table', 'database': 'SA_PRD', 'warehouse': 'COMPUTE_WH'}
    """
    result = {}

    conformed_prop_names = [
        "sql",
        "database",
        "schema",
        "warehouse",
        "table",
        "report_id",
        "spreadsheet",
        "bucket",
        "dataset_id",
        "file_url",
        "host",
        "port",
    ]

    for prop_name in conformed_prop_names:
        if hasattr(stream_obj, prop_name):
            try:
                value = getattr(stream_obj, prop_name, None)
                if value is not None:
                    result[prop_name] = value
            except DomoError:
                continue

    return result


# Alternative: Mixin class approach
class ConformedPropertyReprMixin:
    """Mixin that adds smart __repr__ for classes with conformed properties.

    Usage:
        class DomoStream(ConformedPropertyReprMixin, DomoEntity):
            ...
    """

    def __repr__(self) -> str:
        """Smart repr that includes conformed properties."""
        return create_stream_repr(self)


__all__ = [
    "create_stream_repr",
    "get_conformed_properties_for_repr",
    "get_missing_mappings",
    "get_available_config_keys",
    "ConformedPropertyReprMixin",
]
