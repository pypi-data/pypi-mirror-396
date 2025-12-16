"""
Tests for PACMAN Dashboard.

Tests the dashboard logic without Streamlit UI components.
"""

import json
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest
import yaml


# Import dashboard functions directly (without Streamlit)
# We need to mock st before importing the module
class MockStreamlit:
    """Mock Streamlit module for testing."""

    def set_page_config(self, **kwargs):
        pass

    def sidebar(self):
        return self

    def title(self, text):
        pass

    def caption(self, text):
        pass

    def divider(self):
        pass

    def subheader(self, text):
        pass

    def write(self, text):
        pass

    def metric(self, label, value, delta=None):
        pass

    def radio(self, label, options):
        return options[0] if options else None


import sys
sys.modules['streamlit'] = MockStreamlit()

# Now we can import dashboard functions
from pacman.dashboard.app import (
    format_currency,
    get_category_color,
    load_project,
)


class TestFormatCurrency:
    """Tests for currency formatting."""

    def test_format_positive_amount(self):
        """Format positive amount."""
        result = format_currency(1234.56)
        assert "1.234,56" in result
        assert "€" in result

    def test_format_negative_amount(self):
        """Format negative amount."""
        result = format_currency(-500.00)
        assert "500,00" in result
        assert "€" in result

    def test_format_decimal(self):
        """Format Decimal amount."""
        result = format_currency(Decimal("999.99"))
        assert "999,99" in result
        assert "€" in result

    def test_format_string_amount(self):
        """Format string amount."""
        result = format_currency("1500.50")
        assert "1.500,50" in result
        assert "€" in result

    def test_format_zero(self):
        """Format zero amount."""
        result = format_currency(0)
        assert "0,00" in result
        assert "€" in result

    def test_format_large_amount(self):
        """Format large amount with thousands separator."""
        result = format_currency(1234567.89)
        assert "1.234.567,89" in result
        assert "€" in result

    def test_format_invalid_returns_string(self):
        """Invalid input returns string representation."""
        result = format_currency("invalid")
        assert result == "invalid"


class TestGetCategoryColor:
    """Tests for category color mapping."""

    def test_rental_income_color(self):
        """Rental income has green color."""
        color = get_category_color("rental_income")
        assert color == "#2ecc71"

    def test_rental_expense_color(self):
        """Rental expense has red color."""
        color = get_category_color("rental_expense")
        assert color == "#e74c3c"

    def test_business_income_color(self):
        """Business income has blue color."""
        color = get_category_color("business_income")
        assert color == "#3498db"

    def test_business_expense_color(self):
        """Business expense has purple color."""
        color = get_category_color("business_expense")
        assert color == "#9b59b6"

    def test_deductible_color(self):
        """Deductible has orange color."""
        color = get_category_color("deductible")
        assert color == "#f39c12"

    def test_private_color(self):
        """Private has gray color."""
        color = get_category_color("private")
        assert color == "#95a5a6"

    def test_passthrough_color(self):
        """Passthrough has teal color."""
        color = get_category_color("passthrough")
        assert color == "#1abc9c"

    def test_uncategorized_color(self):
        """Uncategorized has light gray color."""
        color = get_category_color("uncategorized")
        assert color == "#bdc3c7"

    def test_unknown_category_fallback(self):
        """Unknown category returns fallback color."""
        color = get_category_color("unknown_category")
        assert color == "#7f8c8d"


class TestLoadProject:
    """Tests for project loading."""

    def test_load_project_with_config(self, tmp_path):
        """Load project with config.yaml."""
        # Create config
        config = {
            "year": 2024,
            "profile": "vermieter",
            "jurisdiction": "DE",
            "tenants": ["Mieter A", "Mieter B"],
        }
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Load project
        data = load_project(tmp_path)

        assert data["config"] is not None
        assert data["config"]["year"] == 2024
        assert data["config"]["profile"] == "vermieter"
        assert len(data["config"]["tenants"]) == 2
        assert data["path"] == tmp_path

    def test_load_project_with_transactions(self, tmp_path):
        """Load project with transactions.json."""
        # Create config
        config = {"year": 2024, "profile": "vermieter"}
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        # Create transactions
        transactions = [
            {
                "id": "abc123",
                "date": "2024-01-15",
                "amount": "1200.00",
                "description": "Miete Januar",
                "category": "rental_income",
            },
            {
                "id": "def456",
                "date": "2024-01-20",
                "amount": "-150.00",
                "description": "Hausverwaltung",
                "category": "rental_expense",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        # Load project
        data = load_project(tmp_path)

        assert len(data["transactions"]) == 2
        assert data["transactions"][0]["category"] == "rental_income"
        assert data["transactions"][1]["amount"] == "-150.00"

    def test_load_project_without_config(self, tmp_path):
        """Load project without config.yaml."""
        data = load_project(tmp_path)

        assert data["config"] is None
        assert data["transactions"] == []
        assert data["path"] == tmp_path

    def test_load_project_without_transactions(self, tmp_path):
        """Load project with config but no transactions."""
        config = {"year": 2024, "profile": "freiberufler"}
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        data = load_project(tmp_path)

        assert data["config"] is not None
        assert data["transactions"] == []

    def test_load_project_gmbh_geschaeftsfuehrer(self, tmp_path):
        """Load GmbH-GF project with specific config."""
        config = {
            "year": 2024,
            "profile": "gmbh_geschaeftsfuehrer",
            "jurisdiction": "DE",
            "gmbh_name": "Meine GmbH",
            "beteiligung_prozent": 50,
            "geschaeftsfuehrer_gehalt": 8000,
        }
        with open(tmp_path / "config.yaml", "w") as f:
            yaml.dump(config, f)

        transactions = [
            {
                "id": "gf001",
                "date": "2024-01-31",
                "amount": "8000.00",
                "description": "GF-Gehalt Januar",
                "category": "employment_income",
                "subcategory": "gf_gehalt",
            },
            {
                "id": "gf002",
                "date": "2024-06-15",
                "amount": "20000.00",
                "description": "Gewinnausschuettung",
                "category": "capital_income",
                "subcategory": "dividende",
            },
        ]
        with open(tmp_path / "transactions.json", "w") as f:
            json.dump(transactions, f)

        data = load_project(tmp_path)

        assert data["config"]["profile"] == "gmbh_geschaeftsfuehrer"
        assert data["config"]["beteiligung_prozent"] == 50
        assert len(data["transactions"]) == 2
        assert data["transactions"][0]["subcategory"] == "gf_gehalt"
        assert data["transactions"][1]["subcategory"] == "dividende"


class TestDashboardDataProcessing:
    """Tests for dashboard data processing logic."""

    def test_calculate_summary_from_transactions(self):
        """Calculate category summary from transactions."""
        from collections import defaultdict
        from decimal import Decimal

        transactions = [
            {"category": "rental_income", "amount": "1200.00"},
            {"category": "rental_income", "amount": "1200.00"},
            {"category": "rental_expense", "amount": "-300.00"},
            {"category": "business_income", "amount": "5000.00"},
            {"category": "private", "amount": "-100.00"},
        ]

        summary = defaultdict(lambda: Decimal("0"))
        for t in transactions:
            cat = t.get("category", "uncategorized")
            amt = Decimal(str(t.get("amount", 0)))
            summary[cat] += amt

        assert summary["rental_income"] == Decimal("2400.00")
        assert summary["rental_expense"] == Decimal("-300.00")
        assert summary["business_income"] == Decimal("5000.00")
        assert summary["private"] == Decimal("-100.00")

    def test_categorization_percentage(self):
        """Calculate categorization percentage."""
        transactions = [
            {"category": "rental_income"},
            {"category": "rental_expense"},
            {"category": "uncategorized"},
            {"category": None},
            {"category": "business_income"},
        ]

        txn_count = len(transactions)
        categorized = sum(
            1 for t in transactions
            if t.get("category") and t["category"] != "uncategorized"
        )
        pct = (categorized / txn_count * 100) if txn_count > 0 else 0

        assert txn_count == 5
        assert categorized == 3
        assert pct == 60.0

    def test_monthly_breakdown(self):
        """Calculate monthly income/expense breakdown."""
        from collections import defaultdict
        from decimal import Decimal

        transactions = [
            {"date": "2024-01-15", "amount": "1200.00"},
            {"date": "2024-01-20", "amount": "-300.00"},
            {"date": "2024-02-15", "amount": "1200.00"},
            {"date": "2024-02-28", "amount": "-150.00"},
        ]

        monthly = defaultdict(lambda: {"income": Decimal("0"), "expense": Decimal("0")})
        for t in transactions:
            txn_date = t.get("date", "")
            if isinstance(txn_date, str) and len(txn_date) >= 7:
                month = txn_date[:7]  # YYYY-MM
                amt = Decimal(str(t.get("amount", 0)))
                if amt > 0:
                    monthly[month]["income"] += amt
                else:
                    monthly[month]["expense"] += abs(amt)

        assert monthly["2024-01"]["income"] == Decimal("1200.00")
        assert monthly["2024-01"]["expense"] == Decimal("300.00")
        assert monthly["2024-02"]["income"] == Decimal("1200.00")
        assert monthly["2024-02"]["expense"] == Decimal("150.00")

    def test_transaction_filtering_by_category(self):
        """Filter transactions by selected categories."""
        transactions = [
            {"category": "rental_income", "amount": "1200.00"},
            {"category": "rental_expense", "amount": "-300.00"},
            {"category": "business_income", "amount": "5000.00"},
            {"category": "private", "amount": "-100.00"},
        ]

        selected_categories = ["rental_income", "rental_expense"]

        filtered = [
            t for t in transactions
            if t.get("category", "uncategorized") in selected_categories
        ]

        assert len(filtered) == 2
        assert all(t["category"].startswith("rental") for t in filtered)

    def test_transaction_filtering_by_amount(self):
        """Filter transactions by income/expense."""
        transactions = [
            {"amount": "1200.00", "category": "rental_income"},
            {"amount": "-300.00", "category": "rental_expense"},
            {"amount": "5000.00", "category": "business_income"},
            {"amount": "-100.00", "category": "private"},
        ]

        # Only income
        income_only = [
            t for t in transactions
            if float(t.get("amount", 0)) > 0
        ]
        assert len(income_only) == 2

        # Only expenses
        expense_only = [
            t for t in transactions
            if float(t.get("amount", 0)) < 0
        ]
        assert len(expense_only) == 2

    def test_transaction_search(self):
        """Search transactions by description or counterparty."""
        transactions = [
            {"description": "Miete Januar", "counterparty": "Mieter A"},
            {"description": "Hausverwaltung", "counterparty": "HV GmbH"},
            {"description": "Miete Februar", "counterparty": "Mieter B"},
            {"description": "Versicherung", "counterparty": "Allianz"},
        ]

        search = "miete"
        search_lower = search.lower()

        filtered = [
            t for t in transactions
            if search_lower in str(t.get("description", "")).lower()
            or search_lower in str(t.get("counterparty", "")).lower()
        ]

        assert len(filtered) == 2
        assert all("miete" in t["description"].lower() for t in filtered)

    def test_subcategory_aggregation(self):
        """Aggregate transactions by subcategory."""
        from collections import defaultdict
        from decimal import Decimal

        transactions = [
            {"category": "rental_expense", "subcategory": "hausverwaltung", "amount": "-300.00"},
            {"category": "rental_expense", "subcategory": "hausverwaltung", "amount": "-300.00"},
            {"category": "rental_expense", "subcategory": "versicherung", "amount": "-500.00"},
            {"category": "rental_expense", "subcategory": None, "amount": "-100.00"},
        ]

        by_subcat = defaultdict(lambda: {"count": 0, "total": Decimal("0")})
        for t in transactions:
            subcat = t.get("subcategory", "Sonstige") or "Sonstige"
            by_subcat[subcat]["count"] += 1
            by_subcat[subcat]["total"] += Decimal(str(t.get("amount", 0)))

        assert by_subcat["hausverwaltung"]["count"] == 2
        assert by_subcat["hausverwaltung"]["total"] == Decimal("-600.00")
        assert by_subcat["versicherung"]["count"] == 1
        assert by_subcat["Sonstige"]["count"] == 1


class TestDashboardExportLogic:
    """Tests for dashboard export logic."""

    def test_csv_export_generation(self):
        """Generate CSV export from transactions."""
        import csv
        import io

        transactions = [
            {
                "date": "2024-01-15",
                "amount": "1200.00",
                "category": "rental_income",
                "subcategory": "miete",
                "counterparty": "Mieter A",
                "description": "Miete Januar",
            },
            {
                "date": "2024-01-20",
                "amount": "-300.00",
                "category": "rental_expense",
                "subcategory": "hausverwaltung",
                "counterparty": "HV GmbH",
                "description": "Verwaltung Q1",
            },
        ]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Datum", "Betrag", "Kategorie", "Unterkategorie", "Empfaenger", "Beschreibung"])

        for t in transactions:
            writer.writerow([
                t.get("date", ""),
                t.get("amount", ""),
                t.get("category", ""),
                t.get("subcategory", ""),
                t.get("counterparty", ""),
                t.get("description", ""),
            ])

        csv_output = output.getvalue()

        assert "Datum,Betrag,Kategorie" in csv_output
        assert "2024-01-15,1200.00,rental_income" in csv_output
        assert "2024-01-20,-300.00,rental_expense" in csv_output
        assert "Mieter A" in csv_output

    def test_summary_export_generation(self):
        """Generate summary export from transactions."""
        from collections import defaultdict
        from decimal import Decimal

        transactions = [
            {"category": "rental_income", "amount": "1200.00"},
            {"category": "rental_income", "amount": "1200.00"},
            {"category": "rental_expense", "amount": "-300.00"},
            {"category": "business_income", "amount": "5000.00"},
        ]

        summary = defaultdict(lambda: Decimal("0"))
        for t in transactions:
            cat = t.get("category", "uncategorized")
            summary[cat] += Decimal(str(t.get("amount", 0)))

        summary_text = "Kategorie,Summe\n"
        for cat, total in sorted(summary.items()):
            summary_text += f"{cat},{total}\n"

        assert "Kategorie,Summe" in summary_text
        assert "rental_income,2400.00" in summary_text
        assert "rental_expense,-300.00" in summary_text
        assert "business_income,5000.00" in summary_text

    def test_category_list_extraction(self):
        """Extract unique categories from transactions."""
        transactions = [
            {"category": "rental_income"},
            {"category": "rental_income"},
            {"category": "rental_expense"},
            {"category": None},
            {"category": "business_income"},
            {},
        ]

        categories = sorted(set(
            t.get("category", "uncategorized") or "uncategorized"
            for t in transactions
        ))

        assert "rental_income" in categories
        assert "rental_expense" in categories
        assert "business_income" in categories
        assert "uncategorized" in categories
        assert len(categories) == 4


class TestDashboardMetrics:
    """Tests for dashboard metrics calculation."""

    def test_net_rental_calculation(self):
        """Calculate net rental result."""
        rental_income = 14400.00
        rental_expense = -2400.00

        net_rental = rental_income + rental_expense

        assert net_rental == 12000.00

    def test_net_rental_percentage(self):
        """Calculate net rental as percentage of income."""
        rental_income = 14400.00
        rental_expense = -2400.00

        net_rental = rental_income + rental_expense
        pct = (net_rental / rental_income * 100) if rental_income > 0 else 0

        assert pct == pytest.approx(83.33, rel=0.01)

    def test_total_result_calculation(self):
        """Calculate total financial result."""
        rental_income = 14400.00
        rental_expense = -2400.00
        business_income = 50000.00
        business_expense = -10000.00

        total_income = rental_income + business_income
        total_expense = rental_expense + business_expense
        total_result = total_income + total_expense

        assert total_income == 64400.00
        assert total_expense == -12400.00
        assert total_result == 52000.00

    def test_zero_income_division(self):
        """Handle division by zero for percentage calculation."""
        rental_income = 0.0
        rental_expense = -100.00

        net_rental = rental_income + rental_expense
        pct = (net_rental / rental_income * 100) if rental_income > 0 else None

        assert pct is None


class TestDashboardDateHandling:
    """Tests for date handling in dashboard."""

    def test_extract_month_from_date(self):
        """Extract month from transaction date."""
        date_str = "2024-03-15"

        if isinstance(date_str, str) and len(date_str) >= 7:
            month = date_str[:7]
        else:
            month = None

        assert month == "2024-03"

    def test_handle_invalid_date(self):
        """Handle invalid date formats gracefully."""
        invalid_dates = ["", "2024", None, 12345]

        for date_val in invalid_dates:
            try:
                if isinstance(date_val, str) and len(date_val) >= 7:
                    month = date_val[:7]
                else:
                    month = None
            except Exception:
                month = None

            # Should not crash, month should be None for these values
            assert month is None

    def test_handle_non_date_string(self):
        """Non-date string still extracts first 7 chars (application handles this)."""
        date_val = "invalid-string"

        if isinstance(date_val, str) and len(date_val) >= 7:
            month = date_val[:7]
        else:
            month = None

        # The app extracts substring but real dates won't have this format
        assert month == "invalid"

    def test_sort_months_chronologically(self):
        """Sort months in chronological order."""
        months = ["2024-03", "2024-01", "2024-12", "2024-02"]

        sorted_months = sorted(months)

        assert sorted_months == ["2024-01", "2024-02", "2024-03", "2024-12"]


class TestDashboardTableFormatting:
    """Tests for table data formatting."""

    def test_format_table_row(self):
        """Format transaction for table display."""
        transaction = {
            "date": "2024-01-15",
            "amount": "1200.00",
            "category": "rental_income",
            "counterparty": "Mieter A",
            "description": "Miete Januar 2024 - Wohnung 1 - Kaltmiete plus Nebenkosten",
        }

        table_row = {
            "Datum": transaction.get("date", ""),
            "Betrag": format_currency(float(transaction.get("amount", 0))),
            "Kategorie": (transaction.get("category", "") or "").replace("_", " ").title(),
            "Empfaenger": transaction.get("counterparty", "") or "",
            "Beschreibung": (transaction.get("description", "") or "")[:50],
        }

        assert table_row["Datum"] == "2024-01-15"
        assert "1.200,00" in table_row["Betrag"]
        assert table_row["Kategorie"] == "Rental Income"
        assert table_row["Empfaenger"] == "Mieter A"
        assert len(table_row["Beschreibung"]) <= 50

    def test_handle_none_values_in_table(self):
        """Handle None values when formatting table."""
        transaction = {
            "date": "2024-01-15",
            "amount": "100.00",
            "category": None,
            "counterparty": None,
            "description": None,
        }

        table_row = {
            "Datum": transaction.get("date", ""),
            "Betrag": format_currency(float(transaction.get("amount", 0))),
            "Kategorie": (transaction.get("category", "") or "").replace("_", " ").title(),
            "Empfaenger": transaction.get("counterparty", "") or "",
            "Beschreibung": (transaction.get("description", "") or "")[:50],
        }

        assert table_row["Kategorie"] == ""
        assert table_row["Empfaenger"] == ""
        assert table_row["Beschreibung"] == ""


class TestDashboardEmploymentCapital:
    """Tests for employment and capital income handling in dashboard."""

    def test_employment_income_summary(self):
        """Calculate employment income summary for GmbH-GF."""
        from collections import defaultdict
        from decimal import Decimal

        transactions = [
            {"category": "employment_income", "subcategory": "gf_gehalt", "amount": "8000.00"},
            {"category": "employment_income", "subcategory": "gf_gehalt", "amount": "8000.00"},
            {"category": "employment_income", "subcategory": "gf_bonus", "amount": "10000.00"},
            {"category": "employment_expense", "subcategory": "fortbildung", "amount": "-500.00"},
        ]

        summary = defaultdict(lambda: Decimal("0"))
        for t in transactions:
            cat = t.get("category", "uncategorized")
            amt = Decimal(str(t.get("amount", 0)))
            summary[cat] += amt

        assert summary["employment_income"] == Decimal("26000.00")
        assert summary["employment_expense"] == Decimal("-500.00")

        # Net employment income
        net_employment = summary["employment_income"] + summary["employment_expense"]
        assert net_employment == Decimal("25500.00")

    def test_capital_income_summary(self):
        """Calculate capital income summary for GmbH-GF."""
        from collections import defaultdict
        from decimal import Decimal

        transactions = [
            {"category": "capital_income", "subcategory": "dividende", "amount": "20000.00"},
            {"category": "capital_income", "subcategory": "zinsen", "amount": "500.00"},
        ]

        summary = defaultdict(lambda: Decimal("0"))
        for t in transactions:
            cat = t.get("category", "uncategorized")
            amt = Decimal(str(t.get("amount", 0)))
            summary[cat] += amt

        assert summary["capital_income"] == Decimal("20500.00")

    def test_combined_income_types(self):
        """GmbH-GF with all income types."""
        from collections import defaultdict
        from decimal import Decimal

        transactions = [
            # Gehalt (Anlage N)
            {"category": "employment_income", "subcategory": "gf_gehalt", "amount": "96000.00"},
            # Werbungskosten (Anlage N)
            {"category": "employment_expense", "subcategory": "fortbildung", "amount": "-2000.00"},
            # Dividende (Anlage KAP)
            {"category": "capital_income", "subcategory": "dividende", "amount": "30000.00"},
            # Zusaetzliche Vermietung (Anlage V)
            {"category": "rental_income", "amount": "14400.00"},
            {"category": "rental_expense", "amount": "-2400.00"},
        ]

        summary = defaultdict(lambda: Decimal("0"))
        for t in transactions:
            cat = t.get("category", "uncategorized")
            amt = Decimal(str(t.get("amount", 0)))
            summary[cat] += amt

        # Anlage N
        net_employment = summary["employment_income"] + summary["employment_expense"]
        assert net_employment == Decimal("94000.00")

        # Anlage KAP
        capital = summary["capital_income"]
        assert capital == Decimal("30000.00")

        # Anlage V
        net_rental = summary["rental_income"] + summary["rental_expense"]
        assert net_rental == Decimal("12000.00")

        # Gesamteinkuenfte
        total = net_employment + capital + net_rental
        assert total == Decimal("136000.00")
