"""Dynamic property registration for conformed properties.

This module provides utilities to automatically register conformed properties
as @property methods on the DomoStream class.
"""


def _create_property_getter(property_name: str, doc: str) -> property:
    """Create a property getter function for a conformed property.

    Args:
        property_name: Name of the conformed property (e.g., "query", "database")
        doc: Docstring for the property

    Returns:
        property object that can be added to a class

    Example:
        >>> prop = _create_property_getter("query", "SQL query")
        >>> DomoStream.sql = prop
    """

    def getter(self) -> str | None:
        return self._get_conformed_value(property_name)

    getter.__doc__ = doc
    getter.__name__ = property_name
    return property(getter)


def register_conformed_properties(cls, properties_registry: dict):
    """Dynamically register conformed properties onto a class.

    Args:
        cls: Class to register properties on (DomoStream)
        properties_registry: Dict of ConformedProperty objects (CONFORMED_PROPERTIES)

    Example:
        >>> from .stream_configs._conformed import CONFORMED_PROPERTIES
        >>> register_conformed_properties(DomoStream, CONFORMED_PROPERTIES)
    """
    # Map of property names to their display names
    property_name_map = {
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
        "custom_query": None,  # Internal, not exposed as property
    }

    for prop_name, conf_prop in properties_registry.items():
        # Get the public property name
        public_name = property_name_map.get(prop_name)

        # Skip if no public name (internal properties)
        if public_name is None:
            continue

        # Skip if property already exists (manual override)
        if hasattr(cls, public_name):
            continue

        # Create docstring
        doc = f"""Get {conf_prop.description or prop_name} from stream configuration.

        {conf_prop.description or "Configuration parameter"}

        Supported providers: {", ".join(conf_prop.supported_providers[:3])}
        {"..." if len(conf_prop.supported_providers) > 3 else ""}
        ({len(conf_prop.supported_providers)} total)

        Returns:
            Value from configuration or None if not available

        Example:
            >>> stream = await DomoStream.get_by_id(auth, stream_id)
            >>> print(stream.{public_name})
        """

        # Create and register the property
        prop = _create_property_getter(prop_name, doc)
        setattr(cls, public_name, prop)


def register_conformed_property(
    cls, property_name: str, public_name: str = None, docstring: str = None
):
    """Register a single conformed property onto a class.

    Decorator-based approach for adding individual properties.

    Args:
        cls: Class to register property on
        property_name: Name in CONFORMED_PROPERTIES registry
        public_name: Name of the property on the class (defaults to property_name)
        docstring: Optional custom docstring

    Example:
        >>> @register_conformed_property(DomoStream, "query", "sql")
        ... class DomoStream:
        ...     pass
    """
    public_name = public_name or property_name

    # Skip if already exists
    if hasattr(cls, public_name):
        return cls

    doc = docstring or f"Get {property_name} from stream configuration."

    prop = _create_property_getter(property_name, doc)
    setattr(cls, public_name, prop)

    return cls


__all__ = [
    "register_conformed_properties",
    "register_conformed_property",
]
