"""
German categorization rules.

Rules are defined in YAML files for easy customization.
"""

from pathlib import Path

from pacman.core.categorizer import CategorizationRule, Categorizer


def load_rules(profile: str) -> list[CategorizationRule]:
    """
    Load categorization rules for a profile.

    Args:
        profile: Profile name ('vermieter', 'einzelunternehmer', 'freiberufler')

    Returns:
        List of CategorizationRule objects
    """
    rules_dir = Path(__file__).parent
    rules_file = rules_dir / f"{profile}.yaml"

    if not rules_file.exists():
        # Fall back to common rules
        rules_file = rules_dir / "common.yaml"
        if not rules_file.exists():
            return []

    categorizer = Categorizer.from_yaml(rules_file)
    return categorizer.rules


def get_categorizer(profile: str) -> Categorizer:
    """Get a configured Categorizer for the profile."""
    rules = load_rules(profile)
    return Categorizer(rules=rules)
