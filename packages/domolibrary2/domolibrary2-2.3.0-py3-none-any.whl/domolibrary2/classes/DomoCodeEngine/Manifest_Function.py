__all__ = [
    "calculate_character_index_of_line_number",
    "extract_return_type_annotation",
    "extract_function_docstring",
    "CodeEngineManifest_Function",
]

import ast
import os
from dataclasses import dataclass, field
from pprint import pprint

from ...utils import (
    compare as dmcp,
    convert as dmcv,
    files as defi,
)
from .Manifest_Argument import CodeEngineManifest_Argument


def calculate_character_index_of_line_number(line_num: int, full_text: str) -> int:
    """
    Calculate the character index at the start of a given line (0-based) in the source file.
    Args:
        line_num (int): The line number (0-based) where the function starts.
        full_text (str): The full text of the file.
    Returns:
        int: Character position from the beginning of the file (0-based).
    """
    character_position = 0

    if not full_text:
        return character_position

    file_lines = full_text.split("\n")

    for line_index in range(line_num):
        if line_index < len(file_lines):
            character_position += len(file_lines[line_index]) + 1  # +1 for newline

    return character_position


def extract_return_type_annotation(function_node: ast.FunctionDef) -> str:
    """
    Extract return type annotation from a function AST node.

    Converts the function's return type annotation from AST format back to
    a string representation for type analysis and schema mapping.

    Note:
        Only works with Python 3.9+ that has ast.unparse(). For older versions,
        returns empty string if return annotation exists but cannot be parsed.
    """
    if function_node.returns and hasattr(ast, "unparse"):
        return ast.unparse(function_node.returns)
    return None


def extract_function_docstring(function_node: ast.FunctionDef) -> str:
    """
    Extract the docstring from a function AST node if present.

    Identifies and extracts the first string literal in a function body,
    which by Python convention serves as the function's documentation.
    Only extracts docstrings that are the first statement in the function.

    Args:
        function_node (ast.FunctionDef): The function AST node to examine

    Returns:
        str: The function's docstring with whitespace stripped, or empty string if none found

    Note:
        Follows Python docstring conventions where the first statement in a function
        body, if it's a string literal, is considered the docstring. Multi-line
        docstrings are preserved but leading/trailing whitespace is removed.
    """
    if (
        function_node.body
        and isinstance(function_node.body[0], ast.Expr)
        and isinstance(function_node.body[0].value, ast.Constant)
        and isinstance(function_node.body[0].value.value, str)
    ):
        return function_node.body[0].value.value.strip()
    return ""


@dataclass
class CodeEngineManifest_Function:
    ast_fn: ast.FunctionDef

    name: str
    display_name: str
    description: str
    is_private: bool
    editor_start_index: int
    has_return: bool

    output: CodeEngineManifest_Argument

    editor_end_index: int = None
    content: str = None

    input_args: list[CodeEngineManifest_Argument] = field(default_factory=list)

    _target_from_api: dict = field(
        default=None
    )  # store the original API manifest for validation

    @classmethod
    def from_ast_function_def(
        cls, ast_fn: ast.FunctionDef, original_module_string
    ) -> "CodeEngineManifest_Function":
        """
        Create a complete function description as a CodeEngineManifest_Function object.

        Combines all extracted function metadata into a structured FunctionMetadata
        dataclass instance that includes the function name, parameters, return type,
        docstring, and editor positioning information required for code engine integration.

        Args:
            function_node (ast.FunctionDef): The AST node representing the function to describe

        Returns:
            FunctionMetadata: Complete function metadata object containing:
                - name (str): Original function name
                - displayName (str): Human-readable function name
                - description (str): Function docstring
                - inputs (list[Dict]): Parameter descriptions
                - output (Dict): Return value description
                - variables (Dict): Variable descriptions (copy of inputs)
                - isPrivate (bool): Whether function is private (based on underscore prefix)
                - editorStartIndex (int): Character position in source file
                - hasReturn (bool): Whether function has return type annotation

        Note:
            The isPrivate field is determined by checking if the function name starts
            with an underscore, following Python naming conventions.
        """
        function_name = ast_fn.name
        is_private = function_name.startswith("_")

        input_args = [
            CodeEngineManifest_Argument.from_ast_arg(arg, ast_fn)
            for arg in ast_fn.args.args
        ]

        output_arg = CodeEngineManifest_Argument.from_ast_function_return_arg(ast_fn)

        editor_start_index = calculate_character_index_of_line_number(
            ast_fn.lineno - 1, full_text=original_module_string
        )

        editor_end_index = calculate_character_index_of_line_number(
            ast_fn.end_lineno - 1, full_text=original_module_string
        )

        content = "\n".join(
            original_module_string.split("\n")[
                ast_fn.lineno - 1 : ast_fn.end_lineno - 1
            ]
            if ast_fn.end_lineno
            else []
        )
        # content = original_module_string[editor_start_index:editor_end_index] if editor_end_index else None

        return cls(
            ast_fn=ast_fn,
            name=function_name,
            is_private=is_private,
            display_name=dmcv.convert_programming_text_to_title_case(function_name),
            description=extract_function_docstring(ast_fn),
            input_args=input_args,
            output=output_arg,
            editor_start_index=editor_start_index,
            editor_end_index=editor_end_index,
            content=content,
            has_return=ast_fn.returns is not None,
        )

    def to_dict(self) -> dict:
        """
        Serialize the function metadata and arguments to a manifest-compatible dictionary.
        """
        return {
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "isPrivate": self.is_private,
            "inputs": [
                arg.to_dict(include_orig=False) if hasattr(arg, "to_dict") else arg
                for arg in self.input_args
            ],
            "code": self.content,
            "output": (
                self.output.to_dict(include_orig=False)
                if hasattr(self.output, "to_dict")
                else self.output
            ),
        }

    def validate_json_to_manifest(
        self, test_obj=None, debug_prn: bool = False, is_suppress_none=False
    ) -> list[dict]:
        test_obj: dict = self._target_from_api or test_obj

        if not test_obj:
            if not is_suppress_none:
                raise ValueError("No test_obj provided for validation")

            return [{"key": "No test_obj", "message": "no original manifest"}]

        assert isinstance(test_obj, dict)

        res = dmcp.compare_dicts(self.to_dict(), test_obj)

        if not res:
            res = [{"key": "no differences found", "is_success": True}]

        if debug_prn:
            pprint(res)

        return res

    def download_source_code(self, export_folder: str = "./EXPORT", file_name=None):
        file_name = file_name or f"{self.name}.py"

        defi.upsert_file(os.path.join(export_folder, file_name), self.content)

        return file_name
