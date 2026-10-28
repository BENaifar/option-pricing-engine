# tests/test_extreme_regimes.py

import math
import pytest

from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.models.flat_volatility import FlatVolatility
from src.instruments.european_option import EuropeanOption
from src.instruments.american_option import AmericanOption
from src.instruments.option_types import OptionType

from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.binomial_tree import BinomialTree
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer

from src.models.black_scholes_model import BlackScholesModel
from src.process.process_factory import ProcessFactory
from src.schemes.euler_scheme import EulerScheme
from src.schemes.binomial_tree_scheme import BinomialTreeScheme


# Helper function to create MarketDataSnapshot
def create_market_snapshot(spot, rate, sigma, dividend_yield):
    return MarketDataSnapshot(
        ticker="test",
        spot=spot,
        rate=YieldCurve(rate),
        sigma=FlatVolatility(sigma),
        dividend_yield=DividendCurve(issuance_dates=None, times=None, dividends=dividend_yield)
    )


# ---------------------------------------------------
# EXTREME MARKET SCENARIOS
# ---------------------------------------------------

@pytest.mark.parametrize(
    "spot,rate,sigma,dividend_yield",
    [
        (100, 0.05, 0.20, 0.00),    # near expiry scenario
        (100, 0.00, 0.20, 0.00),    # zero rates
        (100, 0.20, 0.20, 0.00),    # high rates
        (100, 0.05, 0.0001, 0.00),  # very low vol
        (100, 0.05, 1.50, 0.00),    # very high vol
        (100, 0.05, 0.20, 0.10),    # dividend heavy
        (200, 0.05, 0.20, 0.00),    # deep ITM
        (50, 0.05, 0.20, 0.00),     # deep OTM
    ]
)
def test_extreme_regimes_european_call_bs(spot, rate, sigma, dividend_yield):
    """Test Black-Scholes pricer with extreme scenarios"""
    pricer = ClosedBlackScholesPricer()
    market = create_market_snapshot(spot, rate, sigma, dividend_yield)

    option = EuropeanOption(
        strike=100,
        maturity=1/365,   # short maturity
        option_type=OptionType.CALL
    )

    model = BlackScholesModel(market, option.strike, option.maturity)
    process = ProcessFactory.create(model=model)

    price = pricer.price(option, process, market.spot)

    assert math.isfinite(price)
    assert price >= 0
    assert price <= market.spot


@pytest.mark.parametrize(
    "spot,rate,sigma,dividend_yield",
    [
        (100, 0.05, 0.20, 0.00),
        (100, 0.00, 0.20, 0.00),
        (100, 0.20, 0.20, 0.00),
    ]
)
def test_extreme_regimes_european_call_bt(spot, rate, sigma, dividend_yield, standard_american_call):
    """Test BinomialTree pricer with extreme scenarios"""
    pricer = BinomialTree(scheme=BinomialTreeScheme(), steps=500)
    market = create_market_snapshot(spot, rate, sigma, dividend_yield)
    model = BlackScholesModel(market, strike=100, maturity=1/365)
    process = ProcessFactory.create(model)

    option = EuropeanOption(
        strike=100,
        maturity=1/365,
        option_type=OptionType.CALL
    )

    price = pricer.price(option, process, market.spot)

    assert math.isfinite(price)
    assert price >= 0
    assert price <= market.spot


def test_european_put_basic():
    """Test European put with extreme deep ITM"""
    pricer = ClosedBlackScholesPricer()
    market = create_market_snapshot(spot=50, rate=0.05, sigma=1.50, dividend_yield=0)

    option = EuropeanOption(
        strike=100,
        maturity=2.0,
        option_type=OptionType.PUT
    )

    model = BlackScholesModel(market, option.strike, option.maturity)
    process = ProcessFactory().create(model)

    price = pricer.price(option, process, market.spot)

    assert math.isfinite(price)
    assert price >= 0
    assert price <= option.strike


def test_near_zero_vol_call_behaves_like_discounted_intrinsic():
    """Near zero volatility should approximate intrinsic value"""
    pricer = ClosedBlackScholesPricer()
    market = create_market_snapshot(spot=120, rate=0.00, sigma=0.0001, dividend_yield=0.00)

    option = EuropeanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL
    )

    model = BlackScholesModel(market, option.strike, option.maturity)
    process = ProcessFactory.create(model)

    price = pricer.price(option, process, market.spot)

    assert price == pytest.approx(20, abs=1.0)


def test_high_vol_call_more_expensive_than_low_vol():
    """Higher volatility should increase call option value"""
    pricer = ClosedBlackScholesPricer()
    low_vol = create_market_snapshot(100, 0.05, 0.10, 0.00)
    high_vol = create_market_snapshot(100, 0.05, 1.00, 0.00)

    option = EuropeanOption(100, 1.0, OptionType.CALL)

    model_low_vol = BlackScholesModel(low_vol, option.strike, option.maturity)
    model_high_vol = BlackScholesModel(high_vol, option.strike, option.maturity)

    process_low_vol = ProcessFactory().create(model_low_vol)
    process_high_vol = ProcessFactory().create(model_high_vol)

    low_price = pricer.price(option, process_low_vol, low_vol.spot)
    high_price = pricer.price(option, process_high_vol, high_vol.spot)

    assert high_price > low_price


# ---------------------------------------------------
# AMERICAN SPECIFIC
# ---------------------------------------------------

def test_american_put_extreme_deep_itm():
    """American put deep in the money should be worth close to intrinsic"""
    pricer = BinomialTree(scheme=BinomialTreeScheme(), steps=500)
    market = create_market_snapshot(spot=20, rate=0.05, sigma=0.20, dividend_yield=0)
    model = BlackScholesModel(market, strike=100, maturity=1.0)
    process = ProcessFactory.create(model)

    option = AmericanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.PUT
    )

    price = pricer.price(option, process, market.spot)

    # should be close to intrinsic
    assert price >= 80


def test_american_call_with_large_dividend_has_value():
    """American call with large dividend should have significant value"""
    pricer = BinomialTree(scheme=BinomialTreeScheme(), steps=500)
    market = create_market_snapshot(spot=100, rate=0.05, sigma=0.20, dividend_yield=0.15)
    model = BlackScholesModel(market, strike=100, maturity=1.0)
    process = ProcessFactory.create(model)

    option = AmericanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL
    )

    price = pricer.price(option, process, market.spot)

    assert price > 0