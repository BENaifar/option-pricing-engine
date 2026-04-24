import pytest

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