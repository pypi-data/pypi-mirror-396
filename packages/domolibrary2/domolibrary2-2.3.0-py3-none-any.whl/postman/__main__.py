"""Main entry point for Postman conversion CLI."""

from __future__ import annotations

import sys

from .cli.convert import main as convert_main
from .cli.migrate import main as migrate_main
from .cli.sync import main as sync_main


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m postman convert --collection <path> [options]")
        print("  python -m postman sync --collection <path> [options]")
        print("  python -m postman migrate [options]")
        print("\nFor help:")
        print("  python -m postman convert --help")
        print("  python -m postman sync --help")
        print("  python -m postman migrate --help")
        sys.exit(1)

    command = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove 'postman' from argv

    if command == "convert":
        convert_main()
    elif command == "sync":
        sync_main()
    elif command == "migrate":
        migrate_main()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: convert, sync, migrate")
        sys.exit(1)


if __name__ == "__main__":
    main()
