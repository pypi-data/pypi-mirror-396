"""
domolibrary2 - A Python library for interacting with Domo APIs.
"""

from pathlib import Path

from .utils.logging import get_colored_logger

get_colored_logger(set_as_global=True)  # Sets as dc_logger global logger


# Always read version from pyproject.toml to ensure sync
import tomllib  # noqa: E402
from importlib import metadata  # noqa: E402

pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
try:
    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        __version__ = pyproject_data["project"]["version"]
    else:
        __version__ = metadata.version("domolibrary2")
except (
    OSError,
    KeyError,
    tomllib.TOMLDecodeError,
    metadata.PackageNotFoundError,
) as exc:
    logger = get_colored_logger()
    logger.warning("Failed to determine domolibrary2 version: %s", exc)
    __version__ = "unknown"

from .base import entities, exceptions  # noqa: E402

# Define what gets imported with "from domolibrary2 import *"
__all__ = [
    "__version__",
    "exceptions",
    "entities",
    # "classes",
    # "integrations",
    # "client",
    # "routes",
    # "utils",
]
