"""
DomoDataflow Combine Data Actions

Actions for joining and combining datasets in Magic ETL v2.
These correspond to the "Combine Data" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_MergeJoin",
    "DomoDataflow_Action_UnionAll",
    "DomoDataflow_Action_SplitJoin",
]


@register_action_type("MergeJoin")
@dataclass
class DomoDataflow_Action_MergeJoin(DomoDataflow_Action_Base):
    """Merge Join action - joins two data sources.

    Attributes:
        join_type: Type of join (INNER, LEFT, RIGHT, OUTER)
        keys1: Join keys from first input
        keys2: Join keys from second input

    Example:
        >>> join_action = dataflow.get_action_objects("MergeJoin")[0]
        >>> print(f"Join type: {join_action.join_type}")
        >>> print(f"Keys: {join_action.keys1} = {join_action.keys2}")
    """

    join_type: str = None
    keys1: list[str] = None
    keys2: list[str] = None
    relationship_type: str = None
    schema_modification1: dict = None
    schema_modification2: dict = None
    step1: str = None
    step2: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.join_type = dd.joinType
        self.keys1 = dd.keys1 or []
        self.keys2 = dd.keys2 or []
        self.relationship_type = dd.relationshipType
        self.schema_modification1 = dd.schemaModification1
        self.schema_modification2 = dd.schemaModification2
        self.step1 = dd.step1
        self.step2 = dd.step2
        self.tables = dd.tables


@register_action_type("UnionAll")
@dataclass
class DomoDataflow_Action_UnionAll(DomoDataflow_Action_Base):
    """Union All action - combines multiple data sources vertically.

    Attributes:
        inputs: List of input action IDs
        union_type: Type of union (UNION_ALL, UNION, etc.)
        strict: Whether to enforce strict schema matching

    Example:
        >>> union_action = dataflow.get_action_objects("UnionAll")[0]
        >>> print(f"Combining {len(union_action.inputs)} inputs")
    """

    inputs: list[str] = None
    union_type: str = None
    strict: bool = False
    schema_source: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.inputs = dd.inputs or []
        self.union_type = dd.unionType
        self.strict = dd.strict or False
        self.schema_source = dd.schemaSource
        self.tables = dd.tables


@register_action_type("SplitJoin")
@dataclass
class DomoDataflow_Action_SplitJoin(DomoDataflow_Action_Base):
    """Split Join action - performs a join that splits into multiple outputs.

    Creates inner, left anti, and right anti outputs from a single join.

    Attributes:
        keys1: Join keys from first input
        keys2: Join keys from second input
        inner_table: Name of inner join output
        left_anti_table: Name of left anti join output
        right_anti_table: Name of right anti join output

    Example:
        >>> splitjoin_action = dataflow.get_action_objects("SplitJoin")[0]
        >>> print(f"Inner: {splitjoin_action.inner_table}")
    """

    keys1: list[str] = None
    keys2: list[str] = None
    step1: str = None
    step2: str = None
    inner_table: str = None
    left_anti_table: str = None
    right_anti_table: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.keys1 = dd.keys1 or []
        self.keys2 = dd.keys2 or []
        self.step1 = dd.step1
        self.step2 = dd.step2
        self.inner_table = dd.innerTable
        self.left_anti_table = dd.leftAntiTable
        self.right_anti_table = dd.rightAntiTable
        self.tables = dd.tables
