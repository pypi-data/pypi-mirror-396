"""Conversion state tracking.

This module manages the state of Postman collection conversions,
tracking what has been converted and what matches were found.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class EndpointState:
    """State for a single endpoint conversion."""

    status: str  # "converted", "pending", "skipped"
    match_type: str | None = None
    existing_route: str | None = None
    staged_file: str | None = None
    converted_at: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "match_type": self.match_type,
            "existing_route": self.existing_route,
            "staged_file": self.staged_file,
            "converted_at": self.converted_at,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EndpointState:
        """Create from dictionary."""
        return cls(
            status=data.get("status", "pending"),
            match_type=data.get("match_type"),
            existing_route=data.get("existing_route"),
            staged_file=data.get("staged_file"),
            converted_at=data.get("converted_at"),
            notes=data.get("notes", ""),
        )


@dataclass
class ConversionState:
    """Complete conversion state for a Postman collection."""

    collection_hash: str
    collection_path: str
    last_converted: str
    endpoints: dict[str, EndpointState] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "collection_hash": self.collection_hash,
            "collection_path": self.collection_path,
            "last_converted": self.last_converted,
            "endpoints": {
                key: state.to_dict() for key, state in self.endpoints.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversionState:
        """Create from dictionary."""
        endpoints = {
            key: EndpointState.from_dict(value)
            for key, value in data.get("endpoints", {}).items()
        }
        return cls(
            collection_hash=data.get("collection_hash", ""),
            collection_path=data.get("collection_path", ""),
            last_converted=data.get("last_converted", ""),
            endpoints=endpoints,
        )


class ConversionTracker:
    """Tracks conversion state for Postman collections."""

    def __init__(self, state_file: str | Path = ".conversion_state.json"):
        """Initialize tracker.

        Args:
            state_file: Path to state file (relative to collection directory)
        """
        self.state_file = Path(state_file)
        self.state: ConversionState | None = None

    def load(self, collection_path: str | Path) -> ConversionState:
        """Load conversion state for a collection.

        Args:
            collection_path: Path to Postman collection

        Returns:
            ConversionState (empty if no state exists)
        """
        collection_path = Path(collection_path)
        state_path = collection_path.parent / self.state_file

        if state_path.exists():
            with open(state_path, encoding="utf-8") as f:
                data = json.load(f)
                self.state = ConversionState.from_dict(data)
        else:
            # Create new state
            collection_hash = self._calculate_hash(collection_path)
            self.state = ConversionState(
                collection_hash=collection_hash,
                collection_path=str(collection_path),
                last_converted=datetime.utcnow().isoformat(),
            )

        return self.state

    def save(self) -> None:
        """Save current state to file."""
        if not self.state:
            return

        state_path = Path(self.state.collection_path).parent / self.state_file
        state_path.parent.mkdir(parents=True, exist_ok=True)

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, indent=2)

    def update_endpoint(
        self,
        endpoint_key: str,
        status: str,
        match_type: str | None = None,
        existing_route: str | None = None,
        staged_file: str | None = None,
        notes: str = "",
    ) -> None:
        """Update state for a specific endpoint.

        Args:
            endpoint_key: Unique key for endpoint (e.g., "accounts/list_accounts")
            status: Status ("converted", "pending", "skipped")
            match_type: Type of match found
            existing_route: Path to existing route if matched
            staged_file: Path to staged file if converted
            notes: Additional notes
        """
        if not self.state:
            return

        endpoint_state = EndpointState(
            status=status,
            match_type=match_type,
            existing_route=existing_route,
            staged_file=staged_file,
            converted_at=datetime.utcnow().isoformat(),
            notes=notes,
        )
        self.state.endpoints[endpoint_key] = endpoint_state

    def get_endpoint_state(self, endpoint_key: str) -> EndpointState | None:
        """Get state for a specific endpoint.

        Args:
            endpoint_key: Unique key for endpoint

        Returns:
            EndpointState or None if not found
        """
        if not self.state:
            return None
        return self.state.endpoints.get(endpoint_key)

    def is_converted(self, endpoint_key: str) -> bool:
        """Check if endpoint has been converted.

        Args:
            endpoint_key: Unique key for endpoint

        Returns:
            True if endpoint is converted
        """
        state = self.get_endpoint_state(endpoint_key)
        return state is not None and state.status == "converted"

    def get_new_endpoints(self, all_endpoint_keys: list[str]) -> list[str]:
        """Get list of endpoints that haven't been converted yet.

        Args:
            all_endpoint_keys: List of all endpoint keys from collection

        Returns:
            List of endpoint keys that are new
        """
        if not self.state:
            return all_endpoint_keys

        new_endpoints = [key for key in all_endpoint_keys if not self.is_converted(key)]
        return new_endpoints

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate hash of collection file.

        Args:
            file_path: Path to collection file

        Returns:
            SHA256 hash as hex string
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
