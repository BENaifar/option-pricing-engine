import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.process.process_factory import ProcessFactory
from src.schemes.euler_scheme import EulerScheme
from src.pricers.monte_carlo import MonteCarloPricer

euler_scheme = EulerScheme()

def test_monte_carlo_randomness(standard_market_with_dividend, standard_call):
    base_model = BlackScholesModel(standard_market_with_dividend, strike=100, maturity=1.0)
    process = ProcessFactory.create(base_model)
    
    pricer_1 = MonteCarloPricer(
        scheme=euler_scheme,
        paths=10000,
        n_steps=128,
        seed=1999
    )

    pricer_2 = MonteCarloPricer(
        scheme=euler_scheme,
        paths=10000,
        n_steps=128,
        seed=1999
    )

    price_1 = pricer_1.price(standard_call, process, standard_market_with_dividend.spot)
    price_2 = pricer_2.price(standard_call, process, standard_market_with_dividend.spot)

    assert price_1 == price_2

def test_monte_carlo_stability(standard_market_with_dividend, standard_call):
    base_model = BlackScholesModel(standard_market_with_dividend, strike=100, maturity=1.0)
    process = ProcessFactory.create(base_model)
    
    pricer = MonteCarloPricer(
        scheme=euler_scheme,
        paths=100000,
        n_steps=128
    )

    runs = [
        pricer.price_with_statistics(standard_call, process, standard_market_with_dividend.spot)
        for _ in range(5)
    ]
    prices = [run.price for run in runs]

    assert len(set(prices)) == len(prices)
    assert max(prices) - min(prices) < 4 * max(run.standard_error for run in runs)