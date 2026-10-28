import pytest

from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.pricers.binomial_tree import BinomialTree
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.process.process_factory import ProcessFactory
from src.schemes.binomial_tree_scheme import BinomialTreeScheme
from src.models.black_scholes_model import BlackScholesModel
from src.schemes.euler_scheme import EulerScheme

def test_price_black_scholes_vs_monte_carlo(
    standard_market_with_dividend: MarketDataSnapshot,
    standard_call,
    black_scholes_pricer,
    monte_carlo_pricer,
):
    monte_carlo_pricer.scheme = EulerScheme()
    model = BlackScholesModel(standard_market_with_dividend, standard_call.strike, standard_call.maturity)
    process = ProcessFactory().create(model)
    bs_price = black_scholes_pricer.price(standard_call, process, standard_market_with_dividend.spot)
    mc = monte_carlo_pricer.price_with_statistics(standard_call, process, standard_market_with_dividend.spot)

    assert abs(mc.price - bs_price) < 4 * mc.standard_error


def test_price_black_scholes_vs_binomial_tree(
    standard_market_with_dividend,
    standard_call,
):
    model = BlackScholesModel(standard_market_with_dividend, standard_call.strike, standard_call.maturity)
    process = ProcessFactory().create(model)
    bs_price = ClosedBlackScholesPricer().price(standard_call, process, standard_market_with_dividend.spot)
    
    bt_pricer = BinomialTree(scheme=BinomialTreeScheme(), steps=10_000)
    bt_price = bt_pricer.price(standard_call, process, standard_market_with_dividend.spot)

    assert bt_price == pytest.approx(bs_price, abs=1e-3)


# @pytest.mark.parametrize("greek_name", ["delta", "gamma", "vega", "theta", "rho"])
# def test_black_scholes_analytical_greeks_match_finite_difference_anchor(
#     greek_name,
#     standard_market_with_dividend,
#     standard_call,
#     black_scholes_pricer,
#     finite_difference_reference_greeks,
# ):
#     analytical = black_scholes_pricer.greeks(standard_call, standard_market_with_dividend)
#     reference = finite_difference_reference_greeks(
#         black_scholes_pricer,
#         standard_call,
#         standard_market_with_dividend,
#     )

#     assert getattr(analytical, greek_name) == pytest.approx(
#         getattr(reference, greek_name),
#         rel=0.02,
#         abs=1e-3,
#     )


# @pytest.mark.parametrize(
#     ("pricer_fixture", "abs_tolerance"),
#     [
#         ("binomial_tree_pricer", 1e-3),
#         ("monte_carlo_pricer", 0.1),
#     ],
#     ids=["binomial_tree", "monte_carlo"],
# )
# @pytest.mark.parametrize("greek_name", ["delta", "gamma", "vega", "theta", "rho"])
# def test_numerical_pricer_greeks_match_finite_difference_anchor(
#     pricer_fixture,
#     abs_tolerance,
#     greek_name,
#     request,
#     standard_market_with_dividend,
#     standard_call,
#     black_scholes_pricer,
#     finite_difference_reference_greeks,
# ):
#     pricer = request.getfixturevalue(pricer_fixture)
#     reference = finite_difference_reference_greeks(
#         black_scholes_pricer,
#         standard_call,
#         standard_market_with_dividend,
#     )
#     actual = pricer.greeks(standard_call, standard_market_with_dividend)

#     assert getattr(actual, greek_name) == pytest.approx(
#         getattr(reference, greek_name),
#         rel=0.1,
#         abs=abs_tolerance,
#     )

