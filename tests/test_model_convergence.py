import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.binomial_tree import BinomialTree
from src.pricers.monte_carlo import MonteCarloPricer

base_model = BlackScholesModel()
euler_scheme = EulerScheme()


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


@pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree", "monte_carlo"])
def test_price_convergence(
    pricer,
    standard_market_with_dividend,
    standard_call,
    black_scholes_pricer,
):
    coarse_price = pricer[0].price(standard_call, standard_market_with_dividend)
    medium_price = pricer[1].price(standard_call, standard_market_with_dividend)
    fine_price = pricer[2].price(standard_call, standard_market_with_dividend)
    anchor_price = black_scholes_pricer.price(standard_call, standard_market_with_dividend)

    assert abs(fine_price - anchor_price) < abs(medium_price - anchor_price) < abs(coarse_price - anchor_price)


@pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree", "monte_carlo"])
@pytest.mark.parametrize("greek_name", ["delta", "gamma", "vega", "theta", "rho"])
def test_greeks_convergence_to_finite_difference_anchor(
    pricer,
    greek_name,
    standard_market_with_dividend,
    standard_call,
    black_scholes_pricer,
    finite_difference_reference_greeks,
):
    coarse_greeks = pricer[0].greeks(standard_call, standard_market_with_dividend)
    fine_greeks = pricer[2].greeks(standard_call, standard_market_with_dividend)
    anchor_greeks = finite_difference_reference_greeks(
        black_scholes_pricer,
        standard_call,
        standard_market_with_dividend,
    )

    assert abs(getattr(fine_greeks, greek_name) - getattr(anchor_greeks, greek_name)) < abs(
        getattr(coarse_greeks, greek_name) - getattr(anchor_greeks, greek_name)
    )

