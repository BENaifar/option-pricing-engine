from dataclasses import dataclass

import matplotlib
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import PercentFormatter
from reportlab.platypus import Image

from src.reporting.pdf.charts.figure_image import CHART_STYLE, figure_to_image, new_figure
from src.reporting.volatility.smile_view import SmileView

MATURITY_COLORS = LinearSegmentedColormap.from_list("maturity", ["#8FD3C9", "#2A9D8F", "#1F3A5F"])


@dataclass(frozen=True)
class OptionMarker:
    moneyness: float
    volatility: float
    maturity: float


class SmileChart:

    def draw(self, smiles: list[SmileView], marker: OptionMarker | None = None) -> Image:
        with matplotlib.rc_context(CHART_STYLE):
            figure = new_figure(0.48)
            axes = figure.add_subplot()

            for i, smile in enumerate(smiles):
                color = MATURITY_COLORS(i / max(len(smiles) - 1, 1))
                axes.plot(smile.fitted_moneyness, smile.fitted_vols, color=color, linewidth=1.4, label=f"T = {smile.maturity:.2f}y")
                axes.scatter(smile.quoted_moneyness, smile.quoted_vols, color=color, s=9, zorder=3)

            if marker:
                axes.scatter([marker.moneyness], [marker.volatility], marker="*", s=140, color="#C62828", zorder=4,
                             label=f"Priced option (T = {marker.maturity:.2f}y)")

            axes.set_xlabel("Moneyness K / S")
            axes.set_ylabel("Implied volatility")
            axes.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
            axes.grid(True, linewidth=0.5)
            axes.legend(frameon=False, ncol=2, fontsize=7)

            return figure_to_image(figure)
