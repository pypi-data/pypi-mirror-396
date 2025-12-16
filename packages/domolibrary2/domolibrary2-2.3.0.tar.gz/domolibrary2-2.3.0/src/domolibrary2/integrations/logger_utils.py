"""
Logger setup utilities for domolibrary2 projects.

Features:
- Colorized console output with filtering and log level control
- Environment-based handler selection (console-only for dev, Datadog for prod/staging)
- App name parameterization
- Handler injection via HandlerType class

Usage:
    from domolibrary2.integrations.logger_utils import generate_logger, HandlerType
    logger = generate_logger(
        app_name="MyApp",
        env="production",
        handler_types=HandlerType.default(),
        exclude_patterns=["get_data"],
        min_level="INFO"
    )
"""

import os

from dc_logger.client.base import (
    HandlerBufferSettings,
    HandlerInstance,
    Logger,
    set_global_logger,
)
from dc_logger.client.models import LogEntry
from dc_logger.logs.services.cloud.datadog import (
    DatadogHandler,
    DatadogServiceConfig,
)
from dc_logger.services.console.base import (
    ConsoleHandler,
    ConsoleServiceConfig,
)


# ANSI color codes for colorized console output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DEBUG = "\033[36m"  # Cyan
    INFO = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta
    TIMESTAMP = "\033[90m"  # Gray
    APP_NAME = "\033[34m"  # Blue


class ColorizedConsoleHandler(ConsoleHandler):
    def __init__(
        self,
        buffer_settings: HandlerBufferSettings,
        service_config: ConsoleServiceConfig,
        exclude_patterns: list[str] = None,
        min_level: str = "DEBUG",
    ):
        super().__init__(buffer_settings, service_config)
        self.exclude_patterns = exclude_patterns or []
        self.min_level = min_level

    def _normalize_entry_level(self, entry: LogEntry) -> LogEntry:
        """Normalize entry.level to be a string to avoid enum access issues."""
        if hasattr(entry.level, "value"):
            entry.level = str(entry.level.value)
        elif hasattr(entry.level, "name"):
            entry.level = str(entry.level.name)
        elif not isinstance(entry.level, str):
            entry.level = str(entry.level)
        return entry

    async def write(self, entries: list[LogEntry]) -> bool:
        """Override write to normalize entry levels and handle output."""
        for entry in entries:
            # Normalize entry level
            self._normalize_entry_level(entry)

            if (
                hasattr(self, "service_config")
                and self.service_config.output_type == "json"
            ):
                import json

                print(json.dumps(entry.__dict__, default=str))
            else:
                await self._write_text(entry)
        return True

    async def _write_text(self, entry: LogEntry) -> bool:
        # Level should already be normalized by write(), but ensure it's uppercase
        level_priority = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4,
        }

        entry_level = str(entry.level).upper()

        if level_priority.get(entry_level, 0) < level_priority.get(self.min_level, 0):
            return True
        message_lower = entry.message.lower()
        for pattern in self.exclude_patterns:
            if pattern.lower() in message_lower:
                return True
        level_colors = {
            "DEBUG": Colors.DEBUG,
            "INFO": Colors.INFO,
            "WARNING": Colors.WARNING,
            "ERROR": Colors.ERROR,
            "CRITICAL": Colors.CRITICAL,
        }
        level_color = level_colors.get(entry_level, Colors.RESET)

        try:
            message = (
                f"{Colors.TIMESTAMP}[{entry.timestamp}]{Colors.RESET} "
                f"{level_color}{Colors.BOLD}{entry_level}{Colors.RESET} "
                f"{Colors.APP_NAME}{entry.app_name}{Colors.RESET}: "
                f"{entry.message}"
            )
            print(message)
        except UnicodeEncodeError as e:
            print(
                f"[{entry.timestamp}] {entry_level} {entry.app_name}: {entry.message}"
            )
            print(f"[WARNING] Error in colorized output: {e}")

        return True


class HandlerType:
    """
    Encapsulates handler configuration for logger setup.
    Allows passing custom handler classes or instances for each handler type.
    Example:
        HandlerType({"console": ConsoleHandler, "datadog": DatadogHandler})
    """

    def __init__(self, handler_dict: dict[str, type] = None):
        self.handler_dict = handler_dict or {}

    @classmethod
    def default(cls):
        """Return default handler types for console and datadog."""
        return cls(
            {
                "console": ColorizedConsoleHandler,
                "datadog": DatadogHandler,
            }
        )

    def get(self, key: str):
        return self.handler_dict.get(key)


def generate_logger(
    app_name: str,
    env: str = "development",
    handler_types: HandlerType = None,
    exclude_patterns: list[str] = None,
    min_level: str = "DEBUG",
) -> Logger:
    """
    Generate a logger with console and optional Datadog handlers.

    Args:
        app_name: Name of the application for logging context
        env: Environment name ('development', 'production', 'staging', etc.)
        handler_types: HandlerType instance specifying handler classes (default: ColorizedConsoleHandler, DatadogHandler)
        exclude_patterns: List of message patterns to filter out
        min_level: Minimum log level to display

    Returns:
        Configured Logger instance
    """
    handlers = []
    handler_types = handler_types or HandlerType.default()

    # Console handler setup
    console_config = ConsoleServiceConfig(
        output_mode="console",
        output_type="text",
    )
    console_handler_cls = handler_types.get("console") or ColorizedConsoleHandler
    console_handler = console_handler_cls(
        buffer_settings=HandlerBufferSettings(),
        service_config=console_config,
        exclude_patterns=exclude_patterns,
        min_level=min_level,
    )
    console_handler_instance = HandlerInstance(
        service_handler=console_handler, handler_name="console"
    )
    handlers.append(console_handler_instance)

    # Datadog handler setup (if production/staging)
    if env.lower() in ("production", "prod", "staging"):
        datadog_api_key = os.getenv("DATADOG_API_KEY")
        if not datadog_api_key:
            print(
                f"[WARNING] Environment is '{env}' but DATADOG_API_KEY not set. Datadog logging disabled."
            )
        else:
            datadog_config = DatadogServiceConfig(
                api_key=datadog_api_key,
                site=os.getenv("DATADOG_SITE", "datadoghq.com"),
                service=app_name,
                env=env,
            )
            datadog_handler_cls = handler_types.get("datadog") or DatadogHandler
            datadog_handler = datadog_handler_cls(config=datadog_config)
            datadog_handler_instance = HandlerInstance(
                service_handler=datadog_handler, handler_name="datadog"
            )
            handlers.append(datadog_handler_instance)
            print(f"[INFO] Datadog logging enabled for environment: {env}")
    else:
        print(f"[INFO] Console-only logging for environment: {env}")

    logger = Logger(app_name=app_name, handlers=handlers)
    set_global_logger(logger)
    return logger
