from types import SimpleNamespace

from src.greeks.greeks import Greeks
from src.instruments.european_option import EuropeanOption
from src.pipeline.pricing_pipeline import ExerciseStyle, PricingResult
from src.pricers.black_scholes import BlackScholesPricer

GREEK_NAMES = ("delta", "gamma", "theta", "vega", "rho")


class AnalyticGreeks:
    """Closed-form Black-Scholes Greeks, the reference for the bump-and-reprice ones. European options only."""

    def compute(self, pricing: PricingResult) -> Greeks | None:
        if pricing.style != ExerciseStyle.EUROPEAN:
            return None

        option = EuropeanOption(strike=pricing.strike, maturity=pricing.maturity, option_type=pricing.option_type)
        flat_market = SimpleNamespace(
            spot=pricing.spot, rate=pricing.rate, dividend_yield=pricing.dividend_yield, sigma=pricing.volatility
        )
        return BlackScholesPricer().greeks(option, flat_market)

    @staticmethod
    def largest_relative_deviation(greeks: Greeks, reference: Greeks) -> float:
        return max(
            abs(getattr(greeks, name) / getattr(reference, name) - 1)
            for name in GREEK_NAMES
            if getattr(reference, name)
        )
