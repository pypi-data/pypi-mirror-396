"""
PACMAN CLI - Privacy-first Automated Calculation & Management of Numbers

Command-line interface for PACMAN tax automation.
"""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from pacman import __version__
from pacman.core.models import PacmanConfig, TaxYear
from pacman.core.privacy import PrivacyGuarantees

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="pacman",
    help="PACMAN - Privacy-first tax automation for freelancers & landlords. 100% local, no cloud.",
    add_completion=False,
)
console = Console()


def _safe_write_file(path: Path, content: str, description: str = "file") -> None:
    """Write content to file with proper error handling."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        console.print(f"[red]Failed to write {description}: {e}[/red]")
        raise typer.Exit(1)


def _validate_profile(profile: str, jurisdiction: str) -> None:
    """Validate that the profile is supported for the given jurisdiction."""
    from pacman.jurisdictions import get_plugin

    try:
        plugin = get_plugin(jurisdiction)
        plugin.validate_profile(profile)
    except ValueError as e:
        console.print(f"[red]Invalid profile: {e}[/red]")
        try:
            plugin = get_plugin(jurisdiction)
            console.print(f"Supported profiles: {', '.join(plugin.supported_profiles)}")
        except Exception:
            pass
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Invalid jurisdiction '{jurisdiction}': {e}[/red]")
        raise typer.Exit(1)


def _safe_load_yaml(path: Path, description: str = "config") -> dict:
    """Safely load YAML file with corruption handling."""
    import yaml

    if not path.exists():
        console.print(f"[red]{description.capitalize()} not found: {path}[/red]")
        raise typer.Exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                console.print(f"[red]{description.capitalize()} is empty: {path}[/red]")
                raise typer.Exit(1)
            return data
    except yaml.YAMLError as e:
        console.print(f"[red]{description.capitalize()} corrupted (invalid YAML): {path}[/red]")
        console.print(f"[dim]Error: {e}[/dim]")
        raise typer.Exit(1)
    except OSError as e:
        console.print(f"[red]Cannot read {description}: {e}[/red]")
        raise typer.Exit(1)


def _safe_load_json(path: Path, description: str = "data") -> list | dict:
    """Safely load JSON file with corruption handling."""
    import json

    if not path.exists():
        console.print(f"[red]{description.capitalize()} not found: {path}[/red]")
        raise typer.Exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]{description.capitalize()} corrupted (invalid JSON): {path}[/red]")
        console.print(f"[dim]Error at line {e.lineno}: {e.msg}[/dim]")
        raise typer.Exit(1)
    except OSError as e:
        console.print(f"[red]Cannot read {description}: {e}[/red]")
        raise typer.Exit(1)


def _safe_load_config(project_dir: Path) -> PacmanConfig:
    """Safely load and validate PacmanConfig from project directory."""
    from pydantic import ValidationError

    config_path = project_dir / "config.yaml"
    config_data = _safe_load_yaml(config_path, "config file")

    try:
        return PacmanConfig(**config_data)
    except ValidationError as e:
        console.print(f"[red]Config file invalid: {config_path}[/red]")
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            console.print(f"[dim]  - {field}: {error['msg']}[/dim]")
        raise typer.Exit(1)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"PACMAN v{__version__}")
        console.print("Privacy-first Automated Calculation & Management of Numbers")
        raise typer.Exit()


def privacy_callback(value: bool) -> None:
    if value:
        PrivacyGuarantees.print_guarantees()
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit."
    ),
    privacy: bool = typer.Option(
        False, "--privacy", callback=privacy_callback, is_eager=True,
        help="Show privacy guarantees and exit."
    ),
) -> None:
    """
    PACMAN - Privacy-first Automated Calculation & Management of Numbers

    100% local tax automation. Your data never leaves your device.
    """
    pass


@app.command()
def init(
    profile: str = typer.Option(
        ..., "--profile", "-p",
        help="Tax profile: vermieter, einzelunternehmer, freiberufler"
    ),
    year: int = typer.Option(
        ..., "--year", "-y",
        help="Tax year (e.g., 2024)"
    ),
    jurisdiction: str = typer.Option(
        "DE", "--jurisdiction", "-j",
        help="Jurisdiction code (DE, AT, CH-ZH)"
    ),
    path: Path = typer.Option(
        Path("."), "--path",
        help="Project directory path"
    ),
) -> None:
    """
    Initialize a new PACMAN project.

    Creates the project structure and config file.
    """
    import yaml

    # Validate profile before creating project
    _validate_profile(profile, jurisdiction)

    project_dir = path.resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (project_dir / "import").mkdir(exist_ok=True)
    (project_dir / "export").mkdir(exist_ok=True)

    # Create config
    config = PacmanConfig(
        version="1.0",
        jurisdiction=jurisdiction,
        profile=profile,
        year=year,
    )

    config_path = project_dir / "config.yaml"
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False, allow_unicode=True)
    except OSError as e:
        console.print(f"[red]Failed to write config.yaml: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Project initialized at: {project_dir}")
    console.print(f"  Profile: {profile}")
    console.print(f"  Year: {year}")
    console.print(f"  Jurisdiction: {jurisdiction}")
    console.print()
    console.print("Next steps:")
    console.print(f"  1. Copy bank exports to: {project_dir / 'import'}")
    console.print(f"  2. Run: pacman import {project_dir / 'import'}")


@app.command("import")
def import_transactions(
    path: Path = typer.Argument(
        ...,
        help="Path to CSV/XLSX files or directory"
    ),
    bank: str = typer.Option(
        "auto", "--bank", "-b",
        help="Bank format: deutsche-bank, sparkasse, generic, auto"
    ),
    project: Path = typer.Option(
        Path("."), "--project", "-p",
        help="Project directory"
    ),
) -> None:
    """
    Import bank transactions from CSV/XLSX files.
    """
    import json

    from pacman.importers import (
        DeutscheBankImporter,
        DKBImporter,
        GenericCSVImporter,
        INGImporter,
        N26Importer,
        SparkasseImporter,
    )

    # Get files to import
    if path.is_dir():
        files = list(path.glob("*.csv")) + list(path.glob("*.xlsx"))
    else:
        files = [path]

    if not files:
        console.print("[red]No CSV/XLSX files found.[/red]")
        raise typer.Exit(1)

    console.print(f"Found {len(files)} file(s) to import")

    # Select importer
    bank_importers = {
        "deutsche-bank": DeutscheBankImporter,
        "sparkasse": SparkasseImporter,
        "ing": INGImporter,
        "n26": N26Importer,
        "dkb": DKBImporter,
        "generic": GenericCSVImporter,
    }

    if bank in bank_importers:
        importer = bank_importers[bank]()
    elif bank == "auto":
        # Auto-detect: try bank-specific importers first
        importers_to_try = [
            SparkasseImporter(),
            DeutscheBankImporter(),
            INGImporter(),
            N26Importer(),
            DKBImporter(),
            GenericCSVImporter(),
        ]
        importer = GenericCSVImporter()  # Fallback
        for candidate in importers_to_try:
            if any(candidate.can_parse(f) for f in files):
                importer = candidate
                break
    else:
        console.print(f"[red]Unknown bank: {bank}[/red]")
        console.print(f"Supported: {', '.join(bank_importers.keys())}, auto")
        raise typer.Exit(1)

    console.print(f"Using importer: {importer.bank_name}")

    # Import transactions
    all_transactions = []
    for file in files:
        if importer.can_parse(file):
            txns = importer.parse(file)
            all_transactions.extend(txns)
            console.print(f"  [green]✓[/green] {file.name}: {len(txns)} transactions")
        else:
            console.print(f"  [yellow]⚠[/yellow] {file.name}: Skipped (format not recognized)")

    if not all_transactions:
        console.print("[red]No transactions imported.[/red]")
        raise typer.Exit(1)

    # Save transactions
    project_dir = project.resolve()
    txn_file = project_dir / "transactions.json"

    txn_data = [t.model_dump(mode="json") for t in all_transactions]
    try:
        with open(txn_file, "w", encoding="utf-8") as f:
            json.dump(txn_data, f, indent=2, ensure_ascii=False, default=str)
    except OSError as e:
        console.print(f"[red]Failed to write transactions.json: {e}[/red]")
        raise typer.Exit(1)

    console.print()
    console.print(f"[green]✓[/green] Imported {len(all_transactions)} transactions")
    console.print(f"  Saved to: {txn_file}")
    console.print()
    console.print("Next step: pacman categorize")


@app.command()
def categorize(
    interactive: bool = typer.Option(
        False, "--interactive", "-i",
        help="Review uncertain categorizations interactively"
    ),
    threshold: float = typer.Option(
        0.8, "--threshold", "-t",
        help="Auto-accept confidence threshold (0-1)"
    ),
    project: Path = typer.Option(
        Path("."), "--project", "-p",
        help="Project directory"
    ),
) -> None:
    """
    Categorize transactions using rules.
    """
    import json

    project_dir = project.resolve()

    # Load config (with corruption handling)
    config = _safe_load_config(project_dir)

    # Load transactions (with corruption handling)
    txn_file = project_dir / "transactions.json"
    txn_data = _safe_load_json(txn_file, "transactions file")

    from pacman.core.models import Transaction
    transactions = [Transaction(**t) for t in txn_data]

    # Get categorizer
    from pacman.jurisdictions import get_plugin
    plugin = get_plugin(config.jurisdiction)
    categorizer = plugin.get_categorizer(config.profile)

    # Set config for dynamic rules
    categorizer.set_config({
        "tenants": config.tenants,
        "landlords": config.landlords,
    })

    # Categorize
    console.print(f"Categorizing {len(transactions)} transactions...")
    categorized = categorizer.categorize_all(transactions)

    # Count results
    categorized_count = sum(1 for t in categorized if t.is_categorized)
    uncertain_count = sum(1 for t in categorized if t.is_categorized and t.confidence < threshold)

    console.print(f"  Categorized: {categorized_count}/{len(categorized)}")
    console.print(f"  Uncertain (< {threshold}): {uncertain_count}")

    # Save categorized transactions
    txn_data = [t.model_dump(mode="json") for t in categorized]
    try:
        with open(txn_file, "w", encoding="utf-8") as f:
            json.dump(txn_data, f, indent=2, ensure_ascii=False, default=str)
    except OSError as e:
        console.print(f"[red]Failed to save categorized transactions: {e}[/red]")
        raise typer.Exit(1)

    console.print()
    console.print("[green]✓[/green] Saved categorized transactions")
    console.print()
    console.print("Next step: pacman calculate")


@app.command()
def tenants(
    action: str = typer.Argument(
        ...,
        help="Action: add, remove, list"
    ),
    name: str | None = typer.Argument(
        None,
        help="Tenant name (for add/remove)"
    ),
    project: Path = typer.Option(
        Path("."), "--project", "-p",
        help="Project directory"
    ),
) -> None:
    """
    Manage tenant list for Vermieter profile.
    """
    import yaml

    project_dir = project.resolve()
    config_path = project_dir / "config.yaml"

    # Load config with corruption handling
    config_data = _safe_load_yaml(config_path, "config file")

    tenants_list = config_data.get("tenants", [])

    if action == "list":
        if tenants_list:
            console.print("Tenants:")
            for tenant in tenants_list:
                console.print(f"  - {tenant}")
        else:
            console.print("No tenants configured.")

    elif action == "add":
        if not name:
            console.print("[red]Please provide a tenant name.[/red]")
            raise typer.Exit(1)
        if name not in tenants_list:
            tenants_list.append(name)
            config_data["tenants"] = tenants_list
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            except OSError as e:
                console.print(f"[red]Failed to update config.yaml: {e}[/red]")
                raise typer.Exit(1)
            console.print(f"[green]✓[/green] Added tenant: {name}")
        else:
            console.print(f"Tenant already exists: {name}")

    elif action == "remove":
        if not name:
            console.print("[red]Please provide a tenant name.[/red]")
            raise typer.Exit(1)
        if name in tenants_list:
            tenants_list.remove(name)
            config_data["tenants"] = tenants_list
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            except OSError as e:
                console.print(f"[red]Failed to update config.yaml: {e}[/red]")
                raise typer.Exit(1)
            console.print(f"[green]✓[/green] Removed tenant: {name}")
        else:
            console.print(f"Tenant not found: {name}")


@app.command()
def calculate(
    project: Path = typer.Option(
        Path("."), "--project", "-p",
        help="Project directory"
    ),
) -> None:
    """
    Calculate tax values from categorized transactions.
    """
    project_dir = project.resolve()

    # Load config and transactions (with corruption handling)
    config = _safe_load_config(project_dir)

    txn_file = project_dir / "transactions.json"
    txn_data = _safe_load_json(txn_file, "transactions file")

    from pacman.core.models import Transaction
    transactions = [Transaction(**t) for t in txn_data]

    # Create TaxYear
    tax_year = TaxYear(
        year=config.year,
        jurisdiction=config.jurisdiction,
        profile=config.profile,
        transactions=transactions,
    )

    # Calculate
    from pacman.jurisdictions import get_plugin
    plugin = get_plugin(config.jurisdiction)
    result = plugin.calculate(tax_year)

    # Display results
    console.print()
    console.print(f"[bold]Tax Calculation - {config.year}[/bold]")
    console.print("=" * 50)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Description")
    table.add_column("Amount (EUR)", justify="right")

    table.add_row("Income (Total)", str(result.income_total))
    table.add_row("Expenses (Total)", str(result.expenses_total))
    table.add_row("Deductibles", str(result.deductibles_total))
    table.add_row("─" * 20, "─" * 15)
    table.add_row("[bold]Taxable Income[/bold]", f"[bold]{result.taxable_income}[/bold]")

    console.print(table)

    if result.notes:
        console.print()
        console.print("[yellow]Notes:[/yellow]")
        for note in result.notes:
            console.print(f"  • {note}")

    console.print()
    console.print("Next step: pacman export")


@app.command()
def export(
    format: str = typer.Option(
        "xlsx", "--format", "-f",
        help="Export format: xlsx, csv"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o",
        help="Output path (default: ./export)"
    ),
    project: Path = typer.Option(
        Path("."), "--project", "-p",
        help="Project directory"
    ),
) -> None:
    """
    Export ELSTER-ready tax files.
    """
    project_dir = project.resolve()

    # Load config and transactions (with corruption handling)
    config = _safe_load_config(project_dir)

    txn_file = project_dir / "transactions.json"
    txn_data = _safe_load_json(txn_file, "transactions file")

    from pacman.core.models import Transaction
    transactions = [Transaction(**t) for t in txn_data]

    # Create TaxYear
    tax_year = TaxYear(
        year=config.year,
        jurisdiction=config.jurisdiction,
        profile=config.profile,
        transactions=transactions,
    )

    # Export
    output_path = output or (project_dir / "export")
    output_path.mkdir(parents=True, exist_ok=True)

    from pacman.jurisdictions import get_plugin
    plugin = get_plugin(config.jurisdiction)
    result_path = plugin.export(tax_year, format, output_path)

    console.print(f"[green]✓[/green] Exported to: {result_path}")


@app.command()
def status(
    project: Path = typer.Option(
        Path("."), "--project", "-p",
        help="Project directory"
    ),
) -> None:
    """
    Show project status and statistics.
    """
    import json

    project_dir = project.resolve()
    config_path = project_dir / "config.yaml"

    if not config_path.exists():
        console.print("[red]No PACMAN project found in current directory.[/red]")
        console.print("Run 'pacman init' to create a new project.")
        raise typer.Exit(1)

    # Load config with corruption handling
    config = _safe_load_config(project_dir)

    console.print("[bold]PACMAN Project Status[/bold]")
    console.print("=" * 40)
    console.print(f"Year: {config.year}")
    console.print(f"Profile: {config.profile}")
    console.print(f"Jurisdiction: {config.jurisdiction}")

    txn_file = project_dir / "transactions.json"
    if txn_file.exists():
        # Load with corruption handling (but don't exit if file doesn't exist)
        try:
            with open(txn_file, encoding="utf-8") as f:
                txn_data = json.load(f)
        except json.JSONDecodeError as e:
            console.print(f"[red]Transactions file corrupted: {e.msg}[/red]")
            raise typer.Exit(1)

        from pacman.core.models import Transaction
        transactions = [Transaction(**t) for t in txn_data]

        categorized = sum(1 for t in transactions if t.is_categorized)

        console.print()
        console.print(f"Transactions: {len(transactions)}")
        pct = (categorized / len(transactions) * 100) if transactions else 0.0
        console.print(f"Categorized: {categorized}/{len(transactions)} ({pct:.1f}%)")
    else:
        console.print()
        console.print("[yellow]No transactions imported yet.[/yellow]")

    if config.tenants:
        console.print()
        console.print(f"Tenants: {len(config.tenants)}")


@app.command()
def dashboard(
    project: Path = typer.Option(
        Path("."), "--project", "-p",
        help="Project directory"
    ),
    port: int = typer.Option(
        8501, "--port",
        help="Port for the dashboard server"
    ),
) -> None:
    """
    Launch the Streamlit dashboard.

    Opens a web-based interface to view and analyze your tax data.
    """
    import subprocess
    import sys

    project_dir = project.resolve()

    # Check if project exists
    if not (project_dir / "config.yaml").exists():
        console.print("[red]No PACMAN project found.[/red]")
        console.print("Run 'pacman init' first to create a project.")
        raise typer.Exit(1)

    # Disable privacy hook for dashboard (Streamlit needs network modules for local UI)
    from pacman.core.privacy import PrivacyGuarantees
    PrivacyGuarantees.disable_for_dashboard()

    # Check if streamlit is installed
    try:
        import streamlit  # noqa: F401
    except ImportError:
        console.print("[red]Streamlit not installed.[/red]")
        console.print("Install with: pip install pacman-tax[dashboard]")
        raise typer.Exit(1)

    # Find dashboard app path
    import inspect

    from pacman.dashboard import app as dashboard_app
    dashboard_path = Path(inspect.getfile(dashboard_app)).resolve()

    console.print("[green]Starting PACMAN Dashboard...[/green]")
    console.print(f"Project: {project_dir}")
    console.print(f"URL: http://localhost:{port}")
    console.print()
    console.print("[dim]Press Ctrl+C to stop[/dim]")

    # Launch streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--",
        "--project", str(project_dir),
    ])


if __name__ == "__main__":
    app()
