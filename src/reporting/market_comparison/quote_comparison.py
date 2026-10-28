from dataclasses import dataclass

from src.reporting.market_comparison.market_quote import MarketQuote

SPREAD_TOLERANCE = 0.01


@dataclass(frozen=True)
class QuoteComparison:
    quote: MarketQuote
    model_price: float
    in_sample: bool
    american: bool

    @property
    def error(self) -> float:
        return self.model_price - self.quote.mid

    @property
    def relative_error(self) -> float:
        return self.error / self.quote.mid

    @property
    def inside_spread(self) -> bool:
        return self.quote.bid - SPREAD_TOLERANCE <= self.model_price <= self.quote.ask + SPREAD_TOLERANCE
