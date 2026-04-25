import pytest

from src.instruments.european_option import EuropeanOption
from src.instruments.option_types import OptionType
from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.monte_carlo import MonteCarloPricer
from src.market_data.market_data import MarketData
from src.pricers.binomial_tree import BinomialTree

def test_binomial_tree_steps_validation():
    with pytest.raises(ValueError):
        BinomialTree(
            steps=0,
        )

    with pytest.raises(ValueError):
        BinomialTree(
            steps=-1,
        )
    
    with pytest.raises(ValueError):
        BinomialTree(
            steps="not an integer",
        )

def test_binomial_tree_finite_differences_greeks_validation():
    with pytest.raises(TypeError):
        BinomialTree(
            steps=32,
            finite_differences_greeks="not a greeks calculator"
        )

def test_binomial_tree_market_bumper_validation():
    with pytest.raises(TypeError):
        BinomialTree(
            steps=32,
            finite_differences_bumper="not a market bumper"
        )


def test_market_data_spot_validation():
    with pytest.raises(ValueError):
        market_data = MarketData(0, 0.05, 0.2, 0.02)
    
    with pytest.raises(ValueError):
        market_data = MarketData(-200, 0.05, 0.2, 0.02)

def test_market_data_volatility_validation():
    with pytest.raises(ValueError):
        market_data = MarketData(100, 0.05, 0, 0.02)

    with pytest.raises(ValueError):
        market_data = MarketData(100, 0.05, -0.2, 0.02)

def test_market_data_dividend_yield():
    with pytest.raises(ValueError):
        market_data = MarketData(1000, 0.05, 0.2, -0.1)


def test_monte_carlo_paths_validation():
    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths=0,
            seed=42
        )
    
    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths=-1,
            seed=42
        )

    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths= "not an integer",
            seed=42
        )

def test_monte_carlo_seed_validation():
    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths=100,
            seed=None
        )
    
    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths=100,
            seed=-1
        )

    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths= 100,
            seed="not an integer"
        )

def test_monte_carlo_steps_validation():
    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            n_steps=0
        )
    
    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            n_steps=-1
        )

    with pytest.raises(ValueError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths= 100,
            seed=42,
            n_steps="not an integer"
        )

def test_monte_carlo_model_validation():
    with pytest.raises(TypeError):
        MonteCarloPricer(
            model="not a model",
            scheme=EulerScheme(),
            paths=100,
            seed=42
        )

def test_monte_carlo_scheme_validation():
    with pytest.raises(TypeError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme="not a scheme",
            paths=100,
            seed=42
        )

def test_monte_carlo_finite_difference_validation():
    with pytest.raises(TypeError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme=EulerScheme(),
            paths=100,
            seed=42,
            finite_differences_greeks='not an analytical greek calculator'
        )

def test_monte_carlo_market_bumper_validation():
    with pytest.raises(TypeError):
        MonteCarloPricer(
            model=BlackScholesModel(),
            scheme="not a scheme",
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
