from dataclasses import dataclass

from src.reporting.market_comparison.market_quote import MarketQuote


@dataclass(frozen=True)
class LiquidityFilter:
    min_maturity: float = 30 / 365
    max_maturity: float = 1.0
    min_moneyness: float = 0.85
    max_moneyness: float = 1.15
    max_relative_spread: float = 0.10

    def accepts_maturity(self, T: float) -> bool:
        return self.min_maturity <= T <= self.max_maturity

    def accepts(self, quote: MarketQuote, spot: float) -> bool:
        return (
            self.min_moneyness <= quote.K / spot <= self.max_moneyness
            and quote.relative_spread <= self.max_relative_spread
        )
