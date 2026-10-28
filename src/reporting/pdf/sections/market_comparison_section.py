from reportlab.platypus import Flowable

from src.reporting.market_comparison.comparison_summary import ComparisonSummary
from src.reporting.market_comparison.quote_comparison import QuoteComparison
from src.reporting.pdf.components import cell, data_table, heading, subheading, text
from src.reporting.pdf.formatting import number, percent, signed, signed_percent
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.pdf.theme import Palette
from src.reporting.report_data import ReportData

METHOD = (
    "Every liquid listed option is repriced from the same snapshot and compared with its live bid and ask. "
    "Liquid means a real two-sided quote, a bid/ask spread under 10% of mid, strikes between 85% and 115% of "
    "spot and maturities from 30 days to 1 year. A price counts as a hit when it lies inside [bid - 0.01, ask + 0.01]."
)
SAMPLES = (
    "<b>In-sample</b> quotes are out-of-the-money: they are the quotes the volatility surface is built from, so "
    "this checks the calibration. <b>Out-of-sample</b> quotes are in-the-money: they never enter the surface, so "
    "this is the real test of the model and of the spot and carry calibration. Listed equity options are American, "
    "so in-the-money puts are priced with early exercise on the binomial tree."
)
QUOTE_HEADER = ["Type", "Strike", "T (y)", "Sample", "Bid", "Ask", "Mid", "Model", "Error", "Rel.", "Hit"]
QUOTE_COLUMNS = [0.07, 0.1, 0.08, 0.1, 0.08, 0.08, 0.09, 0.09, 0.09, 0.12, 0.1]


class MarketComparisonSection(ReportSection):
    starts_on_new_page = True

    def build(self, data: ReportData) -> list[Flowable]:
        result = data.market_comparison
        intro = [heading("Model vs market"), text(METHOD), text(SAMPLES)]

        if result.unavailable_reason:
            return intro + [text(f"<b>Not available:</b> {result.unavailable_reason}")]

        return intro + [
            subheading("Summary"),
            self._summary_table(result.summaries()),
            subheading("All quotes"),
            self._quotes_table(result.comparisons),
        ]

    @staticmethod
    def _summary_table(summaries: list[ComparisonSummary]) -> Flowable:
        rows = [["Group", "Quotes", "Inside bid/ask", "Mean abs. error", "Median abs. rel. error"]]
        rows += [
            [cell(s.label, bold=True), str(s.count), percent(s.hit_rate, 1), number(s.mean_absolute_error, 3), percent(s.median_absolute_relative_error)]
            for s in summaries
        ]
        return data_table(rows, [0.34, 0.12, 0.16, 0.18, 0.2])

    def _quotes_table(self, comparisons: list[QuoteComparison]) -> Flowable:
        rows = [QUOTE_HEADER] + [self._quote_row(c) for c in comparisons]
        highlights = [("ALIGN", (3, 0), (3, -1), "CENTER")]
        for row, comparison in enumerate(comparisons, start=1):
            highlights += self._hit_highlight(row, comparison.inside_spread)

        return data_table(rows, QUOTE_COLUMNS, highlights=highlights)

    @staticmethod
    def _quote_row(c: QuoteComparison) -> list:
        sample = "in" if c.in_sample else ("out, Am." if c.american else "out")
        q = c.quote
        return [
            q.option_type.value, number(q.K, 2), number(q.T, 3), sample, number(q.bid, 2), number(q.ask, 2),
            number(q.mid, 3), number(c.model_price, 3), signed(c.error), signed_percent(c.relative_error),
            "yes" if c.inside_spread else "no",
        ]

    @staticmethod
    def _hit_highlight(row: int, hit: bool) -> list[tuple]:
        highlights = [
            ("TEXTCOLOR", (-1, row), (-1, row), Palette.GOOD if hit else Palette.BAD),
            ("FONT", (-1, row), (-1, row), "Helvetica-Bold", 8),
        ]
        if not hit:
            highlights.append(("BACKGROUND", (-3, row), (-1, row), Palette.BAD_BACKGROUND))
        return highlights
