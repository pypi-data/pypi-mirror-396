"""Lineage package for Domo entity dependency tracking.

This package provides lineage handling for tracking dependencies between
Domo entities (datasets, cards, pages, dataflows, publications, etc.).

Modules:
    link: Lineage link classes representing connections in the dependency graph
    base: Base DomoLineage class and registry system
    page: Page-specific lineage handler
    publication: Publication and Subscription lineage handlers
    card: Card-specific lineage handler
    dataset: Dataset-specific lineage handler
    other: Other entity type lineage handlers (Sandbox, AppStudio, Dataflow)
"""

from __future__ import annotations

# Base class and registry
from .base import (
    DomoLineage,
    FederatedLineageAuthRequiredError,
    get_lineage_type,
    register_lineage,
    register_lineage_type,
)
from .card import DomoLineage_Card
from .dataset import DomoLineage_Dataset

# Link classes
from .link import (
    DomoLineage_Link,
    DomoLineageLink_Card,
    DomoLineageLink_Dataflow,
    DomoLineageLink_Dataset,
    DomoLineageLink_Publication,
    DomoLineageLink_Subscription,
)
from .other import DomoLineage_AppStudio, DomoLineage_Dataflow, DomoLineage_Sandbox

# Entity-specific lineage handlers
# NOTE: These imports must come AFTER base.py to ensure the registry exists
# before the @register_lineage decorators run
from .page import DomoLineage_Page
from .publication import DomoLineage_Publication, DomoLineage_Subscription

__all__ = [
    # Link classes
    "DomoLineage_Link",
    "DomoLineageLink_Dataflow",
    "DomoLineageLink_Publication",
    "DomoLineageLink_Subscription",
    "DomoLineageLink_Card",
    "DomoLineageLink_Dataset",
    # Base class and registry
    "DomoLineage",
    "FederatedLineageAuthRequiredError",
    "register_lineage_type",
    "get_lineage_type",
    "register_lineage",
    # Entity-specific lineage handlers
    "DomoLineage_Page",
    "DomoLineage_Publication",
    "DomoLineage_Subscription",
    "DomoLineage_Sandbox",
    "DomoLineage_Card",
    "DomoLineage_Dataset",
    "DomoLineage_AppStudio",
    "DomoLineage_Dataflow",
]
