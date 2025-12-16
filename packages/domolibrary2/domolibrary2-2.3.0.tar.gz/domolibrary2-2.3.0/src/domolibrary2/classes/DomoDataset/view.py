"""DomoDatasetView - A dataset view that references a parent dataset"""

from dataclasses import dataclass, field
from typing import Any

import httpx

from ...auth import DomoAuth
from ..subentity.lineage import register_lineage_type
from .dataset_default import DomoDataset_Default


@register_lineage_type("DomoDatasetView", lineage_type="DATA_SOURCE")
@dataclass
class DomoDatasetView(DomoDataset_Default):
    """A dataset view that references a parent dataset.

    Views are derived datasets that are based on another dataset.
    They cannot exist without a parent dataset.

    The parent dataset ID should be retrieved from lineage, not stored on the entity.
    """

    _parent_dataset: Any = field(default=None, repr=False)

    @staticmethod
    def _is_view(obj: dict[str, Any]) -> bool:
        """Check if a dataset JSON represents a view (dataset-view).

        Args:
            obj: Dataset metadata dictionary

        Returns:
            True if the dataset is a view, False otherwise
        """
        display_type = obj.get("displayType", "").lower()
        data_type = obj.get("dataType", "").lower()
        provider_type = obj.get("providerType", "").lower()

        return any(
            "dataset-view" in dt for dt in [display_type, data_type, provider_type]
        )

    @property
    def is_view(self) -> bool:
        """Check if this dataset is a view."""
        return self._is_view(self.raw) if self.raw else False

    async def get_parent_dataset(
        self,
        debug_api: bool = False,
        session: httpx.AsyncClient | None = None,
    ) -> DomoDataset_Default | None:
        """Get the parent dataset for this view from lineage.

        For views, the parent dataset is included in the lineage.
        This method retrieves it from the lineage rather than storing it on the entity.

        Args:
            debug_api: Enable API debugging
            session: HTTP client session (optional)

        Returns:
            The parent dataset instance, or None if not found
        """
        if self._parent_dataset:
            return self._parent_dataset

        # Get parent dataset from lineage using lineage subclass method
        # For views, the parent dataset should be in the immediate lineage
        await self.Lineage.get(
            debug_api=debug_api,
            session=session,
            is_recursive=False,
        )

        parent_item = self.Lineage.get_parent_dataset()

        if parent_item:
            self._parent_dataset = parent_item
            return self._parent_dataset

        return None

    @classmethod
    def from_dict(
        cls,
        auth: DomoAuth,
        obj: dict[str, Any],
        is_use_default_dataset_class: bool = True,
        new_cls=None,
        **kwargs,
    ) -> "DomoDatasetView":
        """Create a DomoDatasetView instance from API response dictionary.

        Args:
            auth: Authentication object
            obj: Dataset metadata dictionary
            is_use_default_dataset_class: Whether to use default class (ignored for views)
            new_cls: Alternative class to use (ignored for views)
            **kwargs: Additional keyword arguments

        Returns:
            DomoDatasetView instance

        Note:
            Parent dataset ID should be retrieved from lineage, not stored on the entity.
        """
        # Create the view instance using parent's from_dict
        view = super().from_dict(
            auth=auth,
            obj=obj,
            is_use_default_dataset_class=True,
            new_cls=cls,
            **kwargs,
        )

        return view
