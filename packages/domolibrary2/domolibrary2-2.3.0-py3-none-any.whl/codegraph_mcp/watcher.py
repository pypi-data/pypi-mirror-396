"""
File Watcher for Incremental Updates

Watches codebase for changes and triggers graph updates.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    FileSystemEventHandler = None  # type: ignore
    Observer = None  # type: ignore


class CodeChangeHandler:
    """Handler for file system change events."""

    def __init__(
        self,
        on_file_changed: Callable[[str], None],
        file_extensions: list[str] | None = None,
    ) -> None:
        """Initialize change handler.

        Args:
            on_file_changed: Callback function when file changes
            file_extensions: List of file extensions to watch (default: ['.py'])
        """
        self.on_file_changed = on_file_changed
        self.file_extensions = file_extensions or [".py"]
        self.debounce_time = 2.0  # Wait 2 seconds before processing
        self.pending_changes: dict[str, float] = {}

    def should_process(self, file_path: str) -> bool:
        """Check if file should be processed.

        Args:
            file_path: Path to file

        Returns:
            True if file should be processed
        """
        path = Path(file_path)
        return path.suffix in self.file_extensions

    def handle_change(self, file_path: str) -> None:
        """Handle file change with debouncing.

        Args:
            file_path: Path to changed file
        """
        if not self.should_process(file_path):
            return

        current_time = time.time()
        self.pending_changes[file_path] = current_time

        # Wait for debounce period
        time.sleep(self.debounce_time)

        # Check if this is still the latest change
        if self.pending_changes.get(file_path) == current_time:
            self.on_file_changed(file_path)
            del self.pending_changes[file_path]


class CodeGraphWatcher:
    """File watcher for codebase graph updates."""

    def __init__(
        self,
        directory: str | Path,
        on_file_changed: Callable[[str], None],
        file_extensions: list[str] | None = None,
    ) -> None:
        """Initialize file watcher.

        Args:
            directory: Directory to watch
            on_file_changed: Callback when file changes
            file_extensions: File extensions to watch
        """
        if Observer is None:
            raise ImportError(
                "watchdog not installed. Install with: pip install watchdog"
            )

        self.directory = Path(directory)
        self.handler = CodeChangeHandler(on_file_changed, file_extensions)
        self.observer = Observer()

        # Create event handler
        if FileSystemEventHandler:

            class ChangeHandler(FileSystemEventHandler):
                """File system event handler."""

                def __init__(self, handler: CodeChangeHandler) -> None:
                    """Initialize handler."""
                    super().__init__()
                    self.handler = handler

                def on_modified(self, event) -> None:
                    """Handle file modification."""
                    if not event.is_directory:
                        self.handler.handle_change(event.src_path)

                def on_created(self, event) -> None:
                    """Handle file creation."""
                    if not event.is_directory:
                        self.handler.handle_change(event.src_path)

            event_handler = ChangeHandler(self.handler)
            self.observer.schedule(event_handler, str(self.directory), recursive=True)

    def start(self) -> None:
        """Start watching for changes."""
        self.observer.start()

    def stop(self) -> None:
        """Stop watching for changes."""
        self.observer.stop()
        self.observer.join()
