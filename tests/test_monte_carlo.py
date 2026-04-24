from dataclasses import replace

import pytest
import numpy as np

from src.market_data.market_bumper import MarketBumper
from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.monte_carlo import MonteCarloPricer
from src.greeks.greeks_bumps_config import GreeksBumpsConfig

base_model = BlackScholesModel()
euler_scheme = EulerScheme()

def test_monte_carlo_call(standard_market_with_dividend, standard_call):
    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    price = pricer.price(standard_call, standard_market_with_dividend)

    assert price == pytest.approx(9.229898019753968, abs=0.05)

def test_monte_carlo_put(standard_market_with_dividend, standard_put):
    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    price = pricer.price(standard_put, standard_market_with_dividend)

    assert price == pytest.approx(6.33297313914773, abs=0.05)

def test_monte_carlo_put_call_parity(standard_market_with_dividend, standard_call, standard_put):
    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call = pricer.price(standard_call, standard_market_with_dividend)
    put = pricer.price(standard_put, standard_market_with_dividend)

    parity = standard_market_with_dividend.spot * np.exp((-standard_market_with_dividend.dividend_yield) * standard_call.maturity) - standard_call.strike * np.exp((-standard_market_with_dividend.rate) * standard_call.maturity)

    assert (call - put) == pytest.approx(parity, abs=0.01)

def test_monte_carlo_call_upper_bound(standard_market_with_dividend, standard_call):
    if standard_market_with_dividend.rate < 0:
        assert True

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call = pricer.price(standard_call, standard_market_with_dividend)

    assert call <= standard_market_with_dividend.spot

def test_monte_carlo_call_lower_bound(standard_market_with_dividend, standard_call):
    if standard_market_with_dividend.rate < 0:
        assert True

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call = pricer.price(standard_call, standard_market_with_dividend)

    intrinsic_value = max(standard_market_with_dividend.spot * np.exp(-standard_market_with_dividend.dividend_yield * standard_call.maturity) - standard_call.strike * np.exp(-standard_market_with_dividend.rate * standard_call.maturity), 0)

    assert call >= intrinsic_value

def test_monte_carlo_put_upper_bound(standard_market_with_dividend, standard_put):
    if standard_market_with_dividend.rate < 0:
        assert True

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    put = pricer.price(standard_put, standard_market_with_dividend)

    assert put <= standard_put.strike * np.exp(-standard_market_with_dividend.rate * standard_put.maturity)

def test_monte_carlo_put_lower_bound(standard_market_with_dividend, standard_put):
    if standard_market_with_dividend.rate < 0:
        assert True

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    put = pricer.price(standard_put, standard_market_with_dividend)

    intrinsic_value = max(
        standard_put.strike * np.exp(-standard_market_with_dividend.rate * standard_put.maturity) - standard_market_with_dividend.spot * np.exp(-standard_market_with_dividend.dividend_yield * standard_put.maturity),
        0
    )

    assert put >= intrinsic_value

def test_monte_carlo_spot_monoticity(standard_market_with_dividend, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    _, market_spot_up = market_bumper.bump_spot(standard_market_with_dividend)

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call = pricer.price(standard_call, standard_market_with_dividend)
    put = pricer.price(standard_put, standard_market_with_dividend)

    call_up = pricer.price(standard_call, market_spot_up)
    put_up = pricer.price(standard_put, market_spot_up)

    assert call_up > call
    assert put_up < put

def test_monte_carlo_strike_monoticity(standard_market_with_dividend, standard_call, standard_put):
    call_strike_up = replace(standard_call, strike=standard_call.strike * 1.1)
    put_strike_up = replace(standard_put, strike=standard_put.strike * 1.1)

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call = pricer.price(standard_call, standard_market_with_dividend)
    put = pricer.price(standard_put, standard_market_with_dividend)

    call_up = pricer.price(call_strike_up, standard_market_with_dividend)
    put_up = pricer.price(put_strike_up, standard_market_with_dividend)

    assert call > call_up
    assert put < put_up

def test_monte_carlo_volatility_monoticity(standard_market_with_dividend, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    volatility_up,volatility_down = market_bumper.bump_volatility(standard_market_with_dividend)

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call = pricer.price(standard_call, standard_market_with_dividend)
    put = pricer.price(standard_put, standard_market_with_dividend)

    call_up = pricer.price(standard_call, volatility_up)
    put_up = pricer.price(standard_put, volatility_up)

    assert call_up > call
    assert put_up > put

def test_monte_carlo_rate_monoticity(standard_market_with_dividend, standard_call, standard_put):
    bump_config = GreeksBumpsConfig()
    market_bumper = MarketBumper(bump_config)

    rate_up,rate_down = market_bumper.bump_rate(standard_market_with_dividend)

    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call = pricer.price(standard_call, standard_market_with_dividend)
    put = pricer.price(standard_put, standard_market_with_dividend)

    call_up = pricer.price(standard_call, rate_up)
    put_up = pricer.price(standard_put, rate_up)

    assert call_up > call
    assert put_up < put

def test_monte_carlo_greeks_bounds(standard_market_with_dividend, standard_call, standard_put):
    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    call_greeks = pricer.greeks(standard_call, standard_market_with_dividend)
    put_greeks = pricer.greeks(standard_put, standard_market_with_dividend)

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




