import json
import sys
import time

import numpy as np
from matplotlib.figure import Figure

from src.pipeline.pricing_pipeline import PricingPipeline
from src.reporting.market_comparison.live_quote_fetcher import LiveQuoteFetcher
from src.reporting.market_comparison.quote_repricer import QuoteRepricer
from src.reporting.market_comparison.comparison_summary import ComparisonSummary

ticker = sys.argv[1]
plot_path = sys.argv[2] if len(sys.argv) > 2 else None

pipeline = PricingPipeline()
start = time.perf_counter()
snapshot = pipeline.get_snapshot(ticker)
snapshot_seconds = time.perf_counter() - start

quotes = LiveQuoteFetcher(pipeline.provider).fetch(ticker, snapshot)
comparisons = QuoteRepricer().reprice_all(snapshot, quotes)

def summary(label, items):
    s = ComparisonSummary.of(label, items)
    rel = [abs(c.relative_error) for c in items]
    return {
        "label": label, "count": s.count, "hit_rate": s.hit_rate, "mae": s.mean_absolute_error,
        "median_abs_rel": s.median_absolute_relative_error,
        "p90_abs_rel": float(np.percentile(rel, 90)) if rel else None,
        "median_spread_rel": float(np.median([c.quote.relative_spread for c in items])) if items else None,
        "mean_signed_error": float(np.mean([c.error for c in items])) if items else None,
    }

ins = [c for c in comparisons if c.in_sample]
oos = [c for c in comparisons if not c.in_sample]
oos_calls = [c for c in oos if c.quote.option_type.value == "call"]
oos_puts = [c for c in oos if c.quote.option_type.value == "put"]

out = {
    "ticker": ticker,
    "timestamp": snapshot.timestamp,
    "spot": snapshot.spot, "quoted_spot": snapshot.quoted_spot, "spot_source": snapshot.spot_source,
    "dividend_source": snapshot.dividend_source,
    "rates_as_of": str(snapshot.rate.as_of),
    "smiles": len(snapshot.sigma.times),
    "snapshot_seconds": snapshot_seconds,
    "summaries": [summary("in-sample OTM", ins), summary("out-of-sample ITM", oos),
                  summary("ITM calls (European)", oos_calls), summary("ITM puts (American tree)", oos_puts),
                  summary("all", comparisons)],
}
print(json.dumps(out, indent=2))

if plot_path and comparisons:
    figure = Figure(figsize=(9, 4))
    left, right = figure.subplots(1, 2)
    for items, label, marker in ((ins, "in-sample (OTM)", "o"), (oos, "out-of-sample (ITM)", "^")):
        left.scatter([c.quote.mid for c in items], [c.model_price for c in items], s=10, marker=marker, label=label, alpha=0.7)
        right.scatter([c.quote.K / snapshot.spot for c in items], [c.error / (c.quote.ask - c.quote.bid) for c in items],
                      s=10, marker=marker, label=label, alpha=0.7)
    top = max(c.quote.mid for c in comparisons)
    left.plot([0, top], [0, top], color="grey", lw=0.8)
    left.set_xlabel("market mid"); left.set_ylabel("model price"); left.set_title(f"{ticker}: model vs mid")
    left.legend(fontsize=8)
    right.axhline(0.5, color="grey", lw=0.8, ls="--"); right.axhline(-0.5, color="grey", lw=0.8, ls="--")
    right.set_xlabel("K / S"); right.set_ylabel("(model - mid) / spread"); right.set_title("error in spreads (dashed = bid/ask)")
    figure.tight_layout()
    figure.savefig(plot_path, dpi=120)
