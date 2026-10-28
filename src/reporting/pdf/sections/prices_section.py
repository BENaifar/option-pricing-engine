from reportlab.platypus import Flowable

from src.pipeline.pricing_pipeline import PricerName, PricerResult, PricingSettings
from src.reporting.pdf.components import cell, data_table, heading, note
from src.reporting.pdf.formatting import MISSING, PRICER_LABELS, number, percent
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.report_data import ReportData

EUROPEAN_NOTE = "The closed form is exact under Black-Scholes, so differences are the numerical error of the tree and of Monte Carlo."
AMERICAN_NOTE = "American options have no closed form: only the binomial tree handles early exercise."


class PricesSection(ReportSection):
    keep_together = True

    def build(self, data: ReportData) -> list[Flowable]:
        reference = data.closed_form_result
        rows = [["Pricer", "Price", "vs closed form", "Relative", "Settings"]]
        rows += [self._row(result, reference, data.settings) for result in data.pricing.results]

        return [
            heading("Prices"),
            data_table(rows, [0.24, 0.12, 0.13, 0.1, 0.41], highlights=[("ALIGN", (4, 0), (4, -1), "LEFT")]),
            note(EUROPEAN_NOTE if reference else AMERICAN_NOTE),
            *self._monte_carlo_note(data),
        ]

    @staticmethod
    def _monte_carlo_note(data: ReportData) -> list[Flowable]:
        result = data.monte_carlo_result
        if result is None or result.statistics is None:
            return []

        s = result.statistics
        low, high = s.confidence_interval
        return [note(
            f"Monte Carlo: standard error {number(s.standard_error)}, "
            f"{percent(data.settings.mc_confidence_level, 0)} confidence interval [{number(low)}, {number(high)}] "
            f"from {s.observations:,} observations."
        )]

    def _row(self, result: PricerResult, reference: PricerResult | None, settings: PricingSettings) -> list:
        difference = result.price - reference.price if reference else None

        return [
            cell(PRICER_LABELS[result.pricer], bold=True),
            number(result.price),
            number(difference) if reference else MISSING,
            percent(difference / reference.price, 3) if reference else MISSING,
            cell(self._settings(result.pricer, settings)),
        ]

    @staticmethod
    def _settings(pricer: PricerName, settings: PricingSettings) -> str:
        if pricer == PricerName.BINOMIAL_TREE:
            return f"{settings.tree_steps} steps"
        if pricer == PricerName.MONTE_CARLO:
            return (f"{settings.mc_paths:,} paths, {settings.mc_steps} steps, {settings.mc_scheme.value} scheme, "
                    f"variance reduction: {settings.mc_variance_reduction.value}, seed {settings.seed}")
        return "Analytic formula"
