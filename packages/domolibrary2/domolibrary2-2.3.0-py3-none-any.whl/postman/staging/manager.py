"""Staging area manager."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .metadata import StagingMetadata


class StagingManager:
    """Manages staging area operations."""

    def __init__(self, staging_root: str | Path):
        """Initialize staging manager.

        Args:
            staging_root: Root directory for staging area
        """
        self.staging_root = Path(staging_root)
        self.metadata: dict[str, StagingMetadata] = {}

    def add_staged_function(
        self,
        function_name: str,
        postman_request_name: str,
        postman_folder: str,
        staged_file: str,
        match_type: str | None = None,
        existing_route: str | None = None,
        notes: str = "",
    ) -> StagingMetadata:
        """Add metadata for a staged function.

        Args:
            function_name: Name of generated function
            postman_request_name: Original Postman request name
            postman_folder: Postman folder path
            staged_file: Path to staged file
            match_type: Type of match if applicable
            existing_route: Existing route if matched
            notes: Additional notes

        Returns:
            StagingMetadata object
        """
        metadata = StagingMetadata(
            function_name=function_name,
            postman_request_name=postman_request_name,
            postman_folder=postman_folder,
            staged_file=staged_file,
            match_type=match_type,
            existing_route=existing_route,
            notes=notes,
        )
        self.metadata[function_name] = metadata
        return metadata

    def get_metadata(self, function_name: str) -> StagingMetadata | None:
        """Get metadata for a function.

        Args:
            function_name: Name of function

        Returns:
            StagingMetadata or None if not found
        """
        return self.metadata.get(function_name)

    def list_staged_functions(self) -> list[StagingMetadata]:
        """List all staged functions.

        Returns:
            List of StagingMetadata objects
        """
        return list(self.metadata.values())

    def generate_report(self) -> dict[str, Any]:
        """Generate staging report.

        Returns:
            Dictionary with staging statistics
        """
        total = len(self.metadata)
        matched = sum(1 for m in self.metadata.values() if m.match_type)
        new = total - matched

        return {
            "total_functions": total,
            "matched_functions": matched,
            "new_functions": new,
            "functions": [m.to_dict() for m in self.metadata.values()],
        }
