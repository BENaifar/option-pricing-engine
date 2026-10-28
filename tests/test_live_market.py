"""
Live integration tests: model prices vs real market quotes.

Hits Yahoo Finance, so skipped by default. Run with:
    pytest -m live -s
    LIVE_TICKER=MSFT pytest -m live -s

Needs open-market bid/ask quotes: outside trading hours Yahoo often returns bid = ask = 0
and the tests skip.
"""
import os

import numpy as np
import pytest

from src.instruments.option_types import OptionType
from src.pipeline.pricing_pipeline import PricingPipeline
from src.reporting.market_comparison.live_quote_fetcher import LiveQuoteFetcher
from src.reporting.market_comparison.quote_comparison import QuoteComparison
from src.reporting.market_comparison.quote_repricer import QuoteRepricer

pytestmark = pytest.mark.live

TICKER = os.environ.get("LIVE_TICKER", "AAPL")

# share of quotes the model must price inside [bid - tick, ask + tick]
MIN_HIT_RATE_CALIBRATION = 0.90
MIN_HIT_RATE_OUT_OF_SAMPLE = 0.70


@pytest.fixture(scope="module")
def live_pipeline():
    return PricingPipeline()


@pytest.fixture(scope="module")
def live_snapshot(live_pipeline):
    try:
        return live_pipeline.get_snapshot(TICKER)
    except Exception as error:
        pytest.skip(f"Could not build a live snapshot for {TICKER}: {error}")


@pytest.fixture(scope="module")
def live_quotes(live_pipeline, live_snapshot):
    quotes = LiveQuoteFetcher(live_pipeline.provider).fetch(TICKER, live_snapshot)

    if len(quotes) < 10:
        pytest.skip(f"Only {len(quotes)} liquid quotes for {TICKER} (market closed?)")

    return quotes


@pytest.fixture(scope="module")
def live_comparisons(live_snapshot, live_quotes) -> list[QuoteComparison]:
    return QuoteRepricer().reprice_all(live_snapshot, live_quotes)


def _misses(comparisons: list[QuoteComparison]) -> list[str]:
    return [
        f"{c.quote.option_type.value} K={c.quote.K} T={c.quote.T:.3f}: "
        f"model={c.model_price:.3f} bid={c.quote.bid:.2f} ask={c.quote.ask:.2f} "
        f"error={c.relative_error:+.2%} of mid"
        for c in comparisons if not c.inside_spread
    ]


def _hit_rate(name: str, comparisons: list[QuoteComparison]) -> tuple[float, list[str]]:
    hit_rate = sum(c.inside_spread for c in comparisons) / len(comparisons)
    misses = _misses(comparisons)

    print(f"\n[{name}] {TICKER}: {len(comparisons)} quotes, {hit_rate:.1%} inside bid/ask")
    for miss in misses[:10]:
        print("  miss:", miss)

    return hit_rate, misses


def test_spot_consistent_with_put_call_parity(live_snapshot, live_quotes):
    """
    The option market implies its own spot: S = (C - P + K e^{-rT}) e^{qT}.
    If the snapshot spot is out of sync with the option quotes (different feeds / timestamps),
    every ITM price is off in the same direction, whatever the volatility.
    """
    calls = {(q.K, q.T): q for q in live_quotes if q.option_type == OptionType.CALL}
    puts = {(q.K, q.T): q for q in live_quotes if q.option_type == OptionType.PUT}
    pairs = [(calls[key], puts[key]) for key in calls.keys() & puts.keys()]
    if len(pairs) < 3:
        pytest.skip("Not enough call/put pairs")

    implied_spots = []
    for call, put in pairs:
        r, q = live_snapshot.rate.r(call.T), live_snapshot.dividend_yield.q(call.T)
        implied_spots.append((call.mid - put.mid + call.K * np.exp(-r * call.T)) * np.exp(q * call.T))

    implied_spot = float(np.median(implied_spots))
    print(f"\n[parity] {TICKER}: snapshot spot={live_snapshot.spot:.2f}, option-implied spot={implied_spot:.2f} ({len(pairs)} pairs)")

    assert implied_spot == pytest.approx(live_snapshot.spot, rel=1e-3)


def test_calibration_round_trip(live_comparisons):
    """OTM quotes are what the surface was built from: repricing them must land inside the spread."""
    hit_rate, misses = _hit_rate("calibration", [c for c in live_comparisons if c.in_sample])

    assert hit_rate >= MIN_HIT_RATE_CALIBRATION, "\n".join(misses[:20])


def test_out_of_sample_itm_quotes(live_comparisons):
    """
    ITM quotes never enter the surface (filtered out), so this is a genuine out-of-sample check:
    vols from OTM options must price ITM options consistently with the market.
    Listed equity options are American: ITM puts are priced on the binomial tree.
    """
    comparisons = [c for c in live_comparisons if not c.in_sample]
    if len(comparisons) < 5:
        pytest.skip("Not enough liquid ITM quotes")

    hit_rate, misses = _hit_rate("out-of-sample", comparisons)

    assert hit_rate >= MIN_HIT_RATE_OUT_OF_SAMPLE, "\n".join(misses[:20])


def test_atm_model_price_close_to_market_mid(live_snapshot, live_comparisons):
    """Coarse sanity check on the whole pipeline: near-the-money prices within 5% of mid."""
    comparisons = [c for c in live_comparisons if abs(c.quote.K / live_snapshot.spot - 1) < 0.03]
    if not comparisons:
        pytest.skip("No near-the-money quotes")

    for c in comparisons:
        assert c.model_price == pytest.approx(c.quote.mid, rel=0.05), c.quote
