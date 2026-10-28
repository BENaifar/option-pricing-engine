from dataclasses import dataclass, field
from functools import partial
from io import BytesIO
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.platypus import Flowable, KeepTogether, PageBreak, SimpleDocTemplate

from src.reporting.pdf.page_template import PageTemplateCanvas
from src.reporting.pdf.sections.automated_tests_section import AutomatedTestsSection
from src.reporting.pdf.sections.cover_section import CoverSection
from src.reporting.pdf.sections.engine_overview_section import EngineOverviewSection
from src.reporting.pdf.sections.greeks_section import GreeksSection
from src.reporting.pdf.sections.limitations_section import LimitationsSection
from src.reporting.pdf.sections.market_comparison_section import MarketComparisonSection
from src.reporting.pdf.sections.market_inputs_section import MarketInputsSection
from src.reporting.pdf.sections.monte_carlo_accuracy_section import MonteCarloAccuracySection
from src.reporting.pdf.sections.prices_section import PricesSection
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.pdf.sections.volatility_surface_section import VolatilitySurfaceSection
from src.reporting.pdf.theme import Page
from src.reporting.report_data import ReportData


def default_sections() -> list[ReportSection]:
    return [
        CoverSection(),
        EngineOverviewSection(),
        MarketInputsSection(),
        VolatilitySurfaceSection(),
        PricesSection(),
        GreeksSection(),
        MonteCarloAccuracySection(),
        MarketComparisonSection(),
        AutomatedTestsSection(),
        LimitationsSection(),
    ]


@dataclass
class PdfReportRenderer:
    sections: list[ReportSection] = field(default_factory=default_sections)

    def render(self, data: ReportData, destination: str | Path | BytesIO):
        document = SimpleDocTemplate(
            str(destination) if isinstance(destination, Path) else destination,
            pagesize=(Page.WIDTH, Page.HEIGHT),
            leftMargin=Page.MARGIN, rightMargin=Page.MARGIN,
            topMargin=Page.MARGIN + 2 * mm, bottomMargin=Page.MARGIN,
            title=f"Option Pricing Report - {data.pricing.ticker}",
            author="Option Pricing Engine",
        )
        canvas = partial(PageTemplateCanvas, title=self._running_title(data), footer=self._footer(data))
        document.build(self._story(data), canvasmaker=canvas)

    def render_bytes(self, data: ReportData) -> bytes:
        buffer = BytesIO()
        self.render(data, buffer)
        return buffer.getvalue()

    def _story(self, data: ReportData) -> list[Flowable]:
        story = []
        for section in self.sections:
            flowables = section.build(data)
            if section.starts_on_new_page and story:
                story.append(PageBreak())
            story += [KeepTogether(flowables)] if section.keep_together else flowables
        return story

    @staticmethod
    def _running_title(data: ReportData) -> str:
        p = data.pricing
        return f"Option Pricing Report  |  {p.ticker}  {p.style.value} {p.option_type.value}  K={p.strike:g}  T={p.maturity:.3f}y"

    @staticmethod
    def _footer(data: ReportData) -> str:
        return f"Generated {data.generated_at:%Y-%m-%d %H:%M}  |  {data.snapshot.source}  |  For information only, not investment advice"
