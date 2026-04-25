# tests/test_extreme_regimes.py

import math
import pytest

from src.market_data.market_data import MarketData
from src.instruments.european_option import EuropeanOption
from src.instruments.american_option import AmericanOption
from src.instruments.option_types import OptionType

from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.binomial_tree import BinomialTree
from src.pricers.monte_carlo import MonteCarloPricer

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme


# ---------------------------------------------------
# PRICERS
# ---------------------------------------------------

base_model = BlackScholesModel()
scheme = EulerScheme()

european_pricers = [
    BlackScholesPricer(),
    BinomialTree(steps=2000),
    MonteCarloPricer(
        model=base_model,
        scheme=scheme,
        paths=100000,
        n_steps=128,
        seed=42
    )
]

american_pricers = [
    BinomialTree(steps=2000)
]


# ---------------------------------------------------
# EXTREME MARKET SCENARIOS
# ---------------------------------------------------

@pytest.mark.parametrize(
    "market",
    [
        # near expiry
        MarketData(100, 0.05, 0.20, 0.00),

        # zero rates
        MarketData(100, 0.00, 0.20, 0.00),

        # high rates
        MarketData(100, 0.20, 0.20, 0.00),

        # very low vol
        MarketData(100, 0.05, 0.0001, 0.00),

        # very high vol
        MarketData(100, 0.05, 1.50, 0.00),

        # dividend heavy
        MarketData(100, 0.05, 0.20, 0.10),

        # deep ITM
        MarketData(200, 0.05, 0.20, 0.00),

        # deep OTM
        MarketData(50, 0.05, 0.20, 0.00),
    ]
)
@pytest.mark.parametrize("pricer", european_pricers)
def test_extreme_regimes_european_call(pricer, market):

    option = EuropeanOption(
        strike=100,
        maturity=1/365,   # short maturity
        option_type=OptionType.CALL
    )

    price = pricer.price(option, market)

    assert math.isfinite(price)
    assert price >= 0
    assert price <= market.spot


@pytest.mark.parametrize("pricer", european_pricers)
def test_extreme_regimes_european_put(pricer):

    market = MarketData(
        spot=50,          # deep ITM put
        rate=0.05,
        sigma=1.50,
        dividend_yield=0
    )

    option = EuropeanOption(
        strike=100,
        maturity=2.0,
        option_type=OptionType.PUT
    )

    price = pricer.price(option, market)

    assert math.isfinite(price)
    assert price >= 0
    assert price <= option.strike


# ---------------------------------------------------
# NEAR ZERO VOL -> INTRINSIC VALUE
# ---------------------------------------------------

@pytest.mark.parametrize("pricer", european_pricers)
def test_near_zero_vol_call_behaves_like_discounted_intrinsic(pricer):

    market = MarketData(
        spot=120,
        rate=0.00,
        sigma=0.0001,
        dividend_yield=0.00
    )

    option = EuropeanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL
    )

    price = pricer.price(option, market)

    assert price == pytest.approx(20, abs=1.0)


# ---------------------------------------------------
# HIGH VOL SHOULD INCREASE OPTION VALUE
# ---------------------------------------------------

@pytest.mark.parametrize("pricer", european_pricers)
def test_high_vol_call_more_expensive_than_low_vol(pricer):

    low_vol = MarketData(100, 0.05, 0.10, 0.00)
    high_vol = MarketData(100, 0.05, 1.00, 0.00)

    option = EuropeanOption(100, 1.0, OptionType.CALL)

    low_price = pricer.price(option, low_vol)
    high_price = pricer.price(option, high_vol)

    assert high_price > low_price


# ---------------------------------------------------
# AMERICAN SPECIFIC
# ---------------------------------------------------

@pytest.mark.parametrize("pricer", american_pricers)
def test_american_put_extreme_deep_itm(pricer):

    market = MarketData(
        spot=20,
        rate=0.05,
        sigma=0.20,
        dividend_yield=0
    )

    option = AmericanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.PUT
    )

    price = pricer.price(option, market)

    # should be close to intrinsic
    assert price >= 80


@pytest.mark.parametrize("pricer", american_pricers)
def test_american_call_with_large_dividend_has_value(pricer):

    market = MarketData(
        spot=100,
        rate=0.05,
        sigma=0.20,
        dividend_yield=0.15
    )

    option = AmericanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL
    )

    price = pricer.price(option, market)

    assert price > 0
    assert price <= market.spot


# ---------------------------------------------------
# GREEKS SHOULD REMAIN FINITE
# ---------------------------------------------------

@pytest.mark.parametrize("pricer", european_pricers)
def test_extreme_regimes_greeks_finite(pricer):

    market = MarketData(
        spot=100,
        rate=0.00,
        sigma=1.20,
        dividend_yield=0
    )

    option = EuropeanOption(
        strike=100,
        maturity=0.25,
        option_type=OptionType.CALL
    )

    greeks = pricer.greeks(option, market)

    assert math.isfinite(greeks.delta)
    assert math.isfinite(greeks.gamma)
    assert math.isfinite(greeks.vega)
    assert math.isfinite(greeks.theta)
    assert math.isfinite(greeks.rho)