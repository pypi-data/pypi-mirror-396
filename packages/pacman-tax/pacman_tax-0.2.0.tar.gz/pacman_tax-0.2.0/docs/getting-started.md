# Getting Started mit PACMAN

> Schritt-fuer-Schritt Anleitung fuer dein erstes Steuer-Projekt

## Voraussetzungen

- Python 3.10 oder hoeher
- pip (Python Package Manager)
- Bank-Export als CSV (von deiner Bank herunterladen)

## 1. Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/pacman.git
cd pacman

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# PACMAN installieren
pip install -e ".[dashboard]"

# Installation pruefen
pacman --version
# Ausgabe: pacman, version 0.2.0
```

## 2. Profil waehlen

PACMAN unterstuetzt verschiedene Unternehmensformen und Branchen:

### Basis-Profile (Rechtsform)

| Profil | Beschreibung | Steuerformulare |
|--------|--------------|-----------------|
| `freiberufler` | Freiberufliche Taetigkeit (§18 EStG) | Anlage S, EUER |
| `einzelunternehmer` | Gewerbetreibende | Anlage G, EUER |
| `vermieter` | Vermietung & Verpachtung | Anlage V |
| `kleinunternehmer` | §19 UStG (ohne USt) | Anlage G/S, EUER |
| `gmbh_geschaeftsfuehrer` | GF mit GmbH-Beteiligung | Anlage N, KAP |
| `nebenberuflich` | Angestellt + Selbstaendig | Anlage N + S/G |

### Branchen-Profile (spezialisierte Regeln)

| Profil | Beschreibung |
|--------|--------------|
| `it_freelancer` | Software-Entwickler, DevOps, Cloud |
| `berater_coach` | Unternehmensberater, Trainer |
| `content_creator` | YouTube, Influencer, Podcast |
| `e_commerce` | Online-Handel, Amazon FBA |
| `handwerker` | Handwerksbetrieb |
| `kuenstler` | Designer, Fotograf, Musiker |
| `heilberufler` | Arzt, Therapeut, Heilpraktiker |

## 3. Projekt erstellen

```bash
# Neues Projekt fuer 2024 erstellen
pacman init --profile freiberufler --year 2024 --path ~/steuer-2024

# Fuer Vermieter mit mehreren Mietern
pacman init --profile vermieter --year 2024 --path ~/vermietung-2024
```

Das erstellt folgende Struktur:

```
~/steuer-2024/
├── config.yaml           # Deine Projekt-Konfiguration
├── transactions.json     # Hier landen deine Buchungen
├── import/               # Bank-CSVs hier ablegen
└── export/               # Generierte Exports
```

## 4. Bank-Export importieren

### Bank-Export herunterladen

1. Logge dich in dein Online-Banking ein
2. Gehe zu Umsaetze/Kontoauszuege
3. Waehle den Zeitraum (ganzes Jahr 2024)
4. Exportiere als CSV

### Unterstuetzte Banken

| Bank | Format | Besonderheiten |
|------|--------|----------------|
| Deutsche Bank | CSV (Semikolon) | Encoding: Windows-1252 |
| Sparkasse | CSV | Encoding: ISO-8859-1 |
| ING-DiBa | CSV | Datumsformat: DD.MM.YYYY |
| N26 | CSV | Englische Spalten |
| DKB | CSV | Header-Zeilen ueberspringen |

### Import durchfuehren

```bash
# CSV in den import-Ordner kopieren
cp ~/Downloads/umsaetze.csv ~/steuer-2024/import/

# Transaktionen importieren
pacman import ~/steuer-2024/import/ --project ~/steuer-2024

# Ausgabe:
# Gefunden: 248 Transaktionen
# Importiert: 248 Transaktionen
# Duplikate: 0
```

## 5. Transaktionen kategorisieren

```bash
# Automatische Kategorisierung
pacman categorize --project ~/steuer-2024

# Ausgabe:
# Kategorisiert: 187/248 (75.4%)
# Manuell pruefen: 61 Transaktionen
```

### Kategorisierungs-Regeln

PACMAN verwendet YAML-basierte Regeln. Beispiel:

```yaml
# In config.yaml oder rules.yaml
rules:
  - id: client_payments
    name: "Kundenzahlungen"
    conditions:
      - field: counterparty
        operator: contains
        value: "Kunde AG"
    category: business_income
    subcategory: honorar
    confidence: 1.0
```

### Verfuegbare Kategorien

**Einnahmen:**
- `business_income` - Betriebseinnahmen (Anlage G/S)
- `rental_income` - Mieteinnahmen (Anlage V)
- `employment_income` - Arbeitslohn (Anlage N)
- `capital_income` - Kapitalertraege (Anlage KAP)

**Ausgaben:**
- `business_expense` - Betriebsausgaben
- `rental_expense` - Werbungskosten Vermietung
- `employment_expense` - Werbungskosten Arbeitnehmer
- `deductible` - Sonderausgaben

**Sonstiges:**
- `private` - Nicht steuerrelevant
- `passthrough` - Durchlaufposten

## 6. Status pruefen

```bash
pacman status --project ~/steuer-2024

# Ausgabe:
# ═══════════════════════════════════════════
# PACMAN Status: steuer-2024
# ═══════════════════════════════════════════
#
# Profil:        freiberufler
# Jahr:          2024
# Jurisdiction:  DE
#
# Transaktionen: 248
# Kategorisiert: 187 (75.4%)
# Offen:         61
#
# Einnahmen:     45.230,00 EUR
# Ausgaben:       8.450,00 EUR
# ───────────────────────────────────────────
# Gewinn:        36.780,00 EUR
```

## 7. Steuer berechnen

```bash
pacman calculate --project ~/steuer-2024

# Ausgabe:
# Berechnung fuer 2024 (freiberufler)
#
# Anlage S:
#   Betriebseinnahmen:     45.230,00 EUR
#   Betriebsausgaben:       8.450,00 EUR
#   Gewinn:                36.780,00 EUR
#
# EUER:
#   Einnahmen:             45.230,00 EUR
#   Ausgaben:               8.450,00 EUR
#   Ergebnis:              36.780,00 EUR
```

## 8. Export fuer ELSTER

```bash
# Excel-Export (empfohlen)
pacman export --format xlsx --project ~/steuer-2024

# CSV-Export
pacman export --format csv --project ~/steuer-2024

# Ausgabe:
# Exportiert: ~/steuer-2024/export/ELSTER_Werte_2024.xlsx
```

### Export-Dateien

Die Export-Datei enthaelt:
- Zusammenfassung pro Anlage
- Detaillierte Buchungsliste
- ELSTER-Feldnummern (soweit bekannt)

## 9. Dashboard (optional)

```bash
# Web-Dashboard starten
pacman dashboard --project ~/steuer-2024

# Oeffnet Browser unter http://localhost:8501
```

Das Dashboard zeigt:
- Einnahmen/Ausgaben-Uebersicht
- Kategorisierungs-Fortschritt
- Monatliche Entwicklung
- Offene Transaktionen

## Haeufige Fragen

### Wie importiere ich mehrere Konten?

```bash
# Mehrere CSVs in import/ ablegen
cp ~/Downloads/girokonto.csv ~/steuer-2024/import/
cp ~/Downloads/geschaeftskonto.csv ~/steuer-2024/import/

# Alle importieren
pacman import ~/steuer-2024/import/ --project ~/steuer-2024
```

### Wie fuege ich Mieter hinzu (Vermieter-Profil)?

```bash
pacman tenants add "Max Mueller" --project ~/vermietung-2024
pacman tenants add "Anna Schmidt" --project ~/vermietung-2024

# Mieter auflisten
pacman tenants list --project ~/vermietung-2024
```

### Wie erstelle ich eigene Regeln?

Bearbeite `config.yaml` in deinem Projekt:

```yaml
# ~/steuer-2024/config.yaml
rules:
  - id: my_custom_rule
    name: "Meine eigene Regel"
    priority: 10  # Hoeher = wird zuerst geprueft
    conditions:
      - field: description
        operator: contains
        value: "RECURRING PAYMENT"
      - field: amount
        operator: lt
        value: 0
    category: business_expense
    subcategory: software_abo
    confidence: 0.9
```

### Wie pruefe ich die Privacy-Garantien?

```bash
pacman --privacy

# Ausgabe:
# PACMAN Privacy-Garantien:
#
# ✅ Keine Netzwerk-Verbindungen
# ✅ Keine Telemetrie
# ✅ Keine Cloud-Speicherung
# ✅ Keine externen APIs
# ✅ Vollstaendig auditierbar (AGPL-3.0)
#
# Deine Daten verlassen niemals dein Geraet.
```

## Naechste Schritte

1. **Regeln anpassen**: Erstelle eigene Kategorisierungs-Regeln fuer wiederkehrende Buchungen
2. **Dashboard nutzen**: Visualisiere deine Finanzen im Web-Dashboard
3. **Backup**: Sichere dein Projekt-Verzeichnis regelmaessig
4. **Export pruefen**: Vergleiche den Export mit deinen Unterlagen

## Hilfe & Support

```bash
# CLI-Hilfe anzeigen
pacman --help
pacman import --help
pacman categorize --help

# Ausfuehrliche Logs
pacman --verbose status --project ~/steuer-2024
```

---

**Hinweis:** PACMAN ersetzt keine Steuerberatung. Fuer verbindliche Auskuenfte wende dich an einen Steuerberater.
