import pytest
import numpy as np

from src.pricers.black_scholes import BlackScholesPricer


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

def test_black_scholes_delta(standard_market, standard_call):
    pricer = BlackScholesPricer()

    delta = pricer.greeks(standard_call, standard_market).delta
    print(delta)

    assert abs(delta - 0.6368) <= 0.0001

def test_black_scholes_gamma(standard_market, standard_call):
    pricer = BlackScholesPricer()

    gamma = pricer.greeks(standard_call, standard_market).gamma

    assert abs(gamma - 0.0188) <= 0.0001

def test_black_scholes_vega(standard_market, standard_call):
    pricer = BlackScholesPricer()

    vega = pricer.greeks(standard_call, standard_market).vega

    assert abs(vega - 37.5240) <= 0.0001

def test_black_scholes_theta(standard_market, standard_call):
    pricer = BlackScholesPricer()

    theta = pricer.greeks(standard_call, standard_market).theta

    assert abs(theta - (-6.4140)) <= 0.0001

def test_black_scholes_rho(standard_market, standard_call):
    pricer = BlackScholesPricer()

    rho = pricer.greeks(standard_call, standard_market).rho

    assert abs(rho - 53.2325) <= 0.0001







