from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from src.reporting.pdf.theme import Page, Palette


class PageTemplateCanvas(canvas.Canvas):
    """Header band, running title and 'Page X of Y' footer; pages are buffered until the total is known."""

    def __init__(self, *args, title: str = "", footer: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._pages = []
        self._title = title
        self._footer = footer

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for page in self._pages:
            self.__dict__.update(page)
            self._draw_header()
            self._draw_footer(len(self._pages))
            super().showPage()
        super().save()

    def _draw_header(self):
        self.saveState()
        self.setFillColor(Palette.NAVY)
        self.rect(0, Page.HEIGHT - 6 * mm, Page.WIDTH, 6 * mm, stroke=0, fill=1)
        self.setFillColor(Palette.TEAL)
        self.rect(0, Page.HEIGHT - 7 * mm, Page.WIDTH, 1 * mm, stroke=0, fill=1)

        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(Palette.NAVY)
            self.drawString(Page.MARGIN, Page.HEIGHT - 13 * mm, self._title)
        self.restoreState()

    def _draw_footer(self, total_pages: int):
        self.saveState()
        self.setStrokeColor(Palette.RULE)
        self.setLineWidth(0.5)
        self.line(Page.MARGIN, 13 * mm, Page.WIDTH - Page.MARGIN, 13 * mm)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(Palette.MUTED)
        self.drawString(Page.MARGIN, 9 * mm, self._footer)
        self.drawRightString(Page.WIDTH - Page.MARGIN, 9 * mm, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()
