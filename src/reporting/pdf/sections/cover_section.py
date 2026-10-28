from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Spacer

from src.reporting.market_comparison.comparison_summary import ComparisonSummary
from src.reporting.pdf.components import kpi_strip, text, warning_box
from src.reporting.pdf.formatting import MISSING, PRICER_LABELS, number, percent
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.report_data import ReportData
from src.reporting.testing.case_result import CaseOutcome

INTRODUCTION = (
    "This report explains what the engine does, the inputs it used, the prices and Greeks it produced, "
    "how those prices compare with live market quotes, how the code is tested, and the known limitations "
    "to keep in mind when using the numbers."
)


class CoverSection(ReportSection):

    def build(self, data: ReportData) -> list[Flowable]:
        pricing, snapshot = data.pricing, data.snapshot
        option = (
            f"{pricing.style.value.capitalize()} {pricing.option_type.value}, "
            f"strike {pricing.strike:,.2f}, maturity {pricing.maturity:.4f} years"
        )

        return [
            Spacer(1, 6 * mm),
            text(f"Option Pricing Report &middot; {pricing.ticker}", "title"),
            text(option, "subtitle"),
            kpi_strip(self._kpis(data)),
            Spacer(1, 4 * mm),
            *self._warnings(data),
            text(f"Generated {data.generated_at:%Y-%m-%d %H:%M} from {snapshot.source} market data "
                 f"(snapshot {snapshot.timestamp[:19]}). {INTRODUCTION}"),
        ]

    @staticmethod
    def _warnings(data: ReportData) -> list[Flowable]:
        if not data.warnings:
            return []
        return [warning_box(data.warnings), Spacer(1, 4 * mm)]

    @staticmethod
    def _kpis(data: ReportData) -> list[tuple[str, str]]:
        headline = data.closed_form_result or data.pricing.results[0]
        out_of_sample = ComparisonSummary.of("", data.market_comparison.out_of_sample)
        tests = data.tests

        return [
            (number(data.pricing.spot, 2), f"Spot ({data.pricing.spot_source})"),
            (number(headline.price), PRICER_LABELS[headline.pricer]),
            (percent(data.pricing.volatility), "Implied volatility"),
            (percent(out_of_sample.hit_rate, 0), "ITM quotes inside bid/ask"),
            (f"{tests.count(CaseOutcome.PASSED)}/{tests.total}" if tests and not tests.error else MISSING, "Tests passed"),
        ]
