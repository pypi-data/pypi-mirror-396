# PACMAN Development Agent Team

## Agent-Architektur

```
                    ┌─────────────────┐
                    │   Coordinator   │
                    │  (Du/Claude)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Code Quality │  │   Tax Domain    │  │    Security     │
│    Agent      │  │     Agent       │  │     Agent       │
└───────────────┘  └─────────────────┘  └─────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Test Writer  │  │ Importer Agent  │  │   Doc Agent     │
│    Agent      │  │                 │  │                 │
└───────────────┘  └─────────────────┘  └─────────────────┘
```

## Agent Definitionen

### 1. Code Quality Agent (`/pacman-quality`)
**Zweck:** Code-Qualität sicherstellen
**Aufgaben:**
- Warnings fixen (SSL, Deprecations)
- Type Hints vervollständigen
- Ruff/MyPy Fehler beheben
- Code-Duplizierung reduzieren

**Trigger:** Nach Feature-Completion, vor Commit

### 2. Test Writer Agent (`/pacman-test`)
**Zweck:** Test Coverage erhöhen
**Aufgaben:**
- Unit Tests für neue Features
- Integration Tests für Workflows
- Property-based Tests (Hypothesis)
- Fixture-Daten generieren

**Trigger:** Nach neuem Feature, nach Bug-Fix

### 3. Tax Domain Agent (`/pacman-tax`)
**Zweck:** Steuerlogik validieren
**Aufgaben:**
- Deutsche Steuerregeln prüfen
- ELSTER-Kompatibilität sicherstellen
- Anlage V/G/S/EÜR Mapping validieren
- Grenzfälle identifizieren

**Trigger:** Bei Änderungen an jurisdictions/, vor Release

### 4. Importer Agent (`/pacman-importer`)
**Zweck:** Bank-Import erweitern
**Aufgaben:**
- Neue Bank-Formate analysieren
- Parser implementieren
- Edge Cases (Encoding, Datumsformate) behandeln
- Auto-Detection verbessern

**Trigger:** Bei neuer Bank-Anforderung

### 5. Security Agent (`/pacman-security`)
**Zweck:** Privacy-Garantien sicherstellen
**Aufgaben:**
- Import-Hook Effektivität prüfen
- Keine Network-Leaks
- Sensitive Data Handling
- AGPL Compliance

**Trigger:** Vor Release, nach Dependency-Update

### 6. Doc Agent (`/pacman-doc`)
**Zweck:** Dokumentation aktuell halten
**Aufgaben:**
- README aktualisieren
- CLI Help verbessern
- Changelog pflegen
- Beispiele erstellen

**Trigger:** Nach Feature-Completion, vor Release

## Workflow-Patterns

### Feature Development
```
1. /pacman-tax     → Anforderungen validieren
2. [Implementierung]
3. /pacman-test    → Tests schreiben
4. /pacman-quality → Code aufräumen
5. /pacman-doc     → Dokumentieren
```

### Bug Fix
```
1. /pacman-test    → Failing Test schreiben
2. [Fix implementieren]
3. /pacman-quality → Seiteneffekte prüfen
```

### New Bank Import
```
1. /pacman-importer → Parser entwickeln
2. /pacman-test     → Import-Tests
3. /pacman-quality  → Code Review
```

### Pre-Release
```
1. /pacman-security → Privacy Audit
2. /pacman-tax      → Steuer-Validierung
3. /pacman-test     → Full Test Suite
4. /pacman-doc      → Release Notes
```

## Agent-Kommunikation

Agents kommunizieren über:
- **Shared Context:** CLAUDE.md, config.yaml
- **Todo-Listen:** TodoWrite für Handoffs
- **Artifacts:** tests/, docs/, CHANGELOG.md

## Erweiterbarkeit

Neue Agents hinzufügen:
1. Command in `.claude/commands/pacman-{name}.md` erstellen
2. In dieser Datei dokumentieren
3. Workflow-Patterns aktualisieren
