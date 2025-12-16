"""
PACMAN Categorizer - YAML-based rules engine for transaction categorization.

The categorizer applies rules to transactions to automatically assign categories.
Rules are defined in YAML files and can be customized per jurisdiction/profile.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from pacman.core.models import TaxCategory, Transaction, TransactionSplit


class RuleCondition(BaseModel):
    """
    Single condition for matching a transaction.

    Conditions are combined with AND logic within a rule.
    """

    field: str = Field(
        description="Field to check: 'counterparty', 'description', 'amount', 'iban'"
    )
    operator: str = Field(
        description="Operator: contains, equals, regex, in_list, gt, lt, between"
    )
    value: str | list[str] | float = Field(
        description="Value to compare against"
    )
    case_sensitive: bool = False

    def matches(self, transaction: Transaction, config: dict[str, Any] | None = None) -> bool:
        """
        Check if this condition matches the transaction.

        Args:
            transaction: Transaction to check
            config: Optional config dict for dynamic values (e.g., tenant list)
        """
        # Get field value from transaction
        field_value = self._get_field_value(transaction)
        if field_value is None:
            return False

        # Resolve dynamic values from config
        compare_value = self._resolve_value(self.value, config)

        # Apply operator
        return self._apply_operator(field_value, compare_value)

    def _get_field_value(self, transaction: Transaction) -> str | Decimal | None:
        """Get the value of the field from the transaction."""
        field_map = {
            "counterparty": transaction.counterparty,
            "description": transaction.description,
            "amount": transaction.amount,
            "iban": transaction.iban,
        }
        return field_map.get(self.field)

    def _resolve_value(
        self, value: str | list[str] | float, config: dict[str, Any] | None
    ) -> str | list[str] | float:
        """
        Resolve dynamic config references in value.

        Values like "$config.tenants" are replaced with actual config values.
        """
        if config is None:
            return value

        if isinstance(value, str) and value.startswith("$config."):
            key = value[8:]  # Remove "$config." prefix
            return config.get(key, [])

        return value

    def _apply_operator(
        self, field_value: str | Decimal | None, compare_value: str | list[str] | float
    ) -> bool:
        """Apply the comparison operator."""
        if field_value is None:
            return False

        # String operations
        if self.operator == "contains":
            if isinstance(field_value, str):
                field_str = field_value if self.case_sensitive else field_value.lower()
                cmp_str = str(compare_value)
                compare_str = cmp_str if self.case_sensitive else cmp_str.lower()
                return compare_str in field_str
            return False

        if self.operator == "equals":
            if isinstance(field_value, str):
                field_str = field_value if self.case_sensitive else field_value.lower()
                cmp_str = str(compare_value)
                compare_str = cmp_str if self.case_sensitive else cmp_str.lower()
                return field_str == compare_str
            return field_value == compare_value

        if self.operator == "regex":
            if isinstance(field_value, str):
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(str(compare_value), field_value, flags))
            return False

        if self.operator == "in_list":
            if isinstance(compare_value, list):
                if isinstance(field_value, str):
                    field_str = field_value if self.case_sensitive else field_value.lower()
                    if self.case_sensitive:
                        compare_list = compare_value
                    else:
                        compare_list = [v.lower() for v in compare_value]
                    return any(item in field_str for item in compare_list)
            return False

        # Numeric operations
        if self.operator in ("gt", "lt", "between"):
            try:
                if isinstance(field_value, Decimal):
                    num_value = field_value
                else:
                    num_value = Decimal(str(field_value))

                if self.operator == "gt":
                    return num_value > Decimal(str(compare_value))
                if self.operator == "lt":
                    return num_value < Decimal(str(compare_value))
                if self.operator == "between":
                    if isinstance(compare_value, list) and len(compare_value) == 2:
                        low = Decimal(str(compare_value[0]))
                        high = Decimal(str(compare_value[1]))
                        return low <= num_value <= high
            except Exception:
                return False

        return False


class CategorizationRule(BaseModel):
    """
    Rule for automatic transaction categorization.

    Rules have conditions (AND logic) and optional conditions_any (OR logic).
    Lower priority numbers are evaluated first.
    """

    id: str
    name: str
    priority: int = Field(default=100, description="Lower = higher priority")

    conditions: list[RuleCondition] = Field(default_factory=list, description="AND conditions")
    conditions_any: list[RuleCondition] | None = Field(default=None, description="OR conditions")

    # Result
    category: TaxCategory
    subcategory: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Optional split for mixed-use transactions
    split: dict[str, float] | None = Field(
        default=None,
        description="Split percentages, e.g., {'rental': 80, 'business': 20}"
    )

    def matches(self, transaction: Transaction, config: dict[str, Any] | None = None) -> bool:
        """
        Check if this rule matches the transaction.

        Returns True if:
        - All conditions in `conditions` match (AND), AND
        - At least one condition in `conditions_any` matches (OR), if conditions_any is set
        """
        # Check AND conditions
        if self.conditions:
            if not all(cond.matches(transaction, config) for cond in self.conditions):
                return False

        # Check OR conditions (if any)
        if self.conditions_any:
            if not any(cond.matches(transaction, config) for cond in self.conditions_any):
                return False

        return True

    def apply(self, transaction: Transaction) -> Transaction:
        """
        Apply this rule to a transaction.

        Modifies the transaction's category, subcategory, confidence, and splits.
        """
        transaction.category = self.category
        transaction.subcategory = self.subcategory
        transaction.confidence = self.confidence
        transaction.rule_matched = self.id

        # Apply splits if defined
        if self.split:
            transaction.splits = []
            for cat_key, percentage in self.split.items():
                # Map string keys to TaxCategory
                cat = self._map_split_category(cat_key)
                if cat:
                    transaction.splits.append(
                        TransactionSplit(
                            category=cat,
                            subcategory=self.subcategory,
                            percentage=Decimal(str(percentage)),
                        )
                    )

        return transaction

    def _map_split_category(self, key: str) -> TaxCategory | None:
        """Map split key to TaxCategory."""
        key_lower = key.lower()
        mapping = {
            "rental": TaxCategory.RENTAL_EXPENSE,
            "vermietung": TaxCategory.RENTAL_EXPENSE,
            "business": TaxCategory.BUSINESS_EXPENSE,
            "gewerbe": TaxCategory.BUSINESS_EXPENSE,
            "private": TaxCategory.PRIVATE,
            "privat": TaxCategory.PRIVATE,
        }
        return mapping.get(key_lower)


class Categorizer:
    """
    Transaction categorizer using YAML-based rules.

    Loads rules from YAML files and applies them to transactions.
    """

    def __init__(self, rules: list[CategorizationRule] | None = None):
        """
        Initialize categorizer.

        Args:
            rules: List of categorization rules (sorted by priority)
        """
        self.rules = sorted(rules or [], key=lambda r: r.priority)
        self.config: dict[str, Any] = {}

    def set_config(self, config: dict[str, Any]) -> None:
        """
        Set configuration for dynamic rule values.

        Config values can be referenced in rules with $config.key syntax.
        """
        self.config = config

    def add_rule(self, rule: CategorizationRule) -> None:
        """Add a rule and re-sort by priority."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)

    def categorize(self, transaction: Transaction) -> Transaction:
        """
        Categorize a single transaction.

        Applies the first matching rule (by priority).
        """
        if transaction.manual_override:
            return transaction

        for rule in self.rules:
            if rule.matches(transaction, self.config):
                return rule.apply(transaction)

        return transaction

    def categorize_all(self, transactions: list[Transaction]) -> list[Transaction]:
        """Categorize all transactions."""
        return [self.categorize(t) for t in transactions]

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> Categorizer:
        """
        Load categorizer from a YAML rules file.

        Args:
            yaml_path: Path to YAML file with rules

        Returns:
            Configured Categorizer instance
        """
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        rules = []
        for rule_data in data.get("rules", []):
            rule_id = rule_data.get("id", "unknown")

            # Parse conditions
            conditions = []
            for cond_data in rule_data.get("conditions", []):
                conditions.append(RuleCondition(**cond_data))

            conditions_any = None
            if "conditions_any" in rule_data:
                conditions_any = [
                    RuleCondition(**cond_data)
                    for cond_data in rule_data["conditions_any"]
                ]

            # Parse category with validation
            category_str = rule_data.get("category")
            if not category_str:
                raise ValueError(f"Rule '{rule_id}' missing required 'category' field")

            try:
                category = TaxCategory(category_str)
            except ValueError:
                valid_categories = [c.value for c in TaxCategory]
                raise ValueError(
                    f"Rule '{rule_id}' has invalid category '{category_str}'. "
                    f"Valid categories: {', '.join(valid_categories)}"
                )

            rule = CategorizationRule(
                id=rule_data["id"],
                name=rule_data["name"],
                priority=rule_data.get("priority", 100),
                conditions=conditions,
                conditions_any=conditions_any,
                category=category,
                subcategory=rule_data.get("subcategory"),
                confidence=rule_data.get("confidence", 1.0),
                split=rule_data.get("split"),
            )
            rules.append(rule)

        return cls(rules=rules)

    @classmethod
    def from_yaml_string(cls, yaml_content: str) -> Categorizer:
        """Load categorizer from YAML string."""
        data = yaml.safe_load(yaml_content)

        rules = []
        for rule_data in data.get("rules", []):
            rule_id = rule_data.get("id", "unknown")
            conditions = [RuleCondition(**c) for c in rule_data.get("conditions", [])]
            conditions_any = None
            if "conditions_any" in rule_data:
                conditions_any = [RuleCondition(**c) for c in rule_data["conditions_any"]]

            # Parse category with validation
            category_str = rule_data.get("category")
            if not category_str:
                raise ValueError(f"Rule '{rule_id}' missing required 'category' field")

            try:
                category = TaxCategory(category_str)
            except ValueError:
                valid_categories = [c.value for c in TaxCategory]
                raise ValueError(
                    f"Rule '{rule_id}' has invalid category '{category_str}'. "
                    f"Valid categories: {', '.join(valid_categories)}"
                )

            rule = CategorizationRule(
                id=rule_data["id"],
                name=rule_data["name"],
                priority=rule_data.get("priority", 100),
                conditions=conditions,
                conditions_any=conditions_any,
                category=category,
                subcategory=rule_data.get("subcategory"),
                confidence=rule_data.get("confidence", 1.0),
                split=rule_data.get("split"),
            )
            rules.append(rule)

        return cls(rules=rules)
