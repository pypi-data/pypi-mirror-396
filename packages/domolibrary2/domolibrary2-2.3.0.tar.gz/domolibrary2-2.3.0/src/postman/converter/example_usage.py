"""
Example script demonstrating the multi-agent Postman to Python converter.

This script shows how to use the pydantic-ai multi-agent framework to convert
a Postman collection into Python API client functions.
"""

import asyncio
import os

from agent_graph import convert_postman_collection


async def main():
    """Run the Postman to Python conversion with the multi-agent graph."""

    # Path to your Postman collection
    collection_path = os.path.join(
        os.path.dirname(__file__), "..", "Domo Product APIs.postman_collection.json"
    )

    # Where to export generated files
    export_folder = os.path.join(os.path.dirname(__file__), "generated")

    # Optional customization
    customize_config = {
        "required_headers": ["authorization", "content-type"],
        "default_params": ["limit", "offset"],
    }

    # Run the conversion
    result = await convert_postman_collection(
        collection_path=collection_path,
        export_folder=export_folder,
        customize_config=customize_config,
        write_files=True,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("📊 CONVERSION SUMMARY")
    print("=" * 60)

    if result.get("conversion_plan"):
        plan = result["conversion_plan"]
        print("\n📋 Plan:")
        print(f"   Collection: {plan['collection_name']}")
        print(f"   Total Requests: {plan['total_requests']}")
        print(f"   Strategy: {plan['processing_strategy']}")
        print(f"   Complexity: {plan['estimated_complexity']}")

    if result.get("aggregated_analysis"):
        analysis = result["aggregated_analysis"]
        print("\n🔍 Analysis:")
        print(f"   Strategy: {analysis['code_generation_strategy']}")
        print(f"   Complexity: {analysis['complexity_assessment']}")
        print(f"   Shared Components: {len(analysis['shared_components'])}")

    if result.get("formatted_code"):
        print("\n💻 Generated Code:")
        print(f"   Files: {len(result['formatted_code'])}")
        for filename in list(result["formatted_code"].keys())[:5]:
            print(f"   • {filename}")
        if len(result["formatted_code"]) > 5:
            print(f"   ... and {len(result['formatted_code']) - 5} more")

    if result.get("export_paths"):
        print("\n📁 Exported to:")
        for path in result["export_paths"][:5]:
            print(f"   • {path}")
        if len(result["export_paths"]) > 5:
            print(f"   ... and {len(result['export_paths']) - 5} more")

    if result.get("warnings"):
        print(f"\n⚠️  Warnings: {len(result['warnings'])}")
        for warning in result["warnings"][:3]:
            print(f"   • {warning}")

    if result.get("errors"):
        print(f"\n❌ Errors: {len(result['errors'])}")
        for error in result["errors"]:
            print(f"   • {error}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
