# Session Continuation Code

Kopiere diesen Block in ein frisches Claude Code Terminal:

---

```
cd /home/noiion/pacman

Ich setze die PACMAN-Entwicklung fort. Session-Stand vom 2025-12-12:

## Kontext
- PACMAN ist ein Privacy-first Tax Automation Tool fuer ALLE deutschen Unternehmensklassen
- Universelles Framework mit YAML-basierter Kategorisierung
- Agent-Team Workflow in .claude/agents.md dokumentiert

## Aktueller Stand
- **255 Tests** bestanden, **71% Coverage**
- **13 Profile** mit **297 Regeln** implementiert
- **6 Importers**: Deutsche Bank, Sparkasse, ING, N26, DKB, Generic CSV
- TaxCategory Enum erweitert (employment_income, capital_income)

## Implementierte Profile

Basis-Profile (6):
- freiberufler (29), einzelunternehmer (24), vermieter (26)
- kleinunternehmer (8), gmbh_geschaeftsfuehrer (17), nebenberuflich (14)

Branchen-Profile (7):
- it_freelancer (18), berater_coach (24), content_creator (26)
- e_commerce (30), handwerker (26), kuenstler (25), heilberufler (30)

## Erledigte Tasks
- Alle Bank-Importer (DE Bank, Sparkasse, ING, N26, DKB)
- Alle 13 Profile mit YAML-Regeln
- 63 Profile-Tests
- README und CLAUDE.md aktualisiert
- Pydantic Warnings gefixt

## Naechste Schritte (optional)
- [ ] Dashboard Tests
- [ ] Utils Tests (dates.py, money.py)
- [ ] Anlage N/KAP Berechnung fuer GmbH-GF
- [ ] Release vorbereiten

## Test-Command
PACMAN_TESTING=1 python3 -m pytest tests/ -v --cov=src/pacman

Was soll ich als naechstes tun?
```

---

## Quick Reference

| Agent | Zweck |
|-------|-------|
| `/pacman-quality` | Code Quality, Warnings, Types |
| `/pacman-test` | Tests schreiben |
| `/pacman-tax` | Steuerlogik validieren |
| `/pacman-importer` | Neue Bank-Formate |
| `/pacman-security` | Privacy Audit |
| `/pacman-doc` | Dokumentation |

## Verfuegbare Profile

| Typ | Profile |
|-----|---------|
| Basis | freiberufler, einzelunternehmer, vermieter, kleinunternehmer, gmbh_geschaeftsfuehrer, nebenberuflich |
| Branchen | it_freelancer, berater_coach, content_creator, e_commerce, handwerker, kuenstler, heilberufler |
