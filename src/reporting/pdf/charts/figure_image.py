from io import BytesIO

from matplotlib.figure import Figure
from reportlab.platypus import Image

from src.reporting.pdf.theme import Page

CHART_STYLE = {
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.edgecolor": "#D5DCE4",
    "axes.labelcolor": "#1D2733",
    "axes.titlesize": 9,
    "xtick.color": "#5B6B7C",
    "ytick.color": "#5B6B7C",
    "grid.color": "#E6EBF0",
}


def new_figure(height_ratio: float = 0.5) -> Figure:
    """Matplotlib figure sized to the page content width (object API: no pyplot global state)."""
    width_inches = Page.CONTENT_WIDTH / 72
    return Figure(figsize=(width_inches, width_inches * height_ratio), dpi=200)


def figure_to_image(figure: Figure) -> Image:
    buffer = BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)

    image = Image(buffer)
    scale = Page.CONTENT_WIDTH / image.imageWidth
    image.drawWidth, image.drawHeight = Page.CONTENT_WIDTH, image.imageHeight * scale
    return image
