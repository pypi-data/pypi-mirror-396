"""
DomoDataflow Data Science Actions

Machine learning and data science actions in Magic ETL v2.
These correspond to the "Data Science" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_MLInferenceAction",
    "DomoDataflow_Action_UserDefined",
]


@register_action_type("MLInferenceAction")
@dataclass
class DomoDataflow_Action_MLInferenceAction(DomoDataflow_Action_Base):
    """ML Inference action - runs ML model predictions.

    Attributes:
        ml_model_id: ID of the ML model to use
        inference_column: Output column name for predictions
        include_input_data: Whether to include input columns in output

    Example:
        >>> ml_action = dataflow.get_action_objects("MLInferenceAction")[0]
        >>> print(f"Model ID: {ml_action.ml_model_id}")
    """

    ml_model_id: str = None
    inference_column: str = None
    inference_column_rename: str = None
    inference_response: dict = None
    include_input_data: bool = True
    model_schema: dict = None
    column_settings: dict = None
    notes: str = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.ml_model_id = dd.mlModelId
        self.inference_column = dd.inferenceColumn
        self.inference_column_rename = dd.inferenceColumnRename
        self.inference_response = dd.inferenceResponse
        self.include_input_data = (
            dd.includeInputData if dd.includeInputData is not None else True
        )
        self.model_schema = dd.modelSchema
        self.column_settings = dd.columnSettings
        self.notes = dd.notes
        self.input = dd.input
        self.tables = dd.tables


# ============================================================================
# Additional Transform Action Types
# ============================================================================


@register_action_type("UserDefinedAction")
@dataclass
class DomoDataflow_Action_UserDefined(DomoDataflow_Action_Base):
    """User Defined Action - custom reusable action from Action Library.

    Attributes:
        action_definition_id: ID of the action definition
        variables: Variable values for the action
        inputs: List of input action IDs
        additions: Output column definitions

    Example:
        >>> uda_action = dataflow.get_action_objects("UserDefinedAction")[0]
        >>> print(f"Action Definition: {uda_action.action_definition_id}")
    """

    action_definition_id: str = None
    variables: dict = None
    inputs: list[str] = None
    additions: list[dict] = None
    remove_by_default: bool = False
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.action_definition_id = dd.actionDefinitionId
        self.variables = dd.variables
        self.inputs = dd.inputs or []
        self.additions = dd.additions or []
        self.remove_by_default = dd.removeByDefault or False
        self.tables = dd.tables
