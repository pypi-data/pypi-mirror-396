"""
Germany (DE) Jurisdiction Plugin.

Implements German tax logic for:
- Vermieter (Anlage V - Vermietung und Verpachtung)
- Einzelunternehmer (Anlage G - Gewerbebetrieb, EÜR)
- Freiberufler (Anlage S - Selbständige Arbeit, EÜR)
"""

from decimal import Decimal
from pathlib import Path
from typing import Any

from pacman.core.categorizer import CategorizationRule
from pacman.core.models import TaxYear
from pacman.jurisdictions.base import JurisdictionPlugin, TaxResult
from pacman.jurisdictions.germany.constants import TAX_CONSTANTS
from pacman.jurisdictions.germany.rules import load_rules


class GermanyPlugin(JurisdictionPlugin):
    """
    Germany jurisdiction plugin.

    Implements ELSTER-compatible tax logic for German tax returns.
    """

    @property
    def code(self) -> str:
        return "DE"

    @property
    def name(self) -> str:
        return "Deutschland"

    @property
    def supported_profiles(self) -> list[str]:
        return [
            # Basis-Profile
            "freiberufler",
            "einzelunternehmer",
            "vermieter",
            "kleinunternehmer",
            "gmbh_geschaeftsfuehrer",
            "nebenberuflich",
            # Branchen-Profile
            "it_freelancer",
            "berater_coach",
            "content_creator",
            "e_commerce",
            "handwerker",
            "kuenstler",
            "heilberufler",
        ]

    def get_tax_constants(self, year: int) -> dict[str, Any]:
        """Get German tax constants for the year."""
        if year not in TAX_CONSTANTS:
            # Use the latest available year
            latest_year = max(TAX_CONSTANTS.keys())
            return TAX_CONSTANTS[latest_year]
        return TAX_CONSTANTS[year]

    def get_rules(self, profile: str) -> list[CategorizationRule]:
        """Get categorization rules for the profile."""
        self.validate_profile(profile)
        return load_rules(profile)

    def calculate(self, tax_year: TaxYear) -> TaxResult:
        """
        Calculate German taxes for the year.

        Handles:
        - Einkünfte aus V+V (Anlage V)
        - Einkünfte aus Gewerbebetrieb (Anlage G)
        - Sonderausgaben / Vorsorgeaufwand
        """
        result = TaxResult()
        constants = self.get_tax_constants(tax_year.year)

        # Calculate aggregates if not already done
        tax_year.calculate_aggregates()

        # Anlage V - Vermietung und Verpachtung
        if tax_year.profile == "vermieter" or tax_year.income_rental > 0:
            anlage_v = self._calculate_anlage_v(tax_year)
            result.add_form_data("Anlage_V", anlage_v)

        # Anlage G / EÜR - Gewerbebetrieb (not for Freiberufler who use Anlage S)
        has_business_income = tax_year.income_business > 0 and tax_year.profile != "freiberufler"
        if tax_year.profile in ["einzelunternehmer", "vermieter", "nebenberuflich"] or has_business_income:
            anlage_g, euer = self._calculate_anlage_g_euer(tax_year)
            result.add_form_data("Anlage_G", anlage_g)
            result.add_form_data("Anlage_EUR", euer)

        # Anlage S - Freiberufler (similar to EÜR but no Gewerbesteuer)
        if tax_year.profile == "freiberufler":
            anlage_s = self._calculate_anlage_s(tax_year)
            result.add_form_data("Anlage_S", anlage_s)

        # Anlage N - Nichtselbständige Arbeit (GmbH-GF, Nebenberuflich)
        if tax_year.profile in ["gmbh_geschaeftsfuehrer", "nebenberuflich"] or tax_year.income_employment > 0:
            anlage_n = self._calculate_anlage_n(tax_year, constants)
            result.add_form_data("Anlage_N", anlage_n)

        # Anlage KAP - Kapitalerträge
        if tax_year.income_capital > 0:
            anlage_kap = self._calculate_anlage_kap(tax_year, constants)
            result.add_form_data("Anlage_KAP", anlage_kap)

        # Total income from all sources
        rental_income = Decimal("0")
        business_income = Decimal("0")
        employment_income = Decimal("0")
        capital_income = Decimal("0")

        if "Anlage_V" in result.forms:
            rental_income = Decimal(str(result.forms["Anlage_V"].get("einkuenfte", 0)))

        if "Anlage_G" in result.forms:
            business_income = Decimal(str(result.forms["Anlage_G"].get("gewinn_verlust", 0)))
        elif "Anlage_S" in result.forms:
            business_income = Decimal(str(result.forms["Anlage_S"].get("gewinn_verlust", 0)))

        if "Anlage_N" in result.forms:
            employment_income = Decimal(str(result.forms["Anlage_N"].get("einkuenfte", 0)))

        if "Anlage_KAP" in result.forms:
            capital_income = Decimal(str(result.forms["Anlage_KAP"].get("einkuenfte_nach_abzug", 0)))

        result.income_total = rental_income + business_income + employment_income + capital_income
        result.expenses_total = (
            tax_year.expenses_rental
            + tax_year.expenses_business
            + tax_year.expenses_employment
        )
        result.deductibles_total = tax_year.deductibles

        # Zu versteuerndes Einkommen
        result.taxable_income = result.income_total - result.deductibles_total

        # Check Grundfreibetrag
        grundfreibetrag = Decimal(str(constants["grundfreibetrag"]))
        if result.taxable_income <= grundfreibetrag:
            result.tax_due = Decimal("0")
            result.notes.append(
                f"Zu versteuerndes Einkommen ({result.taxable_income} EUR) "
                f"unter Grundfreibetrag ({grundfreibetrag} EUR) - keine Einkommensteuer."
            )
        else:
            # Simplified tax calculation (actual German tax formula is complex)
            result.notes.append(
                "Einkommensteuer-Berechnung erfordert vollständige Progressionsformel. "
                "Bitte ELSTER oder Steuerberater für genaue Berechnung nutzen."
            )

        return result

    def _calculate_anlage_v(self, tax_year: TaxYear) -> dict[str, Any]:
        """Calculate Anlage V (Vermietung und Verpachtung)."""
        # Rohertrag = Mieteinnahmen - Durchlaufposten
        rohertrag = tax_year.income_rental - (tax_year.passthrough_in - tax_year.passthrough_out)

        # If passthrough equals income, use the net difference
        if tax_year.passthrough_in > 0:
            rohertrag = tax_year.passthrough_in - tax_year.passthrough_out

        # Werbungskosten = Rental expenses
        werbungskosten = tax_year.expenses_rental

        # Einkünfte = Rohertrag - Werbungskosten
        einkuenfte = rohertrag - werbungskosten

        return {
            "zeile_4": "Vermietung und Verpachtung",
            "zeile_21_mieteinnahmen": str(rohertrag),
            "zeile_33_werbungskosten": str(werbungskosten),
            "zeile_22_einkuenfte": str(einkuenfte),
            "rohertrag": str(rohertrag),
            "werbungskosten": str(werbungskosten),
            "einkuenfte": str(einkuenfte),
        }

    def _calculate_anlage_g_euer(self, tax_year: TaxYear) -> tuple[dict[str, Any], dict[str, Any]]:
        """Calculate Anlage G and EÜR (Gewerbebetrieb)."""
        einnahmen = tax_year.income_business
        ausgaben = tax_year.expenses_business
        gewinn_verlust = einnahmen - ausgaben

        anlage_g = {
            "zeile_4": "Gewerbebetrieb",
            "zeile_11_gewinn": str(gewinn_verlust),
            "gewinn_verlust": str(gewinn_verlust),
        }

        euer = {
            "zeile_11_einnahmen": str(einnahmen),
            "zeile_60_ausgaben": str(ausgaben),
            "zeile_67_gewinn_verlust": str(gewinn_verlust),
            "einnahmen": str(einnahmen),
            "ausgaben": str(ausgaben),
            "gewinn_verlust": str(gewinn_verlust),
        }

        return anlage_g, euer

    def _calculate_anlage_s(self, tax_year: TaxYear) -> dict[str, Any]:
        """Calculate Anlage S (Freiberufliche Tätigkeit)."""
        einnahmen = tax_year.income_business
        ausgaben = tax_year.expenses_business
        gewinn_verlust = einnahmen - ausgaben

        return {
            "zeile_4": "Freiberufliche Tätigkeit",
            "zeile_5_einnahmen": str(einnahmen),
            "zeile_6_ausgaben": str(ausgaben),
            "zeile_7_gewinn": str(gewinn_verlust),
            "einnahmen": str(einnahmen),
            "ausgaben": str(ausgaben),
            "gewinn_verlust": str(gewinn_verlust),
        }

    def _calculate_anlage_n(self, tax_year: TaxYear, constants: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate Anlage N (Nichtselbständige Arbeit).

        For GmbH-Geschäftsführer and employees with additional income.
        """
        # Bruttoarbeitslohn (employment income)
        bruttoarbeitslohn = tax_year.income_employment

        # Werbungskosten (employment expenses)
        werbungskosten = tax_year.expenses_employment

        # Arbeitnehmerpauschbetrag (minimum deduction)
        arbeitnehmer_pauschbetrag = Decimal(str(constants.get("arbeitnehmer_pauschbetrag", 1230)))

        # Use higher of actual Werbungskosten or Pauschbetrag
        werbungskosten_effektiv = max(werbungskosten, arbeitnehmer_pauschbetrag)

        # Einkünfte aus nichtselbständiger Arbeit
        einkuenfte = bruttoarbeitslohn - werbungskosten_effektiv

        return {
            "zeile_4": "Einkünfte aus nichtselbständiger Arbeit",
            "zeile_6_bruttoarbeitslohn": str(bruttoarbeitslohn),
            "zeile_31_werbungskosten": str(werbungskosten),
            "zeile_32_pauschbetrag": str(arbeitnehmer_pauschbetrag),
            "zeile_33_werbungskosten_effektiv": str(werbungskosten_effektiv),
            "zeile_41_einkuenfte": str(einkuenfte),
            "bruttoarbeitslohn": str(bruttoarbeitslohn),
            "werbungskosten": str(werbungskosten),
            "werbungskosten_effektiv": str(werbungskosten_effektiv),
            "einkuenfte": str(einkuenfte),
        }

    def _calculate_anlage_kap(self, tax_year: TaxYear, constants: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate Anlage KAP (Kapitalerträge).

        For dividends, interest, and other capital income.
        Abgeltungsteuer: 25% + Soli (5.5% of 25% = 1.375%)
        """
        # Kapitalerträge
        kapitalertraege = tax_year.income_capital

        # Sparer-Pauschbetrag (tax-free allowance for capital income)
        sparer_pauschbetrag = Decimal(str(constants.get("sparer_pauschbetrag", 1000)))

        # Einkünfte nach Abzug des Pauschbetrags
        einkuenfte_nach_abzug = max(Decimal("0"), kapitalertraege - sparer_pauschbetrag)

        # Abgeltungsteuer (25%)
        abgeltungsteuer_satz = Decimal("0.25")
        abgeltungsteuer = einkuenfte_nach_abzug * abgeltungsteuer_satz

        # Solidaritätszuschlag (5.5% auf Abgeltungsteuer)
        soli_satz = Decimal("0.055")
        solidaritaetszuschlag = abgeltungsteuer * soli_satz

        # Gesamte Steuer auf Kapitalerträge
        steuer_gesamt = abgeltungsteuer + solidaritaetszuschlag

        return {
            "zeile_4": "Einkünfte aus Kapitalvermögen",
            "zeile_7_kapitalertraege": str(kapitalertraege),
            "zeile_12_sparer_pauschbetrag": str(sparer_pauschbetrag),
            "zeile_15_einkuenfte": str(einkuenfte_nach_abzug),
            "zeile_51_abgeltungsteuer": str(abgeltungsteuer),
            "zeile_52_solidaritaetszuschlag": str(solidaritaetszuschlag),
            "kapitalertraege": str(kapitalertraege),
            "sparer_pauschbetrag": str(sparer_pauschbetrag),
            "einkuenfte_nach_abzug": str(einkuenfte_nach_abzug),
            "abgeltungsteuer": str(abgeltungsteuer),
            "solidaritaetszuschlag": str(solidaritaetszuschlag),
            "steuer_gesamt": str(steuer_gesamt),
        }

    def export(self, tax_year: TaxYear, format: str, output_path: Path) -> Path:
        """
        Export tax data.

        Supported formats:
        - xlsx: Excel file with ELSTER-compatible values
        - csv: CSV export
        """
        if format == "xlsx":
            return self._export_xlsx(tax_year, output_path)
        elif format == "csv":
            return self._export_csv(tax_year, output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_xlsx(self, tax_year: TaxYear, output_path: Path) -> Path:
        """Export to XLSX format."""
        import pandas as pd

        result = self.calculate(tax_year)

        # Determine output file path
        if output_path.is_dir():
            file_path = output_path / f"ELSTER_Werte_{tax_year.year}.xlsx"
        else:
            file_path = output_path

        # Create Excel writer
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Summary sheet
            summary_data = {
                "Beschreibung": [
                    "Steuerjahr",
                    "Summe Einkünfte",
                    "Sonderausgaben",
                    "Zu versteuerndes Einkommen",
                ],
                "Wert": [
                    tax_year.year,
                    str(result.income_total),
                    str(result.deductibles_total),
                    str(result.taxable_income),
                ],
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Zusammenfassung", index=False)

            # Form-specific sheets
            for form_name, form_data in result.forms.items():
                form_df = pd.DataFrame([
                    {"Zeile": k, "Wert": v}
                    for k, v in form_data.items()
                ])
                form_df.to_excel(writer, sheet_name=form_name, index=False)

            # Transactions sheet
            txn_data = []
            for txn in tax_year.transactions:
                txn_data.append({
                    "Datum": txn.date.isoformat(),
                    "Betrag": str(txn.amount),
                    "Beschreibung": txn.description,
                    "Kategorie": txn.category.value,
                    "Unterkategorie": txn.subcategory or "",
                })
            pd.DataFrame(txn_data).to_excel(writer, sheet_name="Buchungen", index=False)

        return file_path

    def _export_csv(self, tax_year: TaxYear, output_path: Path) -> Path:
        """Export transactions to CSV."""
        import csv

        if output_path.is_dir():
            file_path = output_path / f"buchungen_{tax_year.year}.csv"
        else:
            file_path = output_path

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Datum", "Betrag", "Beschreibung", "Kategorie", "Unterkategorie"])

            for txn in tax_year.transactions:
                writer.writerow([
                    txn.date.isoformat(),
                    str(txn.amount),
                    txn.description,
                    txn.category.value,
                    txn.subcategory or "",
                ])

        return file_path
