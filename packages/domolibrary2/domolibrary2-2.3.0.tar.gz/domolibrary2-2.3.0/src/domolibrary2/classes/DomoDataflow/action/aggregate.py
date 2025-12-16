"""
DomoDataflow Aggregate Actions

Aggregation and windowing actions in Magic ETL v2.
These correspond to the "Aggregate" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_GroupBy",
    "DomoDataflow_Action_WindowAction",
]


@register_action_type("GroupBy")
@dataclass
class DomoDataflow_Action_GroupBy(DomoDataflow_Action_Base):
    """Group By action - aggregates data by grouping columns.

    Attributes:
        groups: List of columns to group by
        fields: List of aggregation fields with aggregation type
        all_rows: Whether to include all rows (not just first per group)

    Example:
        >>> groupby_action = dataflow.get_action_objects("GroupBy")[0]
        >>> print(f"Grouping by: {groupby_action.group_columns}")
        >>> print(f"Aggregations: {groupby_action.aggregations}")
    """

    groups: list[dict] = None
    fields: list[dict] = None
    all_rows: bool = False
    add_line_number: bool = False
    give_back_row: str = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.groups = dd.groups or []
        self.fields = dd.fields or []
        self.all_rows = dd.allRows or False
        self.add_line_number = dd.addLineNumber or False
        self.give_back_row = dd.giveBackRow
        self.input = dd.input
        self.tables = dd.tables

    @property
    def group_columns(self) -> list[str]:
        """Get list of columns being grouped by."""
        if not self.groups:
            return []
        return [g.get("column") or g.get("name") for g in self.groups if g]

    @property
    def aggregations(self) -> dict[str, str]:
        """Get mapping of output column -> aggregation type."""
        if not self.fields:
            return {}
        return {
            f.get("name"): f.get("aggregation", "FIRST")
            for f in self.fields
            if f.get("name")
        }


@register_action_type("WindowAction")
@dataclass
class DomoDataflow_Action_WindowAction(DomoDataflow_Action_Base):
    """Window action - performs window/ranking functions.

    Also known as "Rank & Window" in the Magic ETL UI.

    Attributes:
        additions: List of window function definitions
        group_rules: Columns to partition by
        order_rules: Columns to order by within partitions

    Example:
        >>> window_action = dataflow.get_action_objects("WindowAction")[0]
        >>> print(f"Partitioning by: {window_action.partition_columns}")
    """

    additions: list[dict] = None
    group_rules: list[dict] = None
    order_rules: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.additions = dd.additions or []
        self.group_rules = dd.groupRules or []
        self.order_rules = dd.orderRules or []
        self.input = dd.input
        self.tables = dd.tables

    @property
    def partition_columns(self) -> list[str]:
        """Get list of columns used for partitioning."""
        if not self.group_rules:
            return []
        return [g.get("column") or g.get("name") for g in self.group_rules if g]

    @property
    def order_columns(self) -> list[str]:
        """Get list of columns used for ordering."""
        if not self.order_rules:
            return []
        return [o.get("column") or o.get("name") for o in self.order_rules if o]
