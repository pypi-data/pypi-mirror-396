"""
DKB (Deutsche Kreditbank) CSV Importer.

Parses CSV exports from DKB online banking.

DKB CSV format:
- Semicolon separated
- German date format (DD.MM.YYYY)
- German number format (1.234,56)
- ISO-8859-1 or UTF-8 encoding
- Has header rows with account info before data
"""

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from pacman.core.models import Transaction
from pacman.importers.base import BaseImporter

logger = logging.getLogger(__name__)


class DKBImporter(BaseImporter):
    """
    DKB (Deutsche Kreditbank) CSV importer.

    Handles CSV exports from DKB online banking for both
    Girokonto and Kreditkarte exports.
    """

    # Known column names in DKB exports (Girokonto)
    COLUMNS_GIRO = {
        "date": ["Buchungstag", "Buchungsdatum", "Buchung"],
        "valuta": ["Wertstellung", "Valuta"],
        "type": ["Buchungstext", "Buchungsart"],
        "counterparty": ["Auftraggeber / Begünstigter", "Auftraggeber/Begünstigter", "Beguenstigter/Zahlungspflichtiger"],
        "description": ["Verwendungszweck", "Beschreibung"],
        "iban": ["Kontonummer", "IBAN"],
        "bic": ["BLZ", "BIC"],
        "amount": ["Betrag (EUR)", "Betrag", "Umsatz"],
    }

    # Known column names for Kreditkarte
    COLUMNS_KREDITKARTE = {
        "date": ["Belegdatum", "Buchungstag"],
        "valuta": ["Wertstellung"],
        "description": ["Beschreibung", "Verwendungszweck"],
        "amount": ["Betrag (EUR)", "Betrag", "Umsatz"],
        "original_amount": ["Ursprünglicher Betrag"],
    }

    @property
    def bank_name(self) -> str:
        return "DKB"

    @property
    def bank_code(self) -> str:
        return "dkb"

    def can_parse(self, file_path: Path) -> bool:
        """Check if this is a DKB CSV file."""
        if not file_path.exists():
            return False

        if file_path.suffix.lower() != ".csv":
            return False

        try:
            content = self._read_file_content(file_path)

            # Check for DKB-specific markers in header
            if "DKB" in content[:1000] or "Deutsche Kreditbank" in content[:1000]:
                return True

            # Check for DKB column patterns
            for encoding in ["utf-8", "iso-8859-1", "cp1252"]:
                try:
                    # Skip potential header rows
                    for skip in range(10):
                        try:
                            df = pd.read_csv(
                                file_path,
                                sep=";",
                                encoding=encoding,
                                skiprows=skip,
                                nrows=1,
                            )
                            if df.empty:
                                continue

                            columns = [str(c).lower() for c in df.columns]

                            # DKB Giro patterns
                            if any("auftraggeber" in c for c in columns):
                                return True
                            if any("begünstigter" in c for c in columns):
                                return True

                            # DKB Kreditkarte patterns
                            if "belegdatum" in columns:
                                return True

                        except Exception:
                            continue
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
        """Find the row where actual data starts (skip DKB header)."""
        for encoding in ["utf-8", "iso-8859-1", "cp1252"]:
            try:
                with open(file_path, encoding=encoding) as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    # Look for the header row with column names
                    lower_line = line.lower()
                    if "buchungstag" in lower_line or "belegdatum" in lower_line:
                        return i
                    if "auftraggeber" in lower_line:
                        return i

            except UnicodeDecodeError:
                continue
        return 0

    def parse(self, file_path: Path) -> list[Transaction]:
        """Parse DKB CSV file."""
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

        # Detect if this is Giro or Kreditkarte
        # Kreditkarte has "Belegdatum" which is unique; "Buchungstag" exists in both
        is_kreditkarte = "Belegdatum" in df.columns

        if is_kreditkarte:
            return self._parse_kreditkarte(df)
        else:
            return self._parse_giro(df)

    def _parse_giro(self, df: pd.DataFrame) -> list[Transaction]:
        """Parse Girokonto transactions."""
        transactions = []

        date_col = self._find_column(df, self.COLUMNS_GIRO["date"])
        counterparty_col = self._find_column(df, self.COLUMNS_GIRO["counterparty"])
        description_col = self._find_column(df, self.COLUMNS_GIRO["description"])
        amount_col = self._find_column(df, self.COLUMNS_GIRO["amount"])
        iban_col = self._find_column(df, self.COLUMNS_GIRO["iban"])

        if not date_col or not amount_col:
            return []

        skipped_rows = 0
        for row_idx, row in df.iterrows():
            try:
                txn = self._parse_row(
                    row, date_col, amount_col, description_col, counterparty_col, iban_col
                )
                if txn:
                    transactions.append(txn)
                else:
                    skipped_rows += 1
                    logger.debug(f"Giro row {row_idx}: Skipped - invalid data")
            except (ValueError, KeyError, InvalidOperation) as e:
                skipped_rows += 1
                logger.warning(f"Giro row {row_idx}: Skipped due to error: {e}")
                continue
            except Exception as e:
                skipped_rows += 1
                logger.warning(f"Giro row {row_idx}: Unexpected error: {e}")
                continue

        if skipped_rows > 0:
            logger.info(f"DKB Giro import: {skipped_rows} rows skipped, {len(transactions)} imported")

        return transactions

    def _parse_kreditkarte(self, df: pd.DataFrame) -> list[Transaction]:
        """Parse Kreditkarte transactions."""
        transactions = []

        date_col = self._find_column(df, self.COLUMNS_KREDITKARTE["date"])
        description_col = self._find_column(df, self.COLUMNS_KREDITKARTE["description"])
        amount_col = self._find_column(df, self.COLUMNS_KREDITKARTE["amount"])

        if not date_col or not amount_col:
            return []

        skipped_rows = 0
        for row_idx, row in df.iterrows():
            try:
                txn = self._parse_row(row, date_col, amount_col, description_col)
                if txn:
                    transactions.append(txn)
                else:
                    skipped_rows += 1
                    logger.debug(f"Kreditkarte row {row_idx}: Skipped - invalid data")
            except (ValueError, KeyError, InvalidOperation) as e:
                skipped_rows += 1
                logger.warning(f"Kreditkarte row {row_idx}: Skipped due to error: {e}")
                continue
            except Exception as e:
                skipped_rows += 1
                logger.warning(f"Kreditkarte row {row_idx}: Unexpected error: {e}")
                continue

        if skipped_rows > 0:
            logger.info(f"DKB Kreditkarte import: {skipped_rows} rows skipped, {len(transactions)} imported")

        return transactions

    def _parse_row(
        self,
        row: pd.Series,
        date_col: str,
        amount_col: str,
        description_col: str | None = None,
        counterparty_col: str | None = None,
        iban_col: str | None = None,
    ) -> Transaction | None:
        """Parse a single row into a Transaction."""
        # Parse date
        date_value = row[date_col]
        if pd.isna(date_value):
            return None

        txn_date = self._parse_date(date_value)
        if txn_date is None:
            return None

        # Parse amount
        amount = self._parse_amount(row[amount_col])
        if amount is None:
            return None

        # Get description
        description = ""
        if description_col:
            desc = row.get(description_col)
            if desc is not None and not pd.isna(desc):
                description = str(desc).strip()

        # Get counterparty
        counterparty = None
        if counterparty_col:
            cp = row.get(counterparty_col)
            if cp is not None and not pd.isna(cp):
                counterparty = str(cp).strip()

        # Get IBAN
        iban = None
        if iban_col:
            iban_val = row.get(iban_col)
            if iban_val is not None and not pd.isna(iban_val):
                iban_str = str(iban_val).strip()
                if len(iban_str) >= 15:  # Valid IBAN length
                    iban = iban_str

        return Transaction(
            date=txn_date,
            amount=amount,
            description=description,
            counterparty=counterparty,
            iban=iban,
        )

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
