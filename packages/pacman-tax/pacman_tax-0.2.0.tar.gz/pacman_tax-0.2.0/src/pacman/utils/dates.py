"""Date parsing utilities."""

from datetime import date, datetime


def parse_german_date(value: str, default_year: int | None = None) -> date | None:
    """
    Parse a German-formatted date.

    Supports formats:
    - DD.MM.YYYY
    - DD.MM.YY
    - DD.MM. (uses default_year or current year)

    Args:
        value: Date string
        default_year: Year to use if not in string

    Returns:
        date object or None if parsing fails
    """
    if not value or not isinstance(value, str):
        return None

    value = value.strip()

    formats = [
        ("%d.%m.%Y", None),    # 31.12.2024
        ("%d.%m.%y", None),    # 31.12.24
        ("%d.%m.", default_year or datetime.now().year),  # 31.12.
    ]

    for fmt, year_override in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            if year_override:
                parsed = parsed.replace(year=year_override)
            return parsed.date()
        except ValueError:
            continue

    return None
