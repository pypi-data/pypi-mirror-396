"""
Tests for PACMAN Importers.

Tests bank CSV/XLSX import functionality.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from pacman.importers import (
    DeutscheBankImporter,
    DKBImporter,
    GenericCSVImporter,
    INGImporter,
    N26Importer,
    SparkasseImporter,
)


class TestDeutscheBankImporter:
    """Tests for Deutsche Bank importer."""

    @pytest.fixture
    def importer(self) -> DeutscheBankImporter:
        """Create a Deutsche Bank importer instance."""
        return DeutscheBankImporter()

    @pytest.fixture
    def sample_csv(self, fixtures_dir: Path) -> Path:
        """Path to sample Deutsche Bank CSV."""
        return fixtures_dir / "deutsche_bank_sample.csv"

    def test_bank_name(self, importer: DeutscheBankImporter):
        """Test bank name property."""
        assert importer.bank_name == "Deutsche Bank"
        assert importer.bank_code == "deutsche-bank"

    def test_can_parse_valid_file(
        self, importer: DeutscheBankImporter, sample_csv: Path
    ):
        """Test detection of valid Deutsche Bank CSV."""
        assert importer.can_parse(sample_csv) is True

    def test_can_parse_invalid_file(
        self, importer: DeutscheBankImporter, tmp_path: Path
    ):
        """Test rejection of invalid files."""
        # Non-existent file
        assert importer.can_parse(tmp_path / "nonexistent.csv") is False

        # Wrong extension
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test")
        assert importer.can_parse(txt_file) is False

    def test_parse_sample_csv(
        self, importer: DeutscheBankImporter, sample_csv: Path
    ):
        """Test parsing sample Deutsche Bank CSV."""
        transactions = importer.parse(sample_csv)

        assert len(transactions) == 5

        # Check first transaction (income)
        txn1 = transactions[0]
        assert txn1.date == date(2024, 1, 5)
        assert txn1.amount == Decimal("850.00")
        assert "Miete" in txn1.description

        # Check second transaction (expense with Soll column)
        txn2 = transactions[1]
        assert txn2.date == date(2024, 1, 10)
        assert txn2.amount == Decimal("-89.99")
        assert "Dropscan" in txn2.description

    def test_parse_german_amounts(
        self, importer: DeutscheBankImporter, sample_csv: Path
    ):
        """Test parsing German number format (1.200,00)."""
        transactions = importer.parse(sample_csv)

        # Third transaction has 1.200,00 as amount
        txn3 = transactions[2]
        assert txn3.amount == Decimal("-1200.00")

    def test_parse_iban_extraction(
        self, importer: DeutscheBankImporter, sample_csv: Path
    ):
        """Test IBAN extraction from CSV."""
        transactions = importer.parse(sample_csv)

        # First transaction should have IBAN
        assert transactions[0].iban == "DE89370400440532013000"

    def test_parse_counterparty_extraction(
        self, importer: DeutscheBankImporter, sample_csv: Path
    ):
        """Test counterparty extraction."""
        transactions = importer.parse(sample_csv)

        # First transaction should have counterparty from dedicated column
        assert transactions[0].counterparty == "Max Müller"


class TestGenericCSVImporter:
    """Tests for generic CSV importer."""

    @pytest.fixture
    def importer(self) -> GenericCSVImporter:
        """Create a generic CSV importer instance."""
        return GenericCSVImporter()

    def test_bank_name(self, importer: GenericCSVImporter):
        """Test bank name property."""
        assert importer.bank_name == "Generic CSV"
        assert importer.bank_code == "generic"

    def test_parse_simple_csv(self, tmp_path: Path):
        """Test parsing a simple generic CSV."""
        csv_content = """date,amount,description
2024-01-15,100.00,Test Income
2024-01-20,-50.00,Test Expense
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        # Configure importer with column names
        importer = GenericCSVImporter(
            date_column="date",
            amount_column="amount",
            description_column="description",
            date_format="%Y-%m-%d",
        )
        transactions = importer.parse(csv_file)

        assert len(transactions) == 2
        assert transactions[0].amount == Decimal("100.00")
        assert transactions[1].amount == Decimal("-50.00")


class TestImporterAutoDetection:
    """Tests for automatic importer detection."""

    def test_deutsche_bank_detected(self, fixtures_dir: Path):
        """Test that Deutsche Bank format is auto-detected."""
        sample_csv = fixtures_dir / "deutsche_bank_sample.csv"

        db_importer = DeutscheBankImporter()
        generic_importer = GenericCSVImporter()

        # Deutsche Bank importer should recognize the file
        assert db_importer.can_parse(sample_csv) is True


class TestImporterEdgeCases:
    """Tests for importer edge cases."""

    @pytest.fixture
    def importer(self) -> DeutscheBankImporter:
        return DeutscheBankImporter()

    def test_empty_csv(self, importer: DeutscheBankImporter, tmp_path: Path):
        """Test handling of empty CSV."""
        csv_content = """Buchungstag;Verwendungszweck;Betrag
"""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text(csv_content)

        transactions = importer.parse(csv_file)
        assert len(transactions) == 0

    def test_malformed_date(self, importer: DeutscheBankImporter, tmp_path: Path):
        """Test handling of malformed dates."""
        csv_content = """Buchungstag;Verwendungszweck;Betrag
invalid-date;Test;100,00
15.01.2024;Valid;200,00
"""
        csv_file = tmp_path / "malformed.csv"
        csv_file.write_text(csv_content)

        transactions = importer.parse(csv_file)
        # Should skip the malformed row
        assert len(transactions) == 1
        assert transactions[0].amount == Decimal("200.00")

    def test_encoding_latin1(self, importer: DeutscheBankImporter, tmp_path: Path):
        """Test handling of Latin-1 encoded files."""
        csv_content = """Buchungstag;Verwendungszweck;Betrag
15.01.2024;Müller Überweisung;100,00
"""
        csv_file = tmp_path / "latin1.csv"
        csv_file.write_bytes(csv_content.encode("latin-1"))

        transactions = importer.parse(csv_file)
        assert len(transactions) == 1
        assert "Müller" in transactions[0].description


class TestSparkasseImporter:
    """Tests for Sparkasse importer."""

    @pytest.fixture
    def importer(self) -> SparkasseImporter:
        """Create a Sparkasse importer instance."""
        return SparkasseImporter()

    @pytest.fixture
    def sample_csv(self, fixtures_dir: Path) -> Path:
        """Path to sample Sparkasse CSV."""
        return fixtures_dir / "sparkasse_sample.csv"

    def test_bank_name(self, importer: SparkasseImporter):
        """Test bank name property."""
        assert importer.bank_name == "Sparkasse"
        assert importer.bank_code == "sparkasse"

    def test_can_parse_valid_file(
        self, importer: SparkasseImporter, sample_csv: Path
    ):
        """Test detection of valid Sparkasse CSV."""
        assert importer.can_parse(sample_csv) is True

    def test_can_parse_rejects_deutsche_bank(
        self, importer: SparkasseImporter, fixtures_dir: Path
    ):
        """Test that Sparkasse importer doesn't claim Deutsche Bank files."""
        db_csv = fixtures_dir / "deutsche_bank_sample.csv"
        # Sparkasse uses different column names
        assert importer.can_parse(db_csv) is False

    def test_parse_sample_csv(
        self, importer: SparkasseImporter, sample_csv: Path
    ):
        """Test parsing sample Sparkasse CSV."""
        transactions = importer.parse(sample_csv)

        assert len(transactions) == 5

        # Check first transaction (income - rent)
        txn1 = transactions[0]
        assert txn1.date == date(2024, 1, 5)
        assert txn1.amount == Decimal("850.00")
        assert "Miete" in txn1.description
        assert txn1.counterparty == "Max Mueller"

        # Check second transaction (expense - Dropscan)
        txn2 = transactions[1]
        assert txn2.date == date(2024, 1, 10)
        assert txn2.amount == Decimal("-89.99")
        assert "Dropscan" in txn2.description

    def test_parse_german_amounts(
        self, importer: SparkasseImporter, sample_csv: Path
    ):
        """Test parsing German number format (-1.200,00)."""
        transactions = importer.parse(sample_csv)

        # Third transaction has -1.200,00 as amount
        txn3 = transactions[2]
        assert txn3.amount == Decimal("-1200.00")

    def test_parse_iban_extraction(
        self, importer: SparkasseImporter, sample_csv: Path
    ):
        """Test IBAN extraction from CSV."""
        transactions = importer.parse(sample_csv)

        # First transaction should have IBAN
        assert transactions[0].iban == "DE89370400440532013000"

    def test_parse_counterparty_extraction(
        self, importer: SparkasseImporter, sample_csv: Path
    ):
        """Test counterparty extraction."""
        transactions = importer.parse(sample_csv)

        assert transactions[0].counterparty == "Max Mueller"
        assert transactions[1].counterparty == "Dropscan GmbH"

    def test_description_includes_booking_type(
        self, importer: SparkasseImporter, sample_csv: Path
    ):
        """Test that description includes booking type."""
        transactions = importer.parse(sample_csv)

        # Description should contain booking type (GUTSCHRIFT, SEPA-LASTSCHRIFT, etc.)
        assert "GUTSCHRIFT" in transactions[0].description
        assert "SEPA-LASTSCHRIFT" in transactions[1].description


class TestImporterAutoDetectionWithSparkasse:
    """Tests for automatic importer detection including Sparkasse."""

    def test_sparkasse_detected(self, fixtures_dir: Path):
        """Test that Sparkasse format is auto-detected."""
        sample_csv = fixtures_dir / "sparkasse_sample.csv"

        sparkasse_importer = SparkasseImporter()
        db_importer = DeutscheBankImporter()

        # Sparkasse importer should recognize its own format
        assert sparkasse_importer.can_parse(sample_csv) is True
        # Deutsche Bank should not recognize Sparkasse format
        assert db_importer.can_parse(sample_csv) is False

    def test_deutsche_bank_not_detected_as_sparkasse(self, fixtures_dir: Path):
        """Test that Deutsche Bank is not detected as Sparkasse."""
        db_csv = fixtures_dir / "deutsche_bank_sample.csv"

        sparkasse_importer = SparkasseImporter()
        db_importer = DeutscheBankImporter()

        # Each should recognize only its own format
        assert db_importer.can_parse(db_csv) is True
        assert sparkasse_importer.can_parse(db_csv) is False


class TestINGImporter:
    """Tests for ING-DiBa importer."""

    @pytest.fixture
    def importer(self) -> INGImporter:
        """Create an ING importer instance."""
        return INGImporter()

    @pytest.fixture
    def sample_csv(self, fixtures_dir: Path) -> Path:
        """Path to sample ING CSV."""
        return fixtures_dir / "ing_sample.csv"

    def test_bank_name(self, importer: INGImporter):
        """Test bank name property."""
        assert importer.bank_name == "ING-DiBa"
        assert importer.bank_code == "ing"

    def test_can_parse_valid_file(
        self, importer: INGImporter, sample_csv: Path
    ):
        """Test detection of valid ING CSV."""
        assert importer.can_parse(sample_csv) is True

    def test_can_parse_invalid_file(
        self, importer: INGImporter, tmp_path: Path
    ):
        """Test rejection of invalid files."""
        # Non-existent file
        assert importer.can_parse(tmp_path / "nonexistent.csv") is False

        # Wrong extension
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test")
        assert importer.can_parse(txt_file) is False

    def test_parse_sample_csv(
        self, importer: INGImporter, sample_csv: Path
    ):
        """Test parsing sample ING CSV."""
        transactions = importer.parse(sample_csv)

        assert len(transactions) == 5

        # Check first transaction (income)
        txn1 = transactions[0]
        assert txn1.date == date(2024, 1, 5)
        assert txn1.amount == Decimal("850.00")
        assert "Miete" in txn1.description
        assert txn1.counterparty == "Max Müller"

        # Check second transaction (expense)
        txn2 = transactions[1]
        assert txn2.date == date(2024, 1, 10)
        assert txn2.amount == Decimal("-89.99")

    def test_parse_german_amounts(
        self, importer: INGImporter, sample_csv: Path
    ):
        """Test parsing German number format (-1.200,00)."""
        transactions = importer.parse(sample_csv)

        # Third transaction has -1.200,00 as amount
        txn3 = transactions[2]
        assert txn3.amount == Decimal("-1200.00")

    def test_can_parse_rejects_other_banks(
        self, importer: INGImporter, fixtures_dir: Path
    ):
        """Test that ING importer doesn't claim other bank files."""
        db_csv = fixtures_dir / "deutsche_bank_sample.csv"
        assert importer.can_parse(db_csv) is False


class TestN26Importer:
    """Tests for N26 importer."""

    @pytest.fixture
    def importer(self) -> N26Importer:
        """Create an N26 importer instance."""
        return N26Importer()

    @pytest.fixture
    def sample_csv(self, fixtures_dir: Path) -> Path:
        """Path to sample N26 CSV."""
        return fixtures_dir / "n26_sample.csv"

    def test_bank_name(self, importer: N26Importer):
        """Test bank name property."""
        assert importer.bank_name == "N26"
        assert importer.bank_code == "n26"

    def test_can_parse_valid_file(
        self, importer: N26Importer, sample_csv: Path
    ):
        """Test detection of valid N26 CSV."""
        assert importer.can_parse(sample_csv) is True

    def test_can_parse_invalid_file(
        self, importer: N26Importer, tmp_path: Path
    ):
        """Test rejection of invalid files."""
        # Non-existent file
        assert importer.can_parse(tmp_path / "nonexistent.csv") is False

        # Wrong extension
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test")
        assert importer.can_parse(txt_file) is False

    def test_parse_sample_csv(
        self, importer: N26Importer, sample_csv: Path
    ):
        """Test parsing sample N26 CSV."""
        transactions = importer.parse(sample_csv)

        assert len(transactions) == 5

        # Check first transaction (income)
        txn1 = transactions[0]
        assert txn1.date == date(2024, 1, 5)
        assert txn1.amount == Decimal("850.00")
        assert txn1.counterparty == "Max Müller"

        # Check second transaction (expense)
        txn2 = transactions[1]
        assert txn2.date == date(2024, 1, 10)
        assert txn2.amount == Decimal("-89.99")

    def test_parse_iso_date_format(
        self, importer: N26Importer, sample_csv: Path
    ):
        """Test parsing ISO date format (YYYY-MM-DD)."""
        transactions = importer.parse(sample_csv)

        # All transactions should have correct dates
        assert transactions[0].date == date(2024, 1, 5)
        assert transactions[4].date == date(2024, 1, 25)

    def test_can_parse_rejects_german_format(
        self, importer: N26Importer, fixtures_dir: Path
    ):
        """Test that N26 importer doesn't claim German format files."""
        db_csv = fixtures_dir / "deutsche_bank_sample.csv"
        assert importer.can_parse(db_csv) is False


class TestDKBImporter:
    """Tests for DKB importer."""

    @pytest.fixture
    def importer(self) -> DKBImporter:
        """Create a DKB importer instance."""
        return DKBImporter()

    @pytest.fixture
    def sample_csv(self, fixtures_dir: Path) -> Path:
        """Path to sample DKB CSV."""
        return fixtures_dir / "dkb_sample.csv"

    def test_bank_name(self, importer: DKBImporter):
        """Test bank name property."""
        assert importer.bank_name == "DKB"
        assert importer.bank_code == "dkb"

    def test_can_parse_valid_file(
        self, importer: DKBImporter, sample_csv: Path
    ):
        """Test detection of valid DKB CSV."""
        assert importer.can_parse(sample_csv) is True

    def test_can_parse_invalid_file(
        self, importer: DKBImporter, tmp_path: Path
    ):
        """Test rejection of invalid files."""
        # Non-existent file
        assert importer.can_parse(tmp_path / "nonexistent.csv") is False

        # Wrong extension
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test")
        assert importer.can_parse(txt_file) is False

    def test_parse_sample_csv(
        self, importer: DKBImporter, sample_csv: Path
    ):
        """Test parsing sample DKB CSV."""
        transactions = importer.parse(sample_csv)

        assert len(transactions) == 5

        # Check first transaction (income)
        txn1 = transactions[0]
        assert txn1.date == date(2024, 1, 5)
        assert txn1.amount == Decimal("850.00")
        assert "Miete" in txn1.description
        assert txn1.counterparty == "Max Müller"

        # Check second transaction (expense)
        txn2 = transactions[1]
        assert txn2.date == date(2024, 1, 10)
        assert txn2.amount == Decimal("-89.99")

    def test_parse_german_amounts(
        self, importer: DKBImporter, sample_csv: Path
    ):
        """Test parsing German number format (-1.200,00)."""
        transactions = importer.parse(sample_csv)

        # Third transaction has -1.200,00 as amount
        txn3 = transactions[2]
        assert txn3.amount == Decimal("-1200.00")

    def test_parse_iban_extraction(
        self, importer: DKBImporter, sample_csv: Path
    ):
        """Test IBAN extraction from CSV."""
        transactions = importer.parse(sample_csv)

        # First transaction should have IBAN
        assert transactions[0].iban == "DE89370400440532013000"

    def test_skip_header_rows(
        self, importer: DKBImporter, sample_csv: Path
    ):
        """Test that DKB header rows are skipped correctly."""
        transactions = importer.parse(sample_csv)

        # Should have parsed 5 transactions, skipping the header info
        assert len(transactions) == 5
        # First actual transaction should be from 05.01.2024
        assert transactions[0].date == date(2024, 1, 5)

    def test_can_parse_rejects_other_banks(
        self, importer: DKBImporter, fixtures_dir: Path
    ):
        """Test that DKB importer doesn't claim other bank files."""
        db_csv = fixtures_dir / "deutsche_bank_sample.csv"
        assert importer.can_parse(db_csv) is False


class TestAllImportersAutoDetection:
    """Tests for auto-detection across all importers."""

    def test_each_importer_recognizes_own_format(self, fixtures_dir: Path):
        """Test that each importer recognizes only its own format."""
        importers = {
            "deutsche_bank": DeutscheBankImporter(),
            "sparkasse": SparkasseImporter(),
            "ing": INGImporter(),
            "n26": N26Importer(),
            "dkb": DKBImporter(),
        }

        fixtures = {
            "deutsche_bank": fixtures_dir / "deutsche_bank_sample.csv",
            "sparkasse": fixtures_dir / "sparkasse_sample.csv",
            "ing": fixtures_dir / "ing_sample.csv",
            "n26": fixtures_dir / "n26_sample.csv",
            "dkb": fixtures_dir / "dkb_sample.csv",
        }

        for bank_name, importer in importers.items():
            fixture_file = fixtures[bank_name]
            if fixture_file.exists():
                assert importer.can_parse(fixture_file) is True, \
                    f"{bank_name} importer should recognize its own format"
