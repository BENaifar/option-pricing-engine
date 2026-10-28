from reportlab.platypus import Flowable

from src.reporting.pdf.components import heading, key_value_table
from src.reporting.pdf.formatting import number, percent
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.report_data import ReportData


class MarketInputsSection(ReportSection):
    keep_together = True

    def build(self, data: ReportData) -> list[Flowable]:
        pricing, snapshot = data.pricing, data.snapshot

        return [
            heading("Market inputs"),
            key_value_table([
                ("Ticker", pricing.ticker),
                ("Spot used", self._spot(data)),
                ("Risk-free rate r(T)", f"{percent(pricing.rate, 4)} (Treasury zero rate interpolated at T)"),
                ("Carry / dividend yield q(T)", f"{percent(pricing.dividend_yield, 4)} ({snapshot.dividend_source})"),
                ("Implied volatility sigma(K, T)", f"{percent(pricing.volatility, 4)} (read from the surface at the option's strike and maturity)"),
                ("Surface expiries", f"{len(getattr(snapshot.sigma, 'times', []))} smiles"),
                ("Data source / time", f"{snapshot.source}, {snapshot.timestamp[:19]}"),
            ]),
        ]

    @staticmethod
    def _spot(data: ReportData) -> str:
        pricing = data.pricing
        spot = f"{number(pricing.spot)} ({pricing.spot_source})"

        if pricing.quoted_spot is None or pricing.spot == pricing.quoted_spot:
            return spot

        gap = pricing.spot / pricing.quoted_spot - 1
        return f"{spot}; quoted feed {number(pricing.quoted_spot)}, gap {percent(gap, 3)}"
