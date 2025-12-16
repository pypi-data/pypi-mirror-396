"""Main conversion command."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from ..converter.deterministic.matcher import RouteMatcher
from ..converter.deterministic.parser import parse_postman_collection
from ..converter.generator.formatter import format_code
from ..converter.generator.route_generator import generate_route_function
from ..converter.generator.wrapper_generator import generate_wrapper_function
from ..converter.integration.route_discovery import discover_routes
from ..converter.integration.staging_writer import StagingWriter
from ..staging.manager import StagingManager


async def convert_collection(
    collection_path: str,
    staging_root: str,
    routes_dir: str,
    match_only: bool = False,
    output_file: str | None = None,
    force: bool = False,
) -> dict:
    """Convert Postman collection to route functions.

    Args:
        collection_path: Path to Postman collection JSON
        staging_root: Root directory for staging area
        routes_dir: Directory containing existing routes
        match_only: If True, only perform matching (dry-run)
        output_file: Optional file to write matches JSON
        force: If True, overwrite existing staged files

    Returns:
        Dictionary with conversion results
    """
    print("=" * 60)
    print("Postman to Route Conversion")
    print("=" * 60)

    # Parse Postman collection
    print("\nParsing Postman collection...")
    parsed = parse_postman_collection(collection_path)
    print(f"   Found {len(parsed.requests)} requests")

    # Discover existing routes
    print("\nDiscovering existing routes...")
    registry = discover_routes(routes_dir)
    print(f"   Found {len(registry.routes)} existing routes")

    # Build route registry for matcher
    route_registry = {}
    for route_name, route_info in registry.routes.items():
        route_registry[route_name] = {
            "module": route_info.module,
            "url": route_info.url or "",
            "method": route_info.method,
            "function_name": route_info.function_name,
        }

    # Match Postman requests to existing routes
    print("\nMatching Postman requests to existing routes...")
    matcher = RouteMatcher(route_registry)
    matches = []
    for request in parsed.requests:
        match = matcher.match(
            request.name,
            request.url_pattern,
            request.method,
        )
        matches.append(match)

    # Categorize matches
    exact_matches = [m for m in matches if m.match_type.value == "EXACT_MATCH"]
    url_matches = [m for m in matches if m.match_type.value == "URL_MATCH"]
    name_matches = [m for m in matches if m.match_type.value == "NAME_MATCH"]
    no_matches = [m for m in matches if m.match_type.value == "NO_MATCH"]

    print(f"   Exact matches: {len(exact_matches)}")
    print(f"   URL matches: {len(url_matches)}")
    print(f"   Name matches: {len(name_matches)}")
    print(f"   New routes: {len(no_matches)}")

    # If match_only, output results and return
    if match_only:
        results = {
            "total_requests": len(parsed.requests),
            "exact_matches": [m.to_dict() for m in exact_matches],
            "url_matches": [m.to_dict() for m in url_matches],
            "name_matches": [m.to_dict() for m in name_matches],
            "no_matches": [m.to_dict() for m in no_matches],
        }

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Matches written to {output_file}")

        return results

    # Generate code
    print("\nGenerating route functions...")
    staging_writer = StagingWriter(staging_root)
    staging_manager = StagingManager(staging_root)
    staging_writer.ensure_staging_structure()

    generated_count = 0

    # Generate wrappers for matches (these are safe - no duplicates)
    print(
        f"\nGenerating wrappers for {len(exact_matches + url_matches)} matched routes..."
    )
    for match in exact_matches + url_matches:
        if match.existing_route_name:
            # Extract folder from Postman request
            folder_path = ""
            for request in parsed.requests:
                if request.name == match.postman_request_name:
                    folder_path = request.folder_path
                    break

            # Skip if already exists in staging and not forcing
            if not force:
                existing_metadata = staging_manager.get_metadata(
                    match.postman_request_name
                )
                if existing_metadata and existing_metadata.staged_file:
                    print(f"   Skipping {match.postman_request_name} (already staged)")
                    continue

            try:
                wrapper = generate_wrapper_function(match, folder_path)
                formatted_code = format_code(wrapper["code"])
            except Exception as e:
                print(
                    f"   Warning: Failed to generate wrapper for {match.postman_request_name}: {e}"
                )
                continue

            # Determine module and submodule from folder path
            module_name, submodule_name = _extract_module_names(folder_path)

            # Write to staging
            staging_writer.write_module(
                module_name=module_name,
                submodule_name=submodule_name,
                functions=[{"name": wrapper["name"], "code": formatted_code}],
            )

            # Track metadata
            staged_file = f"{module_name}/{submodule_name}.py"
            staging_manager.add_staged_function(
                function_name=wrapper["name"],
                postman_request_name=match.postman_request_name,
                postman_folder=folder_path,
                staged_file=staged_file,
                match_type=match.match_type.value,
                existing_route=match.existing_route_module or "",
            )
            generated_count += 1
            print(f"   ✓ Wrapper: {wrapper['name']} -> {match.existing_route_name}")

    # Generate full routes for new endpoints (review these for potential duplicates)
    print(f"\nGenerating new routes for {len(no_matches)} unmatched endpoints...")
    print("   Note: Review these carefully - they may duplicate existing functionality")

    for request in parsed.requests:
        # Check if this request was matched
        matched = any(
            m.postman_request_name == request.name for m in exact_matches + url_matches
        )
        if not matched:
            # Skip if already exists in staging and not forcing
            if not force:
                existing_metadata = staging_manager.get_metadata(request.name)
                if existing_metadata and existing_metadata.staged_file:
                    print(f"   Skipping {request.name} (already staged)")
                    continue

            try:
                route_func = generate_route_function(request)
                formatted_code = format_code(route_func["code"])
            except Exception as e:
                print(f"   Warning: Failed to generate route for {request.name}: {e}")
                continue

            # Determine module and submodule
            module_name, submodule_name = _extract_module_names(request.folder_path)

            # Write to staging
            staging_writer.write_module(
                module_name=module_name,
                submodule_name=submodule_name,
                functions=[{"name": route_func["name"], "code": formatted_code}],
            )

            # Track metadata
            staged_file = f"{module_name}/{submodule_name}.py"
            staging_manager.add_staged_function(
                function_name=route_func["name"],
                postman_request_name=request.name,
                postman_folder=request.folder_path,
                staged_file=staged_file,
                match_type=None,
            )
            generated_count += 1
            print(f"   ✓ New route: {route_func['name']}")

    print(f"\nGenerated {generated_count} functions")

    # Generate report
    report = staging_manager.generate_report()
    print("\nStaging Report:")
    print(f"   Total: {report['total_functions']}")
    print(f"   Matched: {report['matched_functions']}")
    print(f"   New: {report['new_functions']}")

    # Generate index.md
    print("\nGenerating index.md...")
    _generate_index_md(
        staging_root=staging_root,
        matches=matches,
        exact_matches=exact_matches,
        url_matches=url_matches,
        name_matches=name_matches,
        no_matches=no_matches,
        parsed_requests=parsed.requests,
        report=report,
    )
    print("   ✓ index.md generated")

    return {
        "matches": len(exact_matches + url_matches),
        "new_routes": len(no_matches),
        "generated": generated_count,
        "report": report,
    }


def _sanitize_path_component(name: str) -> str:
    """Sanitize a path component to be alphanumeric with underscores/hyphens only.

    Args:
        name: Path component name

    Returns:
        Sanitized name safe for file/folder names
    """
    import re

    # Replace spaces and special chars with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Remove leading/trailing underscores and hyphens
    sanitized = sanitized.strip("_-")
    # Ensure it's not empty
    if not sanitized:
        sanitized = "misc"
    # Ensure it doesn't start with a number
    if sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized.lower()


def _extract_module_names(folder_path: str) -> tuple[str, str]:
    """Extract module and submodule names from folder path.

    Args:
        folder_path: Postman folder path (e.g., "Accounts/OAuth")

    Returns:
        Tuple of (module_name, submodule_name) - sanitized for safe file paths
    """
    if not folder_path:
        return ("misc", "core")

    parts = folder_path.split("/")
    module_name = _sanitize_path_component(parts[0])
    submodule_name = _sanitize_path_component(parts[1]) if len(parts) > 1 else "core"

    return (module_name, submodule_name)


def _generate_index_md(
    staging_root: str,
    matches: list,
    exact_matches: list,
    url_matches: list,
    name_matches: list,
    no_matches: list,
    parsed_requests: list,
    report: dict,
) -> None:
    """Generate index.md file documenting all exported functions.

    Args:
        staging_root: Root staging directory
        matches: All route matches
        exact_matches: Exact matches
        url_matches: URL matches
        name_matches: Name matches
        no_matches: No matches
        parsed_requests: All parsed Postman requests
        report: Staging report
    """

    staging_path = Path(staging_root)
    index_file = staging_path / "index.md"

    # Build match lookup for quick access
    {m.postman_request_name: m for m in matches}

    # Group by match type
    lines = []
    lines.append("# Postman Route Conversion Index")
    lines.append("")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Requests**: {len(parsed_requests)}")
    lines.append(f"- **Exact Matches**: {len(exact_matches)} (wrappers generated)")
    lines.append(f"- **URL Matches**: {len(url_matches)} (wrappers generated)")
    lines.append(f"- **Name Matches**: {len(name_matches)} (review needed)")
    lines.append(f"- **New Routes**: {len(no_matches)} (new functions generated)")
    lines.append(f"- **Total Generated**: {report['total_functions']}")
    lines.append("")

    # Exact Matches Section
    if exact_matches:
        lines.append("## Exact Matches (Wrappers)")
        lines.append("")
        lines.append(
            "These Postman endpoints exactly match existing routes. Wrapper functions were generated."
        )
        lines.append("")
        lines.append(
            "| Postman Request | Generated Function | Existing Route | Module |"
        )
        lines.append("|----------------|-------------------|----------------|--------|")
        for match in exact_matches:
            request = next(
                (r for r in parsed_requests if r.name == match.postman_request_name),
                None,
            )
            if request:
                module_name, submodule_name = _extract_module_names(request.folder_path)
                existing_route = match.existing_route_name or "N/A"
                existing_module = match.existing_route_module or "N/A"
                func_name = (
                    match.postman_request_name.lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                )
                lines.append(
                    f"| {match.postman_request_name} | `{func_name}_postman` | `{existing_route}` | `{existing_module}` |"
                )
        lines.append("")

    # URL Matches Section
    if url_matches:
        lines.append("## URL Matches (Wrappers)")
        lines.append("")
        lines.append(
            "These Postman endpoints match existing routes by URL. Wrapper functions were generated."
        )
        lines.append("")
        lines.append(
            "| Postman Request | Generated Function | Existing Route | Module |"
        )
        lines.append("|----------------|-------------------|----------------|--------|")
        for match in url_matches:
            request = next(
                (r for r in parsed_requests if r.name == match.postman_request_name),
                None,
            )
            if request:
                module_name, submodule_name = _extract_module_names(request.folder_path)
                existing_route = match.existing_route_name or "N/A"
                existing_module = match.existing_route_module or "N/A"
                func_name = (
                    match.postman_request_name.lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                )
                lines.append(
                    f"| {match.postman_request_name} | `{func_name}_postman` | `{existing_route}` | `{existing_module}` |"
                )
        lines.append("")

    # Name Matches Section
    if name_matches:
        lines.append("## Name Matches (Review Needed)")
        lines.append("")
        lines.append(
            "These Postman endpoints have similar names to existing routes but different URLs. Review needed."
        )
        lines.append("")
        lines.append(
            "| Postman Request | Postman URL | Existing Route | Existing URL | Confidence |"
        )
        lines.append(
            "|----------------|------------|----------------|--------------|------------|"
        )
        for match in name_matches:
            existing_route = match.existing_route_name or "N/A"
            existing_url = match.existing_route_url or "N/A"
            postman_url = match.postman_url or "N/A"
            # Truncate long URLs
            postman_url_display = (
                postman_url[:60] + "..." if len(postman_url) > 60 else postman_url
            )
            existing_url_display = (
                existing_url[:60] + "..." if len(existing_url) > 60 else existing_url
            )
            lines.append(
                f"| {match.postman_request_name} | `{postman_url_display}` | `{existing_route}` | `{existing_url_display}` | {match.confidence:.2f} |"
            )
        lines.append("")

    # New Routes Section
    if no_matches:
        lines.append("## New Routes")
        lines.append("")
        lines.append(
            "These Postman endpoints have no matching existing routes. New functions were generated."
        )
        lines.append("")
        lines.append("| Postman Request | Generated Function | Module | Status |")
        lines.append("|----------------|-------------------|--------|--------|")
        for match in no_matches:
            request = next(
                (r for r in parsed_requests if r.name == match.postman_request_name),
                None,
            )
            if request:
                module_name, submodule_name = _extract_module_names(request.folder_path)
                func_name = request.name.lower().replace(" ", "_").replace("-", "_")
                # Check if it was successfully generated
                status = "Generated"
                lines.append(
                    f"| {match.postman_request_name} | `{func_name}` | `{module_name}/{submodule_name}` | {status} |"
                )
        lines.append("")

    # Write index file
    index_file.write_text("\n".join(lines), encoding="utf-8")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Convert Postman collection to routes")
    parser.add_argument(
        "--collection",
        required=True,
        help="Path to Postman collection JSON",
    )
    parser.add_argument(
        "--staging",
        default="src/postman/_postman_staging",
        help="Staging directory (default: src/postman/_postman_staging)",
    )
    parser.add_argument(
        "--routes-dir",
        default="src/domolibrary2/routes",
        help="Routes directory (default: src/domolibrary2/routes)",
    )
    parser.add_argument(
        "--match-only",
        action="store_true",
        help="Only perform matching (dry-run)",
    )
    parser.add_argument(
        "--output",
        help="Output file for matches JSON (when using --match-only)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing staged files",
    )

    args = parser.parse_args()

    asyncio.run(
        convert_collection(
            collection_path=args.collection,
            staging_root=args.staging,
            routes_dir=args.routes_dir,
            match_only=args.match_only,
            output_file=args.output,
            force=args.force,
        )
    )

    print("\n" + "=" * 60)
    print("Conversion Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
