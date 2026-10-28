import sys
from datetime import datetime
from src.market_data.providers.yahoo_market_data_provider import YahooMarketDataProvider
from src.market_data.services.market_data_service import MarketDataService
from src.reporting.market_comparison.live_quote_fetcher import LiveQuoteFetcher
from src.reporting.market_comparison.quote_repricer import QuoteRepricer
from src.reporting.market_comparison.comparison_summary import ComparisonSummary
ticker = sys.argv[1]
provider = YahooMarketDataProvider()
now = datetime.now()
for use_parity in (False, True):
    snap = MarketDataService(provider=provider, ticker=ticker, valuation_at=now, use_parity=use_parity).get_market_data_snapshot()
    quotes = LiveQuoteFetcher(provider).fetch(ticker, snap)
    comps = QuoteRepricer().reprice_all(snap, quotes)
    for s in (ComparisonSummary.of("in", [c for c in comps if c.in_sample]), ComparisonSummary.of("oos", [c for c in comps if not c.in_sample])):
        print(f"parity={use_parity} spot={snap.spot:.4f} {s.label} n={s.count} hit={s.hit_rate:.3f} mae={s.mean_absolute_error:.4f} medrel={s.median_absolute_relative_error:.5f}")
