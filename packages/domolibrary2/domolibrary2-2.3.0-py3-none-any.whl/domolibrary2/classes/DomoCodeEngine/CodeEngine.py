"""DomoCodeEngine Package and Version Classes

This module provides classes for interacting with Domo CodeEngine packages including
package management, version control, and code deployment.

## Class Hierarchy

The CodeEngine classes follow the DomoEntity pattern:

- **DomoCodeEngine_Package** (DomoEntity): Represents a CodeEngine package
  - Contains multiple versions
  - Manages package metadata (name, description, language)
  - Provides methods for creation, retrieval, updates, and deployment

- **DomoCodeEngine_PackageVersion** (DomoSubEntity): Represents a specific version
  - Belongs to a parent DomoCodeEngine_Package
  - Contains source code and function definitions
  - Inherits authentication from parent package
  - May contain a CodeEngineManifest for Python packages

- **DomoCodeEngine_Packages** (DomoManager): Manages collections of packages
  - Provides search and retrieval methods
  - Returns lists of DomoCodeEngine_Package instances


## Relationships

```mermaid
classDiagram
    class DomoEntity {
        +str id
        +DomoAuth auth
        +dict raw
        +display_url() str
        +from_dict() DomoEntity
        +get_by_id() DomoEntity
    }

    class DomoSubEntity {
        +DomoEntity parent
        +auth (from parent)
    }

    class DomoManager {
        +DomoAuth auth
        +get() list
    }

    class DomoCodeEngine_Package {
        +str id
        +str name
        +str language
        +str current_version
        +list~DomoCodeEngine_PackageVersion~ versions
        +create() DomoCodeEngine_Package
        +get_by_id() DomoCodeEngine_Package
        +upsert() DomoCodeEngine_Package
        +deploy_version() dict
        +_create_manifest_from_code() CodeEngineManifest
        +_build_payload() dict
    }

    class DomoCodeEngine_PackageVersion {
        +str package_id
        +str version
        +str code
        +CodeEngineManifest Manifest
        +from_dict() DomoCodeEngine_PackageVersion
        +get_by_id_and_version() DomoCodeEngine_PackageVersion
        +download_source_code() str
    }

    class DomoCodeEngine_Packages {
        +get() list~DomoCodeEngine_Package~
        +search_by_name() list~DomoCodeEngine_Package~
    }

    class CodeEngineManifest {
        +list~CodeEngineManifest_Function~ functions
        +dict configuration
        +from_python_string() CodeEngineManifest
    }

    DomoEntity <|-- DomoCodeEngine_Package
    DomoSubEntity <|-- DomoCodeEngine_PackageVersion
    DomoManager <|-- DomoCodeEngine_Packages
    DomoCodeEngine_Package "1" *-- "many" DomoCodeEngine_PackageVersion : contains
    DomoCodeEngine_PackageVersion "1" *-- "0..1" CodeEngineManifest : has
    DomoCodeEngine_Packages "1" *-- "many" DomoCodeEngine_Package : manages
    DomoCodeEngine_Package ..> CodeEngineManifest : creates via _create_manifest_from_code
```

## Usage Example

```python
from domolibrary2.auth import DomoTokenAuth
from domolibrary2.classes.DomoCodeEngine import DomoCodeEngine_Package

auth = DomoTokenAuth(domo_instance="...", domo_access_token="...")

# Create a new package from Python code
code = "def process_data(input_data: list, limit: int = 100) -> dict:\\n    return {'processed': len(input_data[:limit])}"

package = await DomoCodeEngine_Package.create(
    auth=auth,
    name="Data Processor",
    code=code,
    version="1.0.0"
)

# Get the current version
current_version = await package.get_current_version()
print(f"Current version: {current_version.version}")

# Deploy new code to existing package
result = await package.deploy_version(
    code=updated_code,
    is_new_version=True
)

# Download source code
file_path = await current_version.download_source_code()
```

Classes:
    DomoCodeEngine_Package: Main package entity class
    DomoCodeEngine_Packages: Manager class for package collections
    DomoCodeEngine_PackageVersion: Package version subentity
"""

from __future__ import annotations

__all__ = [
    "ExportExtension",
    "DomoCodeEngine_ConfigError",
    "DomoCodeEngine_Package",
    "DomoCodeEngine_Packages",
    "DomoCodeEngine_PackageVersion",
    # Re-export route exceptions
    "CodeEngine_GET_Error",
    "CodeEngine_CRUD_Error",
    "SearchCodeEngineNotFoundError",
]

import builtins
import datetime as dt
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from ...auth import DomoAuth
from ...base.entities import DomoEntity, DomoManager, DomoSubEntity
from ...base.exceptions import ClassError
from ...client.context import RouteContext
from ...routes import codeengine as codeengine_routes
from ...routes.codeengine.exceptions import (
    CodeEngine_CRUD_Error,
    CodeEngine_GET_Error,
    SearchCodeEngineNotFoundError,
)
from ...utils import files as dmuf
from ...utils.convert import convert_string_to_datetime
from .. import DomoUser as dmdu
from .Manifest import CodeEngineManifest


class ExportExtension(Enum):
    """File extension types for CodeEngine exports."""

    JAVASCRIPT = "js"
    PYTHON = "py"


class DomoCodeEngine_ConfigError(ClassError):
    """Exception raised when CodeEngine configuration is invalid."""

    def __init__(
        self,
        cls_instance=None,
        package_id: str | None = None,
        version: str | None = None,
        message: str | None = None,
        domo_instance: str | None = None,
    ):
        full_message = f"version {version} | {message}" if version else message
        super().__init__(
            cls_instance=cls_instance,
            entity_id=package_id,
            message=full_message,
            domo_instance=domo_instance,
        )


@dataclass
class DomoCodeEngine_PackageVersion(DomoSubEntity):
    """CodeEngine Package Version subentity.

    Represents a specific version of a CodeEngine package with its code,
    configuration, and function definitions.

    Attributes:
        parent: Reference to the parent DomoCodeEngine_Package (inherited from DomoSubEntity)
        auth: Authentication object (inherited from parent via DomoSubEntity)
        package_id: ID of the parent package
        version: Version string (e.g., "1.0.0")
        language: Programming language
        description: Version description
        createdby_id: ID of user who created this version
        released_dt: Release datetime
        configuration: Version configuration dict
        code: Source code string
        functions: Function definitions dict
        Manifest: CodeEngineManifest for Python packages
        createdby: DomoUser who created this version
        accounts_mapping: Account mapping configuration
        ml_model: ML model configuration
    """

    package_id: str
    version: str

    language: str | None = None
    description: str | None = None
    createdby_id: int | None = None
    released_dt: dt.datetime | None = None
    configuration: dict | None = None

    createdby: dmdu.DomoUser | None = None
    accounts_mapping: list[int] | None = None
    ml_model: list[str] | None = None

    code: str | None = field(repr=False, default=None)
    functions: dict | None = None

    Manifest: CodeEngineManifest | None = field(default=None)

    def _set_configuration(self, configuration=None):
        if configuration:
            self.configuration = configuration

        if not self.configuration:
            raise DomoCodeEngine_ConfigError(
                cls_instance=self,
                package_id=self.package_id,
                version=self.version,
                message="unable to set configuration",
            )

        self.accounts_mapping = self.configuration.get("accountsMapping", [])
        self.ml_model = self.configuration.get("mlModel", [])

        return self

    @classmethod
    def _create_temp_parent(cls, auth: DomoAuth, package_id: str):
        """Create a temporary parent object for DomoSubEntity initialization.

        Used when parent package is not yet available during version creation.
        The parent will be set properly after package creation.

        Args:
            auth: Authentication object
            package_id: Package identifier

        Returns:
            Temporary parent object with auth and id attributes
        """

        class TempParent:
            def __init__(self, auth_instance):
                self.auth = auth_instance
                self.id = package_id

        return TempParent(auth)

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict[str, Any],
        package_id: str,
        language: str | None = None,
        is_supress_error: bool = True,
        parent: DomoCodeEngine_Package | None = None,
    ):
        """Create DomoCodeEngine_PackageVersion from API response.

        Args:
            auth: Authentication object
            obj: API response dictionary
            package_id: Parent package ID
            language: Programming language (optional, will use obj value if not provided)
            is_supress_error: Whether to suppress configuration errors
            parent: Optional parent package reference (set after package creation if None)

        Returns:
            DomoCodeEngine_PackageVersion instance
        """
        language = (language or obj.get("language", "PYTHON")).upper()

        # DomoSubEntity requires parent, but we may not have it yet during package creation
        # Create a minimal parent object if needed (will be set properly after package creation)
        if parent is None:
            temp_parent = cls._create_temp_parent(auth=auth, package_id=package_id)
        else:
            temp_parent = parent

        # Only create Manifest if code is present and language is PYTHON
        code = obj.get("code")
        manifest = None
        if language == "PYTHON" and code:
            try:
                manifest = CodeEngineManifest.from_api(obj=obj)
            except (ValueError, AttributeError):
                # Code might be missing or invalid, skip manifest creation
                manifest = None

        domo_version = cls(
            parent=temp_parent,
            package_id=package_id,
            language=language,
            version=obj.get("version"),
            code=code,
            description=obj.get("description"),
            createdby_id=obj.get("createdBy"),
            released_dt=convert_string_to_datetime(obj.get("releasedOn")),
            configuration=obj.get("configuration"),
            Manifest=manifest,
        )

        # If we used a temp parent, update it to the real parent now
        if parent is not None and domo_version.parent is not parent:
            domo_version.parent = parent

        # Set configuration if available
        if domo_version.configuration:
            try:
                domo_version._set_configuration()
            except DomoCodeEngine_ConfigError:
                if not is_supress_error:
                    raise

        return domo_version

    @classmethod
    async def get_by_id_and_version(
        cls,
        auth: DomoAuth,
        package_id: str,
        version: str,
        language: str | None = None,
        params: dict | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        return_raw: bool = False,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Retrieve a specific package version.

        Args:
            auth: Authentication object
            package_id: Package identifier
            version: Version string
            language: Programming language (optional)
            params: Optional query parameters
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            return_raw: If True, return raw API response
            session: Optional httpx session
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoCodeEngine_PackageVersion instance or ResponseGetData if return_raw=True

        Raises:
            CodeEngine_GET_Error: If version retrieval fails
        """
        params = params or {"parts": "functions,code"}

        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await codeengine_routes.get_codeengine_package_by_id_and_version(
            auth=auth,
            package_id=package_id,
            version=version,
            params=params,
            context=context,
        )

        if return_raw:
            return res

        # For get_by_id_and_version, we don't have the parent package yet
        # Create a temporary parent object with auth
        temp_parent = cls._create_temp_parent(auth=auth, package_id=package_id)

        return cls.from_dict(
            auth=auth,
            obj=res.response,
            package_id=package_id,
            language=language,
            parent=temp_parent,
        )

    def __eq__(self, other):
        """Check equality based on package ID and version."""
        if not isinstance(other, DomoCodeEngine_PackageVersion):
            return False

        return self.version == other.version and self.package_id == other.package_id

    async def download_source_code(
        self,
        download_folder: str = "./EXPORT/codeengine",
        file_name: str | None = None,
        replace_folder: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Download the source code for this version to a file.

        Args:
            download_folder: Folder to save the code
            file_name: Optional file name (auto-generated if not provided)
            replace_folder: Whether to replace existing folder
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, etc.)

        Returns:
            Path to the downloaded file
        """
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        if not self.code:
            # Fetch code if not already loaded
            version_with_code = await self.get_by_id_and_version(
                auth=self.auth,
                package_id=self.package_id,
                version=self.version,
                params={"parts": "code"},
                context=context,
            )
            self.code = version_with_code.code

        extension = ".txt"
        if self.language == "PYTHON":
            extension = ".py"
        elif self.language == "JAVASCRIPT":
            extension = ".js"

        file_name = (
            file_name or f"{self.package_id}/{self.version}/functions{extension}"
        )

        file_path = os.path.join(download_folder, file_name)

        if self.Manifest:
            return self.Manifest.download_source_code(
                export_folder=os.path.join(download_folder, file_path),
                replace_folder=replace_folder,
            )

        dmuf.upsert_file(file_path, content=self.code, replace_folder=replace_folder)
        return file_path

    def export(
        self,
        file_name: str | None = None,
        output_folder: str = "EXPORT/codeengine/",
        debug_prn: bool = False,
    ):
        """Export the source code to a file.

        Args:
            file_name: Optional file name (defaults to package_id)
            output_folder: Output folder path
            debug_prn: Enable debug printing

        Returns:
            Path to the exported file
        """
        output_folder = (
            f"{output_folder}/" if not output_folder.endswith("/") else output_folder
        )

        dmuf.upsert_folder(output_folder)

        file_name = file_name or self.package_id
        file_name = dmuf.change_extension(
            file_name, ExportExtension[self.language].value
        )

        file_path = os.path.join(output_folder, file_name)

        if debug_prn:
            print(output_folder, file_name)

        with builtins.open(file_path, "w+", newline="\n", encoding="utf-8") as f:
            f.write(self.code)

        return file_path


@dataclass
class DomoCodeEngine_Package(DomoEntity):
    """Domo CodeEngine Package entity.

    Represents a CodeEngine package with versions and associated metadata.
    Packages contain executable code functions that can be deployed in Domo.

    Attributes:
        id: Unique package identifier
        auth: Authentication object
        raw: Raw API response data
        name: Package display name
        description: Package description
        language: Programming language (PYTHON or JAVASCRIPT)
        environment: Execution environment
        availability: Package availability status
        owner_id: ID of the package owner
        created: Package creation datetime
        last_modified: Last modification datetime
        functions: List of function definitions
        current_version: Latest version number
        versions: List of DomoCodeEngine_PackageVersion instances
        owner: DomoUser instance of the package owner

    Relationships:
        - **Package → Versions**: One package contains many versions (one-to-many)
        - **Package → Manager**: DomoCodeEngine_Packages manages collections of packages
        - **Version → Manifest**: Each version may contain a CodeEngineManifest (for Python packages)

    Class Constants:
        DEFAULT_RUNTIME: Default runtime version ("PYTHON_3_13")
        DEFAULT_ENVIRONMENT: Default execution environment ("LAMBDA")
        DEFAULT_LANGUAGE: Default programming language ("PYTHON")

    Key Methods:
        - create(): Create a new package from Python code
        - deploy_version(): Deploy code to this package (updates or creates new version)
        - _create_manifest_from_code(): Internal method to create manifest from Python code
        - _build_payload(): Internal method to build API payload

    Example:
        >>> package = await DomoCodeEngine_Package.create(
        ...     auth=auth,
        ...     name="My Package",
        ...     code="def hello(): return 'world'"
        ... )
        >>> result = await package.deploy_version(
        ...     code="def hello(): return 'updated'",
        ...     is_new_version=True
        ... )
    """

    # Default constants for package creation
    DEFAULT_RUNTIME = "PYTHON_3_13"
    DEFAULT_ENVIRONMENT = "LAMBDA"
    DEFAULT_LANGUAGE = "PYTHON"

    # Required DomoEntity attributes
    id: str
    name: str
    description: str
    language: str
    environment: str
    availability: str
    owner_id: int
    created: dt.datetime
    last_modified: dt.datetime
    functions: list

    current_version: str | None = None
    versions: list[DomoCodeEngine_PackageVersion] | None = None
    owner: list[dmdu.DomoUser] | None = None

    def __post_init__(self):
        """Initialize package and set current version."""
        self.id = str(self.id)
        self._set_current_version()

    @property
    def entity_type(self) -> str:
        """Get the EntityType for CodeEngine packages."""
        return "CODEENGINE_PACKAGE"

    @property
    def display_url(self) -> str:
        """Generate the URL to display this package in the Domo interface."""
        return f"https://{self.auth.domo_instance}.domo.com/admin/codeengine/packages/{self.id}"

    @classmethod
    async def get_entity_by_id(cls, auth: DomoAuth, entity_id: str, **kwargs):
        """Fetch a CodeEngine package by its ID.

        This method is used by the base DomoEntity class for entity resolution.
        """
        return await cls.get_by_id(auth=auth, package_id=entity_id, **kwargs)

    def _set_current_version(self):
        """Determine and set the current (latest) version of the package."""
        if not self.versions:
            return

        versions = [version.version for version in self.versions]
        self.current_version = max(versions) if versions else None

    @classmethod
    def _create_manifest_from_code(
        cls,
        code: str,
        handler_name: str | None = None,
        metadata: dict | None = None,
    ) -> CodeEngineManifest:
        """Create a CodeEngineManifest from Python code string.

        Internal method that wraps CodeEngineManifest.from_python_string()
        with additional metadata handling (runtime, handler reordering).

        Args:
            code: Python source code string to analyze
            handler_name: Optional name of the handler function. If not provided,
                uses the first top-level function encountered in AST.
            metadata: Optional metadata overrides to merge into manifest.
                Supported keys:
                - runtime: Runtime version (default: "PYTHON_3_13")
                - accountsMapping: List of account mapping dicts
                - description: Package description

        Returns:
            CodeEngineManifest with functions and configuration extracted from code.
        """
        metadata = metadata or {}
        accounts_mapping = metadata.get("accountsMapping", [])

        manifest = CodeEngineManifest.from_python_string(
            python_str=code,
            accounts_mapping=accounts_mapping,
        )

        # Reorder functions if handler_name specified
        if handler_name and manifest.functions:
            for i, fn in enumerate(manifest.functions):
                if fn.name == handler_name:
                    manifest.functions.insert(0, manifest.functions.pop(i))
                    break

        # Add runtime to configuration
        runtime = metadata.get("runtime", cls.DEFAULT_RUNTIME)
        manifest.configuration["runtime"] = runtime

        return manifest

    @classmethod
    def from_dict(cls, auth: DomoAuth, obj: dict[str, Any]):
        """Create DomoCodeEngine_Package from API response dictionary.

        Args:
            auth: Authentication object
            obj: API response dictionary

        Returns:
            DomoCodeEngine_Package instance
        """
        package_id = str(obj.get("id"))
        language = obj.get("language")

        # Create package first (without versions) so we can reference it as parent
        package = cls(
            auth=auth,
            id=package_id,
            name=obj.get("name"),
            description=obj.get("description"),
            language=language,
            environment=obj.get("environment"),
            availability=obj.get("availability"),
            owner_id=obj.get("owner"),
            versions=None,  # Will set after creating versions
            created=convert_string_to_datetime(obj.get("createdOn")),
            last_modified=convert_string_to_datetime(obj.get("updatedOn")),
            functions=obj.get("functions", []),
            raw=obj,
        )

        # Parse versions if present, now that we have the parent package
        versions = []
        if obj.get("versions"):
            versions = [
                DomoCodeEngine_PackageVersion.from_dict(
                    auth=auth,
                    obj=version,
                    package_id=package_id,
                    language=language,
                    parent=package,
                )
                for version in obj.get("versions", [])
            ]
            package.versions = versions

        return package

    @classmethod
    async def create(
        cls,
        auth: DomoAuth,
        name: str,
        code: str,
        version: str = "1.0.0",
        metadata: dict | None = None,
        *,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoCodeEngine_Package:
        """Create a new CodeEngine package from Python source code.

        Args:
            auth: Authentication object with access to the target Domo instance.
            name: Display name for the new package.
            code: Python source code string to upload.
            version: Initial version string (default: "1.0.0").
            metadata: Optional overrides for manifest / package configuration. Supported keys:
                - runtime: Runtime version (default: "PYTHON_3_13")
                - accountsMapping: List of account mapping dicts
                - description: Package description
                - environment: Execution environment (default: "LAMBDA")
                - language: Language identifier (default: "PYTHON")
            debug_api: Enable API debugging for underlying calls.
            debug_num_stacks_to_drop: Stack frames to drop in logging.
            session: Optional httpx session for connection reuse.

        Returns:
            DomoCodeEngine_Package instance for the created package.
        """
        metadata = metadata or {}

        manifest = cls._create_manifest_from_code(code=code, metadata=metadata)

        functions = [fn.to_dict() for fn in manifest.functions]

        environment = metadata.get("environment", cls.DEFAULT_ENVIRONMENT)
        language = metadata.get("language", cls.DEFAULT_LANGUAGE)
        description = metadata.get("description")
        initial_version = metadata.get("version", version)

        payload: dict = {
            "code": code,
            "environment": environment,
            "language": language,
            "manifest": {
                "functions": functions,
                "configuration": manifest.configuration,
            },
            "name": name,
            "version": initial_version,
        }

        if description is not None:
            payload["description"] = description

        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await codeengine_routes.create_codeengine_package(
            auth=auth,
            payload=payload,
            context=context,
            return_raw=False,
        )

        return cls.from_dict(auth=auth, obj=res.response)

    @classmethod
    async def get_by_id(
        cls,
        auth: DomoAuth,
        package_id: str,
        params: dict | None = None,
        return_raw: bool = False,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ):
        """Retrieve a CodeEngine package by ID.

        Args:
            auth: Authentication object
            package_id: Package identifier
            params: Optional query parameters
            return_raw: If True, return raw API response
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            session: Optional httpx session
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            DomoCodeEngine_Package instance or ResponseGetData if return_raw=True

        Raises:
            CodeEngine_GET_Error: If package retrieval fails
        """
        # Create temporary instance to use _build_route_context()
        dummy = cls.__new__(cls)
        dummy.auth = auth
        base_context = dummy._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await codeengine_routes.get_codeengine_package_by_id(
            auth=auth,
            package_id=package_id,
            params=params,
            context=context,
        )

        if return_raw:
            return res

        return cls.from_dict(auth=auth, obj=res.response)

    def __eq__(self, other):
        """Check equality based on package ID."""
        if not isinstance(other, DomoCodeEngine_Package):
            return False
        return self.id == other.id

    @classmethod
    async def upsert(
        cls,
        auth: DomoAuth,
        name: str,
        code: str,
        *,
        search_existing: bool = True,
        create_if_missing: bool = True,
        is_new_version: bool = True,
        version: str = "1.0.0",
        metadata: dict | None = None,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoCodeEngine_Package:
        """Create or update a CodeEngine package from Python source code.

        Args:
            auth: Authentication object.
            name: Logical package name to search for / create.
            code: Python source to deploy.
            search_existing: If True, search by name before creating.
            create_if_missing: If True, create a new package when none exists.
            is_new_version: Passed to deploy_version for existing packages.
            version: Initial version to use when creating a new package.
            metadata: Optional manifest / package metadata overrides.
            debug_api: Enable API debugging for underlying calls.
            debug_num_stacks_to_drop: Stack frames to drop in logging.
            session: Optional httpx session for connection reuse.

        Returns:
            DomoCodeEngine_Package for the updated or created package.
        """
        metadata = metadata or {}

        # 1) Try to find an existing package by name
        existing_pkg: DomoCodeEngine_Package | None = None
        if search_existing:
            manager = DomoCodeEngine_Packages(auth=auth)
            try:
                matches = await manager.search_by_name(
                    name=name,
                    context=context,
                    **context_kwargs,
                )
            except SearchCodeEngineNotFoundError:
                matches = []

            # Prefer exact name match if multiple results come back
            exact_matches = [
                pkg for pkg in matches if (pkg.name or "").lower() == name.lower()
            ]
            if exact_matches:
                existing_pkg = exact_matches[0]
            elif matches:
                # Fallback: first partial match
                existing_pkg = matches[0]

        # 2) If we found an existing package, deploy a new or updated version
        if existing_pkg is not None:
            result = await existing_pkg.deploy_version(
                code=code,
                is_new_version=is_new_version,
                metadata=metadata,
                context=context,
                **context_kwargs,
            )

            # Refresh package state from API to reflect new version
            return await cls.get_by_id(
                auth=auth,
                package_id=result["package_id"],
                context=context,
                **context_kwargs,
            )

        # 3) Otherwise, optionally create a brand new package
        if not create_if_missing:
            raise CodeEngine_CRUD_Error(
                operation="upsert",
                message=f"No existing CodeEngine package found for name '{name}', and create_if_missing=False",
            )

        return await cls.create(
            auth=auth,
            name=name,
            code=code,
            version=version,
            metadata=metadata,
            context=context,
            **context_kwargs,
        )

    async def get_current_version(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> DomoCodeEngine_PackageVersion:
        """Get the current (latest) version of this package.

        Args:
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, debug_num_stacks_to_drop, etc.)

        Returns:
            DomoCodeEngine_PackageVersion instance

        Raises:
            DomoCodeEngine_ConfigError: If no current version found
        """
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        if not self.current_version:
            raise DomoCodeEngine_ConfigError(
                package_id=self.id,
                version=None,
                message="No current version found for the package",
                domo_instance=self.auth.domo_instance,
            )

        domo_version = await DomoCodeEngine_PackageVersion.get_by_id_and_version(
            auth=self.auth,
            package_id=self.id,
            version=self.current_version,
            language=self.language,
            context=context,
        )

        return domo_version

    async def get_owner(
        self,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> dmdu.DomoUser | None:
        """Get the owner (user) of this package.

        Args:
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, debug_num_stacks_to_drop, etc.)

        Returns:
            DomoUser instance or None if owner_id not set
        """
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        if not self.owner_id:
            return None

        self.owner = await dmdu.DomoUser.get_by_id(
            auth=self.auth,
            user_id=str(self.owner_id),
            context=context,
        )

        return self.owner

    def _build_payload(
        self,
        code: str,
        manifest: CodeEngineManifest,
        version: str,
        metadata: dict | None = None,
    ) -> dict:
        """Build package payload for API submission.

        Internal method that constructs the payload dictionary
        for package creation/update API calls.

        Args:
            code: Python source code
            manifest: Generated manifest
            version: Version string
            metadata: Optional metadata overrides

        Returns:
            Dictionary payload for CodeEngine API
        """
        metadata = metadata or {}
        functions_list = [fn.to_dict() for fn in manifest.functions]

        return {
            "code": code,
            "environment": metadata.get("environment", self.DEFAULT_ENVIRONMENT),
            "id": self.id,
            "language": metadata.get("language", self.DEFAULT_LANGUAGE),
            "manifest": {
                "functions": functions_list,
                "configuration": manifest.configuration,
            },
            "name": metadata.get("name", self.name),
            "version": version,
        }

    async def deploy_version(
        self,
        code: str,
        is_new_version: bool = False,
        metadata: dict | None = None,
        *,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
    ) -> dict:
        """Deploy Python code to this package.

        Creates a manifest from the code and deploys it to this package.
        Supports either updating the current version or creating a new version.

        Args:
            code: Python source code string to deploy
            is_new_version: If True, create a new version. If False (default),
                update the current version.
            metadata: Optional metadata overrides including:
                - runtime: Runtime version (default: "PYTHON_3_13")
                - accountsMapping: List of account mapping dicts
                - name: Package name override
                - description: Package description
                - handler_name: Name of the handler function
            debug_api: Enable API debugging
            session: Optional httpx session for connection reuse

        Returns:
            dict containing:
                - package_id: The package ID
                - version: The version that was created/updated
                - status: "created" or "updated"
                - response: Raw API response data

        Raises:
            CodeEngine_GET_Error: If package retrieval fails
            CodeEngine_CRUD_Error: If deployment fails
        """
        metadata = metadata or {}

        # Build manifest from code
        handler_name = metadata.get("handler_name")
        manifest = self._create_manifest_from_code(
            code=code,
            handler_name=handler_name,
            metadata=metadata,
        )

        # Determine version
        current_version = self.current_version or "1.0.0"
        if is_new_version:
            from ...routes.codeengine import increment_version

            version = increment_version(current_version)
        else:
            version = current_version

        # Build payload
        payload = self._build_payload(
            code=code,
            manifest=manifest,
            version=version,
            metadata=metadata,
        )

        # Deploy using upsert route
        from ...routes.codeengine import upsert_package

        res = await upsert_package(
            auth=self.auth,
            payload=payload,
            create_new_version=is_new_version,
            debug_prn=debug_api,
        )

        return {
            "package_id": self.id,
            "version": version,
            "status": "created" if is_new_version else "updated",
            "response": res.response,
        }


@dataclass
class DomoCodeEngine_Packages(DomoManager):
    """Manager class for CodeEngine package collections.

    Provides methods to retrieve, search, and manage multiple CodeEngine packages.

    Attributes:
        auth: Authentication object
    """

    auth: DomoAuth = field(repr=False)

    async def get(
        self,
        debug_api: bool = False,
        debug_num_stacks_to_drop: int = 2,
        session: httpx.AsyncClient | None = None,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoCodeEngine_Package]:
        """Get all CodeEngine packages.

        Args:
            debug_api: Enable API debugging
            debug_num_stacks_to_drop: Stack frames to drop in logging
            session: Optional httpx session
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            List of DomoCodeEngine_Package instances

        Raises:
            CodeEngine_GET_Error: If package retrieval fails
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await codeengine_routes.get_packages(
            auth=self.auth,
            context=context,
        )

        return [
            DomoCodeEngine_Package.from_dict(auth=self.auth, obj=obj)
            for obj in res.response
        ]

    async def search_by_name(
        self,
        name: str,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> list[DomoCodeEngine_Package]:
        """Search for packages by name.

        Args:
            name: Package name to search for (case-insensitive partial match)
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters (debug_api, session, debug_num_stacks_to_drop, etc.)

        Returns:
            List of matching DomoCodeEngine_Package instances

        Raises:
            SearchCodeEngine_NotFound: If no packages match the search
        """
        base_context = self._build_route_context(**context_kwargs)
        context = RouteContext.build_context(context=context or base_context)

        all_packages = await self.get(
            context=context,
        )

        matches = [
            pkg for pkg in all_packages if name.lower() in (pkg.name or "").lower()
        ]

        if not matches:
            raise SearchCodeEngineNotFoundError(
                search_criteria=f"name contains '{name}'",
            )

        return matches
