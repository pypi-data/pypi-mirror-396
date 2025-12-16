"""
DomoDataflow Pivot Actions

Pivot and unpivot actions for reshaping data in Magic ETL v2.
These correspond to the "Pivot" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_Normalizer",
    "DomoDataflow_Action_NormalizeAll",
    "DomoDataflow_Action_Denormalizer",
]


@register_action_type("Normalizer")
@dataclass
class DomoDataflow_Action_Normalizer(DomoDataflow_Action_Base):
    """Normalizer action - unpivots columns to rows.

    Also known as "Unpivot" in the Magic ETL UI.

    Attributes:
        fields: Columns to unpivot
        typefield: Name of the column containing original column names

    Example:
        >>> normalizer_action = dataflow.get_action_objects("Normalizer")[0]
        >>> print(f"Unpivoting columns into '{normalizer_action.typefield}'")
    """

    fields: list[dict] = None
    typefield: str = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.typefield = dd.typefield
        self.input = dd.input
        self.tables = dd.tables

    @property
    def unpivot_columns(self) -> list[str]:
        """Get list of columns being unpivoted."""
        if not self.fields:
            return []
        return [f.get("name") for f in self.fields if f.get("name")]


@register_action_type("NormalizeAll")
@dataclass
class DomoDataflow_Action_NormalizeAll(DomoDataflow_Action_Base):
    """Normalize All action - unpivots all columns except ID columns.

    Also known as "Dynamic Unpivot" in the Magic ETL UI.

    Attributes:
        id_fields: Columns to keep as identifiers (not unpivoted)
        key_field: Name of the column for original column names
        value_field: Name of the column for values

    Example:
        >>> normalize_action = dataflow.get_action_objects("NormalizeAll")[0]
        >>> print(f"ID columns: {normalize_action.id_columns}")
    """

    id_fields: list[dict] = None
    key_field: str = None
    value_field: str = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.id_fields = dd.idFields or []
        self.key_field = dd.keyField
        self.value_field = dd.valueField
        self.input = dd.input
        self.tables = dd.tables

    @property
    def id_columns(self) -> list[str]:
        """Get list of ID columns (not being unpivoted)."""
        if not self.id_fields:
            return []
        return [f.get("name") for f in self.id_fields if f.get("name")]


@register_action_type("Denormaliser")
@dataclass
class DomoDataflow_Action_Denormalizer(DomoDataflow_Action_Base):
    """Denormaliser action - pivots rows to columns.

    Also known as "Pivot" in the Magic ETL UI.

    Attributes:
        key_field: Column containing values to become column headers
        group: Columns to group by
        fields: Columns to pivot

    Example:
        >>> pivot_action = dataflow.get_action_objects("Denormaliser")[0]
        >>> print(f"Pivoting on '{pivot_action.key_field}'")
    """

    key_field: str = None
    group: list[dict] = None
    fields: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.key_field = dd.keyField
        self.group = dd.group or []
        self.fields = dd.fields or []
        self.input = dd.input
        self.tables = dd.tables

    @property
    def group_columns(self) -> list[str]:
        """Get list of columns being grouped by."""
        if not self.group:
            return []
        return [g.get("name") for g in self.group if g.get("name")]
