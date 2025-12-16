"""
End-to-End Tests for PACMAN.

Tests the complete workflow from import to export.
"""

import csv
import json
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from pacman.core.categorizer import Categorizer
from pacman.core.models import PacmanConfig, TaxCategory, TaxYear, Transaction
from pacman.importers.generic_csv import GenericCSVImporter
from pacman.jurisdictions.germany import GermanyPlugin


class TestE2EFreiberuflerWorkflow:
    """End-to-end test for Freiberufler (freelancer) workflow."""

    @pytest.fixture
    def project_dir(self, tmp_path):
        """Create a test project directory."""
        project = tmp_path / "steuer-2024"
        project.mkdir()
        (project / "import").mkdir()
        (project / "export").mkdir()
        return project

    @pytest.fixture
    def sample_transactions_csv(self, project_dir):
        """Create sample bank transactions CSV."""
        csv_path = project_dir / "import" / "umsaetze.csv"

        transactions = [
            # Income
            ("2024-01-15", "5000.00", "Kunde ABC GmbH", "Rechnung 2024-001"),
            ("2024-02-15", "5000.00", "Kunde ABC GmbH", "Rechnung 2024-002"),
            ("2024-03-15", "3500.00", "Kunde XYZ AG", "Beratung Maerz"),
            # Expenses
            ("2024-01-10", "-39.99", "Adobe Systems", "Creative Cloud Abo"),
            ("2024-02-10", "-39.99", "Adobe Systems", "Creative Cloud Abo"),
            ("2024-03-05", "-150.00", "Steuerberater Meier", "Beratung Q1"),
            ("2024-01-20", "-89.00", "Deutsche Bahn", "Dienstreise Muenchen"),
            # Private
            ("2024-01-25", "-50.00", "REWE", "Lebensmittel"),
        ]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Datum", "Betrag", "Empfaenger", "Verwendungszweck"])
            for txn in transactions:
                writer.writerow(txn)

        return csv_path

    @pytest.fixture
    def config(self, project_dir):
        """Create project config."""
        config = PacmanConfig(
            year=2024,
            jurisdiction="DE",
            profile="freiberufler",
            name="Max Mustermann",
            business_name="Max Mustermann IT-Beratung",
            business_type="IT-Dienstleistungen",
        )

        config_path = project_dir / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.model_dump(), f, allow_unicode=True)

        return config

    def test_complete_workflow(self, project_dir, sample_transactions_csv, config):
        """Test complete Freiberufler workflow: import -> categorize -> calculate -> export."""
        plugin = GermanyPlugin()

        # Step 1: Import transactions
        importer = GenericCSVImporter(
            date_column="Datum",
            amount_column="Betrag",
            counterparty_column="Empfaenger",
            description_column="Verwendungszweck",
            separator=";",
            date_format="%Y-%m-%d",
        )

        transactions = importer.parse(sample_transactions_csv)

        assert len(transactions) == 8
        assert all(isinstance(t, Transaction) for t in transactions)

        # Step 2: Create TaxYear and add transactions
        tax_year = TaxYear(year=2024, profile="freiberufler")
        for txn in transactions:
            tax_year.add_transaction(txn)

        assert len(tax_year.transactions) == 8
        assert tax_year.categorization_progress == 0.0  # Nothing categorized yet

        # Step 3: Load rules and categorize
        rules = plugin.get_rules("freiberufler")
        assert len(rules) > 0

        categorizer = Categorizer(rules=rules)

        categorized = []
        for txn in tax_year.transactions:
            cat_txn = categorizer.categorize(txn)
            categorized.append(cat_txn)

        # Update transactions
        tax_year.transactions = categorized

        # Check categorization
        categorized_count = sum(1 for t in tax_year.transactions if t.is_categorized)
        assert categorized_count > 0, "At least some transactions should be categorized"

        # Step 4: Calculate aggregates
        tax_year.calculate_aggregates()

        # Should have some business income (from client payments)
        assert tax_year.income_business > 0, "Should have business income"

        # Step 5: Calculate tax
        result = plugin.calculate(tax_year)

        # Should generate Anlage S for Freiberufler
        assert "Anlage_S" in result.forms

        # Income should be recorded
        assert result.income_total > 0

        # Step 6: Export
        export_path = project_dir / "export"
        xlsx_path = plugin.export(tax_year, "xlsx", export_path)

        assert xlsx_path.exists()
        assert xlsx_path.suffix == ".xlsx"

        # Also test CSV export
        csv_export = plugin.export(tax_year, "csv", export_path)
        assert csv_export.exists()


class TestE2EVermieterWorkflow:
    """End-to-end test for Vermieter (landlord) workflow."""

    @pytest.fixture
    def project_dir(self, tmp_path):
        """Create a test project directory."""
        project = tmp_path / "vermietung-2024"
        project.mkdir()
        return project

    def test_complete_rental_workflow(self, project_dir):
        """Test complete rental property workflow."""
        plugin = GermanyPlugin()

        # Create config with tenants
        config = PacmanConfig(
            year=2024,
            jurisdiction="DE",
            profile="vermieter",
            tenants=["Mieter A", "Mieter B"],
        )

        # Create transactions
        tax_year = TaxYear(year=2024, profile="vermieter")

        # Rental income - 12 months
        for month in range(1, 13):
            # Tenant A pays 800 EUR
            tax_year.add_transaction(Transaction(
                date=date(2024, month, 1),
                amount=Decimal("800.00"),
                description=f"Miete {month:02d}/2024",
                counterparty="Mieter A",
                category=TaxCategory.RENTAL_INCOME,
                subcategory="miete",
            ))

            # Tenant B pays 650 EUR
            tax_year.add_transaction(Transaction(
                date=date(2024, month, 1),
                amount=Decimal("650.00"),
                description=f"Miete {month:02d}/2024",
                counterparty="Mieter B",
                category=TaxCategory.RENTAL_INCOME,
                subcategory="miete",
            ))

        # Rental expenses
        # Hausverwaltung
        tax_year.add_transaction(Transaction(
            date=date(2024, 3, 15),
            amount=Decimal("-600.00"),
            description="Hausverwaltung Q1",
            counterparty="HV GmbH",
            category=TaxCategory.RENTAL_EXPENSE,
            subcategory="hausverwaltung",
        ))

        # Versicherung
        tax_year.add_transaction(Transaction(
            date=date(2024, 1, 15),
            amount=Decimal("-480.00"),
            description="Gebaeudeversicherung 2024",
            counterparty="Allianz",
            category=TaxCategory.RENTAL_EXPENSE,
            subcategory="versicherung",
        ))

        # Reparatur
        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 20),
            amount=Decimal("-850.00"),
            description="Heizungsreparatur",
            counterparty="Heizung Meister",
            category=TaxCategory.RENTAL_EXPENSE,
            subcategory="reparatur",
        ))

        # Calculate
        tax_year.calculate_aggregates()

        # Verify
        expected_income = Decimal("800.00") * 12 + Decimal("650.00") * 12  # 17400
        expected_expenses = Decimal("600.00") + Decimal("480.00") + Decimal("850.00")  # 1930

        assert tax_year.income_rental == expected_income
        assert tax_year.expenses_rental == expected_expenses

        # Calculate tax
        result = plugin.calculate(tax_year)

        # Should have Anlage V
        assert "Anlage_V" in result.forms

        anlage_v = result.forms["Anlage_V"]
        assert Decimal(anlage_v["rohertrag"]) == expected_income
        assert Decimal(anlage_v["werbungskosten"]) == expected_expenses


class TestE2EGmbHGFWorkflow:
    """End-to-end test for GmbH-Geschaeftsfuehrer workflow."""

    def test_complete_gmbh_gf_workflow(self, tmp_path):
        """Test GmbH-GF with salary, dividend, and rental."""
        plugin = GermanyPlugin()

        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Monthly salary (12 x 8000 = 96000)
        for month in range(1, 13):
            tax_year.add_transaction(Transaction(
                date=date(2024, month, 28),
                amount=Decimal("8000.00"),
                description=f"GF-Gehalt {month:02d}/2024",
                counterparty="Meine GmbH",
                category=TaxCategory.EMPLOYMENT_INCOME,
                subcategory="gf_gehalt",
            ))

        # Bonus
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 20),
            amount=Decimal("12000.00"),
            description="Tantieme 2024",
            counterparty="Meine GmbH",
            category=TaxCategory.EMPLOYMENT_INCOME,
            subcategory="gf_bonus",
        ))

        # Dividend
        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 30),
            amount=Decimal("25000.00"),
            description="Gewinnausschuettung",
            counterparty="Meine GmbH",
            category=TaxCategory.CAPITAL_INCOME,
            subcategory="dividende",
        ))

        # Werbungskosten
        tax_year.add_transaction(Transaction(
            date=date(2024, 9, 15),
            amount=Decimal("-2500.00"),
            description="MBA Fortbildung",
            counterparty="Business School",
            category=TaxCategory.EMPLOYMENT_EXPENSE,
            subcategory="fortbildung",
        ))

        # Calculate
        tax_year.calculate_aggregates()

        # Verify income
        assert tax_year.income_employment == Decimal("108000.00")  # 96000 + 12000
        assert tax_year.income_capital == Decimal("25000.00")
        assert tax_year.expenses_employment == Decimal("2500.00")

        # Calculate tax
        result = plugin.calculate(tax_year)

        # Should have Anlage N and KAP
        assert "Anlage_N" in result.forms
        assert "Anlage_KAP" in result.forms

        # Anlage N: 108000 - 2500 = 105500
        anlage_n = result.forms["Anlage_N"]
        assert Decimal(anlage_n["bruttoarbeitslohn"]) == Decimal("108000.00")
        assert Decimal(anlage_n["einkuenfte"]) == Decimal("105500.00")

        # Anlage KAP: 25000 - 1000 = 24000
        anlage_kap = result.forms["Anlage_KAP"]
        assert Decimal(anlage_kap["einkuenfte_nach_abzug"]) == Decimal("24000.00")

        # Total income
        # Employment: 105500 + Capital: 24000 = 129500
        assert result.income_total == Decimal("129500.00")


class TestE2EDataPersistence:
    """Tests for saving and loading project data."""

    def test_save_and_load_transactions(self, tmp_path):
        """Test transactions can be saved and loaded."""
        project = tmp_path / "test-project"
        project.mkdir()

        # Create transactions
        transactions = [
            Transaction(
                date=date(2024, 1, 15),
                amount=Decimal("1000.00"),
                description="Test Income",
                category=TaxCategory.BUSINESS_INCOME,
            ),
            Transaction(
                date=date(2024, 1, 20),
                amount=Decimal("-100.00"),
                description="Test Expense",
                category=TaxCategory.BUSINESS_EXPENSE,
            ),
        ]

        # Save
        txn_path = project / "transactions.json"
        with open(txn_path, "w", encoding="utf-8") as f:
            json.dump(
                [t.model_dump(mode="json") for t in transactions],
                f,
                indent=2,
                default=str,
            )

        # Load
        with open(txn_path, encoding="utf-8") as f:
            loaded_data = json.load(f)

        loaded_transactions = [Transaction(**t) for t in loaded_data]

        assert len(loaded_transactions) == 2
        assert loaded_transactions[0].amount == Decimal("1000.00")
        assert loaded_transactions[1].category == TaxCategory.BUSINESS_EXPENSE

    def test_save_and_load_config(self, tmp_path):
        """Test config can be saved and loaded."""
        project = tmp_path / "test-project"
        project.mkdir()

        # Create config
        config = PacmanConfig(
            year=2024,
            jurisdiction="DE",
            profile="freiberufler",
            name="Test User",
        )

        # Save
        config_path = project / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.model_dump(), f, allow_unicode=True)

        # Load
        with open(config_path, encoding="utf-8") as f:
            loaded_data = yaml.safe_load(f)

        loaded_config = PacmanConfig(**loaded_data)

        assert loaded_config.year == 2024
        assert loaded_config.profile == "freiberufler"
        assert loaded_config.name == "Test User"
