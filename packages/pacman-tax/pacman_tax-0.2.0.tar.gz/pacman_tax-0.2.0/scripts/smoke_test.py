#!/usr/bin/env python3
"""
PACMAN MVP Smoke Test

Testet den kompletten Workflow von Projekt-Erstellung bis Export.
Fuehrt realistische Szenarien fuer verschiedene Profile durch.

Usage:
    python scripts/smoke_test.py
    python scripts/smoke_test.py --profile freiberufler
    python scripts/smoke_test.py --all
"""

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from random import choice, randint, uniform


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_step(step: int, text: str) -> None:
    """Print a step indicator."""
    print(f"{Colors.YELLOW}[Step {step}]{Colors.END} {text}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}[OK]{Colors.END} {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}[FAIL]{Colors.END} {text}")


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, "PACMAN_TESTING": "1"},
    )
    return result.returncode, result.stdout, result.stderr


def generate_freiberufler_csv(path: Path, year: int = 2024) -> None:
    """Generate realistic freelancer transactions."""
    transactions = []

    # Monatliche Kundeneinnahmen
    clients = [
        ("Kunde ABC GmbH", "Rechnung", 4500, 6500),
        ("Startup XYZ AG", "Beratung", 2000, 4000),
        ("Agentur Digital", "Projekt", 1500, 3000),
    ]

    for month in range(1, 13):
        # 1-3 Kundenzahlungen pro Monat
        for client_name, desc, min_amt, max_amt in clients[:randint(1, 3)]:
            day = randint(5, 25)
            amount = round(uniform(min_amt, max_amt), 2)
            transactions.append({
                "date": f"{year}-{month:02d}-{day:02d}",
                "amount": f"{amount:.2f}",
                "counterparty": client_name,
                "description": f"{desc} {month:02d}/{year}",
            })

    # Regelmaessige Ausgaben
    monthly_expenses = [
        ("Adobe Systems", "Creative Cloud", -59.99),
        ("GitHub Inc", "Pro Subscription", -4.00),
        ("Hetzner", "Cloud Server", -29.90),
        ("Deutsche Telekom", "Internet Business", -49.95),
    ]

    for month in range(1, 13):
        for vendor, desc, amount in monthly_expenses:
            day = randint(1, 10)
            transactions.append({
                "date": f"{year}-{month:02d}-{day:02d}",
                "amount": f"{amount:.2f}",
                "counterparty": vendor,
                "description": desc,
            })

    # Einmalige Ausgaben
    one_time = [
        (f"{year}-02-15", "Apple Store", "MacBook Pro", -2499.00),
        (f"{year}-04-20", "IKEA", "Bueromoebel", -450.00),
        (f"{year}-06-10", "Steuerberater Meier", "Beratung", -350.00),
        (f"{year}-09-05", "Deutsche Bahn", "Dienstreise Muenchen", -189.00),
        (f"{year}-11-20", "Amazon Business", "Bueromaterial", -89.50),
    ]

    for txn_date, vendor, desc, amount in one_time:
        transactions.append({
            "date": txn_date,
            "amount": f"{amount:.2f}",
            "counterparty": vendor,
            "description": desc,
        })

    # Private Ausgaben (sollten als private kategorisiert werden)
    private = [
        (f"{year}-01-25", "REWE", "Lebensmittel", -85.30),
        (f"{year}-03-15", "Netflix", "Streaming", -12.99),
        (f"{year}-07-01", "Lufthansa", "Urlaub Mallorca", -450.00),
    ]

    for txn_date, vendor, desc, amount in private:
        transactions.append({
            "date": txn_date,
            "amount": f"{amount:.2f}",
            "counterparty": vendor,
            "description": desc,
        })

    # CSV schreiben
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Datum", "Betrag", "Empfaenger", "Verwendungszweck"])
        for txn in sorted(transactions, key=lambda x: x["date"]):
            writer.writerow([
                txn["date"],
                txn["amount"].replace(".", ","),  # German format
                txn["counterparty"],
                txn["description"],
            ])

    return len(transactions)


def generate_vermieter_csv(path: Path, year: int = 2024) -> None:
    """Generate realistic landlord transactions."""
    transactions = []

    # Mieter mit monatlichen Zahlungen
    tenants = [
        ("Mueller, Hans", 850.00),
        ("Schmidt, Anna", 720.00),
    ]

    for month in range(1, 13):
        for tenant, rent in tenants:
            # Miete kommt zwischen 1. und 5.
            day = randint(1, 5)
            transactions.append({
                "date": f"{year}-{month:02d}-{day:02d}",
                "amount": f"{rent:.2f}",
                "counterparty": tenant,
                "description": f"Miete {month:02d}/{year}",
            })

    # Nebenkosten-Nachzahlung
    for tenant, _ in tenants:
        transactions.append({
            "date": f"{year}-03-15",
            "amount": f"{round(uniform(150, 350), 2):.2f}",
            "counterparty": tenant,
            "description": f"NK-Nachzahlung {year-1}",
        })

    # Ausgaben
    expenses = [
        (f"{year}-01-15", "Allianz Versicherung", "Gebaeudeversicherung", -580.00),
        (f"{year}-02-01", "HV Mustermann GmbH", "Hausverwaltung Q1", -450.00),
        (f"{year}-03-20", "Handwerker Schulze", "Heizungsreparatur", -890.00),
        (f"{year}-05-01", "HV Mustermann GmbH", "Hausverwaltung Q2", -450.00),
        (f"{year}-06-15", "Gartenbau Gruener", "Gartenpflege", -280.00),
        (f"{year}-08-01", "HV Mustermann GmbH", "Hausverwaltung Q3", -450.00),
        (f"{year}-09-10", "Elektriker Blitz", "Reparatur Steckdosen", -320.00),
        (f"{year}-11-01", "HV Mustermann GmbH", "Hausverwaltung Q4", -450.00),
        (f"{year}-12-01", "Gemeinde", "Grundsteuer", -420.00),
    ]

    for txn_date, vendor, desc, amount in expenses:
        transactions.append({
            "date": txn_date,
            "amount": f"{amount:.2f}",
            "counterparty": vendor,
            "description": desc,
        })

    # CSV schreiben
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Datum", "Betrag", "Empfaenger", "Verwendungszweck"])
        for txn in sorted(transactions, key=lambda x: x["date"]):
            writer.writerow([
                txn["date"],
                txn["amount"].replace(".", ","),
                txn["counterparty"],
                txn["description"],
            ])

    return len(transactions)


def test_profile(profile: str, test_dir: Path) -> dict:
    """Test a complete workflow for a profile."""
    results = {
        "profile": profile,
        "steps": [],
        "success": True,
    }

    project_dir = test_dir / f"test-{profile}"

    # Step 1: Init
    print_step(1, f"Projekt erstellen ({profile})")
    code, stdout, stderr = run_command([
        "pacman", "init",
        "--profile", profile,
        "--year", "2024",
        "--path", str(project_dir),
    ])

    if code == 0 and (project_dir / "config.yaml").exists():
        print_success(f"Projekt erstellt: {project_dir}")
        results["steps"].append(("init", True))
    else:
        print_error(f"Init fehlgeschlagen: {stderr}")
        results["steps"].append(("init", False))
        results["success"] = False
        return results

    # Step 2: Generate test data
    print_step(2, "Test-Transaktionen generieren")
    csv_path = project_dir / "import" / "umsaetze.csv"

    if profile == "vermieter":
        txn_count = generate_vermieter_csv(csv_path)
    else:
        txn_count = generate_freiberufler_csv(csv_path)

    print_success(f"{txn_count} Transaktionen generiert")
    results["steps"].append(("generate", True))
    results["txn_count"] = txn_count

    # Step 3: Import
    print_step(3, "Transaktionen importieren")
    code, stdout, stderr = run_command([
        "pacman", "import",
        str(project_dir / "import"),
        "--project", str(project_dir),
    ])

    if code == 0:
        print_success("Import erfolgreich")
        results["steps"].append(("import", True))
    else:
        print_error(f"Import fehlgeschlagen: {stderr}")
        results["steps"].append(("import", False))
        results["success"] = False
        return results

    # Step 4: Categorize
    print_step(4, "Automatisch kategorisieren")
    code, stdout, stderr = run_command([
        "pacman", "categorize",
        "--project", str(project_dir),
    ])

    if code == 0:
        print_success("Kategorisierung erfolgreich")
        results["steps"].append(("categorize", True))
    else:
        print_error(f"Kategorisierung fehlgeschlagen: {stderr}")
        results["steps"].append(("categorize", False))
        # Continue anyway

    # Step 5: Status
    print_step(5, "Status pruefen")
    code, stdout, stderr = run_command([
        "pacman", "status",
        "--project", str(project_dir),
    ])

    if code == 0:
        print_success("Status OK")
        print(f"    {stdout[:200]}..." if len(stdout) > 200 else f"    {stdout}")
        results["steps"].append(("status", True))
    else:
        print_error(f"Status fehlgeschlagen: {stderr}")
        results["steps"].append(("status", False))

    # Step 6: Calculate
    print_step(6, "Steuer berechnen")
    code, stdout, stderr = run_command([
        "pacman", "calculate",
        "--project", str(project_dir),
    ])

    if code == 0:
        print_success("Berechnung erfolgreich")
        results["steps"].append(("calculate", True))
    else:
        print_error(f"Berechnung fehlgeschlagen: {stderr}")
        results["steps"].append(("calculate", False))

    # Step 7: Export XLSX
    print_step(7, "Excel-Export erstellen")
    code, stdout, stderr = run_command([
        "pacman", "export",
        "--format", "xlsx",
        "--project", str(project_dir),
    ])

    export_files = list((project_dir / "export").glob("*.xlsx"))
    if code == 0 and export_files:
        print_success(f"Export erstellt: {export_files[0].name}")
        results["steps"].append(("export_xlsx", True))
        results["export_file"] = str(export_files[0])
    else:
        print_error(f"Export fehlgeschlagen: {stderr}")
        results["steps"].append(("export_xlsx", False))

    # Step 8: Export CSV
    print_step(8, "CSV-Export erstellen")
    code, stdout, stderr = run_command([
        "pacman", "export",
        "--format", "csv",
        "--project", str(project_dir),
    ])

    csv_files = list((project_dir / "export").glob("*.csv"))
    if code == 0 and csv_files:
        print_success(f"CSV Export erstellt: {csv_files[0].name}")
        results["steps"].append(("export_csv", True))
    else:
        print_error(f"CSV Export fehlgeschlagen: {stderr}")
        results["steps"].append(("export_csv", False))

    # Validate results
    print_step(9, "Ergebnisse validieren")

    # Check transactions.json exists and has data
    txn_file = project_dir / "transactions.json"
    if txn_file.exists():
        with open(txn_file) as f:
            txns = json.load(f)

        categorized = sum(1 for t in txns if t.get("category") and t["category"] != "uncategorized")
        pct = (categorized / len(txns) * 100) if txns else 0

        print_success(f"Transaktionen: {len(txns)}, Kategorisiert: {categorized} ({pct:.1f}%)")
        results["categorized_pct"] = pct
        results["steps"].append(("validate", True))
    else:
        print_error("transactions.json nicht gefunden")
        results["steps"].append(("validate", False))
        results["success"] = False

    return results


def main():
    parser = argparse.ArgumentParser(description="PACMAN MVP Smoke Test")
    parser.add_argument("--profile", choices=["freiberufler", "vermieter", "einzelunternehmer"],
                       default="freiberufler", help="Profil zum Testen")
    parser.add_argument("--all", action="store_true", help="Alle Profile testen")
    parser.add_argument("--keep", action="store_true", help="Test-Verzeichnis behalten")
    args = parser.parse_args()

    print_header("PACMAN MVP Smoke Test")
    print(f"Version: 0.2.0")
    print(f"Datum: {date.today()}")

    # Create temp directory
    test_dir = Path(tempfile.mkdtemp(prefix="pacman_smoke_"))
    print(f"Test-Verzeichnis: {test_dir}\n")

    profiles = ["freiberufler", "vermieter"] if args.all else [args.profile]
    all_results = []

    try:
        for profile in profiles:
            print_header(f"Test: {profile.upper()}")
            result = test_profile(profile, test_dir)
            all_results.append(result)

    finally:
        # Summary
        print_header("ZUSAMMENFASSUNG")

        total_steps = 0
        passed_steps = 0

        for result in all_results:
            profile = result["profile"]
            steps_passed = sum(1 for _, ok in result["steps"] if ok)
            steps_total = len(result["steps"])
            total_steps += steps_total
            passed_steps += steps_passed

            status = f"{Colors.GREEN}BESTANDEN{Colors.END}" if result["success"] else f"{Colors.RED}FEHLGESCHLAGEN{Colors.END}"
            print(f"  {profile}: {status} ({steps_passed}/{steps_total} Steps)")

            if "categorized_pct" in result:
                print(f"    Kategorisierung: {result['categorized_pct']:.1f}%")

        print(f"\n{Colors.BOLD}Gesamt: {passed_steps}/{total_steps} Steps bestanden{Colors.END}")

        # Cleanup
        if not args.keep:
            shutil.rmtree(test_dir)
            print(f"\nTest-Verzeichnis geloescht.")
        else:
            print(f"\nTest-Verzeichnis behalten: {test_dir}")

        # Exit code
        all_passed = all(r["success"] for r in all_results)
        sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
