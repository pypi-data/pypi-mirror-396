"""
DomoDataflow AI Services Actions

AI-powered actions in Magic ETL v2.
These correspond to the "AI Services" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_TextGeneration",
]


@register_action_type("TextGeneration")
@dataclass
class DomoDataflow_Action_TextGeneration(DomoDataflow_Action_Base):
    """Text Generation action - generates text using AI models.

    Attributes:
        model_id: ID of the AI model
        prompt: Prompt template for generation
        instructions: System instructions
        temperature: Sampling temperature
        output_column_name: Name of output column

    Example:
        >>> textgen_action = dataflow.get_action_objects("TextGeneration")[0]
        >>> print(f"Model: {textgen_action.model_id}")
        >>> print(f"Prompt: {textgen_action.prompt}")
    """

    model_id: str = None
    prompt: str = None
    instructions: str = None
    temperature: float = None
    output_column_name: str = None
    parameters: dict = None
    path: str = None
    model_input_schema: dict = None
    model_output_schema: dict = None
    column_settings: dict = None
    input: str = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.model_id = dd.modelId
        self.prompt = dd.prompt
        self.instructions = dd.instructions
        self.temperature = dd.temperature
        self.output_column_name = dd.outputColumnName
        self.parameters = dd.parameters
        self.path = dd.path
        self.model_input_schema = dd.modelInputSchema
        self.model_output_schema = dd.modelOutputSchema
        self.column_settings = dd.columnSettings
        self.input = dd.input
        self.tables = dd.tables


# ============================================================================
# Action Result Class (for execution history)
# ============================================================================
