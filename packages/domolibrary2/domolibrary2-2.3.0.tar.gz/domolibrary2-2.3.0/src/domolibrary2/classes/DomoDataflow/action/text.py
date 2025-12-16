"""
DomoDataflow Text Actions

Text manipulation and formatting actions in Magic ETL v2.
These correspond to the "Text" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_ConcatFields",
    "DomoDataflow_Action_ReplaceString",
    "DomoDataflow_Action_SplitColumn",
    "DomoDataflow_Action_TextFormatting",
]


@register_action_type("ConcatFields")
@dataclass
class DomoDataflow_Action_ConcatFields(DomoDataflow_Action_Base):
    """Concat Fields action - concatenates multiple columns into one.

    Also known as "Combine Columns" in the Magic ETL UI.

    Attributes:
        fields: List of columns to concatenate
        separator: Separator string between values
        target_field_name: Name of the output column
        remove_selected_fields: Whether to remove source columns

    Example:
        >>> concat_action = dataflow.get_action_objects("ConcatFields")[0]
        >>> print(f"Combining {concat_action.source_columns} with '{concat_action.separator}'")
    """

    fields: list[dict] = None
    separator: str = None
    target_field_name: str = None
    remove_selected_fields: bool = False
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.separator = dd.separator or ""
        self.target_field_name = dd.targetFieldName
        self.remove_selected_fields = dd.removeSelectedFields or False
        self.input = dd.input
        self.tables = dd.tables

    @property
    def source_columns(self) -> list[str]:
        """Get list of columns being concatenated."""
        if not self.fields:
            return []
        return [f.get("name") for f in self.fields if f.get("name")]


@register_action_type("ReplaceString")
@dataclass
class DomoDataflow_Action_ReplaceString(DomoDataflow_Action_Base):
    """Replace String action - replaces strings in columns.

    Also known as "Replace Text" in the Magic ETL UI.

    Attributes:
        fields: List of replacement configurations

    Example:
        >>> replace_action = dataflow.get_action_objects("ReplaceString")[0]
        >>> for field in replace_action.fields:
        ...     print(f"{field.get('name')}: {field.get('find')} -> {field.get('replace')}")
    """

    fields: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.input = dd.input
        self.tables = dd.tables


@register_action_type("SplitColumnAction")
@dataclass
class DomoDataflow_Action_SplitColumn(DomoDataflow_Action_Base):
    """Split Column action - splits a column into multiple columns.

    Attributes:
        source_column: Column to split
        delimiter: Delimiter to split on
        delimiter_type: Type of delimiter (STRING, REGEX, etc.)
        use_regex: Whether delimiter is a regex
        additions: New columns to create from splits
        combine_extra_splits: Whether to combine extra splits into last column

    Example:
        >>> split_action = dataflow.get_action_objects("SplitColumnAction")[0]
        >>> print(f"Splitting {split_action.source_column} on '{split_action.delimiter}'")
    """

    source_column: str = None
    delimiter: str = None
    delimiter_type: str = None
    use_regex: bool = False
    additions: list[dict] = None
    combine_extra_splits: bool = False
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.source_column = dd.sourceColumn
        self.delimiter = dd.delimiter
        self.delimiter_type = dd.delimiterType
        self.use_regex = dd.useRegex or False
        self.additions = dd.additions or []
        self.combine_extra_splits = dd.combineExtraSplits or False
        self.input = dd.input
        self.tables = dd.tables

    @property
    def output_columns(self) -> list[str]:
        """Get list of output column names."""
        if not self.additions:
            return []
        return [a.get("name") for a in self.additions if a.get("name")]


@register_action_type("TextFormatting")
@dataclass
class DomoDataflow_Action_TextFormatting(DomoDataflow_Action_Base):
    """Text Formatting action - applies text formatting transformations.

    Attributes:
        fields: List of text formatting configurations

    Example:
        >>> text_action = dataflow.get_action_objects("TextFormatting")[0]
        >>> for field in text_action.fields:
        ...     print(f"{field.get('name')}: {field.get('operation')}")
    """

    fields: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields or []
        self.input = dd.input
        self.tables = dd.tables
