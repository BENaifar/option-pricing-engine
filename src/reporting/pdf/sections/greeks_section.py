from reportlab.platypus import Flowable

from src.greeks.greeks import Greeks
from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.reporting.analytic_greeks import GREEK_NAMES, AnalyticGreeks
from src.reporting.pdf.components import NO_NUMERIC_COLUMNS, cell, data_table, heading, note, subheading, text
from src.reporting.pdf.formatting import PRICER_LABELS, number, percent
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.pdf.theme import Palette
from src.reporting.report_data import ReportData

METHOD = (
    "Greeks are computed the same way for every pricer: bump one input, reprice, and take a central finite "
    "difference. Bump sizes come from <font face='Courier'>config.ini</font>. The volatility bump moves sigma of the "
    "process with the spot fixed, so these are <i>sticky-strike</i> Greeks. For Monte Carlo every bumped price "
    "reuses the same random numbers (common random numbers); otherwise the differences would be dominated by "
    "simulation noise."
)
NO_REFERENCE_NOTE = "No analytic reference: closed-form Greeks only exist for European options."
TREE_GAMMA_NOTE = "Binomial gamma oscillates with the step count (odd / even nodes), which is normal for trees."


class GreeksSection(ReportSection):

    def build(self, data: ReportData) -> list[Flowable]:
        return [
            heading("Greeks"),
            text(METHOD),
            self._method_table(data.bumps, data.pricing.spot),
            subheading("Results"),
            self._results_table(data),
            note(self._deviation_note(data)),
        ]

    @staticmethod
    def _method_table(bumps: GreeksBumpsConfig, spot: float) -> Flowable:
        methods = [
            ("Delta", f"spot &plusmn; {percent(bumps.spot_rel, 1)} (h = {number(spot * bumps.spot_rel, 2)})", "(V(S+h) - V(S-h)) / 2h"),
            ("Gamma", "same spot bumps", "(V(S+h) - 2V(S) + V(S-h)) / h&sup2;"),
            ("Vega", f"sigma &plusmn; {bumps.vol_abs * 100:.2f} vol points", "(V(&sigma;+d) - V(&sigma;-d)) / 2d, per 1.00 of vol"),
            ("Rho", f"r &plusmn; {bumps.rate_abs * 1e4:.0f} bp", "(V(r+d) - V(r-d)) / 2d, per 1.00 of rate"),
            ("Theta", f"maturity &plusmn; {bumps.time_days * 365:.0f} day", "-(V(T+d) - V(T-d)) / 2d, per year"),
        ]
        rows = [["Greek", "Bump", "Formula"]] + [[cell(g, bold=True), cell(b), cell(f)] for g, b, f in methods]
        return data_table(rows, [0.12, 0.38, 0.5], numeric_from=NO_NUMERIC_COLUMNS)

    def _results_table(self, data: ReportData) -> Flowable:
        rows = [["Pricer"] + [name.capitalize() for name in GREEK_NAMES]]
        rows += [self._greeks_row(PRICER_LABELS[r.pricer], r.greeks) for r in data.pricing.results]

        highlights = []
        if data.analytic_greeks:
            rows.append(self._greeks_row("Analytic reference", data.analytic_greeks))
            highlights.append(("LINEABOVE", (0, -1), (-1, -1), 1, Palette.TEAL))

        return data_table(rows, [0.25] + [0.15] * len(GREEK_NAMES), highlights=highlights)

    @staticmethod
    def _greeks_row(label: str, greeks: Greeks) -> list:
        return [cell(label, bold=True)] + [number(getattr(greeks, name), 5) for name in GREEK_NAMES]

    @staticmethod
    def _deviation_note(data: ReportData) -> str:
        if data.analytic_greeks is None:
            return NO_REFERENCE_NOTE

        deviations = "; ".join(
            f"{PRICER_LABELS[r.pricer]} {percent(AnalyticGreeks.largest_relative_deviation(r.greeks, data.analytic_greeks))}"
            for r in data.pricing.results
        )
        return f"Largest relative deviation from the analytic Greeks: {deviations}. {TREE_GAMMA_NOTE}"
