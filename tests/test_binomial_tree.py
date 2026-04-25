import pytest

import numpy as np

from src.pricers.binomial_tree import BinomialTree

def test_binomial_tree_call(standard_market, standard_call):
    pricer = BinomialTree()

    price = pricer.price(standard_call, standard_market)

    assert price == pytest.approx(10.450583572185565, abs=0.005)

def test_binomial_tree_put(standard_market, standard_put):
    pricer = BinomialTree()

    price = pricer.price(standard_put, standard_market)

    assert price == pytest.approx(5.573526022256969, abs=0.005)

def test_binomial_tree_put_call_parity(standard_market, standard_call, standard_put):
    pricer = BinomialTree()

    call = pricer.price(standard_call, standard_market)
    put = pricer.price(standard_put, standard_market)

    parity = standard_market.spot * np.exp((-standard_market.dividend_yield) * standard_call.maturity) - standard_call.strike * np.exp((-standard_market.rate) * standard_call.maturity)

    assert (call - put) == pytest.approx(parity, abs=1e-8)