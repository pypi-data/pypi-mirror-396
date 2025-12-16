"""
DomoDataflow Filter Actions

Filter and data cleaning actions in Magic ETL v2.
These correspond to the "Filter" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_Filter",
    "DomoDataflow_Action_Unique",
]


@register_action_type("Filter")
@dataclass
class DomoDataflow_Action_Filter(DomoDataflow_Action_Base):
    """Filter action - filters rows based on conditions.

    Attributes:
        filter_list: List of filter conditions

    Example:
        >>> filter_action = dataflow.get_action_objects("Filter")[0]
        >>> print(filter_action.filter_list)
    """

    filter_list: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.filter_list = dd.filterList or []
        self.input = dd.input
        self.tables = dd.tables


@register_action_type("Unique")
@dataclass
class DomoDataflow_Action_Unique(DomoDataflow_Action_Base):
    """Unique action - removes duplicate rows.

    Also known as "Remove Duplicates" in the Magic ETL UI.

    Attributes:
        fields: Columns to consider for uniqueness
        count_rows: Whether to add a count column

    Example:
        >>> unique_action = dataflow.get_action_objects("Unique")[0]
        >>> print(f"Deduping on: {unique_action.dedup_columns}")
    """

    fields: list[dict] = None
    count_rows: bool = False
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.count_rows = dd.countRows or False
        self.input = dd.input
        self.tables = dd.tables

    @property
    def dedup_columns(self) -> list[str]:
        """Get list of columns used for deduplication."""
        if not self.fields:
            return []
        return [f.get("name") for f in self.fields if f.get("name")]
