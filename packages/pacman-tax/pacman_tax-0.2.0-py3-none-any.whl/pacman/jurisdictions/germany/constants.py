"""
German Tax Constants.

Contains tax-relevant values for different years:
- Grundfreibetrag
- Gewerbesteuer-Freibetrag
- EÜR Grenzen
- Kleinunternehmerregelung
- Solidaritätszuschlag
"""

TAX_CONSTANTS = {
    2023: {
        "grundfreibetrag": 10908,
        "gewerbe_freibetrag": 24500,
        "euer_grenze_umsatz": 600000,
        "euer_grenze_gewinn": 60000,
        "kleinunternehmer_grenze": 22000,
        "soli_grenze": 17543,
        # Anlage N (Nichtselbständige Arbeit)
        "arbeitnehmer_pauschbetrag": 1230,  # Werbungskostenpauschale
        # Anlage KAP (Kapitalerträge)
        "sparer_pauschbetrag": 1000,  # Sparerpauschbetrag (Single)
        "sparer_pauschbetrag_verheiratet": 2000,  # Sparerpauschbetrag (Verheiratet)
        "abgeltungsteuer_satz": 0.25,  # 25%
    },
    2024: {
        "grundfreibetrag": 11604,
        "gewerbe_freibetrag": 24500,
        "euer_grenze_umsatz": 600000,
        "euer_grenze_gewinn": 60000,
        "kleinunternehmer_grenze": 22000,
        "soli_grenze": 18130,
        # Anlage N
        "arbeitnehmer_pauschbetrag": 1230,
        # Anlage KAP
        "sparer_pauschbetrag": 1000,
        "sparer_pauschbetrag_verheiratet": 2000,
        "abgeltungsteuer_satz": 0.25,
    },
    2025: {
        "grundfreibetrag": 12084,
        "gewerbe_freibetrag": 24500,
        "euer_grenze_umsatz": 800000,  # Erhöht ab 2024
        "euer_grenze_gewinn": 80000,   # Erhöht ab 2024
        "kleinunternehmer_grenze": 25000,  # Erhöht
        "soli_grenze": 18130,
        # Anlage N
        "arbeitnehmer_pauschbetrag": 1230,
        # Anlage KAP
        "sparer_pauschbetrag": 1000,
        "sparer_pauschbetrag_verheiratet": 2000,
        "abgeltungsteuer_satz": 0.25,
    },
}


def get_constants(year: int) -> dict:
    """
    Get tax constants for a specific year.

    Falls back to the latest available year if not found.
    """
    if year in TAX_CONSTANTS:
        return TAX_CONSTANTS[year]

    # Fall back to latest year
    latest = max(TAX_CONSTANTS.keys())
    return TAX_CONSTANTS[latest]
