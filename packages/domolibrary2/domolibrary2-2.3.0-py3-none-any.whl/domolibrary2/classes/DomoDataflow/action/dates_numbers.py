"""
DomoDataflow Date and Number Actions

Date and numeric calculation actions in Magic ETL v2.
These correspond to the "Dates and Numbers" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_DateCalculator",
    "DomoDataflow_Action_NumericCalculator",
]


@register_action_type("DateCalculator")
@dataclass
class DomoDataflow_Action_DateCalculator(DomoDataflow_Action_Base):
    """Date Calculator action - performs date calculations.

    Attributes:
        calculations: List of date calculation definitions

    Example:
        >>> date_action = dataflow.get_action_objects("DateCalculator")[0]
        >>> for calc in date_action.calculations:
        ...     print(f"{calc.get('name')}: {calc.get('operation')}")
    """

    calculations: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.calculations = dd.calculations or []
        self.input = dd.input
        self.tables = dd.tables


@register_action_type("NumericCalculator")
@dataclass
class DomoDataflow_Action_NumericCalculator(DomoDataflow_Action_Base):
    """Numeric Calculator action - performs numeric calculations.

    Also known as "Calculator" in the Magic ETL UI.

    Attributes:
        calculations: List of calculation definitions

    Example:
        >>> calc_action = dataflow.get_action_objects("NumericCalculator")[0]
        >>> for calc in calc_action.calculations:
        ...     print(f"{calc.get('name')}: {calc.get('operation')}")
    """

    calculations: list[dict] = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.calculations = dd.calculations or []
        self.input = dd.input
        self.tables = dd.tables
