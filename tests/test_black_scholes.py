from dataclasses import replace

import pytest
import numpy as np

from src.market_data.market_bumper import MarketBumper
from src.pricers.black_scholes import BlackScholesPricer
from src.greeks.greeks_bumps_config import GreeksBumpsConfig


def test_black_scholes_call(standard_market, standard_call):
    pricer = BlackScholesPricer()

    price = pricer.price(standard_call, standard_market)

    assert price == pytest.approx(10.450583572185565, rel=1e-10)

def test_black_scholes_put(standard_market, standard_put):
    pricer = BlackScholesPricer()

    price = pricer.price(standard_put, standard_market)

    assert price == pytest.approx(5.573526022256969, rel=1e-10)

def test_black_scholes_put_call_parity(standard_market, standard_call, standard_put):
    pricer = BlackScholesPricer()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    parity = standard_market.spot * np.exp((-standard_market.dividend_yield) * standard_call.maturity) - standard_call.strike * np.exp((-standard_market.rate) * standard_call.maturity)

    assert (call - put) == pytest.approx(parity, rel=1e-12)

def test_black_scholes_call_upper_bound(standard_market, standard_call):
    if standard_market.rate < 0:
        assert True

    pricer = BlackScholesPricer()

    call = pricer.price(standard_call, standard_market)

    assert call <= standard_market.spot

def test_black_scholes_call_lower_bound(standard_market, standard_call):
    if standard_market.rate < 0:
        assert True

    pricer = BlackScholesPricer()

    call = pricer.price(standard_call, standard_market)

    intrinsic_value = max(standard_market.spot * np.exp(-standard_market.dividend_yield * standard_call.maturity) - standard_call.strike * np.exp(-standard_market.rate * standard_call.maturity), 0)

    assert call >= intrinsic_value

def test_black_scholes_put_upper_bound(standard_market, standard_put):
    if standard_market.rate < 0:
        assert True

    pricer = BlackScholesPricer()

    put = pricer.price(standard_put, standard_market)

    assert put <= standard_put.strike * np.exp(-standard_market.rate * standard_put.maturity)

def test_black_scholes_put_lower_bound(standard_market, standard_put):
    if standard_market.rate < 0:
        assert True

    pricer = BlackScholesPricer()

    put = pricer.price(standard_put, standard_market)

    intrinsic_value = max(
        standard_put.strike * np.exp(-standard_market.rate * standard_put.maturity) - standard_market.spot * np.exp(-standard_market.dividend_yield * standard_put.maturity),
        0
    )

    assert put >= intrinsic_value

def test_black_scholes_spot_monoticity(standard_market, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    _, market_spot_up = market_bumper.bump_spot(standard_market)

    pricer = BlackScholesPricer()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(standard_call, market_spot_up)
    put_up = pricer.price(standard_put, market_spot_up)

    assert call_up > call
    assert put_up < put

def test_black_scholes_strike_monoticity(standard_market, standard_call, standard_put):
    call_strike_up = replace(standard_call, strike=standard_call.strike * 1.1)
    put_strike_up = replace(standard_put, strike=standard_put.strike * 1.1)

    pricer = BlackScholesPricer()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(call_strike_up, standard_market)
    put_up = pricer.price(put_strike_up, standard_market)

    assert call > call_up
    assert put < put_up

def test_black_scholes_volatility_monoticity(standard_market, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    volatility_up,volatility_down = market_bumper.bump_volatility(standard_market)

    pricer = BlackScholesPricer()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(standard_call, volatility_up)
    put_up = pricer.price(standard_put, volatility_up)

    assert call_up > call
    assert put_up > put

def test_black_scholes_rate_monoticity(standard_market, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    rate_up,rate_down = market_bumper.bump_rate(standard_market)

    pricer = BlackScholesPricer()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    call_up = pricer.price(standard_call, rate_up)
    put_up = pricer.price(standard_put, rate_up)

    assert call_up > call
    assert put_up < put

def test_black_scholes_greeks_bounds(standard_market, standard_call, standard_put):
    pricer = BlackScholesPricer()

    call_greeks = pricer.greeks(standard_call, standard_market)
    put_greeks = pricer.greeks(standard_put, standard_market)

    assert 0 <= call_greeks.delta <= 1
    assert 0 >= put_greeks.delta >= -1
    assert call_greeks.gamma >= 0
    assert put_greeks.gamma >= 0
    assert call_greeks.vega >= 0
    assert put_greeks.vega >= 0
    assert call_greeks.theta <= 0
    assert put_greeks.theta <= 0
    assert call_greeks.rho >= 0
    assert put_greeks.rho <= 0




