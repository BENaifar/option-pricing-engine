from reportlab.platypus import Flowable

from src.reporting.pdf.components import NO_NUMERIC_COLUMNS, cell, data_table, heading, text
from src.reporting.pdf.sections.report_section import ReportSection
from src.reporting.report_data import ReportData

PIPELINE_STEPS = [
    ("1. Market data", "market_data", "Fetches spot, Treasury yields (local FRED files), dividends and the full option chain."),
    ("2. Spot and carry", "calibrators/implied_spot", "Backs the spot and a carry curve q(T) out of put-call parity, so the inputs agree with the option quotes."),
    ("3. Implied volatility", "calibrators/implied_volatility", "Newton-Raphson inversion of Black-Scholes on liquid out-of-the-money quotes."),
    ("4. Vol surface", "models/volatility_surface", "Cubic spline smile per expiry in log-moneyness, linear in total variance across expiries."),
    ("5. Snapshot", "market_data_snapshot", "Freezes spot, curves and surface with a timestamp and source: the contract with the pricers."),
    ("6. Model and process", "models, process", "Black-Scholes with r(T), q(T), sigma(K, T) read for the option; geometric Brownian motion."),
    ("7. Pricers", "pricers", "Closed form, CRR binomial tree (European and American), Monte Carlo (exact GBM or Euler)."),
    ("8. Greeks", "greeks", "Bump-and-reprice finite differences, identical for every pricer."),
]

INTRODUCTION = (
    "Every price goes through the same pipeline. The CLI (<font face='Courier'>main.py</font>) and the FastAPI "
    "service (<font face='Courier'>/price</font>, <font face='Courier'>/market-data</font>, "
    "<font face='Courier'>/report</font>) are thin layers over it."
)


class EngineOverviewSection(ReportSection):

    def build(self, data: ReportData) -> list[Flowable]:
        rows = [["Step", "Module", "What it does"]]
        rows += [[cell(step, bold=True), cell(module), cell(description)] for step, module, description in PIPELINE_STEPS]

        return [
            heading("How the engine works"),
            text(INTRODUCTION),
            data_table(rows, [0.2, 0.25, 0.55], numeric_from=NO_NUMERIC_COLUMNS),
        ]
