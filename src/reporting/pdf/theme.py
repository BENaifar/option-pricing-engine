from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm


class Palette:
    NAVY = colors.HexColor("#1F3A5F")
    TEAL = colors.HexColor("#2A9D8F")
    INK = colors.HexColor("#1D2733")
    WHITE = colors.white
    MUTED = colors.HexColor("#5B6B7C")
    RULE = colors.HexColor("#D5DCE4")
    ZEBRA = colors.HexColor("#F4F6F8")
    GOOD = colors.HexColor("#2E7D32")
    BAD = colors.HexColor("#C62828")
    BAD_BACKGROUND = colors.HexColor("#FDECEA")
    WARNING = colors.HexColor("#B26A00")
    WARNING_BACKGROUND = colors.HexColor("#FFF4E0")


class Page:
    WIDTH, HEIGHT = A4
    MARGIN = 18 * mm
    CONTENT_WIDTH = WIDTH - 2 * MARGIN


def _style(name: str, size: float, leading: float, color=Palette.INK, font: str = "Helvetica", **kwargs) -> ParagraphStyle:
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading, textColor=color, **kwargs)


STYLES = {
    "title": _style("title", 24, 28, Palette.NAVY, "Helvetica-Bold", spaceAfter=4),
    "subtitle": _style("subtitle", 11.5, 15, Palette.MUTED, spaceAfter=10),
    "heading": _style("heading", 15, 19, Palette.NAVY, "Helvetica-Bold", spaceBefore=14, spaceAfter=6),
    "subheading": _style("subheading", 11.5, 15, font="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
    "body": _style("body", 9.5, 13.5, spaceAfter=6),
    "note": _style("note", 8.5, 11.5, Palette.MUTED, spaceAfter=6),
    "cell": _style("cell", 8, 10.5),
    "cell_bold": _style("cell_bold", 8, 10.5, font="Helvetica-Bold"),
    "kpi_value": _style("kpi_value", 15, 18, Palette.NAVY, "Helvetica-Bold", alignment=TA_CENTER),
    "kpi_label": _style("kpi_label", 7.5, 9.5, Palette.MUTED, alignment=TA_CENTER),
    "bullet": _style("bullet", 9.5, 13.5, leftIndent=12, bulletIndent=2, spaceAfter=3),
}
