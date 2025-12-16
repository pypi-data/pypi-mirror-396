"""
PACMAN Dashboard - Streamlit Web Interface

Privacy-first tax automation dashboard.
Run with: streamlit run src/pacman/dashboard/app.py -- --project <path>
Or: pacman dashboard --project <path>
"""

import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import streamlit as st
import yaml

# Page config must be first Streamlit command
st.set_page_config(
    page_title="PACMAN Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_project(project_path: Path) -> dict:
    """Load project data from disk."""
    data = {
        "config": None,
        "transactions": [],
        "path": project_path,
    }

    # Load config
    config_path = project_path / "config.yaml"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            data["config"] = yaml.safe_load(f)

    # Load transactions
    txn_path = project_path / "transactions.json"
    if txn_path.exists():
        with open(txn_path, encoding="utf-8") as f:
            data["transactions"] = json.load(f)

    return data


def format_currency(amount: float | Decimal | str) -> str:
    """Format amount as currency."""
    try:
        value = float(amount) if not isinstance(amount, float) else amount
        return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(amount)


def get_category_color(category: str) -> str:
    """Get color for category."""
    colors = {
        "rental_income": "#2ecc71",
        "rental_expense": "#e74c3c",
        "business_income": "#3498db",
        "business_expense": "#9b59b6",
        "deductible": "#f39c12",
        "private": "#95a5a6",
        "passthrough": "#1abc9c",
        "uncategorized": "#bdc3c7",
    }
    return colors.get(category, "#7f8c8d")


def render_sidebar(data: dict) -> None:
    """Render sidebar with project info."""
    st.sidebar.title("📊 PACMAN")
    st.sidebar.caption("Privacy-first Tax Automation")

    if data["config"]:
        st.sidebar.divider()
        st.sidebar.subheader("Projekt")
        st.sidebar.write(f"**Jahr:** {data['config'].get('year', 'N/A')}")
        st.sidebar.write(f"**Profil:** {data['config'].get('profile', 'N/A')}")
        st.sidebar.write(f"**Jurisdiction:** {data['config'].get('jurisdiction', 'N/A')}")

        tenants = data["config"].get("tenants", [])
        if tenants:
            st.sidebar.write(f"**Mieter:** {len(tenants)}")

    st.sidebar.divider()
    st.sidebar.subheader("Status")
    txn_count = len(data["transactions"])
    categorized = sum(
        1 for t in data["transactions"]
        if t.get("category") and t["category"] != "uncategorized"
    )
    pct = (categorized / txn_count * 100) if txn_count > 0 else 0

    st.sidebar.metric("Transaktionen", txn_count)
    st.sidebar.metric("Kategorisiert", f"{pct:.1f}%")

    st.sidebar.divider()
    st.sidebar.caption("🔒 100% lokal - Keine Cloud")


def render_overview(data: dict) -> None:
    """Render overview page."""
    st.header("📈 Übersicht")

    if not data["transactions"]:
        st.warning("Keine Transaktionen gefunden. Importiere zuerst Bank-Daten.")
        st.code("pacman import ./import/ --project <path>", language="bash")
        return

    # Calculate summary
    summary = defaultdict(lambda: Decimal("0"))
    for t in data["transactions"]:
        cat = t.get("category", "uncategorized")
        amt = Decimal(str(t.get("amount", 0)))
        summary[cat] += amt

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    rental_income = float(summary.get("rental_income", 0))
    rental_expense = float(summary.get("rental_expense", 0))
    business_income = float(summary.get("business_income", 0))
    business_expense = float(summary.get("business_expense", 0))

    with col1:
        st.metric(
            "Mieteinnahmen",
            format_currency(rental_income),
            delta=None,
        )

    with col2:
        st.metric(
            "Vermietungskosten",
            format_currency(rental_expense),
            delta=None,
        )

    with col3:
        net_rental = rental_income + rental_expense
        st.metric(
            "Netto Vermietung",
            format_currency(net_rental),
            delta=f"{(net_rental/rental_income*100):.1f}%" if rental_income > 0 else None,
        )

    with col4:
        total_income = rental_income + business_income
        total_expense = rental_expense + business_expense
        st.metric(
            "Gesamt Ergebnis",
            format_currency(total_income + total_expense),
        )

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Einnahmen vs. Ausgaben")

        try:
            import plotly.graph_objects as go

            income_total = rental_income + business_income
            expense_total = abs(rental_expense + business_expense)

            fig = go.Figure(data=[
                go.Bar(
                    name="Einnahmen",
                    x=["Summe"],
                    y=[income_total],
                    marker_color="#2ecc71",
                ),
                go.Bar(
                    name="Ausgaben",
                    x=["Summe"],
                    y=[expense_total],
                    marker_color="#e74c3c",
                ),
            ])
            fig.update_layout(
                barmode="group",
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.info("Plotly nicht installiert. Installiere mit: pip install plotly")

    with col2:
        st.subheader("Kategorien")

        try:
            import plotly.express as px

            # Prepare data for pie chart
            cat_data = []
            for cat, amt in summary.items():
                if cat != "private" and float(amt) != 0:
                    cat_data.append({
                        "Kategorie": cat.replace("_", " ").title(),
                        "Betrag": abs(float(amt)),
                        "Typ": "Einnahme" if float(amt) > 0 else "Ausgabe",
                    })

            if cat_data:
                fig = px.pie(
                    cat_data,
                    values="Betrag",
                    names="Kategorie",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                fig.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pass

    # Monthly breakdown
    st.divider()
    st.subheader("Monatliche Übersicht")

    monthly = defaultdict(lambda: {"income": Decimal("0"), "expense": Decimal("0")})
    for t in data["transactions"]:
        try:
            txn_date = t.get("date", "")
            if isinstance(txn_date, str) and len(txn_date) >= 7:
                month = txn_date[:7]  # YYYY-MM
                amt = Decimal(str(t.get("amount", 0)))
                if amt > 0:
                    monthly[month]["income"] += amt
                else:
                    monthly[month]["expense"] += abs(amt)
        except Exception:
            continue

    if monthly:
        try:
            import plotly.graph_objects as go

            months = sorted(monthly.keys())
            incomes = [float(monthly[m]["income"]) for m in months]
            expenses = [float(monthly[m]["expense"]) for m in months]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Einnahmen",
                x=months,
                y=incomes,
                marker_color="#2ecc71",
            ))
            fig.add_trace(go.Bar(
                name="Ausgaben",
                x=months,
                y=expenses,
                marker_color="#e74c3c",
            ))
            fig.update_layout(
                barmode="group",
                height=350,
                xaxis_title="Monat",
                yaxis_title="Betrag (€)",
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            # Fallback to simple table
            st.dataframe(
                {
                    "Monat": list(monthly.keys()),
                    "Einnahmen": [format_currency(monthly[m]["income"]) for m in monthly],
                    "Ausgaben": [format_currency(monthly[m]["expense"]) for m in monthly],
                }
            )


def render_transactions(data: dict) -> None:
    """Render transactions page."""
    st.header("📋 Transaktionen")

    if not data["transactions"]:
        st.warning("Keine Transaktionen gefunden.")
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    categories = sorted(set(
        t.get("category", "uncategorized") or "uncategorized"
        for t in data["transactions"]
    ))

    with col1:
        selected_categories = st.multiselect(
            "Kategorien",
            options=categories,
            default=categories,
        )

    with col2:
        amount_filter = st.selectbox(
            "Betragsfilter",
            options=["Alle", "Nur Einnahmen", "Nur Ausgaben"],
        )

    with col3:
        search = st.text_input("Suche", placeholder="Beschreibung oder Empfänger...")

    # Filter transactions
    filtered = []
    for t in data["transactions"]:
        cat = t.get("category", "uncategorized") or "uncategorized"
        if cat not in selected_categories:
            continue

        amt = float(t.get("amount", 0))
        if amount_filter == "Nur Einnahmen" and amt <= 0:
            continue
        if amount_filter == "Nur Ausgaben" and amt >= 0:
            continue

        if search:
            search_lower = search.lower()
            desc = str(t.get("description", "")).lower()
            cp = str(t.get("counterparty", "")).lower()
            if search_lower not in desc and search_lower not in cp:
                continue

        filtered.append(t)

    st.caption(f"{len(filtered)} von {len(data['transactions'])} Transaktionen")

    # Display as table
    if filtered:
        table_data = []
        for t in filtered:
            table_data.append({
                "Datum": t.get("date", ""),
                "Betrag": format_currency(t.get("amount", 0)),
                "Kategorie": (t.get("category", "") or "").replace("_", " ").title(),
                "Empfänger": t.get("counterparty", "") or "",
                "Beschreibung": (t.get("description", "") or "")[:50],
            })

        st.dataframe(
            table_data,
            use_container_width=True,
            height=500,
        )


def render_categories(data: dict) -> None:
    """Render category breakdown page."""
    st.header("🏷️ Kategorien")

    if not data["transactions"]:
        st.warning("Keine Transaktionen gefunden.")
        return

    # Calculate by category
    by_category = defaultdict(list)
    for t in data["transactions"]:
        cat = t.get("category", "uncategorized") or "uncategorized"
        by_category[cat].append(t)

    # Display each category
    for cat in sorted(by_category.keys()):
        txns = by_category[cat]
        total = sum(Decimal(str(t.get("amount", 0))) for t in txns)

        with st.expander(
            f"**{cat.replace('_', ' ').title()}** - {len(txns)} Transaktionen - {format_currency(total)}",
            expanded=cat in ["rental_income", "rental_expense"],
        ):
            # Sub-category breakdown
            by_subcat = defaultdict(lambda: {"count": 0, "total": Decimal("0")})
            for t in txns:
                subcat = t.get("subcategory", "Sonstige") or "Sonstige"
                by_subcat[subcat]["count"] += 1
                by_subcat[subcat]["total"] += Decimal(str(t.get("amount", 0)))

            for subcat, info in sorted(by_subcat.items()):
                st.write(
                    f"- **{subcat}**: {info['count']}x = {format_currency(info['total'])}"
                )


def render_export(data: dict) -> None:
    """Render export page."""
    st.header("📤 Export")

    if not data["transactions"]:
        st.warning("Keine Transaktionen zum Exportieren.")
        return

    st.write("Exportiere deine Daten für ELSTER oder weitere Verarbeitung.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CSV Export")
        st.write("Alle Transaktionen als CSV-Datei.")

        if st.button("CSV generieren", key="csv"):
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Datum", "Betrag", "Kategorie", "Unterkategorie", "Empfänger", "Beschreibung"])

            for t in data["transactions"]:
                writer.writerow([
                    t.get("date", ""),
                    t.get("amount", ""),
                    t.get("category", ""),
                    t.get("subcategory", ""),
                    t.get("counterparty", ""),
                    t.get("description", ""),
                ])

            st.download_button(
                "⬇️ CSV herunterladen",
                output.getvalue(),
                file_name=f"pacman_export_{data['config'].get('year', 'data')}.csv",
                mime="text/csv",
            )

    with col2:
        st.subheader("Zusammenfassung")
        st.write("Aggregierte Werte nach Kategorie.")

        summary = defaultdict(lambda: Decimal("0"))
        for t in data["transactions"]:
            cat = t.get("category", "uncategorized")
            summary[cat] += Decimal(str(t.get("amount", 0)))

        summary_text = "Kategorie,Summe\n"
        for cat, total in sorted(summary.items()):
            summary_text += f"{cat},{total}\n"

        st.download_button(
            "⬇️ Zusammenfassung herunterladen",
            summary_text,
            file_name=f"pacman_summary_{data['config'].get('year', 'data')}.csv",
            mime="text/csv",
        )

    st.divider()

    st.subheader("CLI Export")
    st.write("Für ELSTER-ready Excel-Export nutze die CLI:")
    st.code(f"pacman export --format xlsx --project {data['path']}", language="bash")


def main() -> None:
    """Main dashboard entry point."""
    # Get project path from command line args
    project_path = None

    # Check for --project argument
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--project" and i + 1 < len(args):
            project_path = Path(args[i + 1])
            break
        if arg.startswith("--project="):
            project_path = Path(arg.split("=", 1)[1])
            break

    # Fallback: check for project in current directory
    if project_path is None:
        if Path("config.yaml").exists():
            project_path = Path(".")
        else:
            st.error("Kein Projekt angegeben. Starte mit: `pacman dashboard --project <path>`")
            st.stop()

    project_path = project_path.resolve()

    if not (project_path / "config.yaml").exists():
        st.error(f"Kein PACMAN-Projekt in: {project_path}")
        st.write("Erstelle ein Projekt mit:")
        st.code("pacman init --profile vermieter --year 2024 --path <path>", language="bash")
        st.stop()

    # Load project data
    data = load_project(project_path)

    # Render sidebar
    render_sidebar(data)

    # Navigation
    pages = {
        "📈 Übersicht": render_overview,
        "📋 Transaktionen": render_transactions,
        "🏷️ Kategorien": render_categories,
        "📤 Export": render_export,
    }

    selection = st.sidebar.radio("Navigation", list(pages.keys()))

    # Render selected page
    pages[selection](data)


if __name__ == "__main__":
    main()
