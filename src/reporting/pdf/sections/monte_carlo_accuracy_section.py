from reportlab.platypus import Flowable

from src.pricers.monte_carlo import VarianceReductionTechnique
from src.reporting.monte_carlo_accuracy.accuracy_result import MonteCarloAccuracyResult
from src.reporting.monte_carlo_accuracy.accuracy_run import AccuracyRun
from src.reporting.pdf.components import cell, data_table, heading, note, text
from src.reporting.pdf.formatting import MISSING, number, percent
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.pdf.theme import Palette
from src.reporting.report_data import ReportData

TECHNIQUE_LABELS = {
    VarianceReductionTechnique.NONE: "None",
    VarianceReductionTechnique.ANTITHETIC: "Antithetic",
    VarianceReductionTechnique.CONTROL_VARIATE: "Control variate",
}
METHOD = (
    "The same option is priced by Monte Carlo with each variance reduction technique and several path counts, "
    "all with the same seed, and compared with the closed-form price. <b>Antithetic</b> averages each path with its "
    "mirror (Z and -Z), so it simulates twice the paths. <b>Control variate</b> corrects the payoff with the "
    "discounted terminal stock price, whose expectation is known. The variance reduction factor is the variance "
    "without reduction divided by the variance with it, at the same number of paths: the number of plain paths "
    "each path is worth."
)
READING_NOTE = (
    "The standard error falls like 1 / sqrt(paths). Roughly one interval in twenty is expected to miss the "
    "closed form at 95% confidence, so an occasional miss is not a defect."
)


class MonteCarloAccuracySection(ReportSection):
    keep_together = True

    def build(self, data: ReportData) -> list[Flowable]:
        result = data.monte_carlo_accuracy
        intro = [heading("Monte Carlo accuracy"), text(METHOD)]

        if result.unavailable_reason:
            return intro + [text(f"<b>Not available:</b> {result.unavailable_reason}")]

        return intro + [
            self._table(result),
            note(f"Closed-form reference price: {number(result.reference_price)}. {READING_NOTE}"),
        ]

    def _table(self, result: MonteCarloAccuracyResult) -> Flowable:
        level = percent(result.confidence_level, 0)
        rows = [["Technique", "Paths", "Price", "Std. error", f"{level} interval", "Contains", "Var. red.", "Time"]]
        highlights = []

        for row, run in enumerate(result.runs, start=1):
            rows.append(self._row(run, result))
            if not run.contains(result.reference_price):
                highlights.append(("TEXTCOLOR", (5, row), (5, row), Palette.BAD))

        return data_table(rows, [0.17, 0.1, 0.11, 0.11, 0.21, 0.1, 0.1, 0.1], highlights=highlights)

    @staticmethod
    def _row(run: AccuracyRun, result: MonteCarloAccuracyResult) -> list:
        low, high = run.statistics.confidence_interval
        factor = result.variance_reduction_factor(run)

        return [
            cell(TECHNIQUE_LABELS[run.technique], bold=True),
            f"{run.paths:,}",
            number(run.statistics.price),
            number(run.statistics.standard_error),
            f"[{number(low, 3)}, {number(high, 3)}]",
            "yes" if run.contains(result.reference_price) else "no",
            f"{factor:.1f}x" if factor is not None else MISSING,
            f"{run.runtime_seconds * 1000:,.0f} ms",
        ]
