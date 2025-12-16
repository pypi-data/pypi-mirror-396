"""
Generic CSV Importer.

A flexible importer that works with various CSV formats.
Users can configure column mappings.
"""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd

from pacman.core.models import Transaction
from pacman.importers.base import BaseImporter


class GenericCSVImporter(BaseImporter):
    """
    Generic CSV importer with configurable column mapping.

    Use this when there's no specific importer for your bank.
    """

    def __init__(
        self,
        date_column: str | None = None,
        amount_column: str | None = None,
        debit_column: str | None = None,
        credit_column: str | None = None,
        description_column: str | None = None,
        counterparty_column: str | None = None,
        date_format: str = "%d.%m.%Y",
        encoding: str = "utf-8",
        separator: str | None = None,
    ):
        """
        Initialize generic CSV importer.

        Args:
            date_column: Name of the date column
            amount_column: Name of the amount column (signed)
            debit_column: Name of the debit column (if separate from credit)
            credit_column: Name of the credit column (if separate from debit)
            description_column: Name of the description column
            counterparty_column: Name of the counterparty column (optional)
            date_format: strftime format for parsing dates
            encoding: File encoding
            separator: CSV separator (auto-detect if None)
        """
        self.date_column = date_column
        self.amount_column = amount_column
        self.debit_column = debit_column
        self.credit_column = credit_column
        self.description_column = description_column
        self.counterparty_column = counterparty_column
        self.date_format = date_format
        self.encoding = encoding
        self.separator = separator

    @property
    def bank_name(self) -> str:
        return "Generic CSV"

    @property
    def bank_code(self) -> str:
        return "generic"

    def can_parse(self, file_path: Path) -> bool:
        """Generic importer can parse any CSV file."""
        return file_path.suffix.lower() == ".csv" and file_path.exists()

    def parse(self, file_path: Path) -> list[Transaction]:
        """Parse CSV file."""
        df = pd.read_csv(
            file_path,
            encoding=self.encoding,
            sep=self.separator if self.separator else None,
            engine="python" if self.separator is None else None,
        )

        transactions = []

        for _, row in df.iterrows():
            try:
                txn = self._row_to_transaction(row)
                if txn:
                    transactions.append(txn)
            except Exception:
                continue

        return transactions

    def _row_to_transaction(self, row: pd.Series) -> Transaction | None:
        """Convert a row to a Transaction."""
        # Parse date
        txn_date = self._parse_date(row)
        if txn_date is None:
            return None

        # Parse amount
        amount = self._parse_amount(row)
        if amount is None:
            return None

        # Get description
        description = ""
        if self.description_column and self.description_column in row:
            description = str(row[self.description_column])

        # Get counterparty
        counterparty = None
        if self.counterparty_column and self.counterparty_column in row:
            cp = row[self.counterparty_column]
            if not pd.isna(cp):
                counterparty = str(cp)

        return Transaction(
            date=txn_date,
            amount=amount,
            description=description,
            counterparty=counterparty,
        )

    def _parse_date(self, row: pd.Series) -> date | None:
        """Parse date from row."""
        if not self.date_column or self.date_column not in row:
            return None

        value = row[self.date_column]
        if pd.isna(value):
            return None

        if isinstance(value, (datetime, pd.Timestamp)):
            return value.date()

        try:
            return datetime.strptime(str(value), self.date_format).date()
        except ValueError:
            return None

    def _parse_amount(self, row: pd.Series) -> Decimal | None:
        """Parse amount from row."""
        # Single amount column
        if self.amount_column and self.amount_column in row:
            value = row[self.amount_column]
            if not pd.isna(value):
                return self._to_decimal(value)

        # Separate debit/credit columns
        amount = Decimal("0")

        if self.debit_column and self.debit_column in row:
            value = row[self.debit_column]
            if not pd.isna(value):
                debit = self._to_decimal(value)
                if debit:
                    amount -= abs(debit)

        if self.credit_column and self.credit_column in row:
            value = row[self.credit_column]
            if not pd.isna(value):
                credit = self._to_decimal(value)
                if credit:
                    amount += abs(credit)

        return amount if amount != Decimal("0") else None

    def _to_decimal(self, value: Any) -> Decimal | None:
        """Convert value to Decimal."""
        if pd.isna(value):
            return None

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        str_value = str(value).strip()
        # Handle German format
        str_value = str_value.replace(".", "").replace(",", ".")
        str_value = str_value.replace("€", "").replace("$", "").strip()

        try:
            return Decimal(str_value)
        except Exception:
            return None
