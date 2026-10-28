import numpy as np
import pytest

from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.binomial_tree import BinomialTree
from src.process.process_factory import ProcessFactory
from src.schemes.binomial_tree_scheme import BinomialTreeScheme

pricers = [
    BinomialTree(scheme=BinomialTreeScheme())
]

@pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree"])
class TestAmerican:
    
    def test_binomial_tree_american_put_call_inequality(self, pricer: BinomialTree, standard_market_with_dividend: MarketDataSnapshot, standard_model: BlackScholesModel, standard_american_call, standard_american_put):
        process = ProcessFactory.create(standard_model)
        call = pricer.price(standard_american_call, process, standard_market_with_dividend.spot)
        put = pricer.price(standard_american_put, process, standard_market_with_dividend.spot)

        lower_bound = standard_market_with_dividend.spot * np.exp(-standard_market_with_dividend.dividend_yield.q(0) * standard_american_call.maturity) - standard_american_call.strike
        upper_bound = standard_market_with_dividend.spot - standard_american_call.strike * np.exp(-standard_market_with_dividend.rate.r(0) * standard_american_call.maturity)

        assert lower_bound <= call - put <= upper_bound

    def test_binomial_tree_american_call_upper_bound(self, pricer, standard_market_with_dividend: MarketDataSnapshot, standard_american_call, standard_model: BlackScholesModel):
        if standard_market_with_dividend.rate.r(0) < 0:
            pass

        process = ProcessFactory.create(standard_model)
        call = pricer.price(standard_american_call, process, standard_market_with_dividend.spot)

        assert call <= standard_market_with_dividend.spot

    def test_binomial_tree_american_call_lower_bound(self, pricer, standard_market_with_dividend, standard_american_call, standard_model: BlackScholesModel):
        if standard_market_with_dividend.rate.r(0) < 0:
            pass

        process = ProcessFactory.create(standard_model)
        call = pricer.price(standard_american_call, process, standard_market_with_dividend.spot)

        intrinsic_value = max(standard_market_with_dividend.spot - standard_american_call.strike, 0)

        assert call >= intrinsic_value

    def test_binomial_tree_american_put_upper_bound(self, pricer, standard_market_with_dividend, standard_american_put, standard_model: BlackScholesModel):
        if standard_market_with_dividend.rate.r(0) < 0:
            pass

        process = ProcessFactory.create(standard_model)
        put = pricer.price(standard_american_put, process, standard_market_with_dividend.spot)

        assert put <= standard_american_put.strike

    def test_binomial_tree_american_put_lower_bound(self, pricer, standard_market_with_dividend, standard_american_put, standard_model: BlackScholesModel):
        if standard_market_with_dividend.rate.r(0) < 0:
            pass

        process = ProcessFactory.create(standard_model)
        put = pricer.price(standard_american_put, process, standard_market_with_dividend.spot)

        assert put >= max(standard_american_put.strike - standard_market_with_dividend.spot, 0)
