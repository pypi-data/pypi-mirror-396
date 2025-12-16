"""
DomoDataflow Action Types

This module provides a registration pattern for Magic ETL v2 action types.
Action classes are organized by their category in the Domo ETL UI sidebar.

The folder structure matches Domo's UI categories:
- datasets: Input/Output actions (LoadFromVault, PublishToVault, etc.)
- utility: General utility actions (SQL, SelectValues, Constant, etc.)
- filter: Filter and data cleaning (Filter, Unique)
- text: Text manipulation (ConcatFields, ReplaceString, etc.)
- dates_numbers: Date and numeric calculations
- combine: Joining and combining data (MergeJoin, UnionAll, SplitJoin)
- aggregate: Aggregation actions (GroupBy, WindowAction)
- pivot: Pivot and unpivot operations
- scripting: Custom code execution (PythonEngine)
- data_science: ML and data science (MLInferenceAction, UserDefined)
- ai_services: AI-powered actions (TextGeneration)

Usage:
    from domolibrary2.classes.DomoDataflow.action import (
        create_action_from_dict,
        DomoDataflow_Action_LoadFromVault,
        DomoDataflow_Action_SQL,
    )

    # Create action from API response
    action = create_action_from_dict(raw_action_dict)

    # Or use specific class
    if isinstance(action, DomoDataflow_Action_SQL):
        print(f"SQL: {action.sql}")
"""

from __future__ import annotations

# Aggregate actions
from .aggregate import (
    DomoDataflow_Action_GroupBy,
    DomoDataflow_Action_WindowAction,
)

# AI services actions
from .ai_services import DomoDataflow_Action_TextGeneration

# Base classes and registry functions
from .base import (  # Base classes; Registry functions
    DomoAction,
    DomoDataflow_Action,
    DomoDataflow_Action_Base,
    DomoDataflow_Action_Type,
    DomoDataflow_Action_Unknown,
    DomoDataflow_ActionResult,
    create_action_from_dict,
    get_action_class,
    get_registered_action_types,
    get_unregistered_action_types,
    register_action_type,
)

# Combine data actions
from .combine import (
    DomoDataflow_Action_MergeJoin,
    DomoDataflow_Action_SplitJoin,
    DomoDataflow_Action_UnionAll,
)

# Data science actions
from .data_science import (
    DomoDataflow_Action_MLInferenceAction,
    DomoDataflow_Action_UserDefined,
)

# Dataset actions (Input/Output)
from .datasets import (
    DomoDataflow_Action_GenerateTable,
    DomoDataflow_Action_LoadFromVault,
    DomoDataflow_Action_PublishToVault,
    DomoDataflow_Action_PublishToWriteback,
)

# Date and number actions
from .dates_numbers import (
    DomoDataflow_Action_DateCalculator,
    DomoDataflow_Action_NumericCalculator,
)

# Filter actions
from .filter import (
    DomoDataflow_Action_Filter,
    DomoDataflow_Action_Unique,
)

# Pivot actions
from .pivot import (
    DomoDataflow_Action_Denormalizer,
    DomoDataflow_Action_NormalizeAll,
    DomoDataflow_Action_Normalizer,
)

# Scripting actions
from .scripting import DomoDataflow_Action_PythonEngine

# Text actions
from .text import (
    DomoDataflow_Action_ConcatFields,
    DomoDataflow_Action_ReplaceString,
    DomoDataflow_Action_SplitColumn,
    DomoDataflow_Action_TextFormatting,
)

# Utility actions
from .utility import (
    DomoDataflow_Action_Constant,
    DomoDataflow_Action_ExpressionEvaluator,
    DomoDataflow_Action_Metadata,
    DomoDataflow_Action_SelectValues,
    DomoDataflow_Action_SetValueField,
    DomoDataflow_Action_SQL,
    DomoDataflow_Action_ValueMapper,
)

__all__ = [
    # Registry functions
    "register_action_type",
    "get_action_class",
    "create_action_from_dict",
    "get_registered_action_types",
    "get_unregistered_action_types",
    # Base classes
    "DomoDataflow_Action_Base",
    "DomoDataflow_Action_Unknown",
    "DomoDataflow_ActionResult",
    # Input/Output action types
    "DomoDataflow_Action_LoadFromVault",
    "DomoDataflow_Action_PublishToVault",
    "DomoDataflow_Action_PublishToWriteback",
    "DomoDataflow_Action_GenerateTable",
    # Utility action types
    "DomoDataflow_Action_SQL",
    "DomoDataflow_Action_SelectValues",
    "DomoDataflow_Action_Constant",
    "DomoDataflow_Action_ExpressionEvaluator",
    "DomoDataflow_Action_Metadata",
    "DomoDataflow_Action_ValueMapper",
    "DomoDataflow_Action_SetValueField",
    # Filter action types
    "DomoDataflow_Action_Filter",
    "DomoDataflow_Action_Unique",
    # Text action types
    "DomoDataflow_Action_ConcatFields",
    "DomoDataflow_Action_SplitColumn",
    "DomoDataflow_Action_ReplaceString",
    "DomoDataflow_Action_TextFormatting",
    # Date and number action types
    "DomoDataflow_Action_DateCalculator",
    "DomoDataflow_Action_NumericCalculator",
    # Combine data action types
    "DomoDataflow_Action_MergeJoin",
    "DomoDataflow_Action_UnionAll",
    "DomoDataflow_Action_SplitJoin",
    # Aggregate action types
    "DomoDataflow_Action_GroupBy",
    "DomoDataflow_Action_WindowAction",
    # Pivot action types
    "DomoDataflow_Action_Normalizer",
    "DomoDataflow_Action_NormalizeAll",
    "DomoDataflow_Action_Denormalizer",
    # Scripting action types
    "DomoDataflow_Action_PythonEngine",
    # Data science action types
    "DomoDataflow_Action_UserDefined",
    "DomoDataflow_Action_MLInferenceAction",
    # AI services action types
    "DomoDataflow_Action_TextGeneration",
    # Legacy exports (for backwards compatibility)
    "DomoDataflow_Action_Type",
    "DomoAction",
    "DomoDataflow_Action",
]
