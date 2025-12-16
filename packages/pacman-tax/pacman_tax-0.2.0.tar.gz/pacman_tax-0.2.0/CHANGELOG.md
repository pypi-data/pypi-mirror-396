# Changelog

All notable changes to PACMAN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-12

### Added

#### Tax Forms
- **Anlage N** (Nichtselbstaendige Arbeit) calculation for employment income
  - GmbH-Geschaeftsfuehrer salary and bonus handling
  - Werbungskosten vs Arbeitnehmer-Pauschbetrag comparison
  - Automatic Pauschbetrag (1230 EUR) application when higher
- **Anlage KAP** (Kapitalertraege) calculation for capital income
  - Dividend and interest income support
  - Sparer-Pauschbetrag (1000 EUR / 2000 EUR married) deduction
  - Abgeltungsteuer (25%) and Solidaritaetszuschlag calculation

#### New Tax Categories
- `EMPLOYMENT_INCOME` - Einkuenfte aus nichtselbstaendiger Arbeit
- `EMPLOYMENT_EXPENSE` - Werbungskosten Anlage N
- `CAPITAL_INCOME` - Kapitalertraege

#### Tax Constants (2023-2025)
- `arbeitnehmer_pauschbetrag` - Werbungskostenpauschale (1230 EUR)
- `sparer_pauschbetrag` - Single (1000 EUR)
- `sparer_pauschbetrag_verheiratet` - Married (2000 EUR)
- `abgeltungsteuer_satz` - Capital gains tax rate (25%)

#### Dashboard Tests
- 31 new tests for dashboard functionality
- Currency formatting tests
- Category color mapping tests
- Project loading tests
- Data processing logic tests

#### Profile Enhancements
- GmbH-Geschaeftsfuehrer: Full Anlage N + KAP support
- Nebenberuflich: Combined Anlage N + G/EUeR support

### Changed
- `TaxYear` model now tracks `income_employment`, `income_capital`, `expenses_employment`
- `calculate_aggregates()` handles all income types
- `total_income` property includes all 4 income sources (rental, business, employment, capital)
- Germany Plugin: Dynamic form generation based on income types

### Fixed
- Freiberufler no longer incorrectly generates Anlage G (uses Anlage S only)

### Test Coverage
- **300 tests** total (from 255)
- **73% coverage** (from 71%)
- Germany Plugin: 99% coverage

## [0.1.0] - 2025-12-11

### Added
- Initial release with 13 profiles and 297 rules
- 6 bank importers: Deutsche Bank, Sparkasse, ING, N26, DKB, Generic CSV
- YAML-based rule engine
- Privacy-first architecture (100% offline)
- CLI with typer + rich
- Streamlit dashboard (optional)
- ELSTER-ready Excel export

### Profiles

**Basis-Profile:**
- freiberufler (29 rules)
- einzelunternehmer (24 rules)
- vermieter (26 rules)
- kleinunternehmer (8 rules)
- gmbh_geschaeftsfuehrer (17 rules)
- nebenberuflich (14 rules)

**Branchen-Profile:**
- it_freelancer (18 rules)
- berater_coach (24 rules)
- content_creator (26 rules)
- e_commerce (30 rules)
- handwerker (26 rules)
- kuenstler (25 rules)
- heilberufler (30 rules)
