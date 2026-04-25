import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.binomial_tree import BinomialTree
from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer

base_model = BlackScholesModel()
euler_scheme = EulerScheme()
black_scholes_pricer = BlackScholesPricer()


pricers = [
    [
        BinomialTree(
            steps=10
        ),
        BinomialTree(
            steps=50
        ),
        BinomialTree(
            steps=1000
        )
    ],
    [
        MonteCarloPricer(
            model=base_model,
            scheme=euler_scheme,
            paths=1000,
            n_steps=128
        ),
        MonteCarloPricer(
            model=base_model,
            scheme=euler_scheme,
            paths=50000,
            n_steps=128
        ),
        MonteCarloPricer(
            model=base_model,
            scheme=euler_scheme,
            paths=200000,
            n_steps=128
        )
    ]
]


@pytest.mark.parametrize("pricer", pricers, ids=['binomial_tree', 'monte_carlo'])
def test_price_convergence(pricer, standard_market_with_dividend, standard_call):

    price10000 = pricer[0].price(standard_call, standard_market_with_dividend)
    price50000 = pricer[1].price(standard_call, standard_market_with_dividend)
    price100000 = pricer[2].price(standard_call, standard_market_with_dividend)

    black_scholes_pricer = BlackScholesPricer()
    price = black_scholes_pricer.price(standard_call, standard_market_with_dividend)

    assert abs(price100000 - price) < abs(price50000 - price) < abs(price10000 - price)

@pytest.mark.parametrize("pricer", pricers, ids=['binomial_tree', 'monte_carlo'])
def test_delta_convergence(pricer, standard_market_with_dividend, standard_call):

    greeks10000 = pricer[0].greeks(standard_call, standard_market_with_dividend)
    greeks100000 = pricer[2].greeks(standard_call, standard_market_with_dividend)

    black_scholes_pricer = BlackScholesPricer()

    greeks = black_scholes_pricer.greeks(standard_call, standard_market_with_dividend)

    assert abs(greeks100000.delta - greeks.delta) < abs(greeks10000.delta - greeks.delta)

@pytest.mark.parametrize("pricer", pricers, ids=['binomial_tree', 'monte_carlo'])
def test_gamma_convergence(pricer, standard_market_with_dividend, standard_call):

    greeks10000 = pricer[0].greeks(standard_call, standard_market_with_dividend)
    greeks100000 = pricer[2].greeks(standard_call, standard_market_with_dividend)

    black_scholes_pricer = BlackScholesPricer()

    greeks = black_scholes_pricer.greeks(standard_call, standard_market_with_dividend)

    assert abs(greeks100000.gamma - greeks.gamma) < abs(greeks10000.gamma - greeks.gamma)

@pytest.mark.parametrize("pricer", pricers, ids=['binomial_tree', 'monte_carlo'])
def test_vega_convergence(pricer, standard_market_with_dividend, standard_call):

    greeks10000 = pricer[0].greeks(standard_call, standard_market_with_dividend)
    greeks100000 = pricer[2].greeks(standard_call, standard_market_with_dividend)

    black_scholes_pricer = BlackScholesPricer()

    greeks = black_scholes_pricer.greeks(standard_call, standard_market_with_dividend)

    assert abs(greeks100000.vega - greeks.vega) < abs(greeks10000.vega - greeks.vega)

@pytest.mark.parametrize("pricer", pricers, ids=['binomial_tree', 'monte_carlo'])
def test_theta_convergence(pricer, standard_market_with_dividend, standard_call):

    greeks10000 = pricer[0].greeks(standard_call, standard_market_with_dividend)
    greeks100000 = pricer[2].greeks(standard_call, standard_market_with_dividend)

    black_scholes_pricer = BlackScholesPricer()

    greeks = black_scholes_pricer.greeks(standard_call, standard_market_with_dividend)

    assert abs(greeks100000.theta - greeks.theta) < abs(greeks10000.theta - greeks.theta)

@pytest.mark.parametrize("pricer", pricers, ids=['binomial_tree', 'monte_carlo'])
def test_rho_convergence(pricer, standard_market_with_dividend, standard_call):

    greeks10000 = pricer[0].greeks(standard_call, standard_market_with_dividend)
    greeks100000 = pricer[2].greeks(standard_call, standard_market_with_dividend)

    black_scholes_pricer = BlackScholesPricer()

    greeks = black_scholes_pricer.greeks(standard_call, standard_market_with_dividend)

    assert abs(greeks100000.rho - greeks.rho) < abs(greeks10000.rho - greeks.rho)

