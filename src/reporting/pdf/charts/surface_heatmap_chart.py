import matplotlib
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import PercentFormatter
from reportlab.platypus import Image

from src.reporting.pdf.charts.figure_image import CHART_STYLE, figure_to_image, new_figure
from src.reporting.volatility.surface_grid import SurfaceGrid

VOLATILITY_COLORS = LinearSegmentedColormap.from_list("volatility", ["#F4F6F8", "#8FD3C9", "#2A9D8F", "#1F3A5F"])


class SurfaceHeatmapChart:
    """Rows are the quoted expiries (evenly spaced, labelled with their maturity) so short expiries stay readable."""

    def draw(self, grid: SurfaceGrid) -> Image:
        with matplotlib.rc_context(CHART_STYLE):
            figure = new_figure(0.5)
            axes = figure.add_subplot()

            rows = np.arange(len(grid.maturities))
            mesh = axes.pcolormesh(grid.moneyness, rows, grid.vols, cmap=VOLATILITY_COLORS, shading="nearest")

            axes.set_yticks(rows, [f"{T:.2f}y" for T in grid.maturities])
            axes.set_xlabel("Moneyness K / S")
            axes.set_ylabel("Expiry")
            axes.axvline(1.0, color="#1D2733", linewidth=0.6, linestyle="--")

            colorbar = figure.colorbar(mesh, ax=axes, pad=0.02)
            colorbar.ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
            colorbar.outline.set_visible(False)

            return figure_to_image(figure)
