"""Staging metadata tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class StagingMetadata:
    """Metadata for a staged route function."""

    function_name: str
    postman_request_name: str
    postman_folder: str
    match_type: str | None = None
    existing_route: str | None = None
    staged_file: str = ""
    generated_at: str = ""
    notes: str = ""

    def __post_init__(self):
        """Set default values."""
        if not self.generated_at:
            self.generated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function_name": self.function_name,
            "postman_request_name": self.postman_request_name,
            "postman_folder": self.postman_folder,
            "match_type": self.match_type,
            "existing_route": self.existing_route,
            "staged_file": self.staged_file,
            "generated_at": self.generated_at,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StagingMetadata:
        """Create from dictionary."""
        return cls(
            function_name=data.get("function_name", ""),
            postman_request_name=data.get("postman_request_name", ""),
            postman_folder=data.get("postman_folder", ""),
            match_type=data.get("match_type"),
            existing_route=data.get("existing_route"),
            staged_file=data.get("staged_file", ""),
            generated_at=data.get("generated_at", ""),
            notes=data.get("notes", ""),
        )
