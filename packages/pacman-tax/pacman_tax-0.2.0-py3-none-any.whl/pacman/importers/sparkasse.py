"""
Sparkasse CSV Importer.

Parses transaction exports from Sparkasse online banking.
Supports both the standard CSV-CAMT format and older CSV formats.
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


class SparkasseImporter(BaseImporter):
    """
    Importer for Sparkasse transaction exports.

    Supports CSV exports from Sparkasse online banking.

    Standard format columns:
    - Auftragskonto: Account number
    - Buchungstag: Booking date
    - Valutadatum: Value date
    - Buchungstext: Transaction type
    - Verwendungszweck: Description/Purpose
    - Beguenstigter/Zahlungspflichtiger: Counterparty
    - Kontonummer/IBAN: Counterparty IBAN
    - BIC: Counterparty BIC
    - Betrag: Amount (German format: -1.234,56)
    - Waehrung: Currency
    - Info: Status info
    """

    @property
    def bank_name(self) -> str:
        return "Sparkasse"

    @property
    def bank_code(self) -> str:
        return "sparkasse"

    def can_parse(self, file_path: Path) -> bool:
        """Check if file looks like a Sparkasse export."""
        if not file_path.exists():
            return False

        suffix = file_path.suffix.lower()
        if suffix not in [".csv"]:
            return False

        try:
            # Try to read first few rows
            df = pd.read_csv(
                file_path,
                nrows=5,
                encoding="utf-8",
                sep=";",
                on_bad_lines="skip",
            )
            columns = [str(c).lower() for c in df.columns]
            columns_str = " ".join(columns)

            # Sparkasse-specific: must have "auftragskonto" (unique to Sparkasse)
            # AND "beguenstigter" or "zahlungspflichtiger" in column names
            has_auftragskonto = "auftragskonto" in columns_str
            has_counterparty = (
                "beguenstigter" in columns_str or
                "zahlungspflichtiger" in columns_str
            )

            # Must have both Sparkasse-specific markers
            return has_auftragskonto and has_counterparty

        except Exception:
            # Try with different encoding
            try:
                df = pd.read_csv(
                    file_path,
                    nrows=5,
                    encoding="latin-1",
                    sep=";",
                    on_bad_lines="skip",
                )
                columns = [str(c).lower() for c in df.columns]
                columns_str = " ".join(columns)
                has_auftragskonto = "auftragskonto" in columns_str
                has_counterparty = "beguenstigter" in columns_str
                return has_auftragskonto and has_counterparty
            except Exception:
                return False

    def parse(self, file_path: Path) -> list[Transaction]:
        """Parse Sparkasse export file."""
        df = self._read_csv(file_path)
        return self._dataframe_to_transactions(df)

    def _read_csv(self, file_path: Path) -> pd.DataFrame:
        """Read CSV with various encoding attempts."""
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                return pd.read_csv(
                    file_path,
                    encoding=encoding,
                    sep=";",
                    on_bad_lines="skip",
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
        date_col = self._find_column(df, ["buchungstag"])
        desc_col = self._find_column(df, ["verwendungszweck"])
        amount_col = self._find_column(df, ["betrag"])
        counterparty_col = self._find_column(df, [
            "beguenstigter/zahlungspflichtiger",
            "beguenstigter",
            "zahlungspflichtiger",
        ])
        iban_col = self._find_column(df, ["kontonummer/iban", "iban", "kontonummer"])
        booking_type_col = self._find_column(df, ["buchungstext"])

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
                amount = self._parse_amount(row, amount_col)
                if amount is None:
                    skipped_rows += 1
                    logger.debug(f"Row {row_idx}: Skipped - invalid amount")
                    continue

                # Build description from booking type + purpose
                description = self._build_description(row, booking_type_col, desc_col)

                # Get counterparty
                counterparty = None
                if counterparty_col and counterparty_col in row:
                    cp_value = row[counterparty_col]
                    if not pd.isna(cp_value) and str(cp_value).strip():
                        counterparty = str(cp_value).strip()

                # Get IBAN
                iban = None
                if iban_col and iban_col in row:
                    iban_value = row[iban_col]
                    if not pd.isna(iban_value) and str(iban_value).strip():
                        iban = str(iban_value).strip()

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
            logger.info(f"Sparkasse import: {skipped_rows} rows skipped, {len(transactions)} imported")

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

        # German format: DD.MM.YYYY
        formats = [
            "%d.%m.%Y",
            "%d.%m.%y",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    def _parse_amount(self, row: pd.Series, amount_col: str | None) -> Decimal | None:
        """Parse amount from row (German format: -1.234,56)."""
        if not amount_col or amount_col not in row:
            return None

        value = row[amount_col]
        if pd.isna(value):
            return None

        return self._to_decimal(value)

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
        # Also handles negative: -1.234,56 -> -1234.56
        if "," in str_value:
            str_value = str_value.replace(".", "").replace(",", ".")

        try:
            return Decimal(str_value)
        except InvalidOperation:
            return None

    def _build_description(
        self,
        row: pd.Series,
        booking_type_col: str | None,
        desc_col: str | None,
    ) -> str:
        """Build description from booking type and purpose."""
        parts = []

        if booking_type_col and booking_type_col in row:
            bt = row[booking_type_col]
            if not pd.isna(bt) and str(bt).strip():
                parts.append(str(bt).strip())

        if desc_col and desc_col in row:
            desc = row[desc_col]
            if not pd.isna(desc) and str(desc).strip():
                parts.append(str(desc).strip())

        return " | ".join(parts) if parts else ""
