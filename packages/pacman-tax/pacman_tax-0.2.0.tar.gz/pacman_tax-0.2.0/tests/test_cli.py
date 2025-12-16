"""
PACMAN CLI Tests

Tests for all CLI commands using Typer's CliRunner.
"""

import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

from pacman import __version__
from pacman.cli import app
from pacman.core.models import TaxCategory, Transaction

runner = CliRunner()


# =============================================================================
# Version & Help Tests
# =============================================================================

class TestVersionAndHelp:
    """Tests for version and help options."""

    def test_version_option(self):
        """Test --version shows version info."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"PACMAN v{__version__}" in result.stdout
        assert "Privacy-first" in result.stdout

    def test_version_short_option(self):
        """Test -v shows version info."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert f"PACMAN v{__version__}" in result.stdout

    def test_help_option(self):
        """Test --help shows help text."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "PACMAN" in result.stdout
        assert "Privacy-first" in result.stdout
        assert "init" in result.stdout
        assert "import" in result.stdout
        assert "categorize" in result.stdout

    def test_privacy_option(self):
        """Test --privacy shows privacy guarantees."""
        result = runner.invoke(app, ["--privacy"])
        assert result.exit_code == 0
        # Privacy guarantees should be displayed (case-insensitive check)
        assert "PRIVACY" in result.stdout.upper()
        assert "NO_NETWORK" in result.stdout or "network" in result.stdout.lower()


# =============================================================================
# Init Command Tests
# =============================================================================

class TestInitCommand:
    """Tests for the init command."""

    def test_init_creates_project(self, tmp_path: Path):
        """Test init creates project structure."""
        project_dir = tmp_path / "test_project"

        result = runner.invoke(app, [
            "init",
            "--profile", "vermieter",
            "--year", "2024",
            "--path", str(project_dir),
        ])

        assert result.exit_code == 0
        assert "initialized" in result.stdout.lower()

        # Check directory structure
        assert project_dir.exists()
        assert (project_dir / "import").exists()
        assert (project_dir / "export").exists()
        assert (project_dir / "config.yaml").exists()

        # Check config content
        with open(project_dir / "config.yaml") as f:
            config = yaml.safe_load(f)
        assert config["profile"] == "vermieter"
        assert config["year"] == 2024
        assert config["jurisdiction"] == "DE"

    def test_init_with_jurisdiction(self, tmp_path: Path):
        """Test init with custom jurisdiction."""
        project_dir = tmp_path / "test_project"

        result = runner.invoke(app, [
            "init",
            "--profile", "einzelunternehmer",
            "--year", "2025",
            "--jurisdiction", "DE",
            "--path", str(project_dir),
        ])

        assert result.exit_code == 0

        with open(project_dir / "config.yaml") as f:
            config = yaml.safe_load(f)
        assert config["profile"] == "einzelunternehmer"
        assert config["year"] == 2025
        assert config["jurisdiction"] == "DE"

    def test_init_requires_profile(self):
        """Test init fails without profile."""
        result = runner.invoke(app, ["init", "--year", "2024"])
        assert result.exit_code != 0

    def test_init_requires_year(self):
        """Test init fails without year."""
        result = runner.invoke(app, ["init", "--profile", "vermieter"])
        assert result.exit_code != 0


# =============================================================================
# Import Command Tests
# =============================================================================

class TestImportCommand:
    """Tests for the import command."""

    def test_import_no_files(self, tmp_path: Path):
        """Test import with no CSV files fails gracefully."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = runner.invoke(app, ["import", str(empty_dir)])

        assert result.exit_code == 1
        assert "No CSV/XLSX files found" in result.stdout

    def test_import_single_file(self, tmp_path: Path):
        """Test import with a single CSV file (Deutsche Bank format)."""
        # Create project
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "import").mkdir()
        (project_dir / "export").mkdir()

        # Create config
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(project_dir / "config.yaml", "w") as f:
            yaml.dump(config, f)

        # Create Deutsche Bank format CSV
        csv_content = """Buchungstag;Wert;Verwendungszweck;Soll;Haben;IBAN;Beguenstigter
05.01.2024;05.01.2024;Miete Januar 2024;;850,00;DE89370400440532013000;Max Mueller
10.01.2024;10.01.2024;Reparatur Heizung;100,00;;DE12500105170648489890;Handwerker GmbH
"""
        csv_file = project_dir / "import" / "test.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = runner.invoke(app, [
            "import", str(csv_file),
            "--bank", "deutsche-bank",
            "--project", str(project_dir),
        ])

        assert result.exit_code == 0
        assert "Imported" in result.stdout
        assert (project_dir / "transactions.json").exists()

    def test_import_directory(self, tmp_path: Path):
        """Test import from directory with multiple files."""
        # Create project
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        import_dir = project_dir / "import"
        import_dir.mkdir()
        (project_dir / "export").mkdir()

        # Create config
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(project_dir / "config.yaml", "w") as f:
            yaml.dump(config, f)

        # Create Deutsche Bank format CSV files
        csv_content = """Buchungstag;Wert;Verwendungszweck;Soll;Haben;IBAN;Beguenstigter
05.01.2024;05.01.2024;Miete Januar 2024;;850,00;DE89370400440532013000;Max Mueller
"""
        (import_dir / "file1.csv").write_text(csv_content, encoding="utf-8")
        (import_dir / "file2.csv").write_text(csv_content, encoding="utf-8")

        result = runner.invoke(app, [
            "import", str(import_dir),
            "--bank", "deutsche-bank",
            "--project", str(project_dir),
        ])

        assert result.exit_code == 0
        assert "Found 2 file(s)" in result.stdout

    def test_import_with_bank_option(self, tmp_path: Path):
        """Test import with specific bank format (short option)."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "import").mkdir()
        (project_dir / "export").mkdir()

        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(project_dir / "config.yaml", "w") as f:
            yaml.dump(config, f)

        # Deutsche Bank format
        csv_content = """Buchungstag;Wert;Verwendungszweck;Soll;Haben;IBAN;Beguenstigter
05.01.2024;05.01.2024;Miete Januar 2024;;850,00;DE89370400440532013000;Max Mueller
"""
        csv_file = project_dir / "import" / "test.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        result = runner.invoke(app, [
            "import", str(csv_file),
            "-b", "deutsche-bank",
            "--project", str(project_dir),
        ])

        assert result.exit_code == 0


# =============================================================================
# Categorize Command Tests
# =============================================================================

class TestCategorizeCommand:
    """Tests for the categorize command."""

    def test_categorize_no_config(self, tmp_path: Path):
        """Test categorize fails without config."""
        result = runner.invoke(app, [
            "categorize",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_categorize_no_transactions(self, tmp_path: Path):
        """Test categorize fails without transactions."""
        # Create config but no transactions
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "categorize",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_categorize_with_transactions(self, tmp_path: Path):
        """Test categorize with valid transactions."""
        # Create config
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
            "tenants": ["Max Mueller"],
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        # Create transactions
        transactions = [
            {
                "date": "2024-01-15",
                "amount": "850.00",
                "description": "Miete Januar Mueller",
                "counterparty": "Max Mueller",
            },
            {
                "date": "2024-01-20",
                "amount": "-100.00",
                "description": "Reparatur Heizung",
                "counterparty": "Handwerker GmbH",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        result = runner.invoke(app, [
            "categorize",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Categorizing" in result.stdout

    def test_categorize_with_threshold(self, tmp_path: Path):
        """Test categorize with custom threshold."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        transactions = [
            {
                "date": "2024-01-15",
                "amount": "850.00",
                "description": "Miete Januar",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        result = runner.invoke(app, [
            "categorize",
            "--threshold", "0.5",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0


# =============================================================================
# Tenants Command Tests
# =============================================================================

class TestTenantsCommand:
    """Tests for the tenants command."""

    def test_tenants_list_empty(self, tmp_path: Path):
        """Test listing tenants when none configured."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "tenants", "list",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "No tenants configured" in result.stdout

    def test_tenants_add(self, tmp_path: Path):
        """Test adding a tenant."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "tenants", "add", "Max Mueller",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Added tenant" in result.stdout

        # Verify config updated
        with open(tmp_path / "config.yaml") as f:
            updated_config = yaml.safe_load(f)
        assert "Max Mueller" in updated_config.get("tenants", [])

    def test_tenants_add_duplicate(self, tmp_path: Path):
        """Test adding duplicate tenant."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
            "tenants": ["Max Mueller"],
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "tenants", "add", "Max Mueller",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "already exists" in result.stdout

    def test_tenants_remove(self, tmp_path: Path):
        """Test removing a tenant."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
            "tenants": ["Max Mueller", "Anna Schmidt"],
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "tenants", "remove", "Max Mueller",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Removed tenant" in result.stdout

        # Verify config updated
        with open(tmp_path / "config.yaml") as f:
            updated_config = yaml.safe_load(f)
        assert "Max Mueller" not in updated_config.get("tenants", [])
        assert "Anna Schmidt" in updated_config.get("tenants", [])

    def test_tenants_remove_not_found(self, tmp_path: Path):
        """Test removing non-existent tenant."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
            "tenants": ["Anna Schmidt"],
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "tenants", "remove", "Max Mueller",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "not found" in result.stdout

    def test_tenants_no_config(self, tmp_path: Path):
        """Test tenants command without config."""
        result = runner.invoke(app, [
            "tenants", "list",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_tenants_add_no_name(self, tmp_path: Path):
        """Test tenants add without name."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "tenants", "add",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 1
        assert "provide a tenant name" in result.stdout

    def test_tenants_list_with_tenants(self, tmp_path: Path):
        """Test listing existing tenants."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
            "tenants": ["Max Mueller", "Anna Schmidt"],
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "tenants", "list",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Max Mueller" in result.stdout
        assert "Anna Schmidt" in result.stdout


# =============================================================================
# Calculate Command Tests
# =============================================================================

class TestCalculateCommand:
    """Tests for the calculate command."""

    def test_calculate_with_transactions(self, tmp_path: Path):
        """Test calculate with categorized transactions."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        transactions = [
            {
                "date": "2024-01-15",
                "amount": "850.00",
                "description": "Miete Januar",
                "category": "rental_income",
                "confidence": 1.0,
            },
            {
                "date": "2024-01-20",
                "amount": "-100.00",
                "description": "Reparatur",
                "category": "rental_expense",
                "confidence": 1.0,
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        result = runner.invoke(app, [
            "calculate",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Tax Calculation" in result.stdout


# =============================================================================
# Export Command Tests
# =============================================================================

class TestExportCommand:
    """Tests for the export command."""

    def test_export_xlsx(self, tmp_path: Path):
        """Test export to XLSX format."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        transactions = [
            {
                "date": "2024-01-15",
                "amount": "850.00",
                "description": "Miete Januar",
                "category": "rental_income",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        result = runner.invoke(app, [
            "export",
            "--format", "xlsx",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Exported" in result.stdout

    def test_export_csv(self, tmp_path: Path):
        """Test export to CSV format."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        transactions = [
            {
                "date": "2024-01-15",
                "amount": "850.00",
                "description": "Miete Januar",
                "category": "rental_income",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        result = runner.invoke(app, [
            "export",
            "-f", "csv",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Exported" in result.stdout

    def test_export_custom_output(self, tmp_path: Path):
        """Test export with custom output path."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        transactions = [
            {
                "date": "2024-01-15",
                "amount": "850.00",
                "description": "Miete Januar",
                "category": "rental_income",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        output_dir = tmp_path / "custom_export"

        result = runner.invoke(app, [
            "export",
            "--output", str(output_dir),
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert output_dir.exists()


# =============================================================================
# Status Command Tests
# =============================================================================

class TestStatusCommand:
    """Tests for the status command."""

    def test_status_no_project(self, tmp_path: Path):
        """Test status without project."""
        result = runner.invoke(app, [
            "status",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 1
        assert "No PACMAN project found" in result.stdout

    def test_status_with_config_only(self, tmp_path: Path):
        """Test status with config but no transactions."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        result = runner.invoke(app, [
            "status",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Project Status" in result.stdout
        assert "vermieter" in result.stdout
        assert "2024" in result.stdout
        assert "No transactions imported" in result.stdout

    def test_status_with_transactions(self, tmp_path: Path):
        """Test status with transactions."""
        config = {
            "version": "1.0",
            "jurisdiction": "DE",
            "profile": "vermieter",
            "year": 2024,
            "tenants": ["Max Mueller"],
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        transactions = [
            {
                "date": "2024-01-15",
                "amount": "850.00",
                "description": "Miete Januar",
                "category": "rental_income",
            },
            {
                "date": "2024-01-20",
                "amount": "-100.00",
                "description": "Reparatur",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        result = runner.invoke(app, [
            "status",
            "--project", str(tmp_path),
        ])

        assert result.exit_code == 0
        assert "Transactions: 2" in result.stdout
        assert "Categorized:" in result.stdout
        assert "Tenants: 1" in result.stdout


# =============================================================================
# Edge Cases & Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_profile(self, tmp_path: Path):
        """Test init with invalid profile shows error and exits."""
        result = runner.invoke(app, [
            "init",
            "--profile", "invalid_profile",
            "--year", "2024",
            "--path", str(tmp_path / "project"),
        ])
        # Profile validation catches invalid profiles at init time (M5 fix)
        assert result.exit_code == 1
        assert "invalid profile" in result.output.lower() or "not supported" in result.output.lower()

    def test_invalid_year_type(self):
        """Test init with invalid year type."""
        result = runner.invoke(app, [
            "init",
            "--profile", "vermieter",
            "--year", "not_a_year",
        ])
        assert result.exit_code != 0

    def test_nonexistent_import_path(self):
        """Test import with non-existent path."""
        result = runner.invoke(app, [
            "import", "/nonexistent/path/file.csv",
        ])
        assert result.exit_code != 0

    def test_command_subcommand_help(self):
        """Test help for specific commands."""
        commands = ["init", "import", "categorize", "tenants", "calculate", "export", "status"]

        for cmd in commands:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0
            assert cmd in result.stdout.lower() or "Usage" in result.stdout


# =============================================================================
# Integration Tests
# =============================================================================

class TestCLIWorkflow:
    """Integration tests for complete CLI workflows."""

    def test_full_workflow(self, tmp_path: Path):
        """Test complete workflow: init -> import -> categorize -> status."""
        project_dir = tmp_path / "full_workflow"

        # 1. Init
        result = runner.invoke(app, [
            "init",
            "--profile", "vermieter",
            "--year", "2024",
            "--path", str(project_dir),
        ])
        assert result.exit_code == 0

        # 2. Add tenant
        result = runner.invoke(app, [
            "tenants", "add", "Max Mueller",
            "--project", str(project_dir),
        ])
        assert result.exit_code == 0

        # 3. Create import file (Deutsche Bank format)
        csv_content = """Buchungstag;Wert;Verwendungszweck;Soll;Haben;IBAN;Beguenstigter
05.01.2024;05.01.2024;Miete Januar Mueller;;850,00;DE89370400440532013000;Max Mueller
15.02.2024;15.02.2024;Miete Februar Mueller;;850,00;DE89370400440532013000;Max Mueller
20.01.2024;20.01.2024;Hausgeld Januar;150,00;;DE44100100100000123456;WEG Musterhaus
"""
        csv_file = project_dir / "import" / "bank.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        # 4. Import
        result = runner.invoke(app, [
            "import", str(csv_file),
            "--bank", "deutsche-bank",
            "--project", str(project_dir),
        ])
        assert result.exit_code == 0
        assert "Imported" in result.stdout

        # 5. Categorize
        result = runner.invoke(app, [
            "categorize",
            "--project", str(project_dir),
        ])
        assert result.exit_code == 0

        # 6. Status
        result = runner.invoke(app, [
            "status",
            "--project", str(project_dir),
        ])
        assert result.exit_code == 0
        assert "Transactions: 3" in result.stdout
