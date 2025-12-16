"""Sync new endpoints from Postman collection."""

from __future__ import annotations

import argparse
import asyncio

from ..converter.deterministic.tracker import ConversionTracker
from .convert import convert_collection


async def sync_new_endpoints(
    collection_path: str,
    staging_root: str,
    routes_dir: str,
) -> dict:
    """Sync only new endpoints from Postman collection.

    Args:
        collection_path: Path to Postman collection JSON
        staging_root: Root directory for staging area
        routes_dir: Directory containing existing routes

    Returns:
        Dictionary with sync results
    """
    print("=" * 60)
    print("Syncing New Endpoints")
    print("=" * 60)

    # Load conversion state
    tracker = ConversionTracker()
    tracker.load(collection_path)

    # Parse collection to get all endpoint keys
    from ..converter.deterministic.parser import parse_postman_collection

    parsed = parse_postman_collection(collection_path)
    all_endpoint_keys = [
        f"{req.folder_path}/{req.name}" if req.folder_path else req.name
        for req in parsed.requests
    ]

    # Get new endpoints
    new_endpoints = tracker.get_new_endpoints(all_endpoint_keys)
    print(f"\nFound {len(new_endpoints)} new endpoints to convert")

    if not new_endpoints:
        print("No new endpoints to sync")
        return {"new_endpoints": 0, "converted": 0}

    # Convert new endpoints (simplified - would need to filter parsed.requests)
    # For now, just run full conversion
    result = await convert_collection(
        collection_path=collection_path,
        staging_root=staging_root,
        routes_dir=routes_dir,
        match_only=False,
        force=False,
    )

    # Update state
    tracker.save()

    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Sync new endpoints from Postman")
    parser.add_argument(
        "--collection",
        required=True,
        help="Path to Postman collection JSON",
    )
    parser.add_argument(
        "--staging",
        default="src/postman/_postman_staging",
        help="Staging directory",
    )
    parser.add_argument(
        "--routes-dir",
        default="src/domolibrary2/routes",
        help="Routes directory",
    )

    args = parser.parse_args()

    asyncio.run(
        sync_new_endpoints(
            collection_path=args.collection,
            staging_root=args.staging,
            routes_dir=args.routes_dir,
        )
    )

    print("\n" + "=" * 60)
    print("Sync Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
