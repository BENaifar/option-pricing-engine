import numpy as np
import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.process.process_factory import ProcessFactory
from src.schemes.euler_scheme import EulerScheme
from src.schemes.binomial_tree_scheme import BinomialTreeScheme
from src.pricers.binomial_tree import BinomialTree
from src.pricers.monte_carlo import MonteCarloPricer
from src.schemes.exact_gbm_scheme import ExactGBMScheme

gbm_scheme = ExactGBMScheme()


def get_pricers_list():
    return [
        [
            BinomialTree(
                scheme=BinomialTreeScheme(),
                steps=10
            ),
            BinomialTree(
                scheme=BinomialTreeScheme(),
                steps=50
            ),
            BinomialTree(
                scheme=BinomialTreeScheme(),
                steps=1000
            )
        ],
        [
            MonteCarloPricer(
                scheme=gbm_scheme,
                paths=1000,
                n_steps=128
            ),
            MonteCarloPricer(
                scheme=gbm_scheme,
                paths=50000,
                n_steps=128
            ),
            MonteCarloPricer(
                scheme=gbm_scheme,
                paths=200000,
                n_steps=128
            )
        ]
    ]

pricers = get_pricers_list()

@pytest.mark.parametrize("pricer_idx", [0], ids=["binomial_tree"])
def test_price_convergence(
    pricer_idx,
    standard_market_with_dividend,
    standard_call,
    black_scholes_pricer,
):
    base_model = BlackScholesModel(standard_market_with_dividend, strike=100, maturity=1.0)
    process = ProcessFactory.create(base_model)
    pricer = pricers[pricer_idx]
    
    coarse_price = pricer[0].price(standard_call, process, standard_market_with_dividend.spot)
    medium_price = pricer[1].price(standard_call, process, standard_market_with_dividend.spot)
    fine_price = pricer[2].price(standard_call, process, standard_market_with_dividend.spot)
    anchor_price = black_scholes_pricer.price(standard_call, process, standard_market_with_dividend.spot)

    assert abs(fine_price - anchor_price) < abs(medium_price - anchor_price) < abs(coarse_price - anchor_price)


def test_monte_carlo_convergence(standard_market_with_dividend, standard_call, black_scholes_pricer):
    """Monte Carlo errors are random: what must shrink, like 1 / sqrt(paths), is the standard error."""
    process = ProcessFactory.create(BlackScholesModel(standard_market_with_dividend, strike=100, maturity=1.0))
    spot = standard_market_with_dividend.spot
    anchor_price = black_scholes_pricer.price(standard_call, process, spot)

    coarse, medium, fine = [p.price_with_statistics(standard_call, process, spot) for p in pricers[1]]

    assert fine.standard_error < medium.standard_error < coarse.standard_error
    assert coarse.standard_error / fine.standard_error == pytest.approx(np.sqrt(fine.observations / coarse.observations), rel=0.1)
    assert abs(fine.price - anchor_price) < 4 * fine.standard_error


# @pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree", "monte_carlo"])
# @pytest.mark.parametrize("greek_name", ["delta", "gamma", "vega", "theta", "rho"])
# def test_greeks_convergence_to_finite_difference_anchor(
#     pricer,
#     greek_name,
#     standard_market_with_dividend,
#     standard_call,
#     black_scholes_pricer,
#     finite_difference_reference_greeks,
# ):
#     coarse_greeks = pricer[0].greeks(standard_call, standard_market_with_dividend)
#     fine_greeks = pricer[2].greeks(standard_call, standard_market_with_dividend)
#     anchor_greeks = finite_difference_reference_greeks(
#         black_scholes_pricer,
#         standard_call,
#         standard_market_with_dividend,
#     )

#     assert abs(getattr(fine_greeks, greek_name) - getattr(anchor_greeks, greek_name)) < abs(
#         getattr(coarse_greeks, greek_name) - getattr(anchor_greeks, greek_name)
#     )

