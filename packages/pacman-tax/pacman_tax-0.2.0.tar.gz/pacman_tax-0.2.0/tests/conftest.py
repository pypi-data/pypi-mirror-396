"""
PACMAN Test Configuration

Shared fixtures and configuration for all tests.

Note: We disable the privacy import hook for tests because test dependencies
(like hypothesis) require network modules. This is acceptable because:
1. Tests run in a controlled environment
2. The privacy hook is tested explicitly in test_privacy.py
3. Production code still has the hook enabled
"""

import sys

# Remove PACMAN's import hook before importing test dependencies
# This allows hypothesis and other test tools to work
_original_meta_path = sys.meta_path.copy()
sys.meta_path = [
    finder for finder in sys.meta_path
    if "PrivacyImportBlocker" not in type(finder).__name__
]

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from pacman.core.models import (
    PacmanConfig,
    TaxCategory,
    TaxYear,
    Transaction,
    TransactionSplit,
)


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture
def fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary PACMAN project directory."""
    project = tmp_path / "test_project"
    project.mkdir()
    (project / "import").mkdir()
    (project / "export").mkdir()
    return project


# =============================================================================
# Transaction Fixtures
# =============================================================================

@pytest.fixture
def sample_income_transaction() -> Transaction:
    """Sample income transaction (rent payment)."""
    return Transaction(
        date=date(2024, 1, 15),
        amount=Decimal("850.00"),
        description="Miete Januar 2024 | Müller | DE89370400440532013000",
        counterparty="Max Müller",
        iban="DE89370400440532013000",
    )


@pytest.fixture
def sample_expense_transaction() -> Transaction:
    """Sample expense transaction (repair costs)."""
    return Transaction(
        date=date(2024, 2, 10),
        amount=Decimal("-245.50"),
        description="Reparatur Heizung | Sanitär Schmidt GmbH",
        counterparty="Sanitär Schmidt GmbH",
    )


@pytest.fixture
def sample_transactions() -> list[Transaction]:
    """List of sample transactions for a month."""
    return [
        Transaction(
            date=date(2024, 1, 5),
            amount=Decimal("850.00"),
            description="Miete Januar | Müller",
            counterparty="Max Müller",
            category=TaxCategory.RENTAL_INCOME,
            subcategory="mieter_mueller",
            confidence=1.0,
        ),
        Transaction(
            date=date(2024, 1, 10),
            amount=Decimal("-89.99"),
            description="Dropscan Abo Januar",
            counterparty="Dropscan GmbH",
            category=TaxCategory.RENTAL_EXPENSE,
            subcategory="dropscan",
            confidence=0.95,
        ),
        Transaction(
            date=date(2024, 1, 15),
            amount=Decimal("-1200.00"),
            description="Hausgeld Januar | WEG Musterstr. 1",
            counterparty="WEG Musterstraße 1",
            category=TaxCategory.RENTAL_EXPENSE,
            subcategory="hausgeld",
            confidence=1.0,
        ),
        Transaction(
            date=date(2024, 1, 20),
            amount=Decimal("-50.00"),
            description="Amazon - Bürobedarf",
            counterparty="Amazon EU S.a.r.l.",
            category=TaxCategory.PRIVATE,
            confidence=0.6,
        ),
    ]


@pytest.fixture
def uncategorized_transaction() -> Transaction:
    """Uncategorized transaction for testing categorizer."""
    return Transaction(
        date=date(2024, 3, 1),
        amount=Decimal("-150.00"),
        description="Unbekannte Zahlung XYZ",
    )


# =============================================================================
# Config Fixtures
# =============================================================================

@pytest.fixture
def vermieter_config() -> PacmanConfig:
    """Sample Vermieter (landlord) configuration."""
    return PacmanConfig(
        version="1.0",
        jurisdiction="DE",
        profile="vermieter",
        year=2024,
        tenants=["Max Müller", "Anna Schmidt"],
        landlords=[],
    )


@pytest.fixture
def einzelunternehmer_config() -> PacmanConfig:
    """Sample Einzelunternehmer (sole proprietor) configuration."""
    return PacmanConfig(
        version="1.0",
        jurisdiction="DE",
        profile="einzelunternehmer",
        year=2024,
        business_name="Musterfirma",
        business_type="IT-Dienstleistungen",
    )


# =============================================================================
# TaxYear Fixtures
# =============================================================================

@pytest.fixture
def sample_tax_year(sample_transactions: list[Transaction]) -> TaxYear:
    """Sample tax year with transactions."""
    return TaxYear(
        year=2024,
        jurisdiction="DE",
        profile="vermieter",
        transactions=sample_transactions,
    )


@pytest.fixture
def empty_tax_year() -> TaxYear:
    """Empty tax year for testing edge cases."""
    return TaxYear(
        year=2024,
        jurisdiction="DE",
        profile="vermieter",
        transactions=[],
    )


# =============================================================================
# Split Transaction Fixtures
# =============================================================================

@pytest.fixture
def split_transaction() -> Transaction:
    """Transaction with split categories (e.g., Steuerberater 80/20)."""
    return Transaction(
        date=date(2024, 4, 15),
        amount=Decimal("-500.00"),
        description="Steuerberater Jahresabschluss",
        counterparty="Steuerkanzlei Mustermann",
        category=TaxCategory.RENTAL_EXPENSE,
        splits=[
            TransactionSplit(
                category=TaxCategory.RENTAL_EXPENSE,
                percentage=Decimal("80"),
            ),
            TransactionSplit(
                category=TaxCategory.BUSINESS_EXPENSE,
                percentage=Decimal("20"),
            ),
        ],
    )
