"""
Deutsche Bank CSV/XLSX Importer.

Parses transaction exports from Deutsche Bank online banking.
"""

import logging
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from pacman.core.models import Transaction
from pacman.importers.base import BaseImporter

logger = logging.getLogger(__name__)


class DeutscheBankImporter(BaseImporter):
    """
    Importer for Deutsche Bank transaction exports.

    Supports both CSV and XLSX formats from Deutsche Bank online banking.

    Expected columns:
    - Buchungstag / Datum: Transaction date
    - Verwendungszweck / Beschreibung: Description
    - Betrag / Soll / Haben: Amount (negative for expenses)
    - IBAN: Counterparty IBAN (optional)
    """

    @property
    def bank_name(self) -> str:
        return "Deutsche Bank"

    @property
    def bank_code(self) -> str:
        return "deutsche-bank"

    def can_parse(self, file_path: Path) -> bool:
        """Check if file looks like a Deutsche Bank export."""
        if not file_path.exists():
            return False

        suffix = file_path.suffix.lower()
        if suffix not in [".csv", ".xlsx", ".xls"]:
            return False

        try:
            if suffix == ".csv":
                # Try to read first few rows and check for Deutsche Bank indicators
                df = pd.read_csv(file_path, nrows=5, encoding="utf-8", sep=None, engine="python")
            else:
                df = pd.read_excel(file_path, nrows=5)

            columns = [str(c).lower() for c in df.columns]
            columns_str = " ".join(columns)

            # Reject if it's a Sparkasse file (has "auftragskonto")
            if "auftragskonto" in columns_str:
                return False

            # Check for typical Deutsche Bank column names
            db_indicators = ["buchungstag", "verwendungszweck", "betrag", "soll", "haben"]
            matches = sum(1 for ind in db_indicators if any(ind in col for col in columns))

            return matches >= 2

        except Exception:
            return False

    def parse(self, file_path: Path) -> list[Transaction]:
        """Parse Deutsche Bank export file."""
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            df = self._read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        return self._dataframe_to_transactions(df)

    def _read_csv(self, file_path: Path) -> pd.DataFrame:
        """Read CSV with various encoding attempts."""
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                # Read without decimal/thousands conversion to preserve dates
                # We'll handle German number format in _to_decimal
                return pd.read_csv(
                    file_path,
                    encoding=encoding,
                    sep=None,  # Auto-detect separator
                    engine="python",
                )
            except Exception:
                continue

        raise ValueError(f"Could not read CSV file: {file_path}")

    def _dataframe_to_transactions(self, df: pd.DataFrame) -> list[Transaction]:
        """Convert DataFrame to Transaction objects."""
        transactions = []

        # Normalize column names
        df.columns = [str(c).lower().strip() for c in df.columns]

        # Find relevant columns
        date_col = self._find_column(df, ["buchungstag", "datum", "date", "monat"])
        desc_col = self._find_column(df, ["verwendungszweck", "beschreibung", "description"])
        amount_col = self._find_column(df, ["betrag", "amount"])
        debit_col = self._find_column(df, ["soll", "debit"])
        credit_col = self._find_column(df, ["haben", "credit"])
        iban_col = self._find_column(df, ["iban"])
        counterparty_col = self._find_column(df, [
            "beguenstigter", "zahlungspflichtiger", "auftraggeber",
            "empfaenger", "name", "counterparty"
        ])

        skipped_rows = 0
        for row_idx, row in df.iterrows():
            try:
                # Parse date
                txn_date = self._parse_date(row, date_col)
                if txn_date is None:
                    skipped_rows += 1
                    logger.debug(f"Row {row_idx}: Skipped - invalid date")
                    continue

                # Parse amount
                amount = self._parse_amount(row, amount_col, debit_col, credit_col)
                if amount is None:
                    skipped_rows += 1
                    logger.debug(f"Row {row_idx}: Skipped - invalid amount")
                    continue

                # Parse description and extract counterparty
                description = str(row.get(desc_col, "")) if desc_col else ""

                # Try dedicated counterparty column first, then extract from description
                counterparty = None
                if counterparty_col and counterparty_col in row:
                    cp_value = row[counterparty_col]
                    if not pd.isna(cp_value) and str(cp_value).strip():
                        counterparty = str(cp_value).strip()
                if not counterparty:
                    counterparty = self._extract_counterparty(description)

                iban = str(row.get(iban_col, "")) if iban_col else None

                # Clean IBAN
                if iban and (pd.isna(iban) or iban.strip() == ""):
                    iban = None

                txn = Transaction(
                    date=txn_date,
                    amount=amount,
                    description=description,
                    counterparty=counterparty,
                    iban=iban,
                )
                transactions.append(txn)

            except (ValueError, KeyError, InvalidOperation) as e:
                skipped_rows += 1
                logger.warning(f"Row {row_idx}: Skipped due to error: {e}")
                continue
            except Exception as e:
                skipped_rows += 1
                logger.warning(f"Row {row_idx}: Unexpected error: {e}")
                continue

        if skipped_rows > 0:
            logger.info(f"Deutsche Bank import: {skipped_rows} rows skipped, {len(transactions)} imported")

        return transactions

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str | None:
        """Find a column matching one of the candidate names."""
        for col in df.columns:
            col_lower = col.lower()
            for candidate in candidates:
                if candidate in col_lower:
                    return col
        return None

    def _parse_date(self, row: pd.Series, date_col: str | None) -> date | None:
        """Parse date from row."""
        if not date_col or date_col not in row:
            return None

        value = row[date_col]
        if pd.isna(value):
            return None

        # If it's already a datetime
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.date()

        # Try various date formats
        date_str = str(value).strip()

        # German format: DD.MM.YYYY or DD.MM.
        formats = [
            "%d.%m.%Y",
            "%d.%m.",
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # If year is missing, assume current year
                if fmt == "%d.%m.":
                    parsed = parsed.replace(year=datetime.now().year)
                return parsed.date()
            except ValueError:
                continue

        return None

    def _parse_amount(
        self,
        row: pd.Series,
        amount_col: str | None,
        debit_col: str | None,
        credit_col: str | None,
    ) -> Decimal | None:
        """Parse amount from row, handling both single amount and debit/credit columns."""
        # Try single amount column
        if amount_col and amount_col in row:
            value = row[amount_col]
            if not pd.isna(value):
                return self._to_decimal(value)

        # Try separate debit/credit columns
        amount = Decimal("0")

        if debit_col and debit_col in row:
            debit_value = row[debit_col]
            if not pd.isna(debit_value):
                debit = self._to_decimal(debit_value)
                if debit:
                    amount -= abs(debit)

        if credit_col and credit_col in row:
            credit_value = row[credit_col]
            if not pd.isna(credit_value):
                credit = self._to_decimal(credit_value)
                if credit:
                    amount += abs(credit)

        return amount if amount != Decimal("0") else None

    def _to_decimal(self, value) -> Decimal | None:
        """Convert value to Decimal, handling German number format."""
        if pd.isna(value):
            return None

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        # Handle string with German format
        str_value = str(value).strip()
        if not str_value:
            return None

        # Remove currency symbols and whitespace
        str_value = re.sub(r"[€$\s]", "", str_value)

        # German format: 1.234,56 -> 1234.56
        if "," in str_value and "." in str_value:
            str_value = str_value.replace(".", "").replace(",", ".")
        elif "," in str_value:
            str_value = str_value.replace(",", ".")

        try:
            return Decimal(str_value)
        except InvalidOperation:
            return None

    def _extract_counterparty(self, description: str) -> str | None:
        """
        Extract counterparty name from description.

        Deutsche Bank descriptions often follow patterns like:
        - "SEPA Überweisung von | Name | ..."
        - "SEPA Lastschrift von | Name | ..."
        - "SEPA Dauerauftrag an | Name | ..."
        """
        if not description:
            return None

        # Pattern: "... von | Name |" or "... an | Name |"
        match = re.search(r"(?:von|an|für)\s*\|\s*([^|]+)\s*\|", description, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Pattern: "Name | IBAN..."
        match = re.search(r"^\s*([^|]+)\s*\|", description)
        if match:
            name = match.group(1).strip()
            # Filter out common non-name prefixes
            if not name.upper().startswith(("SEPA", "LASTSCHRIFT", "ÜBERWEISUNG")):
                return name

        return None
