"""
Germany (DE) Jurisdiction Plugin for PACMAN.

Supports:
- Vermieter (Anlage V)
- Einzelunternehmer (Anlage G, EÜR)
- Freiberufler (Anlage S, EÜR)
"""

from pacman.jurisdictions.germany.plugin import GermanyPlugin

# Export Plugin class for auto-discovery
Plugin = GermanyPlugin

__all__ = ["GermanyPlugin", "Plugin"]
