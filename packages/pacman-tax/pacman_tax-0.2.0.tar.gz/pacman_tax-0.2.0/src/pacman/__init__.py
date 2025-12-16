"""
PACMAN - Privacy-first Automated Calculation & Management of Numbers

A local-first, privacy-focused tax automation tool for freelancers and landlords.
All data stays on your device. No cloud, no tracking, no accounts.

License: AGPL-3.0-or-later
"""

import os

__version__ = "0.2.0"
__author__ = "Manu"

# Skip privacy verification in test environment
# This allows test tools like hypothesis to use network modules
if os.environ.get("PACMAN_TESTING") != "1":
    from pacman.core.privacy import PrivacyGuarantees
    PrivacyGuarantees.verify()
