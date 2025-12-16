"""
AST Parser for Codebase Graph

Adapted from Graph-Codebase-MCP's ast_parser/parser.py.
Parses Python code to extract classes, functions, imports, and relationships.
"""

from __future__ import annotations

import ast
import json
import os
from typing import Any


class CodeNode:
    """Represents a code entity (class, function, variable, etc.)."""

    def __init__(
        self,
        node_id: str,
        node_type: str,
        name: str,
        file_path: str,
        line_no: int,
        end_line_no: int | None = None,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a code node.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (Class, Function, etc.)
            name: Name of the entity
            file_path: Path to the file containing this entity
            line_no: Starting line number
            end_line_no: Ending line number (optional)
            properties: Additional properties dictionary
        """
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.file_path = file_path
        self.line_no = line_no
        self.end_line_no = end_line_no
        self.properties = properties or {}
        self.code_snippet = ""

    def __str__(self) -> str:
        """String representation of the node."""
        return f"{self.node_type}:{self.name} ({self.file_path}:{self.line_no})"


class CodeRelation:
    """Represents a relationship between code entities (calls, inherits, etc.)."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a code relationship.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Type of relationship (CALLS, IMPORTS, etc.)
            properties: Additional properties dictionary
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.properties = properties or {}

    def __str__(self) -> str:
        """String representation of the relationship."""
        return f"{self.source_id} -{self.relation_type}-> {self.target_id}"


class ASTParser:
    """Parser using Python AST module to extract code structure."""

    def __init__(self) -> None:
        """Initialize the AST parser."""
        self.nodes: dict[str, CodeNode] = {}
        self.relations: list[CodeRelation] = []
        self.current_file: str = ""
        self.current_function: str | None = None
        self.current_class: str | None = None
        self.imports: dict[str, str] = {}
        # Track module definitions for cross-file dependencies
        self.module_definitions: dict[str, dict[str, str]] = {}
        # Track pending import dependencies
        self.pending_imports: list[dict[str, Any]] = []
        # Track module name to file node mapping
        self.module_to_file: dict[str, str] = {}
        # Track established relations to avoid duplicates
        self.established_relations: set[str] = set()

    def parse_directory(
        self, directory_path: str
    ) -> tuple[dict[str, CodeNode], list[CodeRelation]]:
        """Parse all Python files in a directory.

        Args:
            directory_path: Path to directory to parse

        Returns:
            Tuple of (nodes dictionary, relations list)
        """
        self.nodes = {}
        self.relations = []
        self.module_definitions = {}
        self.pending_imports = []
        self.module_to_file = {}
        self.established_relations = set()

        # First pass: Create all nodes and build module definition index
        for root, _, files in os.walk(directory_path):
            for file_name in files:
                if file_name.endswith(".py"):
                    file_path = os.path.join(root, file_name)
                    self.parse_file(file_path, build_index=True)

        # Second pass: Process all pending import relationships
        self._process_pending_imports()

        return self.nodes, self.relations

    def parse_file(
        self, file_path: str, build_index: bool = False
    ) -> tuple[dict[str, CodeNode], list[CodeRelation]]:
        """Parse a single Python file.

        Args:
            file_path: Path to Python file
            build_index: Whether to build module index for cross-file dependencies

        Returns:
            Tuple of (nodes dictionary, relations list)
        """
        self.current_file = file_path
        self.imports = {}

        try:
            with open(file_path, encoding="utf-8") as file:
                file_content = file.read()
                tree = ast.parse(file_content)
                file_node_id = self._create_file_node(file_path)

                # Generate module name for indexing
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                if build_index:
                    if module_name not in self.module_definitions:
                        self.module_definitions[module_name] = {}
                    # Associate module name with file node
                    self.module_to_file[module_name] = file_node_id

                self._parse_ast(tree, build_index, module_name)

            return self.nodes, self.relations
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return {}, []

    def _create_file_node(self, file_path: str) -> str:
        """Create a file node.

        Args:
            file_path: Path to the file

        Returns:
            File node ID
        """
        file_name = os.path.basename(file_path)
        node_id = f"file:{file_path}"
        self.nodes[node_id] = CodeNode(
            node_id=node_id,
            node_type="File",
            name=file_name,
            file_path=file_path,
            line_no=0,
        )
        return node_id

    def _get_node_id(
        self, node_type: str, name: str, file_path: str, line_no: int
    ) -> str:
        """Generate unique node identifier.

        Args:
            node_type: Type of node
            name: Name of entity
            file_path: File path
            line_no: Line number

        Returns:
            Unique node ID
        """
        return f"{node_type}:{file_path}:{name}:{line_no}"

    def _parse_ast(
        self, tree: ast.AST, build_index: bool = False, module_name: str = ""
    ) -> None:
        """Recursively parse AST tree structure.

        Args:
            tree: AST node to parse
            build_index: Whether to build index
            module_name: Current module name
        """
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                node_id = self._parse_class(node)
                if build_index and module_name:
                    self.module_definitions[module_name][node.name] = node_id
            elif isinstance(node, ast.FunctionDef):
                node_id = self._parse_function(node)
                if build_index and module_name:
                    self.module_definitions[module_name][node.name] = node_id
            elif isinstance(node, ast.Import | ast.ImportFrom):
                self._parse_import(node)
            elif isinstance(node, ast.Assign):
                self._parse_assignment(node)
            else:
                self._parse_ast(node, build_index, module_name)

    def _parse_class(self, node: ast.ClassDef) -> str:
        """Parse class definition.

        Args:
            node: AST ClassDef node

        Returns:
            Class node ID
        """
        prev_class = self.current_class
        node_id = self._get_node_id("Class", node.name, self.current_file, node.lineno)

        # Create class node
        self.nodes[node_id] = CodeNode(
            node_id=node_id,
            node_type="Class",
            name=node.name,
            file_path=self.current_file,
            line_no=node.lineno,
            end_line_no=getattr(node, "end_lineno", None),
        )

        # Create file contains class relationship
        file_node_id = f"file:{self.current_file}"
        self.relations.append(
            CodeRelation(
                source_id=file_node_id,
                target_id=node_id,
                relation_type="CONTAINS",
            )
        )

        # Handle class inheritance
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                if base_name in self.imports:
                    # Add to pending imports queue
                    self.pending_imports.append(
                        {
                            "type": "EXTENDS",
                            "source_id": node_id,
                            "imported_module": self.imports[base_name].split(".")[0],
                            "imported_name": (
                                self.imports[base_name].split(".")[-1]
                                if "." in self.imports[base_name]
                                else self.imports[base_name]
                            ),
                            "original_name": base_name,
                        }
                    )
                else:
                    # Create inheritance relationship
                    self.relations.append(
                        CodeRelation(
                            source_id=node_id,
                            target_id=f"Class:{self.current_file}:{base_name}:0",
                            relation_type="EXTENDS",
                        )
                    )

        # Set current class context
        self.current_class = node_id

        # Parse class members
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._parse_method(item)
            elif isinstance(item, ast.Assign):
                self._parse_class_attribute(item)

        # Restore context
        self.current_class = prev_class

        return node_id

    def _parse_method(self, node: ast.FunctionDef) -> None:
        """Parse class method.

        Args:
            node: AST FunctionDef node
        """
        node_id = self._get_node_id("Method", node.name, self.current_file, node.lineno)

        # Create method node
        self.nodes[node_id] = CodeNode(
            node_id=node_id,
            node_type="Method",
            name=node.name,
            file_path=self.current_file,
            line_no=node.lineno,
            end_line_no=getattr(node, "end_lineno", None),
            properties={"is_method": True},
        )

        # Create class defines method relationship
        self.relations.append(
            CodeRelation(
                source_id=self.current_class or "",
                target_id=node_id,
                relation_type="DEFINES",
            )
        )

        # Set current function context and parse function body
        prev_function = self.current_function
        self.current_function = node_id

        # Parse function arguments
        self._parse_function_args(node, node_id)

        # Parse function body
        for item in node.body:
            if isinstance(item, ast.Expr):
                if isinstance(item.value, ast.Constant):
                    # Handle function docstring (Python 3.8+)
                    if isinstance(item.value.value, str):
                        self.nodes[node_id].properties["docstring"] = item.value.value
                elif isinstance(item.value, ast.Str):  # Python < 3.8
                    self.nodes[node_id].properties["docstring"] = item.value.s

            # Find function calls
            self._find_function_calls(item)

        # Restore context
        self.current_function = prev_function

    def _parse_function(self, node: ast.FunctionDef) -> str:
        """Parse function definition.

        Args:
            node: AST FunctionDef node

        Returns:
            Function node ID
        """
        node_id = self._get_node_id(
            "Function", node.name, self.current_file, node.lineno
        )

        # Create function node
        self.nodes[node_id] = CodeNode(
            node_id=node_id,
            node_type="Function",
            name=node.name,
            file_path=self.current_file,
            line_no=node.lineno,
            end_line_no=getattr(node, "end_lineno", None),
            properties={"is_method": False},
        )

        # Create file contains function relationship
        file_node_id = f"file:{self.current_file}"
        self.relations.append(
            CodeRelation(
                source_id=file_node_id,
                target_id=node_id,
                relation_type="CONTAINS",
            )
        )

        # Set current function context
        prev_function = self.current_function
        self.current_function = node_id

        # Parse function arguments
        self._parse_function_args(node, node_id)

        # Parse function body
        for item in node.body:
            if isinstance(item, ast.Expr):
                if isinstance(item.value, ast.Constant):
                    # Handle function docstring (Python 3.8+)
                    if isinstance(item.value.value, str):
                        self.nodes[node_id].properties["docstring"] = item.value.value
                elif isinstance(item.value, ast.Str):  # Python < 3.8
                    self.nodes[node_id].properties["docstring"] = item.value.s

            # Find function calls
            self._find_function_calls(item)

        # Restore context
        self.current_function = prev_function

        return node_id

    def _parse_function_args(self, node: ast.FunctionDef, node_id: str) -> None:
        """Parse function arguments.

        Args:
            node: AST FunctionDef node
            node_id: Function node ID
        """
        args = []

        # Process positional arguments
        for arg in node.args.args:
            arg_info = {"name": arg.arg}
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    arg_info["type"] = arg.annotation.id
            args.append(arg_info)

        # Process default arguments
        defaults = node.args.defaults
        if defaults:
            offset = len(args) - len(defaults)
            for i, default in enumerate(defaults):
                index = offset + i
                if index < len(args):
                    args[index]["has_default"] = True

        # Serialize args list as JSON string
        self.nodes[node_id].properties["args"] = json.dumps(args)

    def _parse_import(self, node: ast.Import | ast.ImportFrom) -> None:
        """Parse import statement.

        Args:
            node: AST Import or ImportFrom node
        """
        file_node_id = f"file:{self.current_file}"

        if isinstance(node, ast.Import):
            for name in node.names:
                import_name = name.name
                asname = name.asname or import_name

                # Add to import mapping
                self.imports[asname] = import_name

                # Module name (take first part, e.g., 'package.module' -> 'package')
                root_module = import_name.split(".")[0]

                # Add to pending imports
                self.pending_imports.append(
                    {
                        "type": "IMPORTS_MODULE",
                        "source_id": file_node_id,
                        "imported_module": root_module,
                        "full_module_path": import_name,
                        "alias": asname,
                    }
                )

        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            for name in node.names:
                import_name = name.name
                asname = name.asname or import_name

                # Add to import mapping
                if module_name:
                    full_name = f"{module_name}.{import_name}"
                    self.imports[asname] = full_name
                else:
                    self.imports[asname] = import_name

                # Add to pending imports
                self.pending_imports.append(
                    {
                        "type": "IMPORTS_SYMBOL",
                        "source_id": file_node_id,
                        "imported_module": module_name,
                        "imported_name": import_name,
                        "alias": asname,
                    }
                )

    def _parse_assignment(self, node: ast.Assign) -> None:
        """Parse assignment statement.

        Args:
            node: AST Assign node
        """
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                node_id = self._get_node_id(
                    "Variable", var_name, self.current_file, node.lineno
                )

                if self.current_class and not self.current_function:
                    # Class attribute
                    self.nodes[node_id] = CodeNode(
                        node_id=node_id,
                        node_type="ClassVariable",
                        name=var_name,
                        file_path=self.current_file,
                        line_no=node.lineno,
                        end_line_no=getattr(node, "end_lineno", None),
                    )

                    self.relations.append(
                        CodeRelation(
                            source_id=self.current_class or "",
                            target_id=node_id,
                            relation_type="DEFINES",
                        )
                    )
                elif self.current_function:
                    # Local variable
                    self.nodes[node_id] = CodeNode(
                        node_id=node_id,
                        node_type="LocalVariable",
                        name=var_name,
                        file_path=self.current_file,
                        line_no=node.lineno,
                        end_line_no=getattr(node, "end_lineno", None),
                    )

                    self.relations.append(
                        CodeRelation(
                            source_id=self.current_function or "",
                            target_id=node_id,
                            relation_type="DEFINES",
                        )
                    )
                else:
                    # Global variable
                    self.nodes[node_id] = CodeNode(
                        node_id=node_id,
                        node_type="GlobalVariable",
                        name=var_name,
                        file_path=self.current_file,
                        line_no=node.lineno,
                        end_line_no=getattr(node, "end_lineno", None),
                    )

                    file_node_id = f"file:{self.current_file}"
                    self.relations.append(
                        CodeRelation(
                            source_id=file_node_id,
                            target_id=node_id,
                            relation_type="DEFINES",
                        )
                    )

    def _parse_class_attribute(self, node: ast.Assign) -> None:
        """Parse class attribute.

        Args:
            node: AST Assign node
        """
        # Similar to _parse_assignment but specifically for class attributes
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                node_id = self._get_node_id(
                    "ClassVariable", var_name, self.current_file, node.lineno
                )

                self.nodes[node_id] = CodeNode(
                    node_id=node_id,
                    node_type="ClassVariable",
                    name=var_name,
                    file_path=self.current_file,
                    line_no=node.lineno,
                    end_line_no=getattr(node, "end_lineno", None),
                )

                self.relations.append(
                    CodeRelation(
                        source_id=self.current_class or "",
                        target_id=node_id,
                        relation_type="DEFINES",
                    )
                )

    def _find_function_calls(self, node: ast.AST) -> None:
        """Find function calls in AST node.

        Args:
            node: AST node to search
        """
        if isinstance(node, ast.Call):
            func = node.func

            if isinstance(func, ast.Name):
                # Direct function call
                func_name = func.id

                if func_name in self.imports:
                    # Handle imported function call
                    imported_func = self.imports[func_name]
                    # Add to pending imports queue
                    if self.current_function:
                        self.pending_imports.append(
                            {
                                "type": "CALLS",
                                "source_id": self.current_function,
                                "imported_module": (
                                    imported_func.split(".")[0]
                                    if "." in imported_func
                                    else imported_func
                                ),
                                "imported_name": (
                                    imported_func.split(".")[-1]
                                    if "." in imported_func
                                    else imported_func
                                ),
                                "original_name": func_name,
                            }
                        )
                elif self.current_function:
                    # Handle local function call
                    self.relations.append(
                        CodeRelation(
                            source_id=self.current_function,
                            target_id=f"Function:{self.current_file}:{func_name}:0",
                            relation_type="CALLS",
                        )
                    )

            elif isinstance(func, ast.Attribute):
                # Call object method
                if isinstance(func.value, ast.Name):
                    obj_name = func.value.id
                    method_name = func.attr

                    if obj_name in self.imports:
                        # Handle imported class/module method call
                        imported_obj = self.imports[obj_name]
                        # Add to pending imports queue
                        if self.current_function:
                            self.pending_imports.append(
                                {
                                    "type": "CALLS_METHOD",
                                    "source_id": self.current_function,
                                    "imported_module": (
                                        imported_obj.split(".")[0]
                                        if "." in imported_obj
                                        else imported_obj
                                    ),
                                    "imported_class": (
                                        imported_obj.split(".")[-1]
                                        if "." in imported_obj
                                        else imported_obj
                                    ),
                                    "method_name": method_name,
                                    "original_obj_name": obj_name,
                                }
                            )
                    elif self.current_function:
                        # Handle local object method call
                        self.relations.append(
                            CodeRelation(
                                source_id=self.current_function,
                                target_id=f"Method:{self.current_file}:{method_name}:0",
                                relation_type="CALLS",
                                properties={"object": obj_name},
                            )
                        )

        # Recursively find nested function calls
        for child in ast.iter_child_nodes(node):
            self._find_function_calls(child)

    def _add_relation(self, relation: CodeRelation) -> None:
        """Add relation, avoiding duplicates.

        Args:
            relation: CodeRelation to add
        """
        # Create unique relation identifier
        relation_key = (
            f"{relation.source_id}|{relation.relation_type}|{relation.target_id}"
        )

        # For certain relation types, also consider properties
        if relation.relation_type == "IMPORTS_FROM":
            # For import relations, same file importing same module only needs one record
            relation_key = (
                f"{relation.source_id}|{relation.relation_type}|{relation.target_id}"
            )
        elif relation.relation_type == "IMPORTS_DEFINITION":
            # For symbol imports, need to consider symbol name
            symbol = relation.properties.get("symbol", "")
            relation_key = f"{relation.source_id}|{relation.relation_type}|{relation.target_id}|{symbol}"

        # Check if relation already exists
        if relation_key not in self.established_relations:
            self.relations.append(relation)
            self.established_relations.add(relation_key)

    def _process_pending_imports(self) -> None:
        """Process all pending import relationships."""
        print(f"Processing cross-file dependencies, {len(self.pending_imports)} items")

        # First create all module nodes, associate them with file nodes
        for module_name, file_node_id in self.module_to_file.items():
            if file_node_id in self.nodes:
                file_node = self.nodes[file_node_id]
                file_node.properties["module_name"] = module_name

        # Group imports by source module
        imports_by_source_module: dict[str, list[dict[str, Any]]] = {}
        for import_info in self.pending_imports:
            source_id = import_info["source_id"]
            if source_id not in imports_by_source_module:
                imports_by_source_module[source_id] = []
            imports_by_source_module[source_id].append(import_info)

        # Process imports for each source file
        for source_id, imports in imports_by_source_module.items():
            # Track already processed modules
            processed_modules: set[str] = set()

            for import_info in imports:
                import_type = import_info["type"]

                if import_type == "IMPORTS_MODULE":
                    # File imports entire module
                    module_name = import_info["imported_module"]

                    # Avoid duplicate processing of same module imports
                    if module_name in processed_modules:
                        continue
                    processed_modules.add(module_name)

                    # Find module's corresponding file node
                    if module_name in self.module_to_file:
                        target_file_id = self.module_to_file[module_name]

                        # Create file-to-file dependency relationship
                        self._add_relation(
                            CodeRelation(
                                source_id=source_id,
                                target_id=target_file_id,
                                relation_type="IMPORTS_FROM",
                                properties={
                                    "module": module_name,
                                    "full_module_path": import_info.get(
                                        "full_module_path", module_name
                                    ),
                                },
                            )
                        )

                elif import_type == "IMPORTS_SYMBOL":
                    # Import specific symbol from module
                    module_name = import_info["imported_module"]
                    symbol_name = import_info["imported_name"]

                    # Check module definition index
                    if (
                        module_name in self.module_definitions
                        and symbol_name in self.module_definitions[module_name]
                    ):
                        target_node_id = self.module_definitions[module_name][
                            symbol_name
                        ]

                        # Create file-to-symbol dependency relationship
                        self._add_relation(
                            CodeRelation(
                                source_id=source_id,
                                target_id=target_node_id,
                                relation_type="IMPORTS_DEFINITION",
                                properties={
                                    "module": module_name,
                                    "symbol": symbol_name,
                                    "alias": import_info.get("alias"),
                                },
                            )
                        )

                        # Avoid duplicate IMPORTS_FROM for already processed modules
                        if (
                            module_name not in processed_modules
                            and module_name in self.module_to_file
                        ):
                            processed_modules.add(module_name)

                            # Create import-to-file relationship
                            self._add_relation(
                                CodeRelation(
                                    source_id=source_id,
                                    target_id=self.module_to_file[module_name],
                                    relation_type="IMPORTS_FROM",
                                    properties={
                                        "module": module_name,
                                        "imports_symbols": [symbol_name],
                                    },
                                )
                            )

                elif import_type == "EXTENDS":
                    # Class inheritance relationship
                    module_name = import_info["imported_module"]
                    class_name = import_info["imported_name"]

                    # Check module definition index
                    if (
                        module_name in self.module_definitions
                        and class_name in self.module_definitions[module_name]
                    ):
                        target_node_id = self.module_definitions[module_name][
                            class_name
                        ]

                        # Create inheritance relationship
                        self._add_relation(
                            CodeRelation(
                                source_id=source_id,
                                target_id=target_node_id,
                                relation_type="EXTENDS",
                                properties={
                                    "original_name": import_info.get("original_name")
                                },
                            )
                        )

                elif import_type == "CALLS":
                    # Function call relationship
                    module_name = import_info["imported_module"]
                    func_name = import_info["imported_name"]

                    # Check module definition index
                    if (
                        module_name in self.module_definitions
                        and func_name in self.module_definitions[module_name]
                    ):
                        target_node_id = self.module_definitions[module_name][func_name]

                        # Create call relationship
                        self._add_relation(
                            CodeRelation(
                                source_id=source_id,
                                target_id=target_node_id,
                                relation_type="CALLS",
                                properties={
                                    "original_name": import_info.get("original_name")
                                },
                            )
                        )

                elif import_type == "CALLS_METHOD":
                    # Object method call relationship
                    module_name = import_info["imported_module"]
                    class_name = import_info["imported_class"]
                    method_name = import_info["method_name"]

                    # Check class in module definition index
                    if (
                        module_name in self.module_definitions
                        and class_name in self.module_definitions[module_name]
                    ):
                        class_node_id = self.module_definitions[module_name][class_name]

                        # Find method defined by that class
                        for relation in self.relations:
                            if (
                                relation.source_id == class_node_id
                                and relation.relation_type == "DEFINES"
                            ):
                                target_node = self.nodes.get(relation.target_id)
                                if (
                                    target_node
                                    and target_node.node_type == "Method"
                                    and target_node.name == method_name
                                ):
                                    # Create call relationship
                                    self._add_relation(
                                        CodeRelation(
                                            source_id=source_id,
                                            target_id=relation.target_id,
                                            relation_type="CALLS",
                                            properties={
                                                "object": import_info.get(
                                                    "original_obj_name"
                                                ),
                                                "class": class_name,
                                            },
                                        )
                                    )
                                    break
