import numpy as np
import pytest

from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme
from src.pricers.binomial_tree import BinomialTree
from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer
from tests.scenario import stress_market, stress_option

base_model = BlackScholesModel()
euler_scheme = EulerScheme()

pricers = [
    BinomialTree(),
    BlackScholesPricer(),
    MonteCarloPricer(
        model=base_model,
        scheme=euler_scheme,
        paths=100_000,
        n_steps=128
    )
]

@pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree","black_scholes", "monte_carlo"])
class TestInvariants:

    def test_call_upper_bound(self, pricer, standard_market, standard_call):
        if standard_market.rate < 0:
            assert True

        call = pricer.price(standard_call, standard_market)

        assert call <= standard_market.spot

    def test_call_lower_bound(self, pricer, standard_market, standard_call):
        if standard_market.rate < 0:
            assert True

        call = pricer.price(standard_call, standard_market)

        intrinsic_value = max(standard_market.spot * np.exp(-standard_market.dividend_yield * standard_call.maturity) - standard_call.strike * np.exp(-standard_market.rate * standard_call.maturity), 0)

        assert call >= intrinsic_value

    def test_put_upper_bound(self, pricer, standard_market, standard_put):
        if standard_market.rate < 0:
            assert True

        put = pricer.price(standard_put, standard_market)

        assert put <= standard_put.strike * np.exp(-standard_market.rate * standard_put.maturity)

    def test_put_lower_bound(self, pricer, standard_market, standard_put):
        if standard_market.rate < 0:
            assert True

        put = pricer.price(standard_put, standard_market)

        intrinsic_value = max(
            standard_put.strike * np.exp(-standard_market.rate * standard_put.maturity) - standard_market.spot * np.exp(-standard_market.dividend_yield * standard_put.maturity),
            0
        )

        assert put >= intrinsic_value

    def test_spot_monoticity(self, pricer, standard_market, standard_call, standard_put):
        market_spot_up = stress_market(standard_market, spot_mult=1.1)

        call = pricer.price(standard_call, standard_market)
        put = pricer.price(standard_put, standard_market)

        call_up = pricer.price(standard_call, market_spot_up)
        put_up = pricer.price(standard_put, market_spot_up)

        assert call_up > call
        assert put_up < put

    def test_strike_monoticity(self, pricer, standard_market, standard_call, standard_put):
        call_strike_up = stress_option(standard_call, strike_mult=1.1)
        put_strike_up = stress_option(standard_put, strike_mult=1.1)

        call = pricer.price(standard_call, standard_market)
        put = pricer.price(standard_put, standard_market)

        call_up = pricer.price(call_strike_up, standard_market)
        put_up = pricer.price(put_strike_up, standard_market)

        assert call > call_up
        assert put < put_up

    def test_volatility_monoticity(self, pricer, standard_market, standard_call, standard_put):
        market_volatility_up = stress_market(standard_market, vol_mult=1.1)

        call = pricer.price(standard_call, standard_market)
        put = pricer.price(standard_put, standard_market)

        call_up = pricer.price(standard_call, market_volatility_up)
        put_up = pricer.price(standard_put, market_volatility_up)

        assert call_up > call
        assert put_up > put

    def test_rate_monoticity(self, pricer, standard_market, standard_call, standard_put):
        market_rate_up = stress_market(standard_market, rate_shift=0.02)

        call = pricer.price(standard_call, standard_market)
        put = pricer.price(standard_put, standard_market)

        call_up = pricer.price(standard_call, market_rate_up)
        put_up = pricer.price(standard_put, market_rate_up)

        assert call_up > call
        assert put_up < put


