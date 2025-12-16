# PACMAN - Claude Code Konfiguration

## Projekt
**PACMAN** - Privacy-first Automated Calculation & Management of Numbers
- Universelles Steuer-Framework fuer alle Unternehmensklassen in DE
- **13 Profile** mit **297 Regeln** fuer verschiedene Unternehmenstypen
- Individuell anpassbar durch YAML-Regeln
- 100% offline, keine Cloud, keine Telemetrie
- AGPL-3.0 Lizenz

### Verfuegbare Profile

**Basis-Profile (Rechtsform):**
- `freiberufler` - Freiberufler (§18 EStG), Anlage S
- `einzelunternehmer` - Gewerbetreibende, Anlage G
- `vermieter` - Vermietung & Verpachtung, Anlage V
- `kleinunternehmer` - §19 UStG (ohne USt)
- `gmbh_geschaeftsfuehrer` - GF mit GmbH-Beteiligung, Anlage N + KAP
- `nebenberuflich` - Angestellt + Selbstaendig, Anlage N + S/G

**Branchen-Profile (spezialisierte Regeln):**
- `it_freelancer` - Software, DevOps, Cloud, AI-Tools
- `berater_coach` - Unternehmensberater, Trainer, Tagessaetze
- `content_creator` - YouTube, Influencer, AdSense, Sponsoring
- `e_commerce` - Online-Handel, Amazon FBA, OSS
- `handwerker` - Material, Fahrzeug, Berufsgenossenschaft
- `kuenstler` - KSK, 7% USt, VG Wort/Bild-Kunst
- `heilberufler` - USt-befreit §4 Nr. 14, Versorgungswerk

## Tech Stack
- Python 3.10+
- Pydantic 2.x (Models)
- Typer + Rich (CLI)
- Pandas + OpenPyXL (Import/Export)
- pytest + hypothesis (Testing)

## Projektstruktur
```
src/pacman/
├── core/           # Models, Categorizer, Privacy
├── importers/      # Bank CSV/XLSX Parser
├── jurisdictions/  # Steuer-Plugins (DE, AT, CH)
├── utils/          # Helpers (money, dates)
└── cli.py          # CLI Entry Point
```

## Agent Team
Dieses Projekt nutzt spezialisierte Agents:

| Command | Agent | Aufgabe |
|---------|-------|---------|
| `/pacman-quality` | Code Quality | Warnings, Types, Linting |
| `/pacman-test` | Test Writer | Unit & Integration Tests |
| `/pacman-tax` | Tax Expert | Deutsche Steuerlogik |
| `/pacman-importer` | Importer Dev | Neue Bank-Formate |
| `/pacman-security` | Security | Privacy-Garantien |
| `/pacman-doc` | Documentation | README, Changelog |

Details: @.claude/agents.md

## Workflows

### Feature entwickeln
```
1. /pacman-tax       # Anforderungen validieren
2. [Implementierung]
3. /pacman-test      # Tests schreiben
4. /pacman-quality   # Code aufraumen
```

### Bug fixen
```
1. /pacman-test      # Failing Test schreiben
2. [Fix]
3. /pacman-quality   # Seiteneffekte pruefen
```

### Release vorbereiten
```
1. /pacman-security  # Privacy Audit
2. /pacman-test      # Full Test Suite
3. /pacman-doc       # Release Notes
```

## Wichtige Dateien
- `src/pacman/core/models.py` - Transaction, TaxYear, Config
- `src/pacman/core/categorizer.py` - YAML-Rules Engine
- `src/pacman/jurisdictions/germany/plugin.py` - DE Steuerlogik
- `pyproject.toml` - Dependencies, Scripts

## Konventionen
- Deutsche User-Doku, englische Code-Kommentare
- Decimal fuer alle Geldbetraege (niemals float!)
- Privacy-First: Kein Network-Code erlaubt
- Type Hints ueberall (mypy strict)

## CLI Commands
```bash
pacman init -p vermieter -y 2024    # Projekt erstellen
pacman import ./import/             # Transaktionen importieren
pacman categorize                   # Automatisch kategorisieren
pacman calculate                    # Steuer berechnen
pacman export -f xlsx               # ELSTER-ready Export
pacman status                       # Projektstatus
```

## Test Status
- **342 Tests** bestanden
- **75% Coverage** gesamt
- Key Coverage:
  - Core Models: 97%
  - Categorizer: 36%
  - CLI: 89%
  - Germany Plugin: 99%
  - Tax Constants: 100%
  - Utils: 100%
  - Importers: 65-85%
  - Dashboard: 14% (UI-Tests schwierig)

## Erledigte Tasks
1. [x] Warnings fixen (`/pacman-quality`)
2. [x] Test Suite aufbauen (`/pacman-test`)
3. [x] Sparkasse Importer (`/pacman-importer`)
4. [x] Tax Logic validieren (`/pacman-tax`)
5. [x] CLI Tests (`/pacman-test`)
6. [x] YAML Rules erstellen (vermieter.yaml, etc.)
7. [x] README vervollstaendigen (`/pacman-doc`)
8. [x] Pydantic Deprecation Warnings fixen
9. [x] ING, N26, DKB Importer Tests
10. [x] **13 Profile implementiert** (Basis + Branchen)
11. [x] TaxCategory Enum erweitert (employment, capital)
12. [x] 63 Profile-Tests geschrieben
13. [x] **Dashboard Tests** (31 Tests)
14. [x] **Anlage N/KAP Berechnung** fuer GmbH-GF
15. [x] **Release 0.2.0** vorbereitet
16. [x] **Utils Tests** (dates.py, money.py) - 100% Coverage
17. [x] **E2E Tests** (Freiberufler, Vermieter, GmbH-GF Workflows)
18. [x] **Getting Started Guide** (docs/getting-started.md)

## Naechste Schritte
- [ ] Mehr Dashboard Coverage (Streamlit-Mocking)
- [ ] PyPI Veroeffentlichung

## Design-Philosophie
- **Universell**: Framework fuer alle Unternehmensklassen, nicht nur Vermieter
- **Individuell anpassbar**: YAML-Regeln pro Nutzer/Use-Case
- **Vermietung ist ein Baustein**: Nicht der Fokus, ausser explizit fuer Immobilieneigentuemer entwickelt
- **Profile sind erweiterbar**: Nutzer koennen eigene Profile definieren
