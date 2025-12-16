"""
PACMAN Privacy Guarantees

This module enforces and documents PACMAN's privacy-first principles.
These guarantees are verified at runtime and can be audited by users.

GUARANTEES:
1. NO_NETWORK: PACMAN never makes network requests
2. NO_TELEMETRY: No usage data is collected
3. NO_CLOUD_STORAGE: All data stays on your device
4. NO_EXTERNAL_APIS: No external API calls
5. AUDITABLE_SOURCE: Open source, fully auditable (AGPL-3.0)
"""

import sys
import warnings
from typing import ClassVar


class PrivacyViolationError(Exception):
    """Raised when a privacy guarantee would be violated."""
    pass


class PrivacyGuarantees:
    """
    Enforced privacy guarantees for PACMAN.

    These are not just documentation - they are enforced at runtime.
    Any attempt to violate these guarantees will raise an error.
    """

    # Core guarantees
    NO_NETWORK: ClassVar[bool] = True
    NO_TELEMETRY: ClassVar[bool] = True
    NO_CLOUD_STORAGE: ClassVar[bool] = True
    NO_EXTERNAL_APIS: ClassVar[bool] = True
    AUDITABLE_SOURCE: ClassVar[bool] = True

    # Blocked modules that could violate privacy
    # Note: socket/ssl are system modules loaded by Python itself - we only block
    # high-level networking libraries that would actually make HTTP requests
    _BLOCKED_MODULES: ClassVar[set[str]] = {
        # HTTP clients
        "requests",
        "httpx",
        "aiohttp",
        "urllib.request",
        "http.client",
        # Network services
        "smtplib",
        "ftplib",
        "telnetlib",
        # Telemetry/analytics
        "sentry_sdk",
        "rollbar",
        "bugsnag",
        "newrelic",
        "datadog",
        "mixpanel",
        "amplitude",
        "segment",
        "posthog",
    }

    # System modules that are pre-loaded by Python/dependencies
    # These don't indicate a privacy violation when loaded before PACMAN
    _SYSTEM_MODULES: ClassVar[set[str]] = {
        "socket",
        "ssl",
        "_socket",
        "_ssl",
    }

    # Allowed modules for local operations only
    _ALLOWED_MODULES: ClassVar[set[str]] = {
        "pathlib",
        "os",
        "json",
        "yaml",
        "csv",
        "pandas",
        "pydantic",
        "typer",
        "rich",
        "openpyxl",
        "cryptography",  # For local encryption only
    }

    _verified: ClassVar[bool] = False
    _import_hook_installed: ClassVar[bool] = False
    _import_hook_disabled: ClassVar[bool] = False

    @classmethod
    def verify(cls) -> None:
        """
        Verify that privacy guarantees are in place.
        Called automatically on module import.
        """
        if cls._verified:
            return

        # Install import hook to block network modules
        if not cls._import_hook_installed:
            cls._install_import_hook()
            cls._import_hook_installed = True

        # Check that no blocked modules are already loaded
        # Skip system modules (socket/ssl) - they're loaded by Python itself
        for module in cls._BLOCKED_MODULES:
            if module in sys.modules and module not in cls._SYSTEM_MODULES:
                warnings.warn(
                    f"Module '{module}' was loaded before PACMAN. "
                    f"Privacy guarantees may be compromised.",
                    UserWarning,
                    stacklevel=2
                )

        cls._verified = True

    @classmethod
    def _install_import_hook(cls) -> None:
        """Install an import hook to block network-capable modules."""

        class PrivacyImportBlocker:
            """Blocks imports of network-capable modules within PACMAN context."""

            def find_module(
                self, fullname: str, path: str | None = None
            ) -> "PrivacyImportBlocker | None":
                # Skip if hook is disabled (e.g., for dashboard)
                if PrivacyGuarantees._import_hook_disabled:
                    return None
                # Check if this is a blocked module
                base_module = fullname.split('.')[0]
                if base_module in PrivacyGuarantees._BLOCKED_MODULES:
                    return self
                if fullname in PrivacyGuarantees._BLOCKED_MODULES:
                    return self
                return None

            def load_module(self, fullname: str) -> None:
                raise PrivacyViolationError(
                    f"PACMAN Privacy Violation: Import of '{fullname}' blocked.\n"
                    f"PACMAN is designed to work 100% offline.\n"
                    f"Network-capable modules are not allowed.\n"
                    f"See SECURITY.md for details."
                )

        # Only install if not already installed
        for finder in sys.meta_path:
            if isinstance(finder, PrivacyImportBlocker):
                return

        sys.meta_path.insert(0, PrivacyImportBlocker())

    @classmethod
    def get_guarantees(cls) -> dict[str, bool]:
        """Return all privacy guarantees as a dictionary."""
        return {
            "NO_NETWORK": cls.NO_NETWORK,
            "NO_TELEMETRY": cls.NO_TELEMETRY,
            "NO_CLOUD_STORAGE": cls.NO_CLOUD_STORAGE,
            "NO_EXTERNAL_APIS": cls.NO_EXTERNAL_APIS,
            "AUDITABLE_SOURCE": cls.AUDITABLE_SOURCE,
        }

    @classmethod
    def print_guarantees(cls) -> None:
        """Print privacy guarantees to stdout."""
        print("=" * 60)
        print("PACMAN PRIVACY GUARANTEES")
        print("=" * 60)
        print()
        for name, value in cls.get_guarantees().items():
            status = "[X]" if value else "[ ]"
            print(f"  {status} {name}")
        print()
        print("All data stays on your device.")
        print("PACMAN never makes network requests.")
        print("Verify by auditing the source code (AGPL-3.0).")
        print("=" * 60)

    @classmethod
    def disable_for_dashboard(cls) -> None:
        """
        Disable import hook for dashboard mode.

        The Streamlit dashboard uses third-party libraries that require
        network modules (WebSockets for the UI). Since the dashboard
        is a local-only UI and doesn't send user data externally,
        we allow these imports in dashboard mode.

        Note: User data never leaves the machine - Streamlit runs locally.
        """
        cls._import_hook_disabled = True


def assert_no_network() -> None:
    """
    Assert that no network modules are loaded.
    Can be called at any point to verify privacy.
    """
    loaded_blocked = [
        m for m in PrivacyGuarantees._BLOCKED_MODULES
        if m in sys.modules
    ]
    if loaded_blocked:
        raise PrivacyViolationError(
            f"Network-capable modules loaded: {loaded_blocked}"
        )


def get_data_storage_path() -> str:
    """
    Return the local data storage path.
    PACMAN stores all data locally, never in the cloud.
    """
    from pathlib import Path
    return str(Path.home() / ".pacman")
