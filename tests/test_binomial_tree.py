import pytest

import numpy as np

from src.models.black_scholes_model import BlackScholesModel
from src.pricers.binomial_tree import BinomialTree
from src.process.process_factory import ProcessFactory
from src.schemes.binomial_tree_scheme import BinomialTreeScheme

def test_binomial_tree_call(standard_market, standard_call):
    pricer = BinomialTree(scheme=BinomialTreeScheme())
    model = BlackScholesModel(standard_market, standard_call.strike, standard_call.maturity)
    process = ProcessFactory.create(model)

    price = pricer.price(standard_call, process, standard_market.spot)

    assert price == pytest.approx(10.450583572185565, abs=0.005)

def test_binomial_tree_put(standard_market, standard_put):
    pricer = BinomialTree(scheme=BinomialTreeScheme())
    model = BlackScholesModel(standard_market, standard_put.strike, standard_put.maturity)
    process = ProcessFactory.create(model)

    price = pricer.price(standard_put, process, standard_market.spot)

    assert price == pytest.approx(5.573526022256969, abs=0.005)

def test_binomial_tree_put_call_parity(standard_market, standard_call, standard_put, standard_model):
    pricer = BinomialTree(scheme=BinomialTreeScheme())

    model = BlackScholesModel(standard_market, standard_call.strike, standard_call.maturity)
    process = ProcessFactory.create(model)

    call = pricer.price(standard_call, process, standard_market.spot)
    put = pricer.price(standard_put, process, standard_market.spot)

    parity = standard_market.spot * np.exp((-standard_market.dividend_yield.q(0)) * standard_call.maturity) - standard_call.strike * np.exp((-standard_market.rate.r(0)) * standard_call.maturity)

    assert (call - put) == pytest.approx(parity, abs=1e-8)