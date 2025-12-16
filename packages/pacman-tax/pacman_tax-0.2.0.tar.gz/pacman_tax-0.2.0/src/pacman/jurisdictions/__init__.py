"""PACMAN Jurisdictions - Country/region-specific tax plugins."""

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pacman.jurisdictions.base import JurisdictionPlugin

_plugins: dict[str, "JurisdictionPlugin"] = {}


def discover_plugins() -> dict[str, "JurisdictionPlugin"]:
    """
    Auto-discover jurisdiction plugins.

    Looks for Plugin classes in subdirectories.
    """
    global _plugins

    if _plugins:
        return _plugins

    base_path = Path(__file__).parent

    for path in base_path.iterdir():
        if path.is_dir() and not path.name.startswith("_"):
            try:
                module = import_module(f".{path.name}", package=__name__)
                if hasattr(module, "Plugin"):
                    plugin = module.Plugin()
                    _plugins[plugin.code] = plugin
            except ImportError:
                continue

    return _plugins


def get_plugin(code: str) -> "JurisdictionPlugin":
    """
    Get a jurisdiction plugin by code.

    Args:
        code: Jurisdiction code (e.g., 'DE', 'AT', 'CH-ZH')

    Returns:
        JurisdictionPlugin instance

    Raises:
        KeyError: If plugin not found
    """
    plugins = discover_plugins()

    if code not in plugins:
        available = ", ".join(plugins.keys())
        raise KeyError(f"Jurisdiction '{code}' not found. Available: {available}")

    return plugins[code]


def list_plugins() -> list[str]:
    """List all available jurisdiction codes."""
    return list(discover_plugins().keys())
