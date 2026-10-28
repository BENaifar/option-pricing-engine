from dataclasses import dataclass, field

from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.reporting.market_comparison.live_quote_fetcher import LiveQuoteFetcher
from src.reporting.market_comparison.market_comparison_result import MarketComparisonResult
from src.reporting.market_comparison.quote_repricer import QuoteRepricer


@dataclass
class MarketComparator:
    fetcher: LiveQuoteFetcher
    repricer: QuoteRepricer = field(default_factory=QuoteRepricer)

    def compare(self, ticker: str, snapshot: MarketDataSnapshot) -> MarketComparisonResult:
        try:
            quotes = self.fetcher.fetch(ticker, snapshot)
        except Exception as error:
            return MarketComparisonResult(unavailable_reason=f"Market quotes could not be fetched: {error}")

        if not quotes:
            return MarketComparisonResult(unavailable_reason="No liquid bid/ask quotes (market closed or illiquid ticker).")

        return MarketComparisonResult(self.repricer.reprice_all(snapshot, quotes))
