"""
DomoDataflow Scripting Actions

Custom scripting actions in Magic ETL v2.
These correspond to the "Scripting" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_PythonEngine",
]


@register_action_type("PythonEngineAction")
@dataclass
class DomoDataflow_Action_PythonEngine(DomoDataflow_Action_Base):
    """Python Engine action - executes Python scripts.

    Also known as "Python Script" in the Magic ETL UI.

    Attributes:
        script: Python code to execute
        conda_env: Conda environment configuration
        inputs: List of input action IDs
        additions: Output column definitions

    Example:
        >>> python_action = dataflow.get_action_objects("PythonEngineAction")[0]
        >>> print(python_action.script)
    """

    script: str = None
    conda_env: dict = None
    account_permission: str = None
    inputs: list[str] = None
    additions: list[dict] = None
    remove_by_default: bool = False
    fill_missing_with_null: bool = False
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.script = dd.script
        self.conda_env = dd.condaEnv
        self.account_permission = dd.accountPermission
        self.inputs = dd.inputs or []
        self.additions = dd.additions or []
        self.remove_by_default = dd.removeByDefault or False
        self.fill_missing_with_null = dd.fillMissingWithNull or False
        self.tables = dd.tables
