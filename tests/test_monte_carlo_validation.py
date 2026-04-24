import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.monte_carlo import MonteCarloPricer

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

