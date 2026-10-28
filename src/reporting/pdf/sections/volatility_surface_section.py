from dataclasses import dataclass, field

from reportlab.platypus import Flowable, KeepTogether

from src.reporting.pdf.charts.smile_chart import OptionMarker, SmileChart
from src.reporting.pdf.charts.surface_heatmap_chart import SurfaceHeatmapChart
from src.reporting.pdf.components import heading, note, subheading, text
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.report_data import ReportData
from src.reporting.volatility.volatility_view_builder import VolatilityViewBuilder

INTRODUCTION = (
    "The implied volatility surface every option is priced from. Each expiry has its own smile, a natural cubic "
    "spline through the implied volatilities of liquid out-of-the-money quotes; between expiries the surface is "
    "linear in total variance."
)
SMILE_NOTE = (
    "Dots are the calibration quotes, lines the fitted smiles, for up to six expiries spread across the surface. "
    "The star is the option priced in this report. Outside the quoted strikes the smile is extended flat."
)
HEATMAP_NOTE = "Every quoted expiry; the dashed line is at the money. Darker means higher volatility."


@dataclass
class VolatilitySurfaceSection(ReportSection):
    views: VolatilityViewBuilder = field(default_factory=VolatilityViewBuilder)
    smile_chart: SmileChart = field(default_factory=SmileChart)
    heatmap_chart: SurfaceHeatmapChart = field(default_factory=SurfaceHeatmapChart)

    def build(self, data: ReportData) -> list[Flowable]:
        intro = [heading("Volatility surface"), text(INTRODUCTION)]
        smiles, grid = self.views.smiles(data.snapshot), self.views.surface(data.snapshot)

        if not smiles or grid is None:
            return intro + [text("<b>Not available:</b> the snapshot has no fitted volatility surface.")]

        return intro + [
            KeepTogether([subheading("Smiles"), self.smile_chart.draw(smiles, self._marker(data)), note(SMILE_NOTE)]),
            KeepTogether([subheading("Surface"), self.heatmap_chart.draw(grid), note(HEATMAP_NOTE)]),
        ]

    @staticmethod
    def _marker(data: ReportData) -> OptionMarker:
        pricing = data.pricing
        return OptionMarker(pricing.strike / pricing.spot, pricing.volatility, pricing.maturity)
