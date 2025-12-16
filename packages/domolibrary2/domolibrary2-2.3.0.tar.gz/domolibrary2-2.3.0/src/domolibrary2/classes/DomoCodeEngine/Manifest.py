__all__ = ["CodeEngineManifest"]

import os
from dataclasses import dataclass
from typing import Any

from ...utils import (
    convert as dmcv,
    files as dmfi,
)
from .Manifest_Function import CodeEngineManifest_Function


@dataclass
class CodeEngineManifest:
    functions: list[CodeEngineManifest_Function]
    configuration: dict[str, Any]

    raw: str = None

    @classmethod
    def from_python_file(
        cls, file_path: str, accounts_mapping: list[Any]
    ) -> "CodeEngineManifest":
        """
        Analyze all functions in a Python script file and return a structured manifest.

        This is the main public method that orchestrates the complete analysis process.
        It loads the specified file, parses its AST, and generates comprehensive metadata
        descriptions for every function found in the script, returning them as a Manifest object.

        Args:
            file_path (str): Path to the Python script file to analyze

        Returns:
            Manifest: A manifest object containing:
                - functions (list[FunctionMetadata]): list of function metadata objects
                - configuration (dict[str, Any]): Configuration dictionary with accountsMapping

        Error Handling:
            - Returns a Manifest with empty functions list if file loading fails
            - Prints error messages for individual function analysis failures but continues processing
            - Skips functions that cannot be analyzed due to errors

        Example:
            >>> analyzer = CodeEngineScriptAnalyzer()
            >>> manifest = analyzer.analyze_all_functions('my_script.py')
            >>> for func in manifest.functions:
            ...     print(f"Function: {func.name} ({len(func.inputs)} parameters)")

        Note:
            This method walks the entire AST and processes all function definitions found,
            including nested functions and methods within classes.
        """
        content = dmcv.convert_python_to_ast_module(
            python_file_path=file_path, return_str=True
        )

        ast_module = dmcv.convert_python_to_ast(python_str=content, return_str=False)

        return cls(
            functions=[
                CodeEngineManifest_Function.from_ast_function(ast_fn, content=content)
                for ast_fn in dmcv.extract_ast_functions(ast_module)
            ],
            configuration={"accountsMapping": accounts_mapping or []},
        )

    @classmethod
    def from_python_string(
        cls, python_str: str, accounts_mapping: list[Any]
    ) -> "CodeEngineManifest":
        """
        Analyze all functions in a Python script string and return a structured manifest.

        This is the main public method that orchestrates the complete analysis process.
        It loads the specified string, parses its AST, and generates comprehensive metadata
        descriptions for every function found in the script, returning them as a Manifest object.

        Args:
            python_str (str): Python script content to analyze

        Returns:
            Manifest: A manifest object containing:
                - functions (list[FunctionMetadata]): list of function metadata objects
                - configuration (dict[str, Any]): Configuration dictionary with accountsMapping

        Error Handling:
            - Returns a Manifest with empty functions list if string loading fails
            - Prints error messages for individual function analysis failures but continues processing
            - Skips functions that cannot be analyzed due to errors

        Example:
            >>> analyzer = CodeEngineScriptAnalyzer()
            >>> manifest = analyzer.analyze_all_functions('def my_func(x): return x')
            >>> for func in manifest.functions:
            ...     print(f"Function: {func.name} ({len(func.inputs)} parameters)")

        Note:
            This method walks the entire AST and processes all function definitions found,
            including nested functions and methods within classes.
        """
        ast_module = dmcv.convert_python_to_ast_module(
            python_str=python_str, return_str=False
        )

        return cls(
            functions=[
                CodeEngineManifest_Function.from_ast_function_def(
                    ast_fn, original_module_string=python_str
                )
                for ast_fn in dmcv.extract_ast_functions(ast_module)
            ],
            configuration={"accountsMapping": accounts_mapping or []},
        )

    @classmethod
    def from_api(cls, obj):
        cem = cls.from_python_string(python_str=obj.get("code"), accounts_mapping=[])
        cem.raw = obj

        for cfn in cem.functions:
            cfn._target_from_api = next(
                (
                    fn_obj
                    for fn_obj in obj["functions"]
                    if fn_obj and fn_obj["name"] == cfn.name
                ),
                None,
            )

        return cem

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary format for API submission.

        Returns:
            Dictionary with 'functions' and 'configuration' keys.
        """
        return {
            "functions": [fn.to_dict() for fn in self.functions],
            "configuration": self.configuration,
        }

    def download_source_code(
        self, export_folder: str = "./EXPORT", replace_folder: bool = False
    ):
        dmfi.upsert_file(
            os.path.join(export_folder, "index.py"),
            content=self.raw.get("code"),
            replace_folder=replace_folder,
        )

        return [
            fn.download_source_code(export_folder=export_folder)
            for fn in self.functions
        ]
        # return file_name
