from dataclasses import replace

import pytest

import numpy as np

from src.market_data.market_bumper import MarketBumper
from src.pricers.binomial_tree import BinomialTree
from src.greeks.greeks_bumps_config import GreeksBumpsConfig


def test_binomial_tree_call(standard_market, standard_call):
    pricer = BinomialTree()

    price = pricer.price(standard_call, standard_market)

    assert price == pytest.approx(10.450583572185565, abs=0.005)

def test_binomial_tree_put(standard_market, standard_put):
    pricer = BinomialTree()

    price = pricer.price(standard_put, standard_market)

    assert price == pytest.approx(5.573526022256969, abs=0.005)

def test_binomial_tree_put_call_parity(standard_market, standard_call, standard_put):
    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    parity = standard_market.spot * np.exp((-standard_market.dividend_yield) * standard_call.maturity) - standard_call.strike * np.exp((-standard_market.rate) * standard_call.maturity)

    assert (call - put) == pytest.approx(parity, abs=1e-8)

def test_binomial_tree_call_upper_bound(standard_market, standard_call):
    if standard_market.rate < 0:
        assert True

    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)

    assert call <= standard_market.spot

def test_binomial_tree_call_lower_bound(standard_market, standard_call):
    if standard_market.rate < 0:
        assert True

    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)

    intrinsic_value = max(standard_market.spot * np.exp(-standard_market.dividend_yield * standard_call.maturity) - standard_call.strike * np.exp(-standard_market.rate * standard_call.maturity), 0)

    assert call >= intrinsic_value

def test_binomial_tree_put_upper_bound(standard_market, standard_put):
    if standard_market.rate < 0:
        assert True

    pricer = BinomialTree()

    put = pricer.price(standard_put, standard_market)

    assert put <= standard_put.strike * np.exp(-standard_market.rate * standard_put.maturity)

def test_binomial_tree_put_lower_bound(standard_market, standard_put):
    if standard_market.rate < 0:
        assert True

    pricer = BinomialTree()

    put = pricer.price(standard_put, standard_market)

    intrinsic_value = max(
        standard_put.strike * np.exp(-standard_market.rate * standard_put.maturity) - standard_market.spot * np.exp(-standard_market.dividend_yield * standard_put.maturity),
        0
    )

    assert put >= intrinsic_value

def test_binomial_tree_american_call(standard_market_with_dividend, standard_american_call):
    pricer = BinomialTree()

    price = pricer.price(standard_american_call, standard_market_with_dividend)

    assert price == pytest.approx(9.229898052272217, abs=0.005)

def test_binomial_tree_american_put(standard_market_with_dividend, standard_american_put):
    pricer = BinomialTree()

    price = pricer.price(standard_american_put, standard_market_with_dividend)

    assert price == pytest.approx(6.663466131715539, abs=0.005)

def test_binomial_tree_american_put_call_parity(standard_market_with_dividend, standard_american_call, standard_american_put):
    pricer = BinomialTree()

    call = pricer.price(standard_american_call, standard_market_with_dividend)
    put = pricer.price(standard_american_put, standard_market_with_dividend)

    lower_bound = standard_market_with_dividend.spot * np.exp(-standard_market_with_dividend.dividend_yield * standard_american_call.maturity) - standard_american_call.strike
    upper_bound = standard_market_with_dividend.spot - standard_american_call.strike * np.exp(-standard_market_with_dividend.rate * standard_american_call.maturity)

    assert lower_bound <= call - put <= upper_bound

def test_binomial_tree_american_call_upper_bound(standard_market_with_dividend, standard_american_call):
    if standard_market_with_dividend.rate < 0:
        pass

    pricer = BinomialTree()

    call = pricer.price(standard_american_call, standard_market_with_dividend)

    assert call <= standard_market_with_dividend.spot

def test_binomial_tree_american_call_lower_bound(standard_market_with_dividend, standard_american_call):
    if standard_market_with_dividend.rate < 0:
        pass

    pricer = BinomialTree()

    call = pricer.price(standard_american_call, standard_market_with_dividend)

    intrinsic_value = max(standard_market_with_dividend.spot - standard_american_call.strike, 0)

    assert call >= intrinsic_value

def test_binomial_tree_american_put_upper_bound(standard_market_with_dividend, standard_american_put):
    if standard_market_with_dividend.rate < 0:
        pass

    pricer = BinomialTree()

    put = pricer.price(standard_american_put, standard_market_with_dividend)

    assert put <= standard_american_put.strike

def test_binomial_tree_american_put_lower_bound(standard_market_with_dividend, standard_american_put):
    if standard_market_with_dividend.rate < 0:
        pass

    pricer = BinomialTree()

    put = pricer.price(standard_american_put, standard_market_with_dividend)

    assert put >= max(standard_american_put.strike - standard_market_with_dividend.spot, 0)


def test_binomial_tree_spot_monoticity(standard_market, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    _, market_spot_up = market_bumper.bump_spot(standard_market)

    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(standard_call, market_spot_up)
    put_up = pricer.price(standard_put, market_spot_up)

    assert call_up > call
    assert put_up < put

def test_binomial_tree_strike_monoticity(standard_market, standard_call, standard_put):
    call_strike_up = replace(standard_call, strike=standard_call.strike * 1.1)
    put_strike_up = replace(standard_put, strike=standard_put.strike * 1.1)

    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(call_strike_up, standard_market)
    put_up = pricer.price(put_strike_up, standard_market)

    assert call > call_up
    assert put < put_up

def test_binomial_tree_volatility_monoticity(standard_market, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    volatility_up,volatility_down = market_bumper.bump_volatility(standard_market)

    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(standard_call, volatility_up)
    put_up = pricer.price(standard_put, volatility_up)

    assert call_up > call
    assert put_up > put

def test_binomial_tree_rate_monoticity(standard_market, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    rate_up,rate_down = market_bumper.bump_rate(standard_market)

    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(standard_call, rate_up)
    put_up = pricer.price(standard_put, rate_up)

    assert call_up > call
    assert put_up < put

def test_binomial_tree_greeks_bounds(standard_market, standard_call, standard_put):
    pricer = BinomialTree()

    call_greeks = pricer.greeks(standard_call, standard_market)
    put_greeks = pricer.greeks(standard_put, standard_market)

    assert 0.0 <= call_greeks.delta <= 1.0
    assert 0.0 >= put_greeks.delta >= -1.0
    assert call_greeks.gamma >= 0.0
    assert put_greeks.gamma >= 0.0
    assert call_greeks.vega >= 0.0
    assert put_greeks.vega >= 0.0
    assert call_greeks.theta <= 0.0
    assert put_greeks.theta <= 0.0
    assert call_greeks.rho >= 0.0
    assert put_greeks.rho <= 0.0




