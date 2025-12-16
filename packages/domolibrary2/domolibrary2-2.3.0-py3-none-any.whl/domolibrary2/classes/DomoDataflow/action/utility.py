"""
DomoDataflow Utility Actions

General utility actions for data transformation in Magic ETL v2.
These correspond to the "Utility" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_SQL",
    "DomoDataflow_Action_SelectValues",
    "DomoDataflow_Action_Constant",
    "DomoDataflow_Action_ExpressionEvaluator",
    "DomoDataflow_Action_Metadata",
    "DomoDataflow_Action_ValueMapper",
    "DomoDataflow_Action_SetValueField",
]


@register_action_type("SQL")
@dataclass
class DomoDataflow_Action_SQL(DomoDataflow_Action_Base):
    """SQL transform action - executes SQL statements.

    Attributes:
        statements: List of SQL statements to execute
        sql_dialect: SQL dialect (e.g., "MAGIC")

    Example:
        >>> sql_action = dataflow.get_action_objects("SQL")[0]
        >>> sql_action.sql = "SELECT * FROM `Input` LIMIT 10"
        >>> dataflow = await dataflow.update_action(sql_action.name, sql_action.raw)
    """

    statements: list[str] = None
    sql_dialect: str = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.statements = dd.statements or []
        if dd.settings:
            self.sql_dialect = dd.settings.get("sqlDialect")

    @property
    def sql(self) -> str | None:
        """Get or set the first SQL statement (convenience property).

        Getting returns the first statement or None.
        Setting updates both self.statements and self.raw.
        """
        if self.statements:
            return self.statements[0]
        return None

    @sql.setter
    def sql(self, value: str | list[str]) -> None:
        """Set SQL statement(s), updating both statements and raw."""
        if isinstance(value, str):
            self.statements = [value]
        else:
            self.statements = list(value)

        # Keep raw in sync
        if self.raw is not None:
            self.raw["statements"] = self.statements


@register_action_type("SelectValues")
@dataclass
class DomoDataflow_Action_SelectValues(DomoDataflow_Action_Base):
    """Select Values action - selects/renames/reorders columns.

    Also known as "Select Columns" in the Magic ETL UI.

    Attributes:
        fields: List of field configurations (name, rename, include/exclude)

    Example:
        >>> select_action = dataflow.get_action_objects("SelectValues")[0]
        >>> for field in select_action.fields:
        ...     print(f"{field.get('name')} -> {field.get('rename', field.get('name'))}")
    """

    fields: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.input = dd.input
        self.tables = dd.tables

    @property
    def column_names(self) -> list[str]:
        """Get list of selected column names."""
        if not self.fields:
            return []
        return [f.get("name") for f in self.fields if f.get("name")]

    @property
    def renamed_columns(self) -> dict[str, str]:
        """Get mapping of original name -> renamed name for renamed columns."""
        if not self.fields:
            return {}
        return {
            f.get("name"): f.get("rename")
            for f in self.fields
            if f.get("rename") and f.get("name") != f.get("rename")
        }


@register_action_type("Constant")
@dataclass
class DomoDataflow_Action_Constant(DomoDataflow_Action_Base):
    """Constant action - adds constant value columns.

    Also known as "Add Constants" in the Magic ETL UI.

    Attributes:
        fields: List of constant field definitions with name, type, and value

    Example:
        >>> constant_action = dataflow.get_action_objects("Constant")[0]
        >>> for field in constant_action.fields:
        ...     print(f"{field.get('name')}: {field.get('value')}")
    """

    fields: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.input = dd.input
        self.tables = dd.tables

    @property
    def constants(self) -> dict[str, Any]:
        """Get mapping of constant name -> value."""
        if not self.fields:
            return {}
        return {f.get("name"): f.get("value") for f in self.fields if f.get("name")}


@register_action_type("ExpressionEvaluator")
@dataclass
class DomoDataflow_Action_ExpressionEvaluator(DomoDataflow_Action_Base):
    """Expression Evaluator action - creates calculated columns using formulas.

    Also known as "Add Formula" or "Beast Mode" in the Magic ETL UI.

    Attributes:
        expressions: List of expression definitions with name, expression, and type

    Example:
        >>> formula_action = dataflow.get_action_objects("ExpressionEvaluator")[0]
        >>> for expr in formula_action.expressions:
        ...     print(f"{expr.get('name')}: {expr.get('expression')}")
    """

    expressions: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.expressions = dd.expressions or []
        self.input = dd.input
        self.tables = dd.tables

    @property
    def formulas(self) -> dict[str, str]:
        """Get mapping of formula name -> expression."""
        if not self.expressions:
            return {}
        return {
            e.get("name"): e.get("expression")
            for e in self.expressions
            if e.get("name") and e.get("expression")
        }


@register_action_type("Metadata")
@dataclass
class DomoDataflow_Action_Metadata(DomoDataflow_Action_Base):
    """Metadata action - modifies column metadata (rename, type change).

    Also known as "Set Column Type" or "Rename Columns" in the Magic ETL UI.

    Attributes:
        fields: List of field metadata modifications

    Example:
        >>> metadata_action = dataflow.get_action_objects("Metadata")[0]
        >>> for field in metadata_action.fields:
        ...     print(f"{field.get('name')}: {field.get('type')}")
    """

    fields: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.input = dd.input
        self.tables = dd.tables

    @property
    def type_changes(self) -> dict[str, str]:
        """Get mapping of column -> new type."""
        if not self.fields:
            return {}
        return {f.get("name"): f.get("type") for f in self.fields if f.get("type")}


@register_action_type("ValueMapper")
@dataclass
class DomoDataflow_Action_ValueMapper(DomoDataflow_Action_Base):
    """Value Mapper action - maps values from one set to another.

    Also known as "Map Values" in the Magic ETL UI.

    Attributes:
        field_to_use: Source column to map from
        target_field: Target column name
        mappings: List of value mappings
        unmapped_behavior: What to do with unmapped values

    Example:
        >>> mapper_action = dataflow.get_action_objects("ValueMapper")[0]
        >>> print(f"Mapping {mapper_action.field_to_use} -> {mapper_action.target_field}")
    """

    field_to_use: str = None
    target_field: str = None
    target_type: str = None
    mappings: list[dict] = None
    unmapped_behavior: str = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.field_to_use = dd.fieldToUse
        self.target_field = dd.targetField
        self.target_type = dd.targetType
        self.mappings = dd.mappings or []
        self.unmapped_behavior = dd.unmappedBehavior
        self.input = dd.input
        self.tables = dd.tables

    @property
    def value_map(self) -> dict[Any, Any]:
        """Get mapping of source value -> target value."""
        if not self.mappings:
            return {}
        return {
            m.get("source"): m.get("target")
            for m in self.mappings
            if m.get("source") is not None and m.get("target") is not None
        }


@register_action_type("SetValueField")
@dataclass
class DomoDataflow_Action_SetValueField(DomoDataflow_Action_Base):
    """Set Value Field action - sets or updates field values.

    Attributes:
        fields: List of field value settings

    Example:
        >>> setvalue_action = dataflow.get_action_objects("SetValueField")[0]
        >>> for field in setvalue_action.fields:
        ...     print(f"{field.get('name')}: {field.get('value')}")
    """

    fields: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.input = dd.input
        self.tables = dd.tables
