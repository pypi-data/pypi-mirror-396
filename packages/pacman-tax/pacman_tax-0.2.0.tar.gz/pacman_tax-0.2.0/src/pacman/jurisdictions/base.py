"""
Base class for jurisdiction plugins.

Each country/region implements this interface to provide tax-specific logic.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from pathlib import Path
from typing import Any

from pacman.core.categorizer import CategorizationRule, Categorizer
from pacman.core.models import TaxYear


class TaxResult:
    """
    Result of tax calculation.

    Contains computed values and ELSTER-ready data.
    """

    def __init__(self) -> None:
        self.income_total: Decimal = Decimal("0")
        self.expenses_total: Decimal = Decimal("0")
        self.deductibles_total: Decimal = Decimal("0")
        self.taxable_income: Decimal = Decimal("0")
        self.tax_due: Decimal = Decimal("0")

        # Form-specific data
        self.forms: dict[str, dict[str, Any]] = {}

        # Warnings and notes
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def add_form_data(self, form_name: str, data: dict[str, Any]) -> None:
        """Add data for a specific tax form."""
        self.forms[form_name] = data

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "income_total": str(self.income_total),
            "expenses_total": str(self.expenses_total),
            "deductibles_total": str(self.deductibles_total),
            "taxable_income": str(self.taxable_income),
            "tax_due": str(self.tax_due),
            "forms": self.forms,
            "warnings": self.warnings,
            "notes": self.notes,
        }


class JurisdictionPlugin(ABC):
    """
    Abstract base class for country/region tax plugins.

    Each jurisdiction (DE, AT, CH-ZH, etc.) implements this interface
    to provide:
    - Tax constants (Grundfreibetrag, etc.)
    - Categorization rules
    - Tax calculation logic
    - Export formats (ELSTER, FinanzOnline, etc.)
    """

    @property
    @abstractmethod
    def code(self) -> str:
        """
        ISO code for this jurisdiction.

        Examples: 'DE', 'AT', 'CH-ZH' (canton-specific for Switzerland)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name (e.g., 'Deutschland', 'Österreich')."""
        pass

    @property
    @abstractmethod
    def supported_profiles(self) -> list[str]:
        """
        List of supported tax profiles.

        Examples: ['vermieter', 'einzelunternehmer', 'freiberufler']
        """
        pass

    @abstractmethod
    def get_tax_constants(self, year: int) -> dict[str, Any]:
        """
        Return tax constants for the given year.

        Example return value for Germany 2024:
        {
            "grundfreibetrag": 11604,
            "gewerbe_freibetrag": 24500,
            "euer_grenze_umsatz": 600000,
            "euer_grenze_gewinn": 60000,
        }
        """
        pass

    @abstractmethod
    def get_rules(self, profile: str) -> list[CategorizationRule]:
        """
        Get categorization rules for the given profile.

        Args:
            profile: Profile name (e.g., 'vermieter')

        Returns:
            List of CategorizationRule objects
        """
        pass

    @abstractmethod
    def calculate(self, tax_year: TaxYear) -> TaxResult:
        """
        Calculate taxes for the given tax year.

        Args:
            tax_year: TaxYear with categorized transactions

        Returns:
            TaxResult with computed values and form data
        """
        pass

    @abstractmethod
    def export(self, tax_year: TaxYear, format: str, output_path: Path) -> Path:
        """
        Export tax data to the specified format.

        Args:
            tax_year: TaxYear with categorized transactions
            format: Export format ('xlsx', 'xml', 'csv')
            output_path: Directory or file path for output

        Returns:
            Path to the created file
        """
        pass

    def get_categorizer(self, profile: str) -> Categorizer:
        """
        Get a configured Categorizer for the profile.

        Convenience method that creates a Categorizer with the profile's rules.
        """
        rules = self.get_rules(profile)
        return Categorizer(rules=rules)

    def validate_profile(self, profile: str) -> None:
        """
        Validate that the profile is supported.

        Raises ValueError if not supported.
        """
        if profile not in self.supported_profiles:
            available = ", ".join(self.supported_profiles)
            raise ValueError(
                f"Profile '{profile}' not supported for {self.name}. "
                f"Available profiles: {available}"
            )
