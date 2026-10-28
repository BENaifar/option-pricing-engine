from reportlab.platypus import Flowable

from src.reporting.pdf.components import bullets, heading, text
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.report_data import ReportData

LIMITATIONS = [
    "<b>Black-Scholes dynamics.</b> Each option gets a single volatility read from the surface. The model has no "
    "smile dynamics, stochastic volatility or jumps, so Greeks are sticky-strike and exotic or path-dependent "
    "products would be mispriced.",
    "<b>American options.</b> Only the binomial tree handles early exercise; the closed form and Monte Carlo are "
    "European only and the pipeline refuses them for American options. Implied volatilities are extracted with "
    "the European formula although listed options are American, which slightly overstates put volatilities.",
    "<b>Rates.</b> Treasury constant-maturity yields from local FRED files, used as continuous zero rates. "
    "The files must be refreshed manually; stale rates are partly absorbed by the implied carry.",
    "<b>Implied carry.</b> Put-call parity absorbs dividend and borrow errors exactly but rate errors only to first "
    "order. With the market closed (no bid/ask), the engine falls back to the quoted spot and the trailing "
    "dividend yield, and prices are less reliable.",
    "<b>Market data.</b> Yahoo Finance quotes are delayed and the equity and option feeds are not synchronised. "
    "Very short-dated, illiquid or far out-of-the-money quotes are excluded from the surface.",
    "<b>Volatility surface.</b> Natural cubic splines through raw implied vols with flat extrapolation in strike and "
    "maturity; no smoothing and no static-arbitrage checks.",
    "<b>Numerical error.</b> Tree prices converge with the step count and Monte Carlo prices carry sampling noise "
    "that falls like 1 / sqrt(paths). Finite-difference Greeks depend on the bump sizes.",
    "<b>Market comparison.</b> Only the liquid region is tested, at a single point in time; a hit means the price is "
    "inside the quoted spread, not that the model is right.",
]


class LimitationsSection(ReportSection):

    def build(self, data: ReportData) -> list[Flowable]:
        return [heading("Limitations"), text("Read the numbers above with these in mind."), *bullets(LIMITATIONS)]
