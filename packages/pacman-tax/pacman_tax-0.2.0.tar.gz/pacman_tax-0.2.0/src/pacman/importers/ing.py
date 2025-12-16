"""
ING-DiBa CSV Importer.

Parses CSV exports from ING-DiBa online banking.

ING-DiBa CSV format:
- Semicolon separated
- German date format (DD.MM.YYYY)
- German number format (1.234,56)
- Header row with specific column names
- UTF-8 or ISO-8859-1 encoding
"""

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from pacman.core.models import Transaction
from pacman.importers.base import BaseImporter

logger = logging.getLogger(__name__)


class INGImporter(BaseImporter):
    """
    ING-DiBa CSV importer.

    Handles the standard CSV export format from ING-DiBa online banking.
    """

    # Known column names in ING exports
    COLUMNS = {
        "date": ["Buchung", "Buchungstag", "Datum"],
        "valuta": ["Valuta", "Wertstellung"],
        "counterparty": ["Auftraggeber/Empfänger", "Auftraggeber / Empfänger", "Name"],
        "type": ["Buchungstext", "Buchungsart"],
        "description": ["Verwendungszweck", "Beschreibung"],
        "amount": ["Betrag", "Betrag (EUR)"],
        "currency": ["Währung"],
        "saldo": ["Saldo", "Saldo nach Buchung"],
    }

    @property
    def bank_name(self) -> str:
        return "ING-DiBa"

    @property
    def bank_code(self) -> str:
        return "ing"

    def can_parse(self, file_path: Path) -> bool:
        """Check if this is an ING-DiBa CSV file."""
        if not file_path.exists():
            return False

        if file_path.suffix.lower() != ".csv":
            return False

        # Try to read and detect ING format
        try:
            # ING files may have a header section before the actual CSV
            content = self._read_file_content(file_path)

            # Check for ING-specific markers
            if "ING" in content[:500] or "ING-DiBa" in content[:500]:
                return True

            # Check for known column headers
            for encoding in ["utf-8", "iso-8859-1", "cp1252"]:
                try:
                    df = pd.read_csv(
                        file_path,
                        sep=";",
                        encoding=encoding,
                        nrows=1,
                    )
                    columns = [str(c).lower() for c in df.columns]
                    # Check for ING-specific columns
                    if any("auftraggeber" in c for c in columns):
                        return True
                    if any("buchung" in c for c in columns) and any("betrag" in c for c in columns):
                        return True
                except Exception:
                    continue

            return False
        except Exception:
            return False

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with encoding detection."""
        for encoding in ["utf-8", "iso-8859-1", "cp1252"]:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return ""

    def _find_data_start(self, file_path: Path) -> int:
        """Find the row where actual data starts (skip ING header)."""
        for encoding in ["utf-8", "iso-8859-1", "cp1252"]:
            try:
                with open(file_path, encoding=encoding) as f:
                    for i, line in enumerate(f):
                        # Data starts when we see a semicolon-separated line
                        # with date-like content
                        if ";" in line and any(
                            col in line.lower()
                            for cols in self.COLUMNS.values()
                            for col in [c.lower() for c in cols]
                        ):
                            return i
                        # Or if it looks like a data row (starts with date)
                        if line.strip() and line[0].isdigit():
                            parts = line.split(";")
                            if len(parts) >= 5:
                                return i - 1 if i > 0 else 0
            except UnicodeDecodeError:
                continue
        return 0

    def parse(self, file_path: Path) -> list[Transaction]:
        """Parse ING-DiBa CSV file."""
        transactions = []

        # Find where data starts
        skip_rows = self._find_data_start(file_path)

        # Try different encodings
        # Note: Don't use decimal/thousands options as they corrupt date columns
        # _parse_amount handles German number format manually
        df = None
        for encoding in ["utf-8", "iso-8859-1", "cp1252"]:
            try:
                df = pd.read_csv(
                    file_path,
                    sep=";",
                    encoding=encoding,
                    skiprows=skip_rows,
                )
                if not df.empty:
                    break
            except Exception:
                continue

        if df is None or df.empty:
            return []

        # Normalize column names
        df.columns = [str(c).strip() for c in df.columns]

        # Find actual column names
        date_col = self._find_column(df, self.COLUMNS["date"])
        counterparty_col = self._find_column(df, self.COLUMNS["counterparty"])
        description_col = self._find_column(df, self.COLUMNS["description"])
        amount_col = self._find_column(df, self.COLUMNS["amount"])

        if not date_col or not amount_col:
            return []

        skipped_rows = 0
        for row_idx, row in df.iterrows():
            try:
                # Parse date
                date_value = row[date_col]
                if pd.isna(date_value):
                    skipped_rows += 1
                    logger.debug(f"Row {row_idx}: Skipped - missing date")
                    continue

                txn_date = self._parse_date(date_value)
                if txn_date is None:
                    skipped_rows += 1
                    logger.debug(f"Row {row_idx}: Skipped - invalid date format")
                    continue

                # Parse amount
                amount = self._parse_amount(row[amount_col])
                if amount is None:
                    skipped_rows += 1
                    logger.debug(f"Row {row_idx}: Skipped - invalid amount")
                    continue

                # Get description
                description = ""
                if description_col:
                    desc = row[description_col]
                    if not pd.isna(desc):
                        description = str(desc).strip()

                # Get counterparty
                counterparty = None
                if counterparty_col:
                    cp = row[counterparty_col]
                    if not pd.isna(cp):
                        counterparty = str(cp).strip()

                transactions.append(
                    Transaction(
                        date=txn_date,
                        amount=amount,
                        description=description,
                        counterparty=counterparty,
                    )
                )
            except (ValueError, KeyError, InvalidOperation) as e:
                skipped_rows += 1
                logger.warning(f"Row {row_idx}: Skipped due to error: {e}")
                continue
            except Exception as e:
                skipped_rows += 1
                logger.warning(f"Row {row_idx}: Unexpected error: {e}")
                continue

        if skipped_rows > 0:
            logger.info(f"ING import: {skipped_rows} rows skipped, {len(transactions)} imported")

        return transactions

    def _find_column(self, df: pd.DataFrame, possible_names: list[str]) -> str | None:
        """Find column by possible names."""
        for name in possible_names:
            if name in df.columns:
                return name
            # Case-insensitive search
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None

    def _parse_date(self, value) -> "datetime.date | None":
        """Parse German date format."""
        if pd.isna(value):
            return None

        if isinstance(value, (datetime, pd.Timestamp)):
            return value.date()

        str_value = str(value).strip()
        for fmt in ["%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(str_value, fmt).date()
            except ValueError:
                continue
        return None

    def _parse_amount(self, value) -> Decimal | None:
        """Parse German number format."""
        if pd.isna(value):
            return None

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        str_value = str(value).strip()
        # Remove currency symbols and spaces
        str_value = str_value.replace("€", "").replace("EUR", "").strip()
        # German format: 1.234,56 -> 1234.56
        str_value = str_value.replace(".", "").replace(",", ".")

        try:
            return Decimal(str_value)
        except Exception:
            return None
