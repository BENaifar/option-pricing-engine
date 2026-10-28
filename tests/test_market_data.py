from src.core.exceptions import MarketDataUnavailableError, TickerNotFoundError
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from src.market_data.calibrators.implied_spot import ImpliedSpotFromParity
from src.market_data.calibrators.implied_volatility import ImpliedVolatilityBS
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.forward_price_engine import ForwardPricing
from src.market_data.implied_vol_inversion_functs import price_fn_bs
from src.market_data.loaders.dividend_loader import build_dividend_yield
from src.market_data.loaders.rates_loader import build_rate_curve
from src.market_data.loaders.spot_loader import load_spot
from src.market_data.loaders.volatilityLoader import filter_quotes, get_all_option_quotes, get_option_chain_snapshot
from src.market_data.models.option_quote import OptionQuote
from src.market_data.models.rate import Rate
from src.market_data.services.market_data_service import MarketDataService
from tests.fake_market_data_provider import (
    RATE, SPOT, STRIKES, VALUATION_DATE, FakeMarketDataProvider, dividend_yield, true_vol
)


@pytest.fixture
def fake_provider():
    return FakeMarketDataProvider()


@pytest.fixture
def fake_service(fake_provider):
    return MarketDataService(provider=fake_provider, ticker="FAKE", valuation_at=VALUATION_DATE)


@pytest.fixture
def fake_snapshot(fake_service):
    return fake_service.get_market_data_snapshot()


@pytest.fixture
def flat_curves():
    return YieldCurve(RATE), DividendCurve(None, None, 0.01)


# ---------- loaders ----------

def test_load_spot_takes_last_close_on_or_before_valuation_date(fake_provider):
    df = fake_provider.fetch_spot("FAKE")
    assert load_spot(df, VALUATION_DATE) == SPOT


def test_load_spot_on_weekend_uses_previous_close(fake_provider):
    df = fake_provider.fetch_spot("FAKE")
    assert load_spot(df, datetime(2026, 1, 18)) == 250.0  # Sunday -> Friday 16th


def test_load_spot_raises_before_first_date(fake_provider):
    df = fake_provider.fetch_spot("FAKE")
    with pytest.raises(MarketDataUnavailableError):
        load_spot(df, datetime(2025, 1, 1))


def test_build_rate_curve_uses_last_rate_on_or_before_date(fake_provider):
    rates = build_rate_curve(VALUATION_DATE, fake_provider.fetch_rate())

    assert [r.rate for r in rates] == pytest.approx([RATE] * len(rates))
    times = [r.time_to_maturity for r in rates]
    assert times == sorted(times)


def test_build_rate_curve_skips_missing_values():
    index = pd.DatetimeIndex(["2026-01-14", "2026-01-15"])
    dfs = {"DGS1": pd.DataFrame({"DGS1": [0.03, np.nan]}, index=index)}

    assert build_rate_curve("2026-01-15", dfs)[0].rate == pytest.approx(0.03)


def test_build_rate_curve_raises_without_history():
    dfs = {"DGS1": pd.DataFrame({"DGS1": [0.03]}, index=pd.DatetimeIndex(["2026-02-01"]))}
    with pytest.raises(MarketDataUnavailableError):
        build_rate_curve("2026-01-15", dfs)


def test_build_rate_curve_rejects_unknown_tenor():
    dfs = {"DGS7": pd.DataFrame({"DGS7": [0.03]}, index=pd.DatetimeIndex(["2026-01-15"]))}
    with pytest.raises(ValueError):
        build_rate_curve("2026-01-15", dfs)


def test_dividend_yield_uses_trailing_twelve_months(fake_provider):
    q = build_dividend_yield(fake_provider.fetch_dividend("FAKE"), SPOT, VALUATION_DATE)
    assert q == pytest.approx(dividend_yield())


def test_dividend_yield_is_zero_without_dividends():
    assert build_dividend_yield(None, SPOT, VALUATION_DATE) == 0.0
    assert build_dividend_yield(pd.Series(dtype=float), SPOT, VALUATION_DATE) == 0.0


def test_option_chain_snapshot_prefers_mid_and_falls_back_to_last():
    chain = pd.DataFrame([
        {"strike": 100.0, "bid": 4.0, "ask": 6.0, "lastPrice": 9.0, "option_type": "call"},
        {"strike": 105.0, "bid": 0.0, "ask": 0.0, "lastPrice": 2.5, "option_type": "call"},
        {"strike": 110.0, "bid": np.nan, "ask": np.nan, "lastPrice": np.nan, "option_type": "call"},
    ])

    quotes = get_option_chain_snapshot(chain, datetime(2026, 1, 15), datetime(2026, 7, 15))

    assert [q.price for q in quotes] == [5.0, 2.5]
    assert [q.is_mid for q in quotes] == [True, False]
    assert quotes[0].T == pytest.approx(181 / 365)


def test_all_option_quotes_skip_expired_and_same_day_expiries(fake_provider):
    quotes = get_all_option_quotes(fake_provider, "FAKE", VALUATION_DATE)
    assert min(q.T for q in quotes) > 0


def test_filter_quotes_keeps_otm_inside_band_and_not_too_short():
    quotes = [
        OptionQuote(K=90, T=0.5, price=1, type="put"),     # OTM put: kept
        OptionQuote(K=110, T=0.5, price=1, type="call"),   # OTM call: kept
        OptionQuote(K=90, T=0.5, price=1, type="call"),    # ITM call
        OptionQuote(K=110, T=0.5, price=1, type="put"),    # ITM put
        OptionQuote(K=50, T=0.5, price=1, type="put"),     # outside band
        OptionQuote(K=110, T=1 / 365, price=1, type="call"),  # too short
    ]

    kept = filter_quotes(quotes, spot=100.0)

    assert [(q.K, q.type) for q in kept] == [(90, "put"), (110, "call")]


# ---------- curves ----------

def test_yield_curve_interpolates_and_extrapolates_flat():
    curve = YieldCurve([Rate(2.0, 0.04), Rate(0.5, 0.03), Rate(10.0, 0.05)])

    assert curve.r(0.5) == pytest.approx(0.03)
    assert curve.r(2.0) == pytest.approx(0.04)
    assert 0.03 < curve.r(1.0) < 0.04
    assert curve.r(0.01) == pytest.approx(0.03)
    assert curve.r(50.0) == pytest.approx(0.05)
    assert isinstance(curve.r(1.0), float)


def test_flat_curves():
    assert YieldCurve(0.05).r(3.0) == 0.05
    assert DividendCurve(None, None, 0.02).q(3.0) == 0.02


def test_interpolated_dividend_curve():
    curve = DividendCurve(None, [0.5, 1.0, 2.0], [0.01, 0.02, 0.03])
    assert curve.q(1.0) == pytest.approx(0.02)


def test_forward_price_with_flat_curves(flat_curves):
    yield_curve, dividend_curve = flat_curves
    forward = ForwardPricing.forward_price(SPOT, yield_curve, dividend_curve, 2.0)
    assert forward == pytest.approx(SPOT * np.exp((RATE - 0.01) * 2.0))


# ---------- implied volatility ----------

@pytest.mark.parametrize("option_type", ["call", "put"])
@pytest.mark.parametrize("K, T, sigma", [(80, 0.25, 0.35), (100, 1.0, 0.2), (130, 2.0, 0.15)])
def test_implied_volatility_round_trip(flat_curves, option_type, K, T, sigma):
    yield_curve, dividend_curve = flat_curves
    price = price_fn_bs(SPOT, K, RATE, 0.01, sigma, T, option_type)

    iv_quote = ImpliedVolatilityBS().get_vol(OptionQuote(K=K, T=T, price=price, type=option_type), SPOT, yield_curve, dividend_curve)

    assert iv_quote.iv == pytest.approx(sigma, abs=1e-6)


def test_implied_volatility_raises_on_arbitrage_price(flat_curves):
    yield_curve, dividend_curve = flat_curves
    quote = OptionQuote(K=120, T=0.5, price=150.0, type="call")

    with pytest.raises(ValueError):
        ImpliedVolatilityBS().get_vol(quote, SPOT, yield_curve, dividend_curve)


# ---------- service / snapshot / surface ----------

def test_snapshot_contents(fake_snapshot):
    assert fake_snapshot.ticker == "FAKE"
    assert fake_snapshot.spot == pytest.approx(SPOT, rel=1e-9)
    assert fake_snapshot.quoted_spot == SPOT
    assert fake_snapshot.rate.r(1.0) == pytest.approx(RATE)
    assert fake_snapshot.dividend_yield.q(1.0) == pytest.approx(dividend_yield())
    assert fake_snapshot.timestamp == str(VALUATION_DATE)
    assert len(fake_snapshot.sigma.times) == 4  # the same-day expiry is dropped


@pytest.mark.parametrize("K", [75.0, 95.0, 100.0, 105.0, 125.0])
def test_surface_recovers_quoted_vols(fake_snapshot, K):
    for T in fake_snapshot.sigma.times:
        assert fake_snapshot.sigma.get_vol(K, T) == pytest.approx(true_vol(K), abs=1e-5)


@pytest.mark.parametrize("K", [85.0, 100.0, 115.0])
def test_surface_between_maturities(fake_snapshot, K):
    # the synthetic smile does not depend on T, so total variance interpolation must give it back
    times = fake_snapshot.sigma.times
    T = 0.5 * (times[1] + times[2])
    assert fake_snapshot.sigma.get_vol(K, T) == pytest.approx(true_vol(K), abs=1e-4)


def test_surface_extrapolates_flat_in_time(fake_snapshot):
    surface = fake_snapshot.sigma
    assert surface.get_vol(100.0, 1 / 365) == pytest.approx(surface.get_vol(100.0, surface.times[0]))
    assert surface.get_vol(100.0, 10.0) == pytest.approx(surface.get_vol(100.0, surface.times[-1]))


def test_surface_extrapolates_flat_in_strike(fake_snapshot):
    surface = fake_snapshot.sigma
    T = surface.times[1]

    far_low, far_high = surface.get_vol(1.0, T), surface.get_vol(1000.0, T)

    assert far_low == pytest.approx(surface.get_vol(min(STRIKES), T), abs=0.02)
    assert 0 < far_low < 1 and 0 < far_high < 1


def test_garbage_quote_does_not_break_the_surface():
    service = MarketDataService(provider=FakeMarketDataProvider(garbage_quote=True), ticker="FAKE", valuation_at=VALUATION_DATE)
    snapshot = service.get_market_data_snapshot()

    assert all(iv.K != 127.5 for iv in service.implied_volatilities)
    assert snapshot.sigma.get_vol(100.0, 0.5) == pytest.approx(true_vol(100.0), abs=1e-3)


def test_non_dividend_ticker():
    service = MarketDataService(provider=FakeMarketDataProvider(pays_dividends=False), ticker="FAKE", valuation_at=VALUATION_DATE)
    snapshot = service.get_market_data_snapshot()

    assert snapshot.dividend_yield.q(1.0) == pytest.approx(0.0, abs=1e-12)
    assert snapshot.sigma.get_vol(100.0, 0.5) == pytest.approx(true_vol(100.0), abs=1e-3)


def test_unknown_ticker_raises():
    service = MarketDataService(provider=FakeMarketDataProvider(empty_spot=True), ticker="NOPE", valuation_at=VALUATION_DATE)
    with pytest.raises(TickerNotFoundError, match="NOPE"):
        service.get_market_data_snapshot()


def test_default_valuation_time_is_not_frozen_at_import():
    first = MarketDataService(provider=FakeMarketDataProvider(), ticker="FAKE")
    second = MarketDataService(provider=FakeMarketDataProvider(), ticker="FAKE")
    assert second.valuation_at >= first.valuation_at > datetime(2026, 1, 1)


# ---------- spot implied from put-call parity ----------

def _parity_quotes(spot, K_list, T, r, q, sigma=0.25, is_mid=True):
    quotes = []
    for K in K_list:
        for option_type in ("call", "put"):
            price = price_fn_bs(spot, K, r, q, sigma, T, option_type)
            quotes.append(OptionQuote(K=K, T=T, price=price, type=option_type, is_mid=is_mid))
    return quotes


def test_parity_recovers_the_spot_options_were_priced_with(flat_curves):
    yield_curve, dividend_curve = flat_curves
    quotes = _parity_quotes(101.0, [97.0, 100.0, 103.0], 0.08, RATE, 0.01)

    implied = ImpliedSpotFromParity().get_spot(quotes, 100.0, yield_curve, dividend_curve)

    assert implied == pytest.approx(101.0, rel=1e-10)


def test_parity_ignores_last_price_quotes(flat_curves):
    yield_curve, dividend_curve = flat_curves
    quotes = _parity_quotes(101.0, [97.0, 100.0, 103.0], 0.08, RATE, 0.01, is_mid=False)

    assert ImpliedSpotFromParity().get_spot(quotes, 100.0, yield_curve, dividend_curve) is None


def test_parity_ignores_far_strikes_and_long_maturities(flat_curves):
    yield_curve, dividend_curve = flat_curves
    quotes = _parity_quotes(101.0, [70.0, 130.0], 0.08, RATE, 0.01) + _parity_quotes(101.0, [100.0], 0.5, RATE, 0.01)

    assert ImpliedSpotFromParity().implied_spots(quotes, 100.0, yield_curve, dividend_curve) == []


def test_parity_rejects_implausible_gap(flat_curves):
    yield_curve, dividend_curve = flat_curves
    quotes = _parity_quotes(110.0, [105.0, 108.0, 110.0], 0.08, RATE, 0.01)

    assert ImpliedSpotFromParity().get_spot(quotes, 108.0, yield_curve, dividend_curve) is not None
    assert ImpliedSpotFromParity().get_spot(quotes, 100.0, yield_curve, dividend_curve) is None


def test_snapshot_corrects_a_lagging_equity_feed():
    service = MarketDataService(provider=FakeMarketDataProvider(spot_feed_offset=-1.0), ticker="FAKE", valuation_at=VALUATION_DATE)
    snapshot = service.get_market_data_snapshot()

    assert snapshot.quoted_spot == SPOT - 1.0
    assert snapshot.spot == pytest.approx(SPOT, rel=1e-9)
    assert snapshot.spot_source == "put-call parity"
    assert snapshot.dividend_yield.q(1.0) == pytest.approx(dividend_yield())
    for K in (80.0, 100.0, 120.0):
        assert snapshot.sigma.get_vol(K, snapshot.sigma.times[1]) == pytest.approx(true_vol(K), abs=1e-5)


def test_lagging_feed_without_parity_distorts_the_surface():
    """What the parity adjustment fixes: calibrating to the wrong spot biases the vols."""
    service = MarketDataService(provider=FakeMarketDataProvider(spot_feed_offset=-1.0), ticker="FAKE", valuation_at=VALUATION_DATE, use_parity=False)
    snapshot = service.get_market_data_snapshot()

    assert snapshot.spot == SPOT - 1.0
    assert snapshot.spot_source == "quoted"
    assert abs(snapshot.sigma.get_vol(100.0, snapshot.sigma.times[0]) - true_vol(100.0)) > 0.005


def test_closed_market_keeps_the_quoted_spot():
    service = MarketDataService(provider=FakeMarketDataProvider(spot_feed_offset=-1.0, has_bid_ask=False), ticker="FAKE", valuation_at=VALUATION_DATE)
    snapshot = service.get_market_data_snapshot()

    assert snapshot.spot == SPOT - 1.0
    assert snapshot.spot_source == "quoted"
    assert snapshot.dividend_source == "trailing dividends"


# ---------- carry implied from parity forwards ----------

class _CarryMismatchProvider(FakeMarketDataProvider):
    """
    Options priced with a carry the inputs miss. By default a higher q (borrow cost, dividend change),
    which parity absorbs exactly; option_rate_shift mimics a wrong rate curve, absorbed only to first order.
    """

    def __init__(self, q_shift: float = 0.01, option_rate_shift: float = 0.0):
        super().__init__()
        self.option_q = dividend_yield() + q_shift
        self.option_rate = RATE + option_rate_shift

    def fetch_option_chain(self, ticker, date):
        T = (pd.to_datetime(date) - pd.to_datetime(VALUATION_DATE)).days / 365.0
        rows = []
        for option_type in ("call", "put"):
            for K in STRIKES:
                price = price_fn_bs(SPOT, K, self.option_rate, self.option_q, true_vol(K), T, option_type)
                rows.append({"strike": K, "bid": price, "ask": price, "lastPrice": price, "option_type": option_type})
        return pd.DataFrame(rows)


def test_parity_forwards_recover_the_forward(flat_curves):
    yield_curve, dividend_curve = flat_curves
    quotes = _parity_quotes(100.0, [97.0, 100.0, 103.0], 0.5, RATE, 0.01)

    forwards = ImpliedSpotFromParity().implied_forwards(quotes, 100.0, yield_curve)

    assert forwards == {0.5: pytest.approx(100.0 * np.exp((RATE - 0.01) * 0.5), rel=1e-10)}


def test_parity_forwards_skip_short_expiries(flat_curves):
    yield_curve, _ = flat_curves
    quotes = _parity_quotes(100.0, [97.0, 100.0, 103.0], 10 / 365, RATE, 0.01)

    assert ImpliedSpotFromParity().implied_forwards(quotes, 100.0, yield_curve) == {}


@pytest.mark.parametrize("q_shift, option_rate_shift, tolerance", [
    (0.01, 0.0, 1e-8),    # carry error in q: absorbed exactly
    (0.0, 0.01, 5e-4),    # carry error in r: absorbed to first order only
])
def test_implied_carry_matches_the_option_forwards(q_shift, option_rate_shift, tolerance):
    provider = _CarryMismatchProvider(q_shift, option_rate_shift)
    snapshot = MarketDataService(provider=provider, ticker="FAKE", valuation_at=VALUATION_DATE).get_market_data_snapshot()

    assert snapshot.dividend_source == "put-call parity"
    for T in snapshot.sigma.times[1:]:
        model_forward = snapshot.spot * np.exp((snapshot.rate.r(T) - snapshot.dividend_yield.q(T)) * T)
        option_forward = SPOT * np.exp((provider.option_rate - provider.option_q) * T)
        assert model_forward == pytest.approx(option_forward, rel=tolerance)


def test_carry_mismatch_without_parity_misprices():
    """What the carry calibration fixes."""
    provider = _CarryMismatchProvider()
    snapshot = MarketDataService(provider=provider, ticker="FAKE", valuation_at=VALUATION_DATE, use_parity=False).get_market_data_snapshot()

    T = snapshot.sigma.times[-1]
    model_forward = snapshot.spot * np.exp((snapshot.rate.r(T) - snapshot.dividend_yield.q(T)) * T)
    assert abs(model_forward / (SPOT * np.exp((provider.option_rate - provider.option_q) * T)) - 1) > 5e-3


def test_implied_carry_reprices_the_market():
    """With spot and carry calibrated, OTM-built vols reprice ITM options (out of sample)."""
    from src.instruments.european_option import EuropeanOption
    from src.instruments.option_types import OptionType
    from src.models.black_scholes_model import BlackScholesModel
    from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
    from src.process.process_factory import ProcessFactory

    provider = _CarryMismatchProvider()
    snapshot = MarketDataService(provider=provider, ticker="FAKE", valuation_at=VALUATION_DATE).get_market_data_snapshot()

    T = snapshot.sigma.times[2]
    for K, option_type in [(85.0, OptionType.CALL), (115.0, OptionType.PUT)]:
        market = price_fn_bs(SPOT, K, provider.option_rate, provider.option_q, true_vol(K), T, option_type.value)
        process = ProcessFactory.create(BlackScholesModel(snapshot, strike=K, maturity=T))
        model = ClosedBlackScholesPricer().price(EuropeanOption(K, T, option_type), process, snapshot.spot)
        assert model == pytest.approx(market, rel=1e-6)


def test_dividend_curve_term_structure_extrapolates_flat():
    curve = DividendCurve(None, [0.5, 1.0], [0.01, 0.02])
    assert curve.q(0.1) == pytest.approx(0.01)
    assert curve.q(5.0) == pytest.approx(0.02)
