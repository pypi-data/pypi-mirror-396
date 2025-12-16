"""
Tests for PACMAN utility modules.

Tests dates.py and money.py utility functions.
"""

from datetime import date
from decimal import Decimal

import pytest

from pacman.utils.dates import parse_german_date
from pacman.utils.money import format_currency, parse_german_decimal


class TestParseGermanDate:
    """Tests for German date parsing."""

    def test_full_date_yyyy(self):
        """Parse DD.MM.YYYY format."""
        result = parse_german_date("31.12.2024")
        assert result == date(2024, 12, 31)

    def test_full_date_yy(self):
        """Parse DD.MM.YY format."""
        result = parse_german_date("15.06.24")
        assert result == date(2024, 6, 15)

    def test_partial_date_with_default_year(self):
        """Parse DD.MM. format with default year."""
        result = parse_german_date("01.03.", default_year=2024)
        assert result == date(2024, 3, 1)

    def test_partial_date_without_year_uses_current(self):
        """Parse DD.MM. without default year uses current year."""
        from datetime import datetime
        current_year = datetime.now().year
        result = parse_german_date("25.12.")
        assert result is not None
        assert result.year == current_year
        assert result.month == 12
        assert result.day == 25

    def test_first_of_month(self):
        """Parse first day of month."""
        result = parse_german_date("01.01.2024")
        assert result == date(2024, 1, 1)

    def test_last_of_february_leap_year(self):
        """Parse Feb 29 in leap year."""
        result = parse_german_date("29.02.2024")
        assert result == date(2024, 2, 29)

    def test_whitespace_handling(self):
        """Strips whitespace from input."""
        result = parse_german_date("  15.06.2024  ")
        assert result == date(2024, 6, 15)

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        assert parse_german_date("") is None

    def test_none_returns_none(self):
        """None input returns None."""
        assert parse_german_date(None) is None

    def test_invalid_format_returns_none(self):
        """Invalid format returns None."""
        assert parse_german_date("2024-12-31") is None
        assert parse_german_date("12/31/2024") is None
        assert parse_german_date("invalid") is None

    def test_invalid_date_returns_none(self):
        """Invalid date (e.g., 32.13.2024) returns None."""
        assert parse_german_date("32.01.2024") is None
        assert parse_german_date("15.13.2024") is None

    def test_non_string_returns_none(self):
        """Non-string input returns None."""
        assert parse_german_date(123) is None
        assert parse_german_date(["15.06.2024"]) is None


class TestParseGermanDecimal:
    """Tests for German decimal parsing."""

    def test_german_format_with_thousands(self):
        """Parse 1.234,56 format."""
        result = parse_german_decimal("1.234,56")
        assert result == Decimal("1234.56")

    def test_german_format_simple(self):
        """Parse simple 1234,56 format."""
        result = parse_german_decimal("1234,56")
        assert result == Decimal("1234.56")

    def test_large_number(self):
        """Parse large numbers with German formatting."""
        result = parse_german_decimal("123.456.789,12")
        assert result == Decimal("123456789.12")

    def test_with_euro_symbol(self):
        """Parse with Euro symbol."""
        result = parse_german_decimal("1.234,56 €")
        assert result == Decimal("1234.56")

    def test_with_eur_text(self):
        """Parse with EUR text."""
        result = parse_german_decimal("EUR 1.234,56")
        assert result == Decimal("1234.56")

    def test_negative_number(self):
        """Parse negative number."""
        result = parse_german_decimal("-500,00")
        assert result == Decimal("-500.00")

    def test_zero(self):
        """Parse zero."""
        result = parse_german_decimal("0,00")
        assert result == Decimal("0.00")

    def test_integer_with_comma(self):
        """Parse integer with comma decimal."""
        result = parse_german_decimal("100,00")
        assert result == Decimal("100.00")

    def test_whitespace_handling(self):
        """Strips whitespace."""
        result = parse_german_decimal("  1.234,56  ")
        assert result == Decimal("1234.56")

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        assert parse_german_decimal("") is None

    def test_none_returns_none(self):
        """None returns None."""
        assert parse_german_decimal(None) is None

    def test_invalid_returns_none(self):
        """Invalid input returns None."""
        assert parse_german_decimal("abc") is None
        assert parse_german_decimal("twelve") is None

    def test_non_string_returns_none(self):
        """Non-string input returns None."""
        assert parse_german_decimal(123.45) is None


class TestFormatCurrency:
    """Tests for currency formatting."""

    def test_german_locale_positive(self):
        """Format positive amount in German locale."""
        result = format_currency(Decimal("1234.56"))
        assert result == "1.234,56 €"

    def test_german_locale_large_number(self):
        """Format large number in German locale."""
        result = format_currency(Decimal("123456789.00"))
        assert result == "123.456.789,00 €"

    def test_german_locale_negative(self):
        """Format negative amount."""
        result = format_currency(Decimal("-500.00"))
        assert "-500,00" in result
        assert "€" in result

    def test_german_locale_zero(self):
        """Format zero."""
        result = format_currency(Decimal("0"))
        assert result == "0,00 €"

    def test_german_locale_small_decimal(self):
        """Format small decimal amount."""
        result = format_currency(Decimal("0.99"))
        assert result == "0,99 €"

    def test_english_locale(self):
        """Format in English locale."""
        result = format_currency(Decimal("1234.56"), locale="en")
        assert result == "€1,234.56"

    def test_rounding(self):
        """Rounds to 2 decimal places."""
        result = format_currency(Decimal("123.456"))
        assert "123,46" in result  # Rounded up

    def test_currency_parameter_ignored(self):
        """Currency parameter currently ignored (always EUR)."""
        result = format_currency(Decimal("100"), currency="USD")
        assert "€" in result  # Still shows Euro


class TestUtilsIntegration:
    """Integration tests combining utils."""

    def test_parse_and_format_roundtrip(self):
        """Parse German decimal, format back to German."""
        original = "1.234,56"
        parsed = parse_german_decimal(original)
        formatted = format_currency(parsed)
        # Should contain same value
        assert "1.234,56" in formatted

    def test_typical_bank_statement_values(self):
        """Test typical bank statement values."""
        test_cases = [
            ("1.500,00 €", Decimal("1500.00")),  # Salary
            ("-89,99 EUR", Decimal("-89.99")),    # Subscription
            ("12,50", Decimal("12.50")),          # Small purchase
            ("-2.345,67", Decimal("-2345.67")),   # Large expense
        ]

        for input_val, expected in test_cases:
            result = parse_german_decimal(input_val)
            assert result == expected, f"Failed for {input_val}"

    def test_date_range_for_tax_year(self):
        """Parse date range for tax year 2024."""
        start = parse_german_date("01.01.2024")
        end = parse_german_date("31.12.2024")

        assert start == date(2024, 1, 1)
        assert end == date(2024, 12, 31)
        assert (end - start).days == 365  # 2024 is leap year

    def test_monthly_dates(self):
        """Parse monthly statement dates."""
        months = [
            "31.01.2024", "29.02.2024", "31.03.2024",
            "30.04.2024", "31.05.2024", "30.06.2024",
            "31.07.2024", "31.08.2024", "30.09.2024",
            "31.10.2024", "30.11.2024", "31.12.2024",
        ]

        for month_str in months:
            result = parse_german_date(month_str)
            assert result is not None, f"Failed to parse {month_str}"
            assert result.year == 2024
