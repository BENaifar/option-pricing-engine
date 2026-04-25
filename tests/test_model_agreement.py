import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.binomial_tree import BinomialTree
from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer

base_model = BlackScholesModel()
euler_scheme = EulerScheme()

pricers = [
    BinomialTree(),
    MonteCarloPricer(
        base_model,
        euler_scheme,
        100_000,
        n_steps=128
    )
]

def test_price_black_scholes_vs_monte_carlo(standard_market_with_dividend, standard_call, standard_model, standard_euler_scheme):
    bs_pricer = BlackScholesPricer()
    ms_pricer = MonteCarloPricer(
        model=standard_model,
        scheme=standard_euler_scheme,
        paths=100_000,
        n_steps=128
    )

    bs_price = bs_pricer.price(standard_call, standard_market_with_dividend)
    ms_price = ms_pricer.price(standard_call, standard_market_with_dividend)

    assert abs(bs_price - ms_price) <= 0.05
    

def test_price_black_scholes_vs_binomial_tree(standard_market_with_dividend, standard_call):
    bs_pricer = BlackScholesPricer()
    bt_pricer = BinomialTree(
        steps=10_000
    )

    bs_price = bs_pricer.price(standard_call, standard_market_with_dividend)
    bt_price = bt_pricer.price(standard_call, standard_market_with_dividend)

    assert abs(bs_price - bt_price) <= 1e-3


@pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree", "monte_carlo"])
def test_delta_black_scholes_vs_monte_carlo(pricer, standard_market_with_dividend, standard_call):
    bs_pricer = BlackScholesPricer()

    bs_greeks = bs_pricer.greeks(standard_call, standard_market_with_dividend)
    num_greeks = pricer.greeks(standard_call, standard_market_with_dividend)

    assert num_greeks.delta == pytest.approx(bs_greeks.delta, rel=0.1, abs=1e-3)
    assert num_greeks.gamma == pytest.approx(bs_greeks.gamma, rel=0.1, abs=1e-3)
    assert num_greeks.vega == pytest.approx(bs_greeks.vega, rel=0.1, abs=1e-3)
    assert num_greeks.theta == pytest.approx(bs_greeks.theta, rel=0.1, abs=1e-3)
    assert num_greeks.rho == pytest.approx(bs_greeks.rho, rel=0.1, abs=1e-3)

