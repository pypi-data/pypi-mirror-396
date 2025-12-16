"""
Base importer class for bank transaction parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from pacman.core.models import Transaction


class BaseImporter(ABC):
    """
    Abstract base class for bank transaction importers.

    Each bank has its own CSV/XLSX format, so we need specific parsers.
    Subclasses implement the actual parsing logic.
    """

    @property
    @abstractmethod
    def bank_name(self) -> str:
        """Human-readable bank name."""
        pass

    @property
    @abstractmethod
    def bank_code(self) -> str:
        """Short code for the bank (e.g., 'deutsche-bank', 'sparkasse')."""
        pass

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this importer can parse the given file.

        Returns True if the file format matches this bank's export format.
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> list[Transaction]:
        """
        Parse a bank export file and return transactions.

        Args:
            file_path: Path to the CSV/XLSX file

        Returns:
            List of Transaction objects
        """
        pass

    def parse_multiple(self, file_paths: list[Path]) -> list[Transaction]:
        """
        Parse multiple files and return all transactions.

        Transactions are sorted by date.
        """
        all_transactions = []
        for path in file_paths:
            if self.can_parse(path):
                transactions = self.parse(path)
                all_transactions.extend(transactions)

        # Sort by date
        all_transactions.sort(key=lambda t: t.date)
        return all_transactions
