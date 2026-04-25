import pytest

from src.pricers.binomial_tree import BinomialTree

def test_price_black_scholes_vs_monte_carlo(
    standard_market_with_dividend,
    standard_call,
    black_scholes_pricer,
    monte_carlo_pricer,
):
    bs_price = black_scholes_pricer.price(standard_call, standard_market_with_dividend)
    mc_price = monte_carlo_pricer.price(standard_call, standard_market_with_dividend)

    assert mc_price == pytest.approx(bs_price, abs=0.05)


def test_price_black_scholes_vs_binomial_tree(
    standard_market_with_dividend,
    standard_call,
    black_scholes_pricer,
):
    bt_pricer = BinomialTree(steps=10_000)

    bs_price = black_scholes_pricer.price(standard_call, standard_market_with_dividend)
    bt_price = bt_pricer.price(standard_call, standard_market_with_dividend)

    assert bt_price == pytest.approx(bs_price, abs=1e-3)


@pytest.mark.parametrize("greek_name", ["delta", "gamma", "vega", "theta", "rho"])
def test_black_scholes_analytical_greeks_match_finite_difference_anchor(
    greek_name,
    standard_market_with_dividend,
    standard_call,
    black_scholes_pricer,
    finite_difference_reference_greeks,
):
    analytical = black_scholes_pricer.greeks(standard_call, standard_market_with_dividend)
    reference = finite_difference_reference_greeks(
        black_scholes_pricer,
        standard_call,
        standard_market_with_dividend,
    )

    assert getattr(analytical, greek_name) == pytest.approx(
        getattr(reference, greek_name),
        rel=0.02,
        abs=1e-3,
    )


@pytest.mark.parametrize(
    ("pricer_fixture", "abs_tolerance"),
    [
        ("binomial_tree_pricer", 1e-3),
        ("monte_carlo_pricer", 0.1),
    ],
    ids=["binomial_tree", "monte_carlo"],
)
@pytest.mark.parametrize("greek_name", ["delta", "gamma", "vega", "theta", "rho"])
def test_numerical_pricer_greeks_match_finite_difference_anchor(
    pricer_fixture,
    abs_tolerance,
    greek_name,
    request,
    standard_market_with_dividend,
    standard_call,
    black_scholes_pricer,
    finite_difference_reference_greeks,
):
    pricer = request.getfixturevalue(pricer_fixture)
    reference = finite_difference_reference_greeks(
        black_scholes_pricer,
        standard_call,
        standard_market_with_dividend,
    )
    actual = pricer.greeks(standard_call, standard_market_with_dividend)

    assert getattr(actual, greek_name) == pytest.approx(
        getattr(reference, greek_name),
        rel=0.1,
        abs=abs_tolerance,
    )

