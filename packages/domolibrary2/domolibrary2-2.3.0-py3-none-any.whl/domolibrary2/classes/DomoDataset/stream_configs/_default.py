"""Default stream configuration mapping for unknown provider types."""

from dataclasses import dataclass, field

from ._base import (
    StreamConfig_Base,
    StreamConfig_Mapping,
    register_mapping,
    register_stream_config,
)

__all__ = [
    # Old pattern (deprecated)
    "DefaultMapping",
    # New pattern (typed config)
    "Default_StreamConfig",
]


@register_mapping("default")
@dataclass
class DefaultMapping(StreamConfig_Mapping):
    """Default data provider mapping for unknown types."""

    data_provider_type: str = "default"
    is_default: bool = True


# ============================================================================
# NEW PATTERN: Typed Stream Config Classes
# ============================================================================


@register_stream_config("default")
@dataclass
class Default_StreamConfig(StreamConfig_Base):
    """Default stream configuration for unknown provider types (typed).

    This is a catch-all config that accepts any parameters.
    Used when the specific provider type is not recognized.
    """

    data_provider_type: str = "default"

    # No specific fields defined - this is intentionally flexible
    # Additional fields will be captured in raw dict

    _fields_for_export: list[str] = field(
        default_factory=list,  # Export nothing by default
        repr=False,
        init=False,
    )
