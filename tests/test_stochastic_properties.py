import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.monte_carlo import MonteCarloPricer

base_model = BlackScholesModel()
euler_scheme = EulerScheme()

def test_monte_carlo_randomness(standard_market_with_dividend, standard_call):
    pricer_1 = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=10000,
        n_steps=128,
        seed=1999
    )

    pricer_2 = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=10000,
        n_steps=128,
        seed=1999
    )

    price_1 = pricer_1.price(standard_call, standard_market_with_dividend)
    price_2 = pricer_2.price(standard_call, standard_market_with_dividend)

    assert price_1 == price_2

def test_monte_carlo_stability(standard_market_with_dividend, standard_call):
    pricer = MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    prices = [
        pricer.price(standard_call, standard_market_with_dividend)
        for _ in range(5)
    ]

    assert max(prices) - min(prices) < 0.1

    