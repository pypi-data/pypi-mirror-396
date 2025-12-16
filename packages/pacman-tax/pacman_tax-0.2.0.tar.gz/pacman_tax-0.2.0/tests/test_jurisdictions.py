"""
Tests for PACMAN Jurisdictions Module.

Tests German tax plugin, constants, and calculations.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from pacman.core.models import TaxCategory, TaxYear, Transaction
from pacman.jurisdictions import discover_plugins, get_plugin, list_plugins
from pacman.jurisdictions.base import JurisdictionPlugin, TaxResult
from pacman.jurisdictions.germany import GermanyPlugin
from pacman.jurisdictions.germany.constants import TAX_CONSTANTS, get_constants


class TestTaxResult:
    """Tests for TaxResult class."""

    def test_init_defaults(self):
        """Test TaxResult initializes with zero values."""
        result = TaxResult()

        assert result.income_total == Decimal("0")
        assert result.expenses_total == Decimal("0")
        assert result.deductibles_total == Decimal("0")
        assert result.taxable_income == Decimal("0")
        assert result.tax_due == Decimal("0")
        assert result.forms == {}
        assert result.warnings == []
        assert result.notes == []

    def test_add_form_data(self):
        """Test adding form data."""
        result = TaxResult()
        form_data = {"zeile_21": "1000", "zeile_33": "200"}

        result.add_form_data("Anlage_V", form_data)

        assert "Anlage_V" in result.forms
        assert result.forms["Anlage_V"]["zeile_21"] == "1000"

    def test_add_multiple_forms(self):
        """Test adding multiple form data."""
        result = TaxResult()

        result.add_form_data("Anlage_V", {"value": "100"})
        result.add_form_data("Anlage_G", {"value": "200"})

        assert len(result.forms) == 2
        assert "Anlage_V" in result.forms
        assert "Anlage_G" in result.forms

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = TaxResult()
        result.income_total = Decimal("1000.50")
        result.expenses_total = Decimal("500.25")
        result.taxable_income = Decimal("500.25")
        result.add_form_data("Anlage_V", {"test": "value"})
        result.notes.append("Test note")
        result.warnings.append("Test warning")

        data = result.to_dict()

        assert data["income_total"] == "1000.50"
        assert data["expenses_total"] == "500.25"
        assert data["taxable_income"] == "500.25"
        assert data["forms"]["Anlage_V"]["test"] == "value"
        assert "Test note" in data["notes"]
        assert "Test warning" in data["warnings"]


class TestTaxConstants:
    """Tests for German tax constants."""

    def test_2023_grundfreibetrag(self):
        """Test 2023 Grundfreibetrag."""
        assert TAX_CONSTANTS[2023]["grundfreibetrag"] == 10908

    def test_2024_grundfreibetrag(self):
        """Test 2024 Grundfreibetrag."""
        assert TAX_CONSTANTS[2024]["grundfreibetrag"] == 11604

    def test_2025_grundfreibetrag(self):
        """Test 2025 Grundfreibetrag."""
        assert TAX_CONSTANTS[2025]["grundfreibetrag"] == 12084

    def test_gewerbe_freibetrag_constant(self):
        """Test Gewerbesteuer-Freibetrag is 24500."""
        for year in TAX_CONSTANTS:
            assert TAX_CONSTANTS[year]["gewerbe_freibetrag"] == 24500

    def test_kleinunternehmer_grenze_2024(self):
        """Test Kleinunternehmerregelung threshold 2024."""
        assert TAX_CONSTANTS[2024]["kleinunternehmer_grenze"] == 22000

    def test_kleinunternehmer_grenze_2025_increased(self):
        """Test Kleinunternehmerregelung threshold increased in 2025."""
        assert TAX_CONSTANTS[2025]["kleinunternehmer_grenze"] == 25000

    def test_euer_grenzen_2025_increased(self):
        """Test EÜR thresholds increased in 2025."""
        assert TAX_CONSTANTS[2025]["euer_grenze_umsatz"] == 800000
        assert TAX_CONSTANTS[2025]["euer_grenze_gewinn"] == 80000

    def test_get_constants_valid_year(self):
        """Test get_constants with valid year."""
        constants = get_constants(2024)
        assert constants["grundfreibetrag"] == 11604

    def test_get_constants_fallback_to_latest(self):
        """Test get_constants falls back to latest for unknown year."""
        constants = get_constants(2030)
        # Should return 2025 values (latest)
        assert constants["grundfreibetrag"] == 12084

    def test_get_constants_past_year(self):
        """Test get_constants with past year returns latest."""
        constants = get_constants(2020)
        # Should return 2025 values (latest available)
        assert constants["grundfreibetrag"] == 12084


class TestPluginDiscovery:
    """Tests for plugin discovery system."""

    def test_discover_plugins_returns_dict(self):
        """Test that discover_plugins returns a dict."""
        plugins = discover_plugins()
        assert isinstance(plugins, dict)

    def test_germany_plugin_discovered(self):
        """Test that Germany plugin is discovered."""
        plugins = discover_plugins()
        assert "DE" in plugins

    def test_get_plugin_germany(self):
        """Test getting Germany plugin by code."""
        plugin = get_plugin("DE")
        assert isinstance(plugin, GermanyPlugin)
        assert plugin.code == "DE"

    def test_get_plugin_invalid_code(self):
        """Test KeyError for invalid plugin code."""
        with pytest.raises(KeyError, match="not found"):
            get_plugin("INVALID")

    def test_list_plugins(self):
        """Test listing available plugins."""
        codes = list_plugins()
        assert "DE" in codes


class TestGermanyPlugin:
    """Tests for Germany plugin."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        """Create Germany plugin instance."""
        return GermanyPlugin()

    def test_code(self, plugin: GermanyPlugin):
        """Test plugin code."""
        assert plugin.code == "DE"

    def test_name(self, plugin: GermanyPlugin):
        """Test plugin name."""
        assert plugin.name == "Deutschland"

    def test_supported_profiles(self, plugin: GermanyPlugin):
        """Test supported profiles."""
        profiles = plugin.supported_profiles
        assert "vermieter" in profiles
        assert "einzelunternehmer" in profiles
        assert "freiberufler" in profiles

    def test_validate_profile_valid(self, plugin: GermanyPlugin):
        """Test profile validation with valid profile."""
        # Should not raise
        plugin.validate_profile("vermieter")
        plugin.validate_profile("einzelunternehmer")
        plugin.validate_profile("freiberufler")

    def test_validate_profile_invalid(self, plugin: GermanyPlugin):
        """Test profile validation with invalid profile."""
        with pytest.raises(ValueError, match="not supported"):
            plugin.validate_profile("invalid_profile")

    def test_get_tax_constants_2024(self, plugin: GermanyPlugin):
        """Test getting tax constants for 2024."""
        constants = plugin.get_tax_constants(2024)
        assert constants["grundfreibetrag"] == 11604

    def test_get_tax_constants_unknown_year_fallback(self, plugin: GermanyPlugin):
        """Test getting tax constants for unknown year falls back."""
        constants = plugin.get_tax_constants(2099)
        # Should fall back to latest (2025)
        assert constants["grundfreibetrag"] == 12084

    def test_get_rules_returns_list(self, plugin: GermanyPlugin):
        """Test get_rules returns a list."""
        rules = plugin.get_rules("vermieter")
        assert isinstance(rules, list)

    def test_get_categorizer(self, plugin: GermanyPlugin):
        """Test getting a categorizer for profile."""
        from pacman.core.categorizer import Categorizer

        categorizer = plugin.get_categorizer("vermieter")
        assert isinstance(categorizer, Categorizer)


class TestGermanyTaxCalculation:
    """Tests for Germany tax calculation."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    @pytest.fixture
    def rental_transactions(self) -> list[Transaction]:
        """Create sample rental transactions."""
        return [
            Transaction(
                date=date(2024, 1, 5),
                amount=Decimal("850.00"),
                description="Miete Januar",
                category=TaxCategory.RENTAL_INCOME,
            ),
            Transaction(
                date=date(2024, 2, 5),
                amount=Decimal("850.00"),
                description="Miete Februar",
                category=TaxCategory.RENTAL_INCOME,
            ),
            Transaction(
                date=date(2024, 1, 15),
                amount=Decimal("-200.00"),
                description="Hausverwaltung",
                category=TaxCategory.RENTAL_EXPENSE,
                subcategory="verwaltung",
            ),
        ]

    @pytest.fixture
    def business_transactions(self) -> list[Transaction]:
        """Create sample business transactions."""
        return [
            Transaction(
                date=date(2024, 1, 10),
                amount=Decimal("5000.00"),
                description="Honorar Projekt A",
                category=TaxCategory.BUSINESS_INCOME,
            ),
            Transaction(
                date=date(2024, 1, 20),
                amount=Decimal("-500.00"),
                description="Software Lizenz",
                category=TaxCategory.BUSINESS_EXPENSE,
                subcategory="software",
            ),
        ]

    def test_calculate_vermieter(
        self, plugin: GermanyPlugin, rental_transactions: list[Transaction]
    ):
        """Test tax calculation for Vermieter profile."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="vermieter",
            transactions=rental_transactions,
        )

        result = plugin.calculate(tax_year)

        assert result.income_total >= Decimal("0")
        assert "Anlage_V" in result.forms

    def test_calculate_vermieter_anlage_v_fields(
        self, plugin: GermanyPlugin, rental_transactions: list[Transaction]
    ):
        """Test Anlage V fields are populated."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="vermieter",
            transactions=rental_transactions,
        )

        result = plugin.calculate(tax_year)
        anlage_v = result.forms.get("Anlage_V", {})

        assert "zeile_21_mieteinnahmen" in anlage_v
        assert "zeile_33_werbungskosten" in anlage_v
        assert "zeile_22_einkuenfte" in anlage_v

    def test_calculate_einzelunternehmer(
        self, plugin: GermanyPlugin, business_transactions: list[Transaction]
    ):
        """Test tax calculation for Einzelunternehmer profile."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="einzelunternehmer",
            transactions=business_transactions,
        )

        result = plugin.calculate(tax_year)

        assert "Anlage_G" in result.forms
        assert "Anlage_EUR" in result.forms

    def test_calculate_einzelunternehmer_euer_fields(
        self, plugin: GermanyPlugin, business_transactions: list[Transaction]
    ):
        """Test EÜR fields are populated."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="einzelunternehmer",
            transactions=business_transactions,
        )

        result = plugin.calculate(tax_year)
        euer = result.forms.get("Anlage_EUR", {})

        assert "zeile_11_einnahmen" in euer
        assert "zeile_60_ausgaben" in euer
        assert "zeile_67_gewinn_verlust" in euer

    def test_calculate_freiberufler(
        self, plugin: GermanyPlugin, business_transactions: list[Transaction]
    ):
        """Test tax calculation for Freiberufler profile."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="freiberufler",
            transactions=business_transactions,
        )

        result = plugin.calculate(tax_year)

        assert "Anlage_S" in result.forms
        # Freiberufler should NOT have Anlage_G
        assert "Anlage_G" not in result.forms

    def test_calculate_freiberufler_anlage_s_fields(
        self, plugin: GermanyPlugin, business_transactions: list[Transaction]
    ):
        """Test Anlage S fields are populated."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="freiberufler",
            transactions=business_transactions,
        )

        result = plugin.calculate(tax_year)
        anlage_s = result.forms.get("Anlage_S", {})

        assert "zeile_4" in anlage_s
        assert "zeile_5_einnahmen" in anlage_s
        assert "zeile_6_ausgaben" in anlage_s
        assert "zeile_7_gewinn" in anlage_s

    def test_calculate_unter_grundfreibetrag(self, plugin: GermanyPlugin):
        """Test tax calculation when income is below Grundfreibetrag."""
        # Small income below Grundfreibetrag
        transactions = [
            Transaction(
                date=date(2024, 1, 1),
                amount=Decimal("5000.00"),
                description="Kleine Einnahme",
                category=TaxCategory.BUSINESS_INCOME,
            ),
        ]
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="freiberufler",
            transactions=transactions,
        )

        result = plugin.calculate(tax_year)

        # Taxable income 5000 < Grundfreibetrag 11604
        assert result.tax_due == Decimal("0")
        assert any("Grundfreibetrag" in note for note in result.notes)

    def test_calculate_empty_transactions(self, plugin: GermanyPlugin):
        """Test calculation with no transactions."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="vermieter",
            transactions=[],
        )

        result = plugin.calculate(tax_year)

        assert result.income_total == Decimal("0")
        assert result.taxable_income == Decimal("0")


class TestGermanyExport:
    """Tests for Germany export functionality."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    @pytest.fixture
    def tax_year(self) -> TaxYear:
        """Create a tax year with sample transactions."""
        transactions = [
            Transaction(
                date=date(2024, 1, 5),
                amount=Decimal("1000.00"),
                description="Test Income",
                category=TaxCategory.BUSINESS_INCOME,
            ),
            Transaction(
                date=date(2024, 1, 10),
                amount=Decimal("-100.00"),
                description="Test Expense",
                category=TaxCategory.BUSINESS_EXPENSE,
            ),
        ]
        return TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="einzelunternehmer",
            transactions=transactions,
        )

    def test_export_xlsx(
        self, plugin: GermanyPlugin, tax_year: TaxYear, tmp_path: Path
    ):
        """Test XLSX export."""
        output_path = plugin.export(tax_year, "xlsx", tmp_path)

        assert output_path.exists()
        assert output_path.suffix == ".xlsx"
        assert "ELSTER" in output_path.name

    def test_export_xlsx_to_specific_file(
        self, plugin: GermanyPlugin, tax_year: TaxYear, tmp_path: Path
    ):
        """Test XLSX export to specific file path."""
        specific_path = tmp_path / "custom_export.xlsx"
        output_path = plugin.export(tax_year, "xlsx", specific_path)

        assert output_path == specific_path
        assert output_path.exists()

    def test_export_csv(
        self, plugin: GermanyPlugin, tax_year: TaxYear, tmp_path: Path
    ):
        """Test CSV export."""
        output_path = plugin.export(tax_year, "csv", tmp_path)

        assert output_path.exists()
        assert output_path.suffix == ".csv"

    def test_export_csv_content(
        self, plugin: GermanyPlugin, tax_year: TaxYear, tmp_path: Path
    ):
        """Test CSV export contains expected data."""
        output_path = plugin.export(tax_year, "csv", tmp_path)

        content = output_path.read_text(encoding="utf-8")
        assert "Datum" in content
        assert "Betrag" in content
        assert "Test Income" in content
        assert "Test Expense" in content

    def test_export_invalid_format(
        self, plugin: GermanyPlugin, tax_year: TaxYear, tmp_path: Path
    ):
        """Test export with invalid format raises error."""
        with pytest.raises(ValueError, match="Unsupported"):
            plugin.export(tax_year, "invalid_format", tmp_path)


class TestVermieterSpecificCalculations:
    """Tests specific to Vermieter profile calculations."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    def test_mieteinnahmen_calculation(self, plugin: GermanyPlugin):
        """Test Mieteinnahmen are correctly summed."""
        transactions = [
            Transaction(
                date=date(2024, 1, 1),
                amount=Decimal("800.00"),
                description="Miete Jan",
                category=TaxCategory.RENTAL_INCOME,
            ),
            Transaction(
                date=date(2024, 2, 1),
                amount=Decimal("800.00"),
                description="Miete Feb",
                category=TaxCategory.RENTAL_INCOME,
            ),
        ]
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="vermieter",
            transactions=transactions,
        )

        result = plugin.calculate(tax_year)
        anlage_v = result.forms.get("Anlage_V", {})

        # rohertrag should be 1600
        assert Decimal(anlage_v["rohertrag"]) == Decimal("1600")

    def test_werbungskosten_calculation(self, plugin: GermanyPlugin):
        """Test Werbungskosten are correctly summed."""
        transactions = [
            Transaction(
                date=date(2024, 1, 1),
                amount=Decimal("1000.00"),
                description="Miete",
                category=TaxCategory.RENTAL_INCOME,
            ),
            Transaction(
                date=date(2024, 1, 15),
                amount=Decimal("-100.00"),
                description="Reparatur",
                category=TaxCategory.RENTAL_EXPENSE,
            ),
            Transaction(
                date=date(2024, 1, 20),
                amount=Decimal("-50.00"),
                description="Verwaltung",
                category=TaxCategory.RENTAL_EXPENSE,
            ),
        ]
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="vermieter",
            transactions=transactions,
        )

        result = plugin.calculate(tax_year)
        anlage_v = result.forms.get("Anlage_V", {})

        # werbungskosten should be 150 (absolute value)
        assert Decimal(anlage_v["werbungskosten"]) == Decimal("150")

    def test_durchlaufposten_handling(self, plugin: GermanyPlugin):
        """Test passthrough items (Durchlaufposten) are handled."""
        transactions = [
            Transaction(
                date=date(2024, 1, 1),
                amount=Decimal("100.00"),
                description="Nebenkosten von Mieter",
                category=TaxCategory.PASSTHROUGH,
            ),
            Transaction(
                date=date(2024, 1, 15),
                amount=Decimal("-90.00"),
                description="Nebenkosten an Versorger",
                category=TaxCategory.PASSTHROUGH,
            ),
        ]
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="vermieter",
            transactions=transactions,
        )

        result = plugin.calculate(tax_year)

        # Passthrough items should be handled (net difference)
        assert result.income_total >= Decimal("0")


class TestFreiberuflerVsEinzelunternehmer:
    """Tests comparing Freiberufler and Einzelunternehmer profiles."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    @pytest.fixture
    def same_transactions(self) -> list[Transaction]:
        """Same transactions for both profiles."""
        return [
            Transaction(
                date=date(2024, 1, 1),
                amount=Decimal("10000.00"),
                description="Honorar",
                category=TaxCategory.BUSINESS_INCOME,
            ),
            Transaction(
                date=date(2024, 1, 15),
                amount=Decimal("-1000.00"),
                description="Buerokosten",
                category=TaxCategory.BUSINESS_EXPENSE,
            ),
        ]

    def test_freiberufler_no_anlage_g(
        self, plugin: GermanyPlugin, same_transactions: list[Transaction]
    ):
        """Test Freiberufler does NOT generate Anlage G."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="freiberufler",
            transactions=same_transactions,
        )

        result = plugin.calculate(tax_year)

        assert "Anlage_S" in result.forms
        assert "Anlage_G" not in result.forms

    def test_einzelunternehmer_has_anlage_g(
        self, plugin: GermanyPlugin, same_transactions: list[Transaction]
    ):
        """Test Einzelunternehmer generates Anlage G."""
        tax_year = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="einzelunternehmer",
            transactions=same_transactions,
        )

        result = plugin.calculate(tax_year)

        assert "Anlage_G" in result.forms
        assert "Anlage_EUR" in result.forms
        # Einzelunternehmer should NOT have Anlage_S
        assert "Anlage_S" not in result.forms

    def test_same_gewinn_calculation(
        self, plugin: GermanyPlugin, same_transactions: list[Transaction]
    ):
        """Test both profiles calculate same profit."""
        tax_year_fb = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="freiberufler",
            transactions=same_transactions,
        )
        tax_year_eu = TaxYear(
            year=2024,
            jurisdiction="DE",
            profile="einzelunternehmer",
            transactions=same_transactions,
        )

        result_fb = plugin.calculate(tax_year_fb)
        result_eu = plugin.calculate(tax_year_eu)

        # Both should have same profit (10000 - 1000 = 9000)
        gewinn_fb = Decimal(result_fb.forms["Anlage_S"]["gewinn_verlust"])
        gewinn_eu = Decimal(result_eu.forms["Anlage_G"]["gewinn_verlust"])

        assert gewinn_fb == gewinn_eu == Decimal("9000")


class TestAllProfilesLoad:
    """Tests that all 13 German tax profiles load correctly."""

    ALL_PROFILES = [
        # Basis-Profile
        "freiberufler",
        "einzelunternehmer",
        "vermieter",
        "kleinunternehmer",
        "gmbh_geschaeftsfuehrer",
        "nebenberuflich",
        # Branchen-Profile
        "it_freelancer",
        "berater_coach",
        "content_creator",
        "e_commerce",
        "handwerker",
        "kuenstler",
        "heilberufler",
    ]

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    @pytest.mark.parametrize("profile", ALL_PROFILES)
    def test_profile_loads_without_error(self, plugin: GermanyPlugin, profile: str):
        """Test each profile loads without YAML errors."""
        from pacman.core.categorizer import Categorizer

        categorizer = plugin.get_categorizer(profile)
        assert isinstance(categorizer, Categorizer)

    @pytest.mark.parametrize("profile", ALL_PROFILES)
    def test_profile_has_rules(self, plugin: GermanyPlugin, profile: str):
        """Test each profile has at least one rule."""
        rules = plugin.get_rules(profile)
        assert len(rules) > 0, f"Profile {profile} has no rules"

    @pytest.mark.parametrize("profile", ALL_PROFILES)
    def test_profile_rules_have_required_fields(
        self, plugin: GermanyPlugin, profile: str
    ):
        """Test all rules have required fields."""
        rules = plugin.get_rules(profile)
        for rule in rules:
            assert rule.id, f"Rule in {profile} missing id"
            assert rule.name, f"Rule {rule.id} in {profile} missing name"
            assert rule.category, f"Rule {rule.id} in {profile} missing category"


class TestProfileMetadata:
    """Tests for profile metadata and structure."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    def test_freiberufler_profile_structure(self, plugin: GermanyPlugin):
        """Test Freiberufler profile has expected structure."""
        rules = plugin.get_rules("freiberufler")
        rule_ids = [r.id for r in rules]

        # Check for income and expense rules
        assert any("income" in rid for rid in rule_ids)
        assert any("expense" in rid for rid in rule_ids)

    def test_kleinunternehmer_extends_freiberufler(self, plugin: GermanyPlugin):
        """Test Kleinunternehmer profile extends Freiberufler."""
        from pathlib import Path
        import yaml

        rules_dir = Path(__file__).parent.parent / "src/pacman/jurisdictions/germany/rules"
        with open(rules_dir / "kleinunternehmer.yaml") as f:
            data = yaml.safe_load(f)

        assert data.get("extends") == "freiberufler"

    def test_it_freelancer_extends_freiberufler(self, plugin: GermanyPlugin):
        """Test IT Freelancer profile extends Freiberufler."""
        from pathlib import Path
        import yaml

        rules_dir = Path(__file__).parent.parent / "src/pacman/jurisdictions/germany/rules"
        with open(rules_dir / "it_freelancer.yaml") as f:
            data = yaml.safe_load(f)

        assert data.get("extends") == "freiberufler"

    def test_heilberufler_has_ust_befreit_info(self, plugin: GermanyPlugin):
        """Test Heilberufler profile has USt-befreit information."""
        from pathlib import Path
        import yaml

        rules_dir = Path(__file__).parent.parent / "src/pacman/jurisdictions/germany/rules"
        with open(rules_dir / "heilberufler.yaml") as f:
            data = yaml.safe_load(f)

        besonderheiten = data.get("metadata", {}).get("besonderheiten", [])
        assert any("4 Nr. 14" in b for b in besonderheiten)


class TestProfileSpecificRules:
    """Tests for profile-specific rule content."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    def test_it_freelancer_has_cloud_rules(self, plugin: GermanyPlugin):
        """Test IT Freelancer has cloud service rules."""
        rules = plugin.get_rules("it_freelancer")
        rule_ids = [r.id for r in rules]

        # Should have rules for cloud services
        cloud_related = [rid for rid in rule_ids if "cloud" in rid or "saas" in rid]
        assert len(cloud_related) > 0

    def test_content_creator_has_adsense_rules(self, plugin: GermanyPlugin):
        """Test Content Creator has AdSense rules."""
        rules = plugin.get_rules("content_creator")
        rule_ids = [r.id for r in rules]

        # Should have AdSense or YouTube income rules
        income_rules = [rid for rid in rule_ids if "adsense" in rid or "youtube" in rid]
        assert len(income_rules) > 0

    def test_handwerker_has_material_rules(self, plugin: GermanyPlugin):
        """Test Handwerker has material expense rules."""
        rules = plugin.get_rules("handwerker")
        rule_ids = [r.id for r in rules]

        # Should have material and tool rules
        material_rules = [
            rid for rid in rule_ids if "material" in rid or "werkzeug" in rid
        ]
        assert len(material_rules) > 0

    def test_kuenstler_has_ksk_rule(self, plugin: GermanyPlugin):
        """Test Künstler has KSK (Künstlersozialkasse) rule."""
        rules = plugin.get_rules("kuenstler")
        rule_ids = [r.id for r in rules]

        assert any("ksk" in rid for rid in rule_ids)

    def test_e_commerce_has_wareneinkauf_rules(self, plugin: GermanyPlugin):
        """Test E-Commerce has Wareneinkauf rules."""
        rules = plugin.get_rules("e_commerce")
        rule_ids = [r.id for r in rules]

        # Should have merchandise/warehouse rules
        warehouse_rules = [
            rid for rid in rule_ids if "waren" in rid or "einkauf" in rid
        ]
        assert len(warehouse_rules) > 0

    def test_gmbh_gf_has_gehalt_rule(self, plugin: GermanyPlugin):
        """Test GmbH-Geschäftsführer has salary rule."""
        rules = plugin.get_rules("gmbh_geschaeftsfuehrer")
        rule_ids = [r.id for r in rules]

        assert any("gehalt" in rid or "lohn" in rid for rid in rule_ids)

    def test_nebenberuflich_has_uebungsleiterpauschale(self, plugin: GermanyPlugin):
        """Test Nebenberuflich has Übungsleiterpauschale rule."""
        rules = plugin.get_rules("nebenberuflich")
        rule_ids = [r.id for r in rules]

        assert any("uebungsleiter" in rid or "ehrenamt" in rid for rid in rule_ids)


class TestProfileRuleCounts:
    """Tests to verify expected rule counts per profile."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    EXPECTED_MIN_RULES = {
        "freiberufler": 25,
        "einzelunternehmer": 20,
        "vermieter": 20,
        "kleinunternehmer": 5,
        "gmbh_geschaeftsfuehrer": 15,
        "nebenberuflich": 10,
        "it_freelancer": 15,
        "berater_coach": 20,
        "content_creator": 20,
        "e_commerce": 25,
        "handwerker": 20,
        "kuenstler": 20,
        "heilberufler": 25,
    }

    @pytest.mark.parametrize(
        "profile,min_rules",
        EXPECTED_MIN_RULES.items(),
    )
    def test_profile_has_minimum_rules(
        self, plugin: GermanyPlugin, profile: str, min_rules: int
    ):
        """Test each profile has expected minimum number of rules."""
        rules = plugin.get_rules(profile)
        assert len(rules) >= min_rules, (
            f"Profile {profile} has {len(rules)} rules, expected >= {min_rules}"
        )


class TestAnlageN:
    """Tests for Anlage N (Nichtselbständige Arbeit) calculation."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    def test_anlage_n_basic_salary(self, plugin: GermanyPlugin):
        """Test basic salary calculation for GmbH-GF."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Add 12 monthly salary payments
        for month in range(1, 13):
            tax_year.add_transaction(Transaction(
                date=date(2024, month, 28),
                amount=Decimal("8000.00"),
                description=f"GF-Gehalt {month:02d}/2024",
                category=TaxCategory.EMPLOYMENT_INCOME,
                subcategory="gf_gehalt",
            ))

        result = plugin.calculate(tax_year)

        assert "Anlage_N" in result.forms
        anlage_n = result.forms["Anlage_N"]
        assert Decimal(anlage_n["bruttoarbeitslohn"]) == Decimal("96000.00")

    def test_anlage_n_with_werbungskosten(self, plugin: GermanyPlugin):
        """Test salary with Werbungskosten exceeding Pauschbetrag."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Salary
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 28),
            amount=Decimal("96000.00"),
            description="GF-Gehalt Gesamt",
            category=TaxCategory.EMPLOYMENT_INCOME,
        ))

        # Werbungskosten (over Pauschbetrag of 1230)
        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 15),
            amount=Decimal("-3000.00"),
            description="Fortbildung MBA",
            category=TaxCategory.EMPLOYMENT_EXPENSE,
            subcategory="fortbildung",
        ))

        result = plugin.calculate(tax_year)

        anlage_n = result.forms["Anlage_N"]
        assert Decimal(anlage_n["werbungskosten"]) == Decimal("3000.00")
        assert Decimal(anlage_n["werbungskosten_effektiv"]) == Decimal("3000.00")
        # Einkünfte = 96000 - 3000 = 93000
        assert Decimal(anlage_n["einkuenfte"]) == Decimal("93000.00")

    def test_anlage_n_pauschbetrag_used_when_higher(self, plugin: GermanyPlugin):
        """Test Pauschbetrag is used when Werbungskosten are lower."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Salary
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 28),
            amount=Decimal("50000.00"),
            description="GF-Gehalt Gesamt",
            category=TaxCategory.EMPLOYMENT_INCOME,
        ))

        # Small Werbungskosten (under Pauschbetrag)
        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 15),
            amount=Decimal("-500.00"),
            description="Fachliteratur",
            category=TaxCategory.EMPLOYMENT_EXPENSE,
        ))

        result = plugin.calculate(tax_year)

        anlage_n = result.forms["Anlage_N"]
        assert Decimal(anlage_n["werbungskosten"]) == Decimal("500.00")
        # Pauschbetrag (1230) is higher, so it's used
        assert Decimal(anlage_n["werbungskosten_effektiv"]) == Decimal("1230")
        # Einkünfte = 50000 - 1230 = 48770
        assert Decimal(anlage_n["einkuenfte"]) == Decimal("48770")

    def test_anlage_n_with_bonus(self, plugin: GermanyPlugin):
        """Test salary plus bonus (Tantieme)."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Regular salary
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 28),
            amount=Decimal("96000.00"),
            description="GF-Gehalt",
            category=TaxCategory.EMPLOYMENT_INCOME,
            subcategory="gf_gehalt",
        ))

        # Bonus/Tantieme
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 31),
            amount=Decimal("24000.00"),
            description="Tantieme 2024",
            category=TaxCategory.EMPLOYMENT_INCOME,
            subcategory="gf_bonus",
        ))

        result = plugin.calculate(tax_year)

        anlage_n = result.forms["Anlage_N"]
        assert Decimal(anlage_n["bruttoarbeitslohn"]) == Decimal("120000.00")


class TestAnlageKAP:
    """Tests for Anlage KAP (Kapitalerträge) calculation."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    def test_anlage_kap_dividend(self, plugin: GermanyPlugin):
        """Test dividend calculation."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Dividend payment
        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 30),
            amount=Decimal("30000.00"),
            description="Gewinnausschüttung GmbH",
            category=TaxCategory.CAPITAL_INCOME,
            subcategory="dividende",
        ))

        result = plugin.calculate(tax_year)

        assert "Anlage_KAP" in result.forms
        anlage_kap = result.forms["Anlage_KAP"]
        assert Decimal(anlage_kap["kapitalertraege"]) == Decimal("30000.00")
        assert Decimal(anlage_kap["sparer_pauschbetrag"]) == Decimal("1000")
        # Einkünfte nach Abzug = 30000 - 1000 = 29000
        assert Decimal(anlage_kap["einkuenfte_nach_abzug"]) == Decimal("29000.00")

    def test_anlage_kap_abgeltungsteuer(self, plugin: GermanyPlugin):
        """Test Abgeltungsteuer calculation."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 30),
            amount=Decimal("11000.00"),
            description="Dividende",
            category=TaxCategory.CAPITAL_INCOME,
        ))

        result = plugin.calculate(tax_year)

        anlage_kap = result.forms["Anlage_KAP"]
        # Einkünfte = 11000 - 1000 = 10000
        einkuenfte = Decimal(anlage_kap["einkuenfte_nach_abzug"])
        assert einkuenfte == Decimal("10000.00")

        # Abgeltungsteuer = 10000 * 0.25 = 2500
        abgeltung = Decimal(anlage_kap["abgeltungsteuer"])
        assert abgeltung == Decimal("2500.00")

        # Soli = 2500 * 0.055 = 137.50
        soli = Decimal(anlage_kap["solidaritaetszuschlag"])
        assert soli == Decimal("137.50")

    def test_anlage_kap_under_pauschbetrag(self, plugin: GermanyPlugin):
        """Test capital income under Sparerpauschbetrag."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 30),
            amount=Decimal("500.00"),
            description="Zinsen",
            category=TaxCategory.CAPITAL_INCOME,
        ))

        result = plugin.calculate(tax_year)

        anlage_kap = result.forms["Anlage_KAP"]
        # Under Pauschbetrag: no tax
        assert Decimal(anlage_kap["einkuenfte_nach_abzug"]) == Decimal("0")
        assert Decimal(anlage_kap["abgeltungsteuer"]) == Decimal("0")

    def test_anlage_kap_interest_income(self, plugin: GermanyPlugin):
        """Test interest income from loans."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Interest from shareholder loan
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 31),
            amount=Decimal("2500.00"),
            description="Darlehenszinsen GmbH",
            category=TaxCategory.CAPITAL_INCOME,
            subcategory="zinsen",
        ))

        result = plugin.calculate(tax_year)

        anlage_kap = result.forms["Anlage_KAP"]
        assert Decimal(anlage_kap["kapitalertraege"]) == Decimal("2500.00")
        # Einkünfte = 2500 - 1000 = 1500
        assert Decimal(anlage_kap["einkuenfte_nach_abzug"]) == Decimal("1500.00")


class TestGmbHGFCompleteCalculation:
    """Tests for complete GmbH-GF tax calculation with all income types."""

    @pytest.fixture
    def plugin(self) -> GermanyPlugin:
        return GermanyPlugin()

    def test_gmbh_gf_all_income_types(self, plugin: GermanyPlugin):
        """Test GmbH-GF with salary, dividend, and rental income."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        # Employment income (Anlage N)
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 28),
            amount=Decimal("96000.00"),
            description="GF-Gehalt 2024",
            category=TaxCategory.EMPLOYMENT_INCOME,
        ))

        # Employment expenses
        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 15),
            amount=Decimal("-2000.00"),
            description="Fortbildung",
            category=TaxCategory.EMPLOYMENT_EXPENSE,
        ))

        # Capital income (Anlage KAP)
        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 30),
            amount=Decimal("20000.00"),
            description="Dividende",
            category=TaxCategory.CAPITAL_INCOME,
        ))

        # Rental income (Anlage V)
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 31),
            amount=Decimal("14400.00"),
            description="Mieteinnahmen",
            category=TaxCategory.RENTAL_INCOME,
        ))

        # Rental expense
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 31),
            amount=Decimal("-2400.00"),
            description="Hausverwaltung",
            category=TaxCategory.RENTAL_EXPENSE,
        ))

        result = plugin.calculate(tax_year)

        # All three Anlagen should be present
        assert "Anlage_N" in result.forms
        assert "Anlage_KAP" in result.forms
        assert "Anlage_V" in result.forms

        # Check individual calculations
        # Anlage N: 96000 - 2000 = 94000
        assert Decimal(result.forms["Anlage_N"]["einkuenfte"]) == Decimal("94000.00")

        # Anlage KAP: 20000 - 1000 = 19000
        assert Decimal(result.forms["Anlage_KAP"]["einkuenfte_nach_abzug"]) == Decimal("19000.00")

        # Anlage V: 14400 - 2400 = 12000
        assert Decimal(result.forms["Anlage_V"]["einkuenfte"]) == Decimal("12000")

        # Total income = 94000 + 19000 + 12000 = 125000
        assert result.income_total == Decimal("125000.00")

    def test_nebenberuflich_profile(self, plugin: GermanyPlugin):
        """Test Nebenberuflich profile with employment and business income."""
        tax_year = TaxYear(year=2024, profile="nebenberuflich")

        # Main employment income
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 28),
            amount=Decimal("60000.00"),
            description="Hauptberuf Gehalt",
            category=TaxCategory.EMPLOYMENT_INCOME,
        ))

        # Side business income
        tax_year.add_transaction(Transaction(
            date=date(2024, 12, 31),
            amount=Decimal("8000.00"),
            description="Nebentätigkeit Beratung",
            category=TaxCategory.BUSINESS_INCOME,
        ))

        result = plugin.calculate(tax_year)

        # Should have Anlage N for employment
        assert "Anlage_N" in result.forms
        # Should have Anlage G/EÜR for business
        assert "Anlage_G" in result.forms or "Anlage_EUR" in result.forms

    def test_tax_year_aggregates_employment_capital(self):
        """Test TaxYear correctly aggregates employment and capital income."""
        tax_year = TaxYear(year=2024, profile="gmbh_geschaeftsfuehrer")

        tax_year.add_transaction(Transaction(
            date=date(2024, 1, 31),
            amount=Decimal("8000.00"),
            description="Gehalt",
            category=TaxCategory.EMPLOYMENT_INCOME,
        ))

        tax_year.add_transaction(Transaction(
            date=date(2024, 6, 30),
            amount=Decimal("5000.00"),
            description="Dividende",
            category=TaxCategory.CAPITAL_INCOME,
        ))

        tax_year.add_transaction(Transaction(
            date=date(2024, 3, 15),
            amount=Decimal("-500.00"),
            description="Fortbildung",
            category=TaxCategory.EMPLOYMENT_EXPENSE,
        ))

        tax_year.calculate_aggregates()

        assert tax_year.income_employment == Decimal("8000.00")
        assert tax_year.income_capital == Decimal("5000.00")
        assert tax_year.expenses_employment == Decimal("500.00")
        assert tax_year.net_employment_income == Decimal("7500.00")
        assert tax_year.net_capital_income == Decimal("5000.00")


class TestTaxConstantsAnlageNKAP:
    """Tests for new tax constants for Anlage N and KAP."""

    def test_arbeitnehmer_pauschbetrag_2024(self):
        """Test Arbeitnehmer-Pauschbetrag for 2024."""
        assert TAX_CONSTANTS[2024]["arbeitnehmer_pauschbetrag"] == 1230

    def test_sparer_pauschbetrag_2024(self):
        """Test Sparer-Pauschbetrag for 2024."""
        assert TAX_CONSTANTS[2024]["sparer_pauschbetrag"] == 1000
        assert TAX_CONSTANTS[2024]["sparer_pauschbetrag_verheiratet"] == 2000

    def test_abgeltungsteuer_satz(self):
        """Test Abgeltungsteuer rate is 25%."""
        for year in TAX_CONSTANTS:
            assert TAX_CONSTANTS[year]["abgeltungsteuer_satz"] == 0.25
