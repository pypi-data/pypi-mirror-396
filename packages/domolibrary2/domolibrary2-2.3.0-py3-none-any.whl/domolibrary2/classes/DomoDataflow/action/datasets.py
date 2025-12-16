"""
DomoDataflow Dataset Actions

Input/Output actions for loading and publishing data in Magic ETL v2.
These correspond to the "DataSets" category in the Domo ETL UI sidebar.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....utils import DictDot as util_dd
from .base import DomoDataflow_Action_Base, register_action_type

__all__ = [
    "DomoDataflow_Action_LoadFromVault",
    "DomoDataflow_Action_PublishToVault",
    "DomoDataflow_Action_GenerateTable",
    "DomoDataflow_Action_PublishToWriteback",
]


@register_action_type("LoadFromVault")
@dataclass
class DomoDataflow_Action_LoadFromVault(DomoDataflow_Action_Base):
    """Input action - loads data from a Domo dataset.

    Attributes:
        datasource_id: The ID of the source dataset
        execute_flow_when_updated: Trigger dataflow on dataset update
        only_load_new_versions: Only load data when dataset has new data
    """

    datasource_id: str = None
    execute_flow_when_updated: bool = False
    only_load_new_versions: bool = False
    column_settings: dict = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.datasource_id = dd.dataSourceId
        self.execute_flow_when_updated = dd.executeFlowWhenUpdated or False
        self.only_load_new_versions = dd.onlyLoadNewVersions or False
        self.column_settings = dd.columnSettings
        self.tables = dd.tables

        # Update name from datasource if not set
        if not self.name and dd.dataSource:
            self.name = dd.dataSource.get("name")


@register_action_type("PublishToVault")
@dataclass
class DomoDataflow_Action_PublishToVault(DomoDataflow_Action_Base):
    """Output action - writes data to a Domo dataset.

    Attributes:
        data_source: Output dataset configuration
        version_chain_type: How to handle versions (REPLACE, APPEND, etc.)
        partitioned: Whether the output is partitioned
    """

    data_source: dict = None
    version_chain_type: str = None
    partitioned: bool = False
    schema_source: str = None
    tables: list[dict] = None

    @property
    def output_dataset_id(self) -> str | None:
        """Get the output dataset ID."""
        if self.data_source:
            return self.data_source.get("guid")
        return None

    @property
    def output_dataset_name(self) -> str | None:
        """Get the output dataset name."""
        if self.data_source:
            return self.data_source.get("name")
        return self.name

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.data_source = dd.dataSource
        self.version_chain_type = dd.versionChainType
        self.partitioned = dd.partitioned or False
        self.schema_source = dd.schemaSource
        self.tables = dd.tables

        # Update name from datasource if not set
        if not self.name and dd.dataSource:
            self.name = dd.dataSource.get("name")


@register_action_type("GenerateTableAction")
@dataclass
class DomoDataflow_Action_GenerateTable(DomoDataflow_Action_Base):
    """Generate table action for creating data programmatically."""

    fields: list[dict] = None
    row_count: int = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.fields = dd.fields
        self.row_count = dd.rowCount


@register_action_type("PublishToWriteback")
@dataclass
class DomoDataflow_Action_PublishToWriteback(DomoDataflow_Action_Base):
    """Publish to Writeback action - writes data to external systems.

    Similar to PublishToVault but for external destinations.

    Attributes:
        data_source: Output destination configuration
        writeback_info: Writeback-specific configuration
        version_chain_type: How to handle versions

    Example:
        >>> writeback_action = dataflow.get_action_objects("PublishToWriteback")[0]
        >>> print(f"Writing to: {writeback_action.data_source}")
    """

    data_source: dict = None
    writeback_info: dict = None
    version_chain_type: str = None
    partitioned: bool = False
    schema_source: str = None
    inputs: list[str] = None
    tables: list[dict] = None

    def _extract_fields(self, dd: util_dd.DictDot) -> None:
        self.data_source = dd.dataSource
        self.writeback_info = dd.writebackInfo
        self.version_chain_type = dd.versionChainType
        self.partitioned = dd.partitioned or False
        self.schema_source = dd.schemaSource
        self.inputs = dd.inputs or []
        self.tables = dd.tables
