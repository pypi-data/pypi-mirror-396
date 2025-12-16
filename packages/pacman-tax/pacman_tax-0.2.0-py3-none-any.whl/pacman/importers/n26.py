"""
N26 CSV Importer.

Parses CSV exports from N26 banking app.

N26 CSV format:
- Comma separated (international format)
- ISO date format (YYYY-MM-DD)
- Standard decimal format (1234.56)
- UTF-8 encoding
- English column headers
"""

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from pacman.core.models import Transaction
from pacman.importers.base import BaseImporter

logger = logging.getLogger(__name__)


class N26Importer(BaseImporter):
    """
    N26 CSV importer.

    Handles CSV exports from the N26 banking app.
    N26 uses international format with English headers.
    """

    # Known column names in N26 exports
    COLUMNS = {
        "date": ["Date", "Datum", "Booking Date"],
        "counterparty": ["Partner Name", "Payee", "Partner", "Name"],
        "type": ["Transaction Type", "Type"],
        "description": ["Reference", "Payment Reference", "Description"],
        "category": ["Category"],
        "amount_eur": ["Amount (EUR)", "Amount"],
        "amount_foreign": ["Amount (Foreign Currency)"],
        "currency": ["Type Foreign Currency", "Foreign Currency"],
    }

    @property
    def bank_name(self) -> str:
        return "N26"

    @property
    def bank_code(self) -> str:
        return "n26"

    def can_parse(self, file_path: Path) -> bool:
        """Check if this is an N26 CSV file."""
        if not file_path.exists():
            return False

        if file_path.suffix.lower() != ".csv":
            return False

        try:
            # N26 uses comma separator and UTF-8
            df = pd.read_csv(file_path, sep=",", encoding="utf-8", nrows=1)
            columns = [str(c).lower() for c in df.columns]

            # Check for N26-specific columns
            if "partner name" in columns or "amount (eur)" in columns:
                return True

            # Check for N26 patterns
            if "date" in columns and any("amount" in c for c in columns):
                # Verify it's not another bank by checking format
                if any("partner" in c for c in columns):
                    return True

            return False
        except Exception:
            return False

    def parse(self, file_path: Path) -> list[Transaction]:
        """Parse N26 CSV file."""
        transactions = []

        try:
            df = pd.read_csv(file_path, sep=",", encoding="utf-8")
        except Exception:
            return []

        if df.empty:
            return []

        # Normalize column names
        df.columns = [str(c).strip() for c in df.columns]

        # Find actual column names
        date_col = self._find_column(df, self.COLUMNS["date"])
        counterparty_col = self._find_column(df, self.COLUMNS["counterparty"])
        description_col = self._find_column(df, self.COLUMNS["description"])
        amount_col = self._find_column(df, self.COLUMNS["amount_eur"])

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

                # Combine description with transaction type if available
                type_col = self._find_column(df, self.COLUMNS["type"])
                if type_col and not pd.isna(row.get(type_col)):
                    txn_type = str(row[type_col]).strip()
                    if txn_type and description:
                        description = f"{txn_type}: {description}"
                    elif txn_type:
                        description = txn_type

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
            logger.info(f"N26 import: {skipped_rows} rows skipped, {len(transactions)} imported")

        return transactions

    def _find_column(self, df: pd.DataFrame, possible_names: list[str]) -> str | None:
        """Find column by possible names."""
        for name in possible_names:
            if name in df.columns:
                return name
            # Case-insensitive search
            for col in df.columns:
                if name.lower() == col.lower():
                    return col
        return None

    def _parse_date(self, value) -> "datetime.date | None":
        """Parse date (N26 uses ISO format YYYY-MM-DD)."""
        if pd.isna(value):
            return None

        if isinstance(value, (datetime, pd.Timestamp)):
            return value.date()

        str_value = str(value).strip()
        for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]:
            try:
                return datetime.strptime(str_value, fmt).date()
            except ValueError:
                continue
        return None

    def _parse_amount(self, value) -> Decimal | None:
        """Parse amount (N26 uses standard decimal format)."""
        if pd.isna(value):
            return None

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        str_value = str(value).strip()
        # Remove currency symbols
        str_value = str_value.replace("€", "").replace("EUR", "").strip()

        try:
            return Decimal(str_value)
        except Exception:
            return None
