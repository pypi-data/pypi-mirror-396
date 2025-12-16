"""
Tests for PACMAN Privacy Guarantees.

Tests that privacy guarantees are enforced correctly.
"""

import sys

import pytest

from pacman.core.privacy import (
    PrivacyGuarantees,
    PrivacyViolationError,
    get_data_storage_path,
)


class TestPrivacyGuarantees:
    """Tests for PrivacyGuarantees class."""

    def test_guarantees_exist(self):
        """Test that all privacy guarantees are defined."""
        guarantees = PrivacyGuarantees.get_guarantees()

        assert "NO_NETWORK" in guarantees
        assert "NO_TELEMETRY" in guarantees
        assert "NO_CLOUD_STORAGE" in guarantees
        assert "NO_EXTERNAL_APIS" in guarantees
        assert "AUDITABLE_SOURCE" in guarantees

    def test_all_guarantees_enabled(self):
        """Test that all guarantees are True by default."""
        guarantees = PrivacyGuarantees.get_guarantees()

        for name, value in guarantees.items():
            assert value is True, f"Guarantee {name} should be True"

    def test_blocked_modules_defined(self):
        """Test that blocked modules list is populated."""
        blocked = PrivacyGuarantees._BLOCKED_MODULES

        # Should block common HTTP libraries
        assert "requests" in blocked
        assert "httpx" in blocked
        assert "aiohttp" in blocked

        # Should block telemetry
        assert "sentry_sdk" in blocked

    def test_system_modules_defined(self):
        """Test that system modules are defined (for ignoring pre-loaded)."""
        system = PrivacyGuarantees._SYSTEM_MODULES

        # socket and ssl are system modules
        assert "socket" in system
        assert "ssl" in system

    def test_verify_is_idempotent(self):
        """Test that verify() can be called multiple times safely."""
        PrivacyGuarantees.verify()
        PrivacyGuarantees.verify()
        PrivacyGuarantees.verify()

        assert PrivacyGuarantees._verified is True

    def test_import_hook_installed(self):
        """Test that import hook is installed after verify."""
        PrivacyGuarantees.verify()

        assert PrivacyGuarantees._import_hook_installed is True

        # Check that hook is in sys.meta_path
        hook_found = False
        for finder in sys.meta_path:
            if "PrivacyImportBlocker" in type(finder).__name__:
                hook_found = True
                break

        assert hook_found, "Import hook should be in sys.meta_path"


class TestDataStoragePath:
    """Tests for local data storage."""

    def test_get_data_storage_path(self):
        """Test that data storage path is local."""
        path = get_data_storage_path()

        # Should be in home directory
        assert ".pacman" in path

        # Should not be a cloud path
        assert "cloud" not in path.lower()
        assert "s3:" not in path.lower()
        assert "gs:" not in path.lower()


class TestPrivacyViolationError:
    """Tests for PrivacyViolationError."""

    def test_error_message(self):
        """Test that error has informative message."""
        error = PrivacyViolationError("Test violation")
        assert "Test violation" in str(error)

    def test_error_inheritance(self):
        """Test that error inherits from Exception."""
        assert issubclass(PrivacyViolationError, Exception)


class TestNoNetworkGuarantee:
    """Tests specifically for NO_NETWORK guarantee."""

    def test_no_requests_import_in_pacman(self):
        """Test that 'requests' is not imported in PACMAN modules."""
        # Get all loaded pacman modules
        pacman_modules = [
            name for name in sys.modules.keys()
            if name.startswith("pacman")
        ]

        # Check that none of them have 'requests' as a dependency
        for mod_name in pacman_modules:
            mod = sys.modules.get(mod_name)
            if mod and hasattr(mod, "__dict__"):
                assert "requests" not in mod.__dict__, \
                    f"Module {mod_name} should not import 'requests'"

    def test_no_httpx_import_in_pacman(self):
        """Test that 'httpx' is not imported in PACMAN modules."""
        pacman_modules = [
            name for name in sys.modules.keys()
            if name.startswith("pacman")
        ]

        for mod_name in pacman_modules:
            mod = sys.modules.get(mod_name)
            if mod and hasattr(mod, "__dict__"):
                assert "httpx" not in mod.__dict__, \
                    f"Module {mod_name} should not import 'httpx'"
