import numpy as np
import pytest

from src.pricers.binomial_tree import BinomialTree

pricers = [
    BinomialTree()
]

@pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree"])
class TestAmerican:
    
    def test_binomial_tree_american_put_call_inequality(self, pricer, standard_market_with_dividend, standard_american_call, standard_american_put):
        call = pricer.price(standard_american_call, standard_market_with_dividend)
        put = pricer.price(standard_american_put, standard_market_with_dividend)

        lower_bound = standard_market_with_dividend.spot * np.exp(-standard_market_with_dividend.dividend_yield * standard_american_call.maturity) - standard_american_call.strike
        upper_bound = standard_market_with_dividend.spot - standard_american_call.strike * np.exp(-standard_market_with_dividend.rate * standard_american_call.maturity)

        assert lower_bound <= call - put <= upper_bound

    def test_binomial_tree_american_call_upper_bound(self, pricer, standard_market_with_dividend, standard_american_call):
        if standard_market_with_dividend.rate < 0:
            pass

        call = pricer.price(standard_american_call, standard_market_with_dividend)

        assert call <= standard_market_with_dividend.spot

    def test_binomial_tree_american_call_lower_bound(self, pricer, standard_market_with_dividend, standard_american_call):
        if standard_market_with_dividend.rate < 0:
            pass

        call = pricer.price(standard_american_call, standard_market_with_dividend)

        intrinsic_value = max(standard_market_with_dividend.spot - standard_american_call.strike, 0)

        assert call >= intrinsic_value

    def test_binomial_tree_american_put_upper_bound(self, pricer, standard_market_with_dividend, standard_american_put):
        if standard_market_with_dividend.rate < 0:
            pass

        put = pricer.price(standard_american_put, standard_market_with_dividend)

        assert put <= standard_american_put.strike

    def test_binomial_tree_american_put_lower_bound(self, pricer, standard_market_with_dividend, standard_american_put):
        if standard_market_with_dividend.rate < 0:
            pass

        put = pricer.price(standard_american_put, standard_market_with_dividend)

        assert put >= max(standard_american_put.strike - standard_market_with_dividend.spot, 0)
