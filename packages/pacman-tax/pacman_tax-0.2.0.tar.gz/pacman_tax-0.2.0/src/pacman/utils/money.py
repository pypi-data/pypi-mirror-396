"""Money and decimal handling utilities."""

from decimal import Decimal, InvalidOperation


def parse_german_decimal(value: str) -> Decimal | None:
    """
    Parse a German-formatted decimal number.

    German format: 1.234,56
    Output: Decimal("1234.56")
    """
    if not value or not isinstance(value, str):
        return None

    # Clean the string
    value = value.strip()
    value = value.replace("€", "").replace("EUR", "").strip()

    # Handle German format
    if "," in value and "." in value:
        # 1.234,56 -> 1234.56
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        # 1234,56 -> 1234.56
        value = value.replace(",", ".")

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def format_currency(
    value: Decimal,
    currency: str = "EUR",
    locale: str = "de"
) -> str:
    """
    Format a decimal value as currency.

    Args:
        value: Decimal amount
        currency: Currency code (EUR, USD, etc.)
        locale: Locale for formatting (de, en)

    Returns:
        Formatted string (e.g., "1.234,56 €")
    """
    if locale == "de":
        # German format
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} €"
    else:
        # Default English format
        return f"€{value:,.2f}"
