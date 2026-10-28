import pytest

from src.instruments.european_option import EuropeanOption
from src.instruments.option_types import OptionType
from src.schemes.euler_scheme import EulerScheme
from src.schemes.binomial_tree_scheme import BinomialTreeScheme
from src.pricers.monte_carlo import MonteCarloPricer
from src.pricers.binomial_tree import BinomialTree

def test_binomial_tree_steps_validation():
    with pytest.raises(ValueError):
        BinomialTree(
            scheme=BinomialTreeScheme(),
            steps=0,
        )

    with pytest.raises(ValueError):
        BinomialTree(
            scheme=BinomialTreeScheme(),
            steps=-1,
        )
    
    with pytest.raises(ValueError):
        BinomialTree(
            scheme=BinomialTreeScheme(),
            steps="not an integer",
        )

# def test_binomial_tree_finite_differences_greeks_validation():
#     with pytest.raises(TypeError):
#         BinomialTree(
#             scheme=BinomialTreeScheme(),
#             steps=32,
#             finite_differences_greeks="not a greeks calculator"
#         )

def test_binomial_tree_scheme_validation():
    with pytest.raises(TypeError):
        BinomialTree(
            scheme="not a scheme"
        )

def test_monte_carlo_paths_validation():
    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=0,
            seed=42
        )
    
    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=-1,
            seed=42
        )

    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths="not an integer",
            seed=42
        )

def test_monte_carlo_seed_validation():
    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed=None
        )
    
    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed=-1
        )

    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed="not an integer"
        )

def test_monte_carlo_steps_validation():
    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            n_steps=0
        )
    
    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            n_steps=-1
        )

    with pytest.raises(ValueError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            n_steps="not an integer"
        )

def test_monte_carlo_scheme_validation():
    with pytest.raises(TypeError):
        MonteCarloPricer(
            scheme="not a scheme",
            paths=100,
            seed=42
        )

def test_monte_carlo_variance_reduction_technique_validation():
    pricer = MonteCarloPricer(
        scheme=EulerScheme(),
        paths=100,
    )
    assert pricer.variance_reduction_technique.value == "antithetic"

    for technique in ("antithetic", "control_variate", "none", None):
        pricer = MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            variance_reduction_technique=technique,
        )
        assert pricer.variance_reduction_technique.value in {
            "antithetic",
            "control_variate",
            "none",
        }

    with pytest.raises(ValueError, match="variance_reduction_technique"):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            variance_reduction_technique="unsupported",
        )

def test_monte_carlo_finite_difference_validation():
    with pytest.raises(TypeError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            finite_differences_greeks='not an analytical greek calculator'
        )

def test_monte_carlo_market_bumper_validation():
    with pytest.raises(TypeError):
        MonteCarloPricer(
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            finite_differences_bumper="not a market bumper"
        )

def test_option_strike_validation():
    with pytest.raises(ValueError):
        option = EuropeanOption(-1, 1, OptionType.CALL)
    
    with pytest.raises(ValueError):
        option = EuropeanOption(0, 1, OptionType.CALL)

def test_option_maturity_validation():
    with pytest.raises(ValueError):
        option = EuropeanOption(100, -1, OptionType.CALL)

    with pytest.raises(ValueError):
        option = EuropeanOption(100, 0, OptionType.CALL)

def test_option_type_validation():
    with pytest.raises(ValueError):
        option = EuropeanOption(100, 1, "call")
