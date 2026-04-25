import pytest
import numpy as np

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.monte_carlo import MonteCarloPricer

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




