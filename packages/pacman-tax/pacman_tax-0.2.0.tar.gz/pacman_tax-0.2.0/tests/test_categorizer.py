"""
Tests for PACMAN Categorizer.

Tests the YAML-based rules engine for transaction categorization.
"""

from datetime import date
from decimal import Decimal

import pytest

from pacman.core.categorizer import (
    CategorizationRule,
    Categorizer,
    RuleCondition,
)
from pacman.core.models import TaxCategory, Transaction


class TestRuleCondition:
    """Tests for RuleCondition matching."""

    def test_contains_operator(self):
        """Test 'contains' operator."""
        condition = RuleCondition(
            field="description",
            operator="contains",
            value="Miete",
        )
        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete Januar 2024",
        )
        txn_no_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("100"),
            description="Amazon Bestellung",
        )

        assert condition.matches(txn_match) is True
        assert condition.matches(txn_no_match) is False

    def test_contains_case_insensitive(self):
        """Test case-insensitive contains."""
        condition = RuleCondition(
            field="description",
            operator="contains",
            value="MIETE",
            case_sensitive=False,
        )
        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="miete januar",
        )
        assert condition.matches(txn) is True

    def test_equals_operator(self):
        """Test 'equals' operator."""
        condition = RuleCondition(
            field="counterparty",
            operator="equals",
            value="Max Müller",
        )
        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Test",
            counterparty="Max Müller",
        )
        txn_no_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Test",
            counterparty="Anna Schmidt",
        )

        assert condition.matches(txn_match) is True
        assert condition.matches(txn_no_match) is False

    def test_regex_operator(self):
        """Test 'regex' operator."""
        condition = RuleCondition(
            field="description",
            operator="regex",
            value=r"Miete\s+\w+\s+\d{4}",
        )
        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete Januar 2024",
        )
        txn_no_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Mietzahlung",
        )

        assert condition.matches(txn_match) is True
        assert condition.matches(txn_no_match) is False

    def test_in_list_operator(self):
        """Test 'in_list' operator."""
        condition = RuleCondition(
            field="counterparty",
            operator="in_list",
            value=["Müller", "Schmidt", "Weber"],
        )
        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Test",
            counterparty="Max Müller",
        )
        txn_no_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Test",
            counterparty="Hans Meier",
        )

        assert condition.matches(txn_match) is True
        assert condition.matches(txn_no_match) is False

    def test_gt_operator(self):
        """Test 'gt' (greater than) operator."""
        condition = RuleCondition(
            field="amount",
            operator="gt",
            value=500,
        )
        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Test",
        )
        txn_no_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("100"),
            description="Test",
        )

        assert condition.matches(txn_match) is True
        assert condition.matches(txn_no_match) is False

    def test_lt_operator(self):
        """Test 'lt' (less than) operator."""
        condition = RuleCondition(
            field="amount",
            operator="lt",
            value=0,
        )
        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("-50"),
            description="Test",
        )
        txn_no_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("100"),
            description="Test",
        )

        assert condition.matches(txn_match) is True
        assert condition.matches(txn_no_match) is False

    def test_between_operator(self):
        """Test 'between' operator."""
        condition = RuleCondition(
            field="amount",
            operator="between",
            value=["100", "500"],  # Must be strings for Pydantic
        )
        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("250"),
            description="Test",
        )
        txn_no_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Test",
        )

        assert condition.matches(txn_match) is True
        assert condition.matches(txn_no_match) is False

    def test_config_variable_resolution(self):
        """Test $config.xxx variable resolution."""
        condition = RuleCondition(
            field="counterparty",
            operator="in_list",
            value="$config.tenants",
        )
        config = {"tenants": ["Müller", "Schmidt"]}

        txn_match = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Test",
            counterparty="Max Müller",
        )

        assert condition.matches(txn_match, config) is True


class TestCategorizationRule:
    """Tests for CategorizationRule."""

    def test_simple_rule_match(self):
        """Test simple rule matching."""
        rule = CategorizationRule(
            id="rent_income",
            name="Rental Income",
            conditions=[
                RuleCondition(
                    field="description",
                    operator="contains",
                    value="Miete",
                ),
                RuleCondition(
                    field="amount",
                    operator="gt",
                    value=0,
                ),
            ],
            category=TaxCategory.RENTAL_INCOME,
            confidence=0.95,
        )

        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete Januar",
        )

        assert rule.matches(txn) is True

    def test_rule_apply(self):
        """Test applying a rule to a transaction."""
        rule = CategorizationRule(
            id="rent_income",
            name="Rental Income",
            conditions=[],
            category=TaxCategory.RENTAL_INCOME,
            subcategory="mieter",
            confidence=0.95,
        )

        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete",
        )

        result = rule.apply(txn)

        assert result.category == TaxCategory.RENTAL_INCOME
        assert result.subcategory == "mieter"
        assert result.confidence == 0.95
        assert result.rule_matched == "rent_income"

    def test_conditions_any_or_logic(self):
        """Test OR logic with conditions_any."""
        rule = CategorizationRule(
            id="dropscan",
            name="Dropscan",
            conditions=[
                RuleCondition(
                    field="amount",
                    operator="lt",
                    value=0,
                ),
            ],
            conditions_any=[
                RuleCondition(
                    field="description",
                    operator="contains",
                    value="Dropscan",
                ),
                RuleCondition(
                    field="counterparty",
                    operator="contains",
                    value="Dropscan",
                ),
            ],
            category=TaxCategory.RENTAL_EXPENSE,
        )

        txn1 = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("-89.99"),
            description="Dropscan Abo",
        )
        txn2 = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("-89.99"),
            description="Abo-Zahlung",
            counterparty="Dropscan GmbH",
        )
        txn3 = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("-50"),
            description="Amazon",
        )

        assert rule.matches(txn1) is True
        assert rule.matches(txn2) is True
        assert rule.matches(txn3) is False


class TestCategorizer:
    """Tests for Categorizer class."""

    def test_categorize_single(self):
        """Test categorizing a single transaction."""
        rules = [
            CategorizationRule(
                id="rent",
                name="Rent",
                priority=10,
                conditions=[
                    RuleCondition(
                        field="description",
                        operator="contains",
                        value="Miete",
                    ),
                ],
                category=TaxCategory.RENTAL_INCOME,
            ),
        ]
        categorizer = Categorizer(rules)

        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete Januar",
        )

        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_INCOME

    def test_categorize_priority(self):
        """Test that lower priority rules are applied first."""
        rules = [
            CategorizationRule(
                id="generic",
                name="Generic Income",
                priority=100,
                conditions=[
                    RuleCondition(
                        field="amount",
                        operator="gt",
                        value=0,
                    ),
                ],
                category=TaxCategory.BUSINESS_INCOME,
            ),
            CategorizationRule(
                id="rent",
                name="Rent",
                priority=10,  # Lower = higher priority
                conditions=[
                    RuleCondition(
                        field="description",
                        operator="contains",
                        value="Miete",
                    ),
                ],
                category=TaxCategory.RENTAL_INCOME,
            ),
        ]
        categorizer = Categorizer(rules)

        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete Januar",
        )

        result = categorizer.categorize(txn)
        # Should match the rent rule (priority 10) not generic (priority 100)
        assert result.category == TaxCategory.RENTAL_INCOME

    def test_categorize_respects_manual_override(self):
        """Test that manual overrides are not changed."""
        rules = [
            CategorizationRule(
                id="rent",
                name="Rent",
                conditions=[
                    RuleCondition(
                        field="description",
                        operator="contains",
                        value="Miete",
                    ),
                ],
                category=TaxCategory.RENTAL_INCOME,
            ),
        ]
        categorizer = Categorizer(rules)

        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete Januar",
            category=TaxCategory.PRIVATE,
            manual_override=True,
        )

        result = categorizer.categorize(txn)
        # Should remain PRIVATE due to manual override
        assert result.category == TaxCategory.PRIVATE

    def test_categorize_all(self):
        """Test categorizing multiple transactions."""
        rules = [
            CategorizationRule(
                id="income",
                name="Income",
                conditions=[
                    RuleCondition(field="amount", operator="gt", value=0),
                ],
                category=TaxCategory.RENTAL_INCOME,
            ),
            CategorizationRule(
                id="expense",
                name="Expense",
                conditions=[
                    RuleCondition(field="amount", operator="lt", value=0),
                ],
                category=TaxCategory.RENTAL_EXPENSE,
            ),
        ]
        categorizer = Categorizer(rules)

        txns = [
            Transaction(date=date(2024, 1, 1), amount=Decimal("100"), description="A"),
            Transaction(date=date(2024, 1, 2), amount=Decimal("-50"), description="B"),
        ]

        results = categorizer.categorize_all(txns)

        assert results[0].category == TaxCategory.RENTAL_INCOME
        assert results[1].category == TaxCategory.RENTAL_EXPENSE

    def test_from_yaml_string(self):
        """Test loading categorizer from YAML string."""
        yaml_content = """
rules:
  - id: rent_income
    name: Rental Income
    priority: 10
    conditions:
      - field: description
        operator: contains
        value: Miete
    category: rental_income
    confidence: 0.95
"""
        categorizer = Categorizer.from_yaml_string(yaml_content)

        assert len(categorizer.rules) == 1
        assert categorizer.rules[0].id == "rent_income"

        txn = Transaction(
            date=date(2024, 1, 1),
            amount=Decimal("850"),
            description="Miete Januar",
        )

        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_INCOME
        assert result.confidence == 0.95


class TestVermieterRules:
    """Tests for Vermieter (landlord) YAML rules."""

    @pytest.fixture
    def categorizer(self):
        """Load the actual vermieter rules."""
        from pacman.jurisdictions import get_plugin
        plugin = get_plugin("DE")
        return plugin.get_categorizer("vermieter")

    def test_hausgeld_categorized(self, categorizer):
        """Test Hausgeld is categorized as rental_expense."""
        txn = Transaction(
            date=date(2024, 1, 10),
            amount=Decimal("-385.00"),
            description="Hausgeld Januar WEG Musterstr 12",
            counterparty="WEG Musterstrasse 12",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_EXPENSE
        assert result.subcategory == "hausgeld"

    def test_grundsteuer_categorized(self, categorizer):
        """Test Grundsteuer is categorized as rental_expense."""
        txn = Transaction(
            date=date(2024, 4, 15),
            amount=Decimal("-142.50"),
            description="Grundsteuer Q2/2024 Musterstr 12",
            counterparty="Stadt Musterstadt",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_EXPENSE
        assert result.subcategory == "grundsteuer"

    def test_reparatur_categorized(self, categorizer):
        """Test repairs are categorized as rental_expense."""
        txn = Transaction(
            date=date(2024, 2, 18),
            amount=Decimal("-478.50"),
            description="Reparatur Heizung Whg 1 Rechnung 2024-0142",
            counterparty="Sanitaer Mueller GmbH",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_EXPENSE
        assert result.subcategory == "reparaturen"

    def test_schornsteinfeger_categorized(self, categorizer):
        """Test Schornsteinfeger is categorized as rental_expense."""
        txn = Transaction(
            date=date(2024, 3, 22),
            amount=Decimal("-95.00"),
            description="Schornsteinfeger Jahresgebuehr",
            counterparty="Schornsteinfeger Meister",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_EXPENSE
        assert result.subcategory == "schornsteinfeger"

    def test_gebaeudeversicherung_categorized(self, categorizer):
        """Test Gebäudeversicherung is categorized as rental_expense."""
        txn = Transaction(
            date=date(2024, 2, 25),
            amount=Decimal("-890.00"),
            description="Gebaeudeversicherung 2024",
            counterparty="Allianz Versicherung AG",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_EXPENSE
        assert result.subcategory == "versicherung"

    def test_amazon_private(self, categorizer):
        """Test Amazon purchases are categorized as private."""
        txn = Transaction(
            date=date(2024, 1, 20),
            amount=Decimal("-89.99"),
            description="Amazon Bestellung Privat",
            counterparty="Amazon EU S.a.r.l.",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.PRIVATE
        assert result.subcategory == "amazon"

    def test_supermarkt_private(self, categorizer):
        """Test supermarket purchases are categorized as private."""
        txn = Transaction(
            date=date(2024, 3, 15),
            amount=Decimal("-67.43"),
            description="REWE Supermarkt",
            counterparty="REWE Markt GmbH",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.PRIVATE
        assert result.subcategory == "einkauf"

    def test_spotify_private(self, categorizer):
        """Test streaming services are categorized as private."""
        txn = Transaction(
            date=date(2024, 5, 20),
            amount=Decimal("-9.99"),
            description="Spotify Premium",
            counterparty="Spotify AB",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.PRIVATE
        assert result.subcategory == "streaming"

    def test_steuerberater_categorized(self, categorizer):
        """Test Steuerberater is categorized as business_expense."""
        txn = Transaction(
            date=date(2024, 4, 28),
            amount=Decimal("-450.00"),
            description="Steuerberater Anlage V 2023",
            counterparty="Steuerkanzlei Dr. Huber",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.BUSINESS_EXPENSE
        assert result.subcategory == "steuerberater"

    def test_miete_with_tenant_config(self, categorizer):
        """Test rental income with tenant from config."""
        categorizer.set_config({"tenants": ["Thomas Schmidt", "Maria Weber"]})

        txn = Transaction(
            date=date(2024, 1, 5),
            amount=Decimal("950.00"),
            description="Miete Januar 2024 Wohnung 1",
            counterparty="Thomas Schmidt",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_INCOME
        assert result.subcategory == "mieter"

    def test_handwerker_categorized(self, categorizer):
        """Test Handwerker (craftsman) is categorized as rental_expense."""
        txn = Transaction(
            date=date(2024, 6, 15),
            amount=Decimal("-320.00"),
            description="Handwerker Balkon Whg 2 Reparatur",
            counterparty="Bau-Service Klein",
        )
        result = categorizer.categorize(txn)
        assert result.category == TaxCategory.RENTAL_EXPENSE
        assert result.subcategory == "reparaturen"
