from datetime import datetime

import pytest

from src.greeks.finite_differences_greeks import FiniteDifferencesGreeks
from src.greeks.greeks import Greeks
from src.greeks.greeks_bumps_config import GreeksBumpsConfig
from src.instruments.european_option import EuropeanOption
from src.instruments.american_option import AmericanOption
from src.instruments.option_types import OptionType
from src.market_data.curves.dividend_curve import DividendCurve
from src.market_data.curves.yield_curve import YieldCurve
from src.market_data.market_bumper import MarketBumper
from src.market_data.market_data_snapshot import MarketDataSnapshot
from src.market_data.models.flat_volatility import FlatVolatility
from src.market_data.services.market_data_service import MarketDataService
from src.models.black_scholes_model import BlackScholesModel
from src.pricers.closed_black_scholes import ClosedBlackScholesPricer
from src.process.gbm_process import GBMProcess
from src.schemes.binomial_tree_scheme import BinomialTreeScheme
from src.schemes.euler_scheme import EulerScheme
from src.pricers.binomial_tree import BinomialTree
from src.pricers.black_scholes import BlackScholesPricer
from src.pricers.monte_carlo import MonteCarloPricer
from src.schemes.exact_gbm_scheme import ExactGBMScheme

@pytest.fixture
def valuation_date():
    return datetime(2025, 1, 1)


@pytest.fixture
def service(valuation_date):
    from src.market_data.providers.yahoo_market_data_provider import YahooMarketDataProvider
    provider = YahooMarketDataProvider()
    return MarketDataService(
        provider=provider,
        ticker="AAPL",
        valuation_at=valuation_date,
    )

@pytest.fixture
def standard_market():
    return MarketDataSnapshot(
        ticker="test",
        spot=100.0,
        rate=YieldCurve(0.05),
        sigma=FlatVolatility(0.2),
        dividend_yield=DividendCurve(issuance_dates=None, times=None, dividends=0.0)
    )

# eur call: 9.229898019753968
# amr call: 9.229898052272217
# eur put: 6.33297313914773
# amr put: 6.663466131715539
@pytest.fixture
def standard_market_with_dividend():
    return MarketDataSnapshot(
        ticker="test",
        spot=100.0,
        rate=YieldCurve(0.05),
        sigma=FlatVolatility(0.2),
        dividend_yield=DividendCurve(issuance_dates=None, times=None, dividends=0.02)
    )

@pytest.fixture
def standard_call():
    return EuropeanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL
    )

@pytest.fixture
def standard_put():
    return EuropeanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.PUT
    )

@pytest.fixture
def standard_american_call():
    return AmericanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.CALL
    )

@pytest.fixture
def standard_american_put():
    return AmericanOption(
        strike=100,
        maturity=1.0,
        option_type=OptionType.PUT
    ) 



@pytest.fixture
def standard_model(standard_market):
    return BlackScholesModel(standard_market, strike=100, maturity=1.0)

@pytest.fixture
def standard_euler_scheme():
    return EulerScheme()

@pytest.fixture
def standard_exact_gbm_scheme():
    return ExactGBMScheme()

@pytest.fixture
def standard_greeks_bumps_config():
    return GreeksBumpsConfig()


@pytest.fixture
def finite_differences_greeks(standard_greeks_bumps_config):
    return FiniteDifferencesGreeks(greek_bumps_config=standard_greeks_bumps_config)


@pytest.fixture
def market_bumper(standard_greeks_bumps_config):
    return MarketBumper(greek_bumps_config=standard_greeks_bumps_config)


@pytest.fixture
def black_scholes_pricer():
    return ClosedBlackScholesPricer()


@pytest.fixture
def binomial_tree_pricer():
    return BinomialTree(scheme=BinomialTreeScheme())


@pytest.fixture
def monte_carlo_pricer(standard_exact_gbm_scheme):
    return MonteCarloPricer(
        scheme=standard_exact_gbm_scheme,
        paths=100_000,
        n_steps=128,
        seed=42,
    )


@pytest.fixture
def finite_difference_reference_greeks(finite_differences_greeks, market_bumper):
    def _reference(pricer, option, market_data):
        market_down, market_up = market_bumper.bump_spot(market_data)
        base_price = pricer.price(option, market_data)
        price_up = pricer.price(option, market_up)
        price_down = pricer.price(option, market_down)

        dt, option_short, option_long = market_bumper.bump_time(option)
        price_short = pricer.price(option_short, market_data)
        price_long = pricer.price(option_long, market_data)

        volatility_up, volatility_down = market_bumper.bump_volatility(market_data)
        price_vol_up = pricer.price(option, volatility_up)
        price_vol_down = pricer.price(option, volatility_down)

        rate_up, rate_down = market_bumper.bump_rate(market_data)
        price_rate_up = pricer.price(option, rate_up)
        price_rate_down = pricer.price(option, rate_down)

        return Greeks(
            delta=finite_differences_greeks.delta(market_data, price_up, price_down),
            gamma=finite_differences_greeks.gamma(market_data, base_price, price_up, price_down),
            theta=finite_differences_greeks.theta(dt, price_short, price_long),
            vega=finite_differences_greeks.vega(price_vol_up, price_vol_down),
            rho=finite_differences_greeks.rho(price_rate_up, price_rate_down),
        )

    return _reference
