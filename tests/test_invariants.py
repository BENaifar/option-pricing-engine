import numpy as np
import pytest

from src.instruments.base_option import BaseOption
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.models.base_model import BaseModel
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.base_pricer import BasePricer
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.process.process_factory import ProcessFactory
from src.schemes.euler_scheme import EulerScheme
from src.schemes.binomial_tree_scheme import BinomialTreeScheme
from src.pricers.binomial_tree import BinomialTree
from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer
from src.schemes.exact_gbm_scheme import ExactGBMScheme
from tests.scenario import stress_market, stress_option

euler_scheme = EulerScheme()

pricers = [
    BinomialTree(scheme=BinomialTreeScheme()),
    ClosedBlackScholesPricer(),
    MonteCarloPricer(
        scheme=ExactGBMScheme(),
        paths=100_000,
        n_steps=128
    )
]

@pytest.mark.parametrize("pricer", pricers, ids=["binomial_tree","black_scholes", "monte_carlo"])
class TestInvariants:

    def test_call_upper_bound(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_call: BaseOption, standard_model: BlackScholesModel):
        if standard_market.rate.r(0) < 0:
            assert True

        process = ProcessFactory.create(standard_model)

        call = pricer.price(standard_call, process, standard_market.spot)

        assert call <= standard_market.spot

    def test_call_lower_bound(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_call: BaseOption, standard_model: BlackScholesModel):
        if standard_market.rate.r(0) < 0:
            assert True

        process = ProcessFactory.create(standard_model)

        call = pricer.price(standard_call, process, standard_market.spot)

        intrinsic_value = max(standard_market.spot * np.exp(-standard_market.dividend_yield.q(0) * standard_call.maturity) - standard_call.strike * np.exp(-standard_market.rate.r(0) * standard_call.maturity), 0)

        assert call >= intrinsic_value

    def test_put_upper_bound(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_put: BaseOption, standard_model: BlackScholesModel):
        if standard_market.rate.r(0) < 0:
            assert True

        process = ProcessFactory.create(standard_model)

        put = pricer.price(standard_put, process,standard_market.spot)

        assert put <= standard_put.strike * np.exp(-standard_market.rate.r(0) * standard_put.maturity)

    def test_put_lower_bound(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_put: BaseOption, standard_model: BlackScholesModel):
        if standard_market.rate.r(0) < 0:
            assert True

        process = ProcessFactory.create(standard_model)

        put = pricer.price(standard_put, process,standard_market.spot)

        intrinsic_value = max(
            standard_put.strike * np.exp(-standard_market.rate.r(0) * standard_put.maturity) - standard_market.spot * np.exp(-standard_market.dividend_yield.q(0) * standard_put.maturity),
            0
        )

        assert put >= intrinsic_value

    def test_spot_monoticity(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_call: BaseOption, standard_put: BaseOption, standard_model: BlackScholesModel):
        market_spot_up = stress_market(standard_market, spot_mult=1.1)

        process = ProcessFactory.create(standard_model)

        call = pricer.price(standard_call, process,standard_market.spot)
        put = pricer.price(standard_put, process,standard_market.spot)

        call_up = pricer.price(standard_call, process, market_spot_up.spot)
        put_up = pricer.price(standard_put, process, market_spot_up.spot)

        assert call_up > call
        assert put_up < put

    def test_strike_monoticity(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_call: BaseOption, standard_put: BaseOption):
        call_strike_up = stress_option(standard_call, strike_mult=1.1)
        put_strike_up = stress_option(standard_put, strike_mult=1.1)

        model = BlackScholesModel(standard_market, standard_call.strike, standard_call.maturity)
        model_strike_up = BlackScholesModel(standard_market, call_strike_up.strike, call_strike_up.maturity)
        process = ProcessFactory.create(model)
        process_strike_up = ProcessFactory().create(model_strike_up)

        call = pricer.price(standard_call, process, standard_market.spot)
        put = pricer.price(standard_put, process, standard_market.spot)

        call_up = pricer.price(call_strike_up, process_strike_up, standard_market.spot)
        put_up = pricer.price(put_strike_up, process_strike_up, standard_market.spot)

        assert call > call_up
        assert put < put_up

    def test_volatility_monoticity(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_call: BaseOption, standard_put: BaseOption):
        market_volatility_up = stress_market(standard_market, vol_mult=1.1)
        
        model = BlackScholesModel(standard_market, standard_call.strike, standard_call.maturity)
        model_vol_up = BlackScholesModel(market_volatility_up, standard_call.strike, standard_call.maturity)


        process = ProcessFactory.create(model)
        process_vol_up = ProcessFactory.create(model_vol_up)

        call = pricer.price(standard_call, process, standard_market.spot)
        put = pricer.price(standard_put, process,standard_market.spot)

        call_up = pricer.price(standard_call, process_vol_up, market_volatility_up.spot)
        put_up = pricer.price(standard_put, process_vol_up, market_volatility_up.spot)


        assert call_up > call
        assert put_up > put

    def test_rate_monoticity(self, pricer: BasePricer, standard_market: MarketDataSnapshot, standard_call: BaseOption, standard_put: BaseOption, standard_model: BlackScholesModel):
        market_rate_up = stress_market(standard_market, rate_shift=0.02)
        model_rate_up = BlackScholesModel(market_rate_up, standard_call.strike, standard_call.maturity)
        process_rate_up = ProcessFactory.create(model_rate_up)

        process = ProcessFactory.create(standard_model)

        call = pricer.price(standard_call, process, standard_market.spot)
        put = pricer.price(standard_put, process, standard_market.spot)

        call_up = pricer.price(standard_call, process_rate_up, market_rate_up.spot)
        put_up = pricer.price(standard_put, process_rate_up, market_rate_up.spot)

        assert call_up > call
        assert put_up < put


