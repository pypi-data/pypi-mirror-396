__all__ = [
    "extract_ast_arg_type_annotation",
    "extract_ast_arg_name",
    "extract_ast_arg_default_value",
    "PythonTypeToSchemaType",
    "CodeEngine_Argument",
    "extract_last_return_node_from_ast_fn",
    "extract_return_variable_name",
    "CodeEngineManifest_Argument",
]

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ...base.base import DomoEnumMixin
from ...utils import convert as dmcv


def extract_ast_arg_type_annotation(
    ast_arg: ast.arg,
) -> str:  # String representation of the type annotation, empty if none exists
    """
    Extract type annotation from a function parameter AST node.

    Converts AST type annotation nodes back to string representation,
    handling different Python versions and annotation formats. Falls back
    to manual parsing for older Python versions without ast.unparse().

    Note:
        Uses ast.unparse() when available (Python 3.9+), otherwise attempts
        manual extraction for common annotation types like ast.Name and ast.Subscript.
    """

    if not getattr(ast_arg, "annotation", None):
        return ""

    if hasattr(ast, "unparse"):
        return ast.unparse(ast_arg.annotation)

    else:
        if isinstance(ast_arg.annotation, ast.Name):
            return ast_arg.annotation.id
        elif isinstance(ast_arg.annotation, ast.Subscript):
            return str(ast_arg.annotation)

    return ""


def extract_ast_arg_name(ast_arg: ast.arg):
    return ast_arg.arg


def extract_ast_arg_default_value(arg, ast_fn: ast.FunctionDef) -> dict[str, bool]:
    """
    Extract the default value for a function parameter if it exists.

    Note:
        Handles different AST node types (Constant, Name) and uses ast.unparse()
        when available for complex expressions.
    """

    args = ast_fn.args.args
    defaults = ast_fn.args.defaults
    num_defaults = len(defaults)

    if num_defaults == 0:
        return {"default_value": None, "has_default_value": False}

    # Map default values to the last N arguments
    for darg, default in zip(args[-num_defaults:], defaults):
        if darg == arg:
            if isinstance(default, ast.Constant):
                return {"default_value": default.value, "has_default_value": True}
            elif isinstance(default, ast.Name):
                return {"default_value": default.id, "has_default_value": True}
            elif hasattr(ast, "unparse"):
                return {
                    "default_value": ast.unparse(default),
                    "has_default_value": True,
                }
            else:
                return {"default_value": "None", "has_default_value": True}

    return {"default_value": None, "has_default_value": False}


class PythonTypeToSchemaType(DomoEnumMixin, Enum):
    STR = "str"
    STRING = "string"
    INT = "int"
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    BOOL = "bool"
    BOOLEAN = "boolean"
    DICT = "dict"
    DICT_CAP = "Dict"
    LIST = "list"
    LIST_CAP = "list"
    OBJECT = "object"
    ANY = "Any"

    @property
    def codeengine_schema_type(self):
        mapping = {
            PythonTypeToSchemaType.STR: "text",
            PythonTypeToSchemaType.STRING: "text",
            PythonTypeToSchemaType.INT: "number",
            PythonTypeToSchemaType.INTEGER: "number",
            PythonTypeToSchemaType.FLOAT: "decimal",
            PythonTypeToSchemaType.DECIMAL: "decimal",
            PythonTypeToSchemaType.BOOL: "boolean",
            PythonTypeToSchemaType.BOOLEAN: "boolean",
            PythonTypeToSchemaType.DICT: "object",
            PythonTypeToSchemaType.DICT_CAP: "object",
            PythonTypeToSchemaType.LIST: "object",
            PythonTypeToSchemaType.LIST_CAP: "object",
            PythonTypeToSchemaType.OBJECT: "object",
            PythonTypeToSchemaType.ANY: "object",
        }
        return mapping.get(self, "object")

    @classmethod
    def get(cls, type_str, default="OBJECT"):
        for member in cls:
            if member.value == type_str.lower():
                return member

            if member.value in type_str.lower():
                return member
        return cls[default]

    @classmethod
    def map_python_type_to_schema(cls, type_str: str, default="OBJECT") -> str:
        return cls.get(type_str, default=default).codeengine_schema_type


@dataclass
class CodeEngine_Argument:
    """converts Python type annotations to Domo CodeEngine argument schema types."""

    annotation_text: str

    has_default_value: bool = None
    ast_arg: ast.arg = None
    schema_type: PythonTypeToSchemaType = None

    is_list: bool = False
    is_nullable: bool = False

    def __post_init__(self):
        self.annotation_text = str(self.annotation_text).strip()

        self.test_is_list_type()
        self.test_is_nullable()
        self.extract_schema_type_from_annotation_text()

    @classmethod
    def init(
        cls, annotation_text: str, has_default_value: bool = None
    ) -> dict[str, Any]:
        return cls(annotation_text=annotation_text, has_default_value=has_default_value)

    def to_dict(self, is_map_type_to_codeengine: bool = True) -> dict[str, Any]:
        schema_type = (
            self.schema_type.codeengine_schema_type
            if is_map_type_to_codeengine
            else self.schema_type.value
        )
        return {
            "nullable": self.is_nullable,
            "isList": self.is_list,
            "type": schema_type,
        }

    def extract_schema_type_from_annotation_text(
        self, default: str = "OBJECT"
    ) -> PythonTypeToSchemaType:
        def _remove_optional_wrapper(annotation_text: str) -> str:
            if "Optional[" in annotation_text:
                return re.sub(r"Optional\[(.*?)\]", r"\1", annotation_text)
            if "Union[" in annotation_text and "None" in annotation_text:
                annotation_text = re.sub(
                    r"Union\[(.*?),\s*None\]", r"\1", annotation_text
                )
                annotation_text = re.sub(
                    r"Union\[None,\s*(.*?)\]", r"\1", annotation_text
                )
            return annotation_text

        self.schema_type = PythonTypeToSchemaType.get(
            _remove_optional_wrapper(self.annotation_text), default=default
        )

        return self.schema_type

    def test_is_list_type(self) -> bool:
        """
        Check if the type annotation represents a list or array type.

        Detects various list type patterns including typing.list, built-in list,
        and generic list annotations from both Python 3.8+ and earlier versions.

        Examples:
            'list[str]' -> True
            'list[int]' -> True
            'list' -> True
            'str' -> False
        """

        self.is_list = (
            "list[" in self.annotation_text
            or "list[" in self.annotation_text
            or self.annotation_text.lower() == "list"
        )

    def test_is_nullable(self) -> str:
        """
        tests for Optional[] or Union[Type, None] wrappers from type annotation strings.

        Examples:
            'str | None' -> 'str'
            'Union[int, None]' -> 'int'
            'Union[None, str]' -> 'str'
        """

        self.is_nullable = False  # assumes no default value

        if "Optional[" in self.annotation_text:
            self.is_nullable = True

        elif "Union[" in self.annotation_text and "None" in self.annotation_text:
            self.is_nullable = True

        elif isinstance(self.has_default_value, bool):
            self.is_nullable = self.has_default_value

        return self.is_nullable

    def extract_inner_list(self) -> str:
        """
        Extract the inner element type from list[InnerType] annotations.

        Parses list type annotations to determine the type of elements contained
        within the list, supporting both typing.list and built-in list formats.

        Args:
            annotation_text (str): list type annotation (e.g., 'list[str]', 'list[int]')

        Returns:
            str: The inner type without the list wrapper (e.g., 'str', 'int')

        Examples:
            'list[str]' -> 'str'
            'list[int]' -> 'int'
            'list[dict[str, Any]]' -> 'dict[str, Any]'
        """

        # is this superfluoous given how enum has been implemented with "in" checks?

        self.is_list = False
        if "list[" in self.annotation_text:
            self.is_list = True
            return self.is_list
        elif "list[" in self.annotation_text:
            self.is_list = True

        return self.is_list


def extract_last_return_node_from_ast_fn(ast_fn: ast.FunctionDef):
    # Filter for ast.Return nodes in the function body
    return_nodes = [node for node in ast_fn.body if isinstance(node, ast.Return)]
    # Return the last one if any exist
    return return_nodes[-1] if return_nodes else None


def extract_return_variable_name(ast_fn: ast.FunctionDef):
    return_node = extract_last_return_node_from_ast_fn(ast_fn)

    if return_node and isinstance(return_node.value, ast.Name):
        return return_node.value.id
    return None


@dataclass
class CodeEngineManifest_Argument(CodeEngine_Argument):
    """display class for formatting AST Argument"""

    name: str = None
    default_value: str = None
    display_name: str = None
    ast_arg: ast.arg = None

    # not implemented yet
    entity_sub_type = None  # not mapped to ast_arg
    value: str = None  # not mapped to ast_arg
    children: list[Any] = field(default_factory=list)  # not mapped to ast_arg

    def __post_init__(self):
        self.process_display_name()
        self.process_has_default_value()
        super().__post_init__()

    def process_has_default_value(self):
        self.has_default_value = False

        if self.default_value:
            self.has_default_value = True

    @classmethod
    def from_ast_arg(cls, ast_arg: ast.arg, ast_fn: ast.FunctionDef):
        default_info = extract_ast_arg_default_value(ast_arg, ast_fn)
        name = extract_ast_arg_name(ast_arg)
        annotation_text = extract_ast_arg_type_annotation(ast_arg)

        return cls(
            annotation_text=annotation_text,
            default_value=default_info["default_value"],
            has_default_value=default_info["has_default_value"],
            ast_arg=ast_arg,
            name=name,
        )

    def process_display_name(self, display_name=None):
        if display_name:
            self.display_name = display_name

        else:
            self.display_name = dmcv.convert_programming_text_to_title_case(self.name)

        return self.display_name

    def _ast_arg_to_string(self):
        if not self.ast_arg:
            return None

        if not hasattr(ast, "unparse"):
            return ast.dump(self.ast_arg)

        return ast.unparse(self.ast_arg)

    def to_dict(self, include_orig: bool = True):
        r = {
            "name": self.name,
            "displayName": self.display_name,
            "defaultValues": self.default_value,
            "entitySubType": self.entity_sub_type,
            "value": self.value,
            "children": self.children,
            **super().to_dict(),
        }

        if include_orig and self.ast_arg:
            r["raw"] = self._ast_arg_to_string()

        return r

    @classmethod
    def from_ast_function_return_arg(cls, ast_fn: ast.FunctionDef):
        # return_node = extract_last_return_node_from_ast_fn(ast_fn)

        annotation_text = extract_ast_arg_type_annotation(ast_fn.returns)

        return_name = extract_return_variable_name(ast_fn) or "result"

        return cls(
            name=return_name,
            display_name=return_name,
            annotation_text=annotation_text,
            default_value=None,
            has_default_value=False,
            ast_arg=ast_fn.returns,
        )
