from reportlab.platypus import Flowable, Paragraph, Table, TableStyle

from src.reporting.pdf.theme import STYLES, Page, Palette
from src.reporting.report_warnings.report_warning import ReportWarning

NO_NUMERIC_COLUMNS = 99


def text(content: str, style: str = "body") -> Paragraph:
    return Paragraph(content, STYLES[style])


def heading(content: str) -> Paragraph:
    return text(content, "heading")


def subheading(content: str) -> Paragraph:
    return text(content, "subheading")


def note(content: str) -> Paragraph:
    return text(content, "note")


def cell(content: str, bold: bool = False) -> Paragraph:
    return text(content, "cell_bold" if bold else "cell")


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph(item, STYLES["bullet"], bulletText="•") for item in items]


def data_table(
    rows: list[list],
    column_fractions: list[float],
    numeric_from: int = 1,
    header: bool = True,
    highlights: list[tuple] | None = None,
) -> Table:
    """Navy header, zebra rows, numbers right-aligned from column `numeric_from` onwards."""
    table = Table(rows, colWidths=[Page.CONTENT_WIDTH * f for f in column_fractions], repeatRows=int(header))
    table.setStyle(TableStyle(_base_style(numeric_from) + _header_style(header) + _zebra_style(len(rows), header) + (highlights or [])))
    return table


def key_value_table(pairs: list[tuple[str, str]], key_fraction: float = 0.42) -> Table:
    rows = [[cell(key, bold=True), cell(value)] for key, value in pairs]
    return data_table(rows, [key_fraction, 1 - key_fraction], numeric_from=NO_NUMERIC_COLUMNS, header=False)


def kpi_strip(kpis: list[tuple[str, str]]) -> Flowable:
    values = [text(value, "kpi_value") for value, _ in kpis]
    labels = [text(label, "kpi_label") for _, label in kpis]

    table = Table([values, labels], colWidths=[Page.CONTENT_WIDTH / len(kpis)] * len(kpis))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), Palette.ZEBRA),
        ("LINEABOVE", (0, 0), (-1, 0), 2, Palette.TEAL),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 9),
        ("LINEAFTER", (0, 0), (-2, -1), 0.5, Palette.RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def warning_box(warnings: list[ReportWarning]) -> Flowable:
    rows = [[text(f"<font color='#B26A00'><b>{w.title}</b></font><br/>{w.message}", "cell")] for w in warnings]

    table = Table(rows, colWidths=[Page.CONTENT_WIDTH])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), Palette.WARNING_BACKGROUND),
        ("LINEBEFORE", (0, 0), (0, -1), 3, Palette.WARNING),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, Palette.WARNING),
    ]))
    return table


def _base_style(numeric_from: int) -> list[tuple]:
    return [
        ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), Palette.INK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (numeric_from, 0), (-1, -1), "RIGHT"),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, Palette.RULE),
    ]


def _header_style(header: bool) -> list[tuple]:
    if not header:
        return []
    return [
        ("BACKGROUND", (0, 0), (-1, 0), Palette.NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), Palette.WHITE),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
    ]


def _zebra_style(row_count: int, header: bool) -> list[tuple]:
    first = int(header)
    return [("BACKGROUND", (0, row), (-1, row), Palette.ZEBRA) for row in range(first + 1, row_count, 2)]
