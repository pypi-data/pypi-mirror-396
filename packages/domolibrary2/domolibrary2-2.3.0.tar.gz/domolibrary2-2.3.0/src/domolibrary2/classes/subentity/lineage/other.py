"""Lineage handlers for other entity types (Sandbox, AppStudio, Dataflow)."""

from __future__ import annotations

__all__ = ["DomoLineage_Sandbox", "DomoLineage_AppStudio", "DomoLineage_Dataflow"]

from dataclasses import dataclass

from .base import DomoLineage, register_lineage


@register_lineage("DomoRepository")
@dataclass
class DomoLineage_Sandbox(DomoLineage):
    """Lineage handler for sandbox/repository entities."""

    pass


@register_lineage("DomoAppStudio", "DomoPublishAppStudio")
@dataclass
class DomoLineage_AppStudio(DomoLineage):
    """Lineage handler for AppStudio entities."""

    pass


@register_lineage("DomoDataflow")
@dataclass
class DomoLineage_Dataflow(DomoLineage):
    """Lineage handler for dataflow entities."""

    pass
