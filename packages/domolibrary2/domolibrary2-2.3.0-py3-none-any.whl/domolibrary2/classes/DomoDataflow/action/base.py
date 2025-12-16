"""
DomoDataflow Action Base Classes and Registry

This module provides the registration pattern for Magic ETL v2 action types.
Each action type can be registered via the @register_action_type decorator,
allowing for graceful handling of unknown action types while providing
typed access to known ones.

Usage:
    # Get the appropriate action class for a type
    action_class = get_action_class("LoadFromVault")
    action = action_class.from_dict(raw_action_dict)

    # Or use the factory function
    action = create_action_from_dict(raw_action_dict)
"""

from __future__ import annotations

import datetime as dt
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ....base import DomoEnumMixin
from ....utils import (
    DictDot as util_dd,
    convert as ct,
)

__all__ = [
    # Registry functions
    "register_action_type",
    "get_action_class",
    "create_action_from_dict",
    "get_registered_action_types",
    "get_unregistered_action_types",
    # Base classes
    "DomoDataflow_Action_Base",
    "DomoDataflow_Action_Unknown",
    "DomoDataflow_ActionResult",
    # Legacy exports (for backwards compatibility)
    "DomoDataflow_Action_Type",
    "DomoAction",
    "DomoDataflow_Action",
]


# Note: Standard logging is NOT used in domolibrary2 - dc_logger is async.
# For sync contexts (like __post_init__), use warnings.warn() instead.


# ============================================================================
# Registry and Decorator
# ============================================================================

# Registry to store action type classes
_ACTION_TYPE_REGISTRY: dict[str, type[DomoDataflow_Action_Base]] = {}

# Track encountered but unregistered types (for discovery)
_UNREGISTERED_TYPES: set[str] = set()


def register_action_type(action_type: str):
    """Decorator to register a DomoDataflow_Action_Base subclass.

    Args:
        action_type: The action type identifier (e.g., 'LoadFromVault', 'Filter')

    Example:
        @register_action_type('Filter')
        @dataclass
        class DomoDataflow_Action_Filter(DomoDataflow_Action_Base):
            filter_list: list[dict] = None
    """

    def decorator(
        cls: type[DomoDataflow_Action_Base],
    ) -> type[DomoDataflow_Action_Base]:
        _ACTION_TYPE_REGISTRY[action_type] = cls
        return cls

    return decorator


def get_action_class(action_type: str) -> type[DomoDataflow_Action_Base]:
    """Get the registered action class for a given type.

    If the type is not registered, returns DomoDataflow_Action_Unknown
    and tracks it for discovery purposes.

    Args:
        action_type: The action type string (e.g., "LoadFromVault")

    Returns:
        The registered action class, or DomoDataflow_Action_Unknown
    """
    cls = _ACTION_TYPE_REGISTRY.get(action_type)
    if cls is None:
        _UNREGISTERED_TYPES.add(action_type)
        # Note: Using warnings.warn() because this is a sync function.
        # dc_logger is async and cannot be used in sync contexts.
        return DomoDataflow_Action_Unknown
    return cls


def create_action_from_dict(
    obj: dict[str, Any], all_actions: list[DomoDataflow_Action_Base] | None = None
) -> DomoDataflow_Action_Base:
    """Factory function to create the appropriate action instance from a dict.

    This is the recommended way to create action instances from API responses.
    It automatically selects the appropriate class based on the 'type' field.

    Args:
        obj: Raw action dict from the API
        all_actions: Optional list of already-created actions for dependency resolution

    Returns:
        Appropriate DomoDataflow_Action_* instance

    Example:
        >>> for raw_action in dataflow.raw['procedures'][0]['actions']:
        ...     action = create_action_from_dict(raw_action)
        ...     print(f"{action.action_type}: {action.name}")
    """
    action_type = obj.get("type", "Unknown")
    cls = get_action_class(action_type)
    return cls.from_dict(obj, all_actions=all_actions)


def get_registered_action_types() -> list[str]:
    """Get list of all registered action types."""
    return sorted(_ACTION_TYPE_REGISTRY.keys())


def get_unregistered_action_types() -> set[str]:
    """Get set of action types that were encountered but not registered.

    Useful for discovering new action types that need to be implemented.
    """
    return _UNREGISTERED_TYPES.copy()


# ============================================================================
# Base Action Classes
# ============================================================================


@dataclass
class DomoDataflow_Action_Base:
    """Base class for all dataflow action types.

    All specific action types should inherit from this class and use
    the @register_action_type decorator.

    Common fields present in all action types:
        - id: Unique identifier for the action
        - action_type: The type string (e.g., "LoadFromVault")
        - name: Display name of the action (tile name)
        - depends_on: List of action IDs this action depends on
        - disabled: Whether the action is disabled
        - gui: GUI positioning data
        - settings: Action-specific settings
        - raw: Original API response dict
    """

    id: str
    action_type: str = None
    name: str = None
    depends_on: list[str] = None
    disabled: bool = False
    gui: dict = field(default=None, repr=False)
    settings: dict = field(default=None, repr=False)
    raw: dict = field(default=None, repr=False)

    # For dependency graph traversal
    parent_actions: list[DomoDataflow_Action_Base] = field(default=None, repr=False)

    @classmethod
    def from_dict(
        cls,
        obj: dict[str, Any],
        all_actions: list[DomoDataflow_Action_Base] | None = None,
    ) -> DomoDataflow_Action_Base:
        """Create an action instance from an API response dict.

        Subclasses can override _extract_fields() to handle type-specific fields.
        """
        dd = obj if isinstance(obj, util_dd.DictDot) else util_dd.DictDot(obj)

        # Extract common fields
        instance = cls(
            id=dd.id,
            action_type=dd.type,
            name=dd.name or dd.targetTableName or dd.tableName,
            depends_on=dd.dependsOn or [],
            disabled=dd.disabled or False,
            gui=dd.gui,
            settings=dd.settings,
            raw=obj,
        )

        # Let subclasses extract type-specific fields
        instance._extract_fields(dd)

        # Resolve parent actions if provided
        if all_actions:
            instance.get_parents(all_actions)

        return instance

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        """Extract type-specific fields from the dict. Override in subclasses."""
        pass

    def get_parents(
        self, domo_actions: list[DomoDataflow_Action_Base]
    ) -> list[DomoDataflow_Action_Base] | None:
        """Resolve parent actions from the depends_on IDs."""
        if self.depends_on and len(self.depends_on) > 0:
            self.parent_actions = [
                parent_action
                for depends_id in self.depends_on
                for parent_action in domo_actions
                if parent_action.id == depends_id
            ]

            if self.parent_actions:
                for parent in self.parent_actions:
                    if parent.depends_on:
                        parent.get_parents(domo_actions)

        return self.parent_actions


@dataclass
class DomoDataflow_Action_Unknown(DomoDataflow_Action_Base):
    """Fallback action class for unregistered action types.

    This class is used when an action type is encountered that hasn't been
    registered. All fields from the API response are preserved in the 'raw'
    attribute.
    """

    def __post_init__(self):
        if self.action_type:
            # Note: Using warnings.warn() because __post_init__ is sync.
            # dc_logger is async and cannot be used in sync contexts.
            warnings.warn(
                f"Unknown action type '{self.action_type}' encountered. "
                f"Consider registering it with @register_action_type('{self.action_type}')",
                stacklevel=2,
            )


# ============================================================================
# Action Result (for execution history)
# ============================================================================


@dataclass
class DomoDataflow_ActionResult:
    """Result of an action execution from dataflow history."""

    id: str
    type: str = None
    name: str = None
    is_success: bool = None
    rows_processed: int = None
    begin_time: dt.datetime = None
    end_time: dt.datetime = None
    duration_in_sec: int = None

    def __post_init__(self):
        if self.begin_time and self.end_time:
            self.duration_in_sec = (self.end_time - self.begin_time).total_seconds()

    @classmethod
    def from_dict(cls, obj: dict[str, Any]):
        return cls(
            id=obj.get("actionId"),
            type=obj.get("type"),
            is_success=obj.get("wasSuccessful"),
            begin_time=ct.convert_epoch_millisecond_to_datetime(
                obj.get("beginTime", None)
            ),
            end_time=ct.convert_epoch_millisecond_to_datetime(obj.get("endTime", None)),
            rows_processed=obj.get("rowsProcessed", None),
        )


# ============================================================================
# Legacy Compatibility Layer
# ============================================================================

# These are kept for backwards compatibility but marked as deprecated


class DomoDataflow_Action_Type(DomoEnumMixin, Enum):
    """DEPRECATED: Use @register_action_type decorator pattern instead.

    This enum is kept for backwards compatibility but new code should use
    the registration pattern with get_action_class() and create_action_from_dict().
    """

    LoadFromVault = "LoadFromVault"
    PublishToVault = "PublishToVault"
    GenerateTableAction = "GenerateTableAction"


@dataclass
class DomoAction:
    """DEPRECATED: Use DomoDataflow_Action_Base instead."""

    id: str
    type: str = None
    name: str = None


@dataclass
class DomoDataflow_Action(DomoAction):
    """DEPRECATED: Use create_action_from_dict() for new code.

    This class is kept for backwards compatibility with existing code
    that uses DomoDataflow_Action directly.
    """

    datasource_id: str = None
    sql: str = None
    depends_on: list[str] = None
    parent_actions: list[dict] = None

    @classmethod
    def from_dict(
        cls, obj: dict[str, Any], all_actions: list[DomoDataflow_Action] = None
    ):
        dd = obj

        if isinstance(dd, dict):
            dd = util_dd.DictDot(obj)

        tbl_name = dd.dataSource.name if dd.dataSource else None
        ds_id = dd.dataSource.guid if dd.dataSource else None

        action = cls(
            type=dd.type,
            id=dd.id,
            name=dd.name or dd.targetTableName or dd.tableName or tbl_name,
            depends_on=dd.dependsOn,
            datasource_id=dd.dataSourceId or ds_id,
            sql=dd.selectStatement or dd.query,
        )

        if all_actions:
            action.get_parents(all_actions)

        return action

    def get_parents(self, domo_actions: list[DomoDataflow_Action]):
        if self.depends_on and len(self.depends_on) > 0:
            self.parent_actions = [
                parent_action
                for depends_id in self.depends_on
                for parent_action in domo_actions
                if parent_action.id == depends_id
            ]

            if self.parent_actions:
                [
                    parent.get_parents(domo_actions)
                    for parent in self.parent_actions
                    if parent.depends_on
                ]

        return self.parent_actions
