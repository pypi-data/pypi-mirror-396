"""
PACMAN Core Models

Pydantic models for transactions, tax years, and configuration.
These are jurisdiction-agnostic and form the foundation of PACMAN.
"""

from __future__ import annotations

import hashlib
from datetime import date
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class TaxCategory(str, Enum):
    """
    Universal tax categories (jurisdiction-agnostic).

    These categories map to specific tax forms in each jurisdiction:
    - DE: Anlage V (rental), Anlage G/EÜR (business), Anlage N (employment), etc.
    - AT: E1/E1a forms
    - CH: Canton-specific forms
    """

    # Vermietung & Verpachtung (Anlage V)
    RENTAL_INCOME = "rental_income"
    RENTAL_EXPENSE = "rental_expense"

    # Selbständige / Gewerbe (Anlage S/G, EÜR)
    BUSINESS_INCOME = "business_income"
    BUSINESS_EXPENSE = "business_expense"

    # Nichtselbständige Arbeit (Anlage N)
    EMPLOYMENT_INCOME = "employment_income"
    EMPLOYMENT_EXPENSE = "employment_expense"

    # Kapitalerträge (Anlage KAP)
    CAPITAL_INCOME = "capital_income"

    # Allgemein
    DEDUCTIBLE = "deductible"  # Sonderausgaben, Vorsorgeaufwand
    PRIVATE = "private"
    PASSTHROUGH = "passthrough"  # Durchlaufposten (e.g., rent collected and forwarded)
    UNCATEGORIZED = "uncategorized"


class TransactionSplit(BaseModel):
    """
    For splitting a transaction across multiple categories.

    Example: Steuerberater costs split 80% Vermietung / 20% Gewerbe
    """

    category: TaxCategory
    subcategory: str | None = None
    percentage: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    amount: Decimal | None = None  # Calculated from percentage if not provided

    @field_validator("percentage", mode="before")
    @classmethod
    def coerce_percentage(cls, v: Any) -> Decimal:
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class Transaction(BaseModel):
    """
    Single financial transaction.

    Represents one line from a bank statement with categorization metadata.
    """

    # Core fields
    id: str = Field(
        default="",
        description="Unique identifier (hash of date+amount+desc)",
    )
    date: date
    amount: Decimal = Field(
        description="Transaction amount. Positive=income, Negative=expense",
    )
    description: str
    counterparty: str | None = None
    iban: str | None = Field(
        default=None,
        description="Counterparty IBAN (validated format)",
    )

    # Categorization
    category: TaxCategory = TaxCategory.UNCATEGORIZED
    subcategory: str | None = None  # e.g., "steuerberater", "dropscan", "mieter_dineva"

    # Metadata
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Categorization confidence (0-1). Higher = more certain.",
    )
    rule_matched: str | None = Field(
        default=None,
        description="ID of the rule that categorized this transaction",
    )
    manual_override: bool = Field(
        default=False,
        description="True if user manually set the category",
    )
    notes: str | None = None

    # Split transactions
    splits: list[TransactionSplit] | None = None

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v: Any) -> Decimal:
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        if isinstance(v, str):
            v = v.strip()
            # Detect format: German uses comma as decimal separator
            # German: "1.234,56" or "1234,56" (comma = decimal)
            # Standard: "1234.56" (dot = decimal)
            if "," in v:
                # German format: 1.234,56 -> 1234.56
                v = v.replace(".", "").replace(",", ".")
            # Standard format with dot - no conversion needed
            return Decimal(v)
        return v

    @field_validator("iban", mode="before")
    @classmethod
    def validate_iban(cls, v: Any) -> str | None:
        """Validate and normalize IBAN format."""
        if v is None or (isinstance(v, str) and not v.strip()):
            return None

        # Normalize: remove spaces and convert to uppercase
        iban = str(v).replace(" ", "").upper().strip()

        # Basic format validation (don't reject, just return None for invalid)
        if len(iban) < 15 or len(iban) > 34:
            return None  # Invalid length, skip silently

        # First 2 chars must be letters (country code)
        if not iban[:2].isalpha():
            return None

        # Chars 3-4 must be digits (check digits)
        if not iban[2:4].isdigit():
            return None

        # Rest must be alphanumeric
        if not iban[4:].isalnum():
            return None

        return iban

    @model_validator(mode="after")
    def generate_id(self) -> Transaction:
        """Generate unique ID if not provided."""
        if not self.id:
            # Create hash from date, amount, and description
            data = f"{self.date.isoformat()}|{self.amount}|{self.description}"
            self.id = hashlib.sha256(data.encode()).hexdigest()[:12]
        return self

    @property
    def is_income(self) -> bool:
        """True if this is an income transaction."""
        return self.amount > 0

    @property
    def is_expense(self) -> bool:
        """True if this is an expense transaction."""
        return self.amount < 0

    @property
    def is_categorized(self) -> bool:
        """True if transaction has been categorized."""
        return self.category != TaxCategory.UNCATEGORIZED

    def get_split_amounts(self) -> dict[TaxCategory, Decimal]:
        """
        Calculate amounts per category for split transactions.
        Returns {category: amount} dict.
        """
        if not self.splits:
            return {self.category: abs(self.amount)}

        result = {}
        for split in self.splits:
            split_amount = abs(self.amount) * split.percentage / Decimal("100")
            result[split.category] = split_amount
        return result


class TaxYear(BaseModel):
    """
    Complete tax year data.

    Contains all transactions for a year and computed aggregates.
    """

    year: int = Field(ge=2020, le=2030)
    jurisdiction: str = Field(
        default="DE",
        description="Jurisdiction code: 'DE', 'AT', 'CH-ZH', etc.",
    )
    profile: str = Field(
        default="vermieter",
        description="Profile: 'vermieter', 'einzelunternehmer', 'freiberufler'",
    )

    transactions: list[Transaction] = Field(default_factory=list)

    # Computed aggregates (filled by calculator)
    income_rental: Decimal = Decimal("0")
    income_business: Decimal = Decimal("0")
    income_employment: Decimal = Decimal("0")  # Anlage N
    income_capital: Decimal = Decimal("0")  # Anlage KAP
    expenses_rental: Decimal = Decimal("0")
    expenses_business: Decimal = Decimal("0")
    expenses_employment: Decimal = Decimal("0")  # Werbungskosten Anlage N
    deductibles: Decimal = Decimal("0")
    passthrough_in: Decimal = Decimal("0")
    passthrough_out: Decimal = Decimal("0")

    def add_transaction(self, txn: Transaction) -> None:
        """Add a transaction to this tax year."""
        self.transactions.append(txn)

    def get_transactions_by_category(
        self, category: TaxCategory
    ) -> list[Transaction]:
        """Get all transactions with a specific category."""
        return [t for t in self.transactions if t.category == category]

    def get_uncategorized(self) -> list[Transaction]:
        """Get all uncategorized transactions."""
        return self.get_transactions_by_category(TaxCategory.UNCATEGORIZED)

    def calculate_aggregates(self) -> None:
        """
        Calculate aggregate values from transactions.
        Should be called after categorization is complete.
        """
        self.income_rental = Decimal("0")
        self.income_business = Decimal("0")
        self.income_employment = Decimal("0")
        self.income_capital = Decimal("0")
        self.expenses_rental = Decimal("0")
        self.expenses_business = Decimal("0")
        self.expenses_employment = Decimal("0")
        self.deductibles = Decimal("0")
        self.passthrough_in = Decimal("0")
        self.passthrough_out = Decimal("0")

        for txn in self.transactions:
            amounts = txn.get_split_amounts()

            for cat, amount in amounts.items():
                if cat == TaxCategory.RENTAL_INCOME:
                    self.income_rental += amount
                elif cat == TaxCategory.RENTAL_EXPENSE:
                    self.expenses_rental += amount
                elif cat == TaxCategory.BUSINESS_INCOME:
                    self.income_business += amount
                elif cat == TaxCategory.BUSINESS_EXPENSE:
                    self.expenses_business += amount
                elif cat == TaxCategory.EMPLOYMENT_INCOME:
                    self.income_employment += amount
                elif cat == TaxCategory.EMPLOYMENT_EXPENSE:
                    self.expenses_employment += amount
                elif cat == TaxCategory.CAPITAL_INCOME:
                    self.income_capital += amount
                elif cat == TaxCategory.DEDUCTIBLE:
                    self.deductibles += amount
                elif cat == TaxCategory.PASSTHROUGH:
                    if txn.is_income:
                        self.passthrough_in += amount
                    else:
                        self.passthrough_out += amount

    @property
    def net_rental_income(self) -> Decimal:
        """Net income from rental (Einkünfte aus V+V)."""
        return self.income_rental - self.expenses_rental

    @property
    def net_business_income(self) -> Decimal:
        """Net income from business (Einkünfte aus Gewerbebetrieb)."""
        return self.income_business - self.expenses_business

    @property
    def net_employment_income(self) -> Decimal:
        """Net income from employment (Einkünfte aus nichtselbständiger Arbeit)."""
        return self.income_employment - self.expenses_employment

    @property
    def net_capital_income(self) -> Decimal:
        """Capital income (Einkünfte aus Kapitalvermögen)."""
        return self.income_capital

    @property
    def total_income(self) -> Decimal:
        """Total taxable income from all sources."""
        return (
            self.net_rental_income
            + self.net_business_income
            + self.net_employment_income
            + self.net_capital_income
        )

    @property
    def categorization_progress(self) -> float:
        """Percentage of transactions that are categorized."""
        if not self.transactions:
            return 0.0
        categorized = sum(1 for t in self.transactions if t.is_categorized)
        return categorized / len(self.transactions) * 100


class PacmanConfig(BaseModel):
    """
    Project configuration for a PACMAN tax project.

    Stored as config.yaml in the project directory.
    """

    version: str = "1.0"
    jurisdiction: str = "DE"
    profile: str = "vermieter"
    year: int

    # User data (optional, for report generation)
    name: str | None = None
    address: str | None = None
    tax_id: str | None = None

    # Profile-specific configuration
    tenants: list[str] = Field(
        default_factory=list,
        description="List of tenant names (for Vermieter profile)",
    )
    landlords: list[str] = Field(
        default_factory=list,
        description="List of landlord names for passthrough detection",
    )

    # Business-specific (for Einzelunternehmer/Freiberufler)
    business_name: str | None = None
    business_type: str | None = None

    # Paths (relative to project directory)
    import_path: str = "./import"
    export_path: str = "./export"
    rules_path: str | None = None  # Custom rules file

    # Categorization settings
    auto_categorize: bool = True
    confidence_threshold: float = 0.8

    def get_import_path(self, project_dir: Path) -> Path:
        """Get absolute import path."""
        return (project_dir / self.import_path).resolve()

    def get_export_path(self, project_dir: Path) -> Path:
        """Get absolute export path."""
        return (project_dir / self.export_path).resolve()
