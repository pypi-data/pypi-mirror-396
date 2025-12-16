"""
Tests for PACMAN Core Models.

Tests Transaction, TaxYear, and PacmanConfig models.
"""

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given, strategies as st

from pacman.core.models import (
    PacmanConfig,
    TaxCategory,
    TaxYear,
    Transaction,
    TransactionSplit,
)


class TestTransaction:
    """Tests for Transaction model."""

    def test_create_simple_transaction(self):
        """Test creating a basic transaction."""
        txn = Transaction(
            date=date(2024, 1, 15),
            amount=Decimal("100.00"),
            description="Test payment",
        )
        assert txn.date == date(2024, 1, 15)
        assert txn.amount == Decimal("100.00")
        assert txn.description == "Test payment"
        assert txn.category == TaxCategory.UNCATEGORIZED
        assert txn.id  # Auto-generated

    def test_transaction_id_generation(self):
        """Test that transaction IDs are generated consistently."""
        txn1 = Transaction(
            date=date(2024, 1, 15),
            amount=Decimal("100.00"),
            description="Test",
        )
        txn2 = Transaction(
            date=date(2024, 1, 15),
            amount=Decimal("100.00"),
            description="Test",
        )
        # Same data should generate same ID
        assert txn1.id == txn2.id

    def test_transaction_id_unique_for_different_data(self):
        """Test that different transactions get different IDs."""
        txn1 = Transaction(
            date=date(2024, 1, 15),
            amount=Decimal("100.00"),
            description="Test A",
        )
        txn2 = Transaction(
            date=date(2024, 1, 15),
            amount=Decimal("100.00"),
            description="Test B",
        )
        assert txn1.id != txn2.id

    def test_is_income(self, sample_income_transaction: Transaction):
        """Test income detection."""
        assert sample_income_transaction.is_income is True
        assert sample_income_transaction.is_expense is False

    def test_is_expense(self, sample_expense_transaction: Transaction):
        """Test expense detection."""
        assert sample_expense_transaction.is_income is False
        assert sample_expense_transaction.is_expense is True

    def test_is_categorized(self):
        """Test categorization status detection."""
        uncategorized = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("50"),
            description="Test",
        )
        assert uncategorized.is_categorized is False

        categorized = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("50"),
            description="Test",
            category=TaxCategory.RENTAL_INCOME,
        )
        assert categorized.is_categorized is True

    def test_amount_parsing_german_format(self):
        """Test German number format parsing (1.234,56)."""
        txn = Transaction(
            date=date(2024, 1, 1),
            amount="1.234,56",  # type: ignore
            description="Test",
        )
        assert txn.amount == Decimal("1234.56")

    def test_amount_parsing_standard_format(self):
        """Test standard number format parsing (1234.56)."""
        txn = Transaction(
            date=date(2024, 1, 1),
            amount="1234.56",  # type: ignore
            description="Test",
        )
        assert txn.amount == Decimal("1234.56")

    def test_amount_parsing_negative(self):
        """Test negative amount parsing."""
        txn = Transaction(
            date=date(2024, 1, 1),
            amount="-500,00",  # type: ignore
            description="Test",
        )
        assert txn.amount == Decimal("-500.00")

    @given(amount=st.decimals(
        min_value=Decimal("-1000000"),
        max_value=Decimal("1000000"),
        allow_nan=False,
        allow_infinity=False,
    ))
    def test_amount_roundtrip(self, amount: Decimal):
        """Property test: Decimal amounts should roundtrip correctly."""
        # Quantize to avoid precision issues
        amount = amount.quantize(Decimal("0.01"))
        txn = Transaction(
            date=date(2024, 1, 1),
            amount=amount,
            description="Test",
        )
        assert txn.amount == amount


class TestTransactionSplit:
    """Tests for TransactionSplit model."""

    def test_create_split(self):
        """Test creating a transaction split."""
        split = TransactionSplit(
            category=TaxCategory.RENTAL_EXPENSE,
            percentage=Decimal("80"),
        )
        assert split.category == TaxCategory.RENTAL_EXPENSE
        assert split.percentage == Decimal("80")

    def test_split_percentage_validation(self):
        """Test that percentage must be 0-100."""
        with pytest.raises(ValueError):
            TransactionSplit(
                category=TaxCategory.RENTAL_EXPENSE,
                percentage=Decimal("150"),
            )

    def test_get_split_amounts(self, split_transaction: Transaction):
        """Test calculating split amounts."""
        amounts = split_transaction.get_split_amounts()

        # Total should be 500 (abs of -500)
        total = sum(amounts.values())
        assert total == Decimal("500.00")

        # 80% rental, 20% business
        assert TaxCategory.RENTAL_EXPENSE in amounts
        assert TaxCategory.BUSINESS_EXPENSE in amounts


class TestTaxYear:
    """Tests for TaxYear model."""

    def test_create_empty_tax_year(self, empty_tax_year: TaxYear):
        """Test creating an empty tax year."""
        assert empty_tax_year.year == 2024
        assert empty_tax_year.jurisdiction == "DE"
        assert empty_tax_year.profile == "vermieter"
        assert len(empty_tax_year.transactions) == 0

    def test_add_transaction(self, empty_tax_year: TaxYear):
        """Test adding a transaction."""
        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("100"),
            description="Test",
        )
        empty_tax_year.add_transaction(txn)
        assert len(empty_tax_year.transactions) == 1

    def test_get_transactions_by_category(self, sample_tax_year: TaxYear):
        """Test filtering transactions by category."""
        rental_income = sample_tax_year.get_transactions_by_category(
            TaxCategory.RENTAL_INCOME
        )
        assert len(rental_income) == 1
        assert rental_income[0].amount == Decimal("850.00")

    def test_get_uncategorized(self, sample_tax_year: TaxYear):
        """Test getting uncategorized transactions."""
        # All sample transactions are categorized
        uncategorized = sample_tax_year.get_uncategorized()
        assert len(uncategorized) == 0

    def test_calculate_aggregates(self, sample_tax_year: TaxYear):
        """Test aggregate calculation."""
        sample_tax_year.calculate_aggregates()

        # Rental income: 850
        assert sample_tax_year.income_rental == Decimal("850.00")

        # Rental expenses: 89.99 + 1200 = 1289.99
        assert sample_tax_year.expenses_rental == Decimal("1289.99")

    def test_net_rental_income(self, sample_tax_year: TaxYear):
        """Test net rental income calculation."""
        sample_tax_year.calculate_aggregates()

        # 850 - 1289.99 = -439.99 (loss)
        assert sample_tax_year.net_rental_income == Decimal("-439.99")

    def test_categorization_progress(self, sample_tax_year: TaxYear):
        """Test categorization progress calculation."""
        progress = sample_tax_year.categorization_progress
        # All 4 transactions are categorized
        assert progress == 100.0

    def test_categorization_progress_empty(self, empty_tax_year: TaxYear):
        """Test categorization progress with no transactions."""
        assert empty_tax_year.categorization_progress == 0.0


class TestPacmanConfig:
    """Tests for PacmanConfig model."""

    def test_create_vermieter_config(self, vermieter_config: PacmanConfig):
        """Test creating a Vermieter config."""
        assert vermieter_config.profile == "vermieter"
        assert vermieter_config.year == 2024
        assert len(vermieter_config.tenants) == 2

    def test_create_einzelunternehmer_config(
        self, einzelunternehmer_config: PacmanConfig
    ):
        """Test creating an Einzelunternehmer config."""
        assert einzelunternehmer_config.profile == "einzelunternehmer"
        assert einzelunternehmer_config.business_name == "Musterfirma"

    def test_get_import_path(self, vermieter_config: PacmanConfig, tmp_path):
        """Test import path resolution."""
        import_path = vermieter_config.get_import_path(tmp_path)
        assert import_path == (tmp_path / "import").resolve()

    def test_get_export_path(self, vermieter_config: PacmanConfig, tmp_path):
        """Test export path resolution."""
        export_path = vermieter_config.get_export_path(tmp_path)
        assert export_path == (tmp_path / "export").resolve()

    def test_default_values(self):
        """Test default configuration values."""
        config = PacmanConfig(year=2024)
        assert config.version == "1.0"
        assert config.jurisdiction == "DE"
        assert config.profile == "vermieter"
        assert config.auto_categorize is True
        assert config.confidence_threshold == 0.8
