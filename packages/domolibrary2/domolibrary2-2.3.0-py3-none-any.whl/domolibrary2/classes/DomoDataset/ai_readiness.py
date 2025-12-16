"""AI Readiness subentity for DomoDataset"""

from __future__ import annotations

__all__ = [
    "DomoDataset_AI_Readiness",
    "AI_Readiness_Column",
]

from dataclasses import dataclass, field
from typing import Any

import httpx

from ...base.entities import DomoSubEntity
from ...client.context import RouteContext
from ...routes import ai as ai_routes


@dataclass
class AI_Readiness_Column:
    """Represents a column in the AI Readiness data dictionary."""

    name: str
    description: str = ""
    synonyms: list[str] = field(default_factory=list)
    subType: str = ""
    agentEnabled: bool = False
    beastmodeId: str = ""

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> AI_Readiness_Column:
        """Create an AI_Readiness_Column from a dictionary."""
        return cls(
            name=obj.get("name", ""),
            description=obj.get("description", ""),
            synonyms=obj.get("synonyms", []),
            subType=obj.get("subType", ""),
            agentEnabled=obj.get("agentEnabled", False),
            beastmodeId=obj.get("beastmodeId", ""),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary format for API requests."""
        return {
            "name": self.name,
            "description": self.description,
            "synonyms": self.synonyms,
            "subType": self.subType,
            "agentEnabled": self.agentEnabled,
            "beastmodeId": self.beastmodeId,
        }


@dataclass
class DomoDataset_AI_Readiness(DomoSubEntity):
    """AI Readiness subentity for managing dataset AI readiness data dictionary."""

    dictionary_id: str | None = None
    dictionary_name: str | None = None
    description: str | None = None
    unit_of_analysis: str = ""
    columns: list[AI_Readiness_Column] = field(default_factory=list)

    @classmethod
    def from_parent(cls, parent):
        """Create an AI Readiness instance from a parent dataset."""
        return cls(parent=parent)

    async def get(
        self,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> dict | DomoDataset_AI_Readiness:
        """Get the AI readiness data dictionary for the dataset.

        Args:
            session: Optional httpx session for connection reuse
            debug_api: Enable API debugging
            return_raw: Return raw API response instead of parsed object
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            Dictionary with AI readiness data if return_raw=True,
            otherwise returns self with populated fields
        """
        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await ai_routes.get_dataset_ai_readiness(
            auth=self.parent.auth,
            dataset_id=self.parent.id,
            context=context,
        )

        if return_raw:
            return res.response

        # Parse response
        data = res.response
        self.dictionary_id = data.get("id")
        self.dictionary_name = data.get("name")
        self.description = data.get("description")
        self.unit_of_analysis = data.get("unitOfAnalysis", "")
        self.columns = [
            AI_Readiness_Column.from_dict(col) for col in data.get("columns", [])
        ]

        return self

    async def create(
        self,
        dictionary_name: str,
        description: str | None = None,
        columns: list[dict | AI_Readiness_Column] | None = None,
        unit_of_analysis: str = "",
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> dict | DomoDataset_AI_Readiness:
        """Create an AI readiness data dictionary for the dataset.

        Args:
            dictionary_name: Name of the data dictionary
            description: Optional description
            columns: Optional list of column dictionaries or AI_Readiness_Column objects
            unit_of_analysis: Unit of analysis for the dictionary
            session: Optional httpx session for connection reuse
            debug_api: Enable API debugging
            return_raw: Return raw API response instead of parsed object
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            Dictionary with created AI readiness data if return_raw=True,
            otherwise returns self with populated fields
        """
        # Convert columns to dict format if needed
        columns_dict = None
        if columns:
            columns_dict = [
                col.to_dict() if isinstance(col, AI_Readiness_Column) else col
                for col in columns
            ]

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await ai_routes.create_dataset_ai_readiness(
            auth=self.parent.auth,
            dataset_id=self.parent.id,
            dictionary_name=dictionary_name,
            description=description,
            columns=columns_dict,
            context=context,
        )

        if return_raw:
            return res.response

        # Refresh from API
        return await self.get(context=context, return_raw=False)

    async def update(
        self,
        dictionary_id: str | None = None,
        dictionary_name: str | None = None,
        description: str | None = None,
        columns: list[dict | AI_Readiness_Column] | None = None,
        body: dict | None = None,
        session: httpx.AsyncClient | None = None,
        debug_api: bool = False,
        return_raw: bool = False,
        *,
        context: RouteContext | None = None,
        **context_kwargs,
    ) -> dict | DomoDataset_AI_Readiness:
        """Update the AI readiness data dictionary for the dataset.

        Args:
            dictionary_id: ID of the dictionary (required if not in body)
            dictionary_name: Updated name
            description: Updated description
            columns: Updated list of column dictionaries or AI_Readiness_Column objects
            body: Optional full body dictionary (overrides other parameters)
            session: Optional httpx session for connection reuse
            debug_api: Enable API debugging
            return_raw: Return raw API response instead of parsed object
            context: Optional RouteContext for API call configuration
            **context_kwargs: Additional context parameters

        Returns:
            Dictionary with updated AI readiness data if return_raw=True,
            otherwise returns self with populated fields
        """
        # Convert columns to dict format if needed
        columns_dict = None
        if columns:
            columns_dict = [
                col.to_dict() if isinstance(col, AI_Readiness_Column) else col
                for col in columns
            ]

        # Use existing dictionary_id if not provided
        dict_id = dictionary_id or self.dictionary_id

        base_context = self._build_route_context(
            session=session,
            debug_api=debug_api,
            **context_kwargs,
        )
        context = RouteContext.build_context(context=context or base_context)

        res = await ai_routes.update_dataset_ai_readiness(
            auth=self.parent.auth,
            dataset_id=self.parent.id,
            dictionary_id=dict_id,
            dictionary_name=dictionary_name,
            description=description,
            columns=columns_dict,
            body=body,
            context=context,
        )

        if return_raw:
            return res.response

        # Refresh from API
        return await self.get(context=context, return_raw=False)

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "id": self.dictionary_id,
            "datasetId": self.parent.id,
            "name": self.dictionary_name,
            "description": self.description,
            "unitOfAnalysis": self.unit_of_analysis,
            "columns": [col.to_dict() for col in self.columns],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        parent=None,
        parent_id: str | None = None,
        auth=None,
    ) -> DomoDataset_AI_Readiness:
        """Create a DomoDataset_AI_Readiness from a dictionary."""
        if not parent and (not parent_id or not auth):
            raise ValueError("Must provide either parent or (parent_id and auth)")

        # Create a minimal parent if needed (for standalone creation)
        if not parent:
            from ...classes.DomoDataset.core import DomoDataset

            parent = DomoDataset(
                id=parent_id or data.get("datasetId", ""),
                auth=auth,
                raw={},
            )

        instance = cls.from_parent(parent=parent)
        instance.dictionary_id = data.get("id")
        instance.dictionary_name = data.get("name")
        instance.description = data.get("description")
        instance.unit_of_analysis = data.get("unitOfAnalysis", "")
        instance.columns = [
            AI_Readiness_Column.from_dict(col) for col in data.get("columns", [])
        ]

        return instance
