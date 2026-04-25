import pytest

from src.instruments.european_option import EuropeanOption
from src.instruments.american_option import AmericanOption
from src.instruments.option_types import OptionType
from src.market_data.market_data import MarketData
from src.models.black_scholes_model import BlackScholesModel
from src.numerics.euler_scheme import EulerScheme

@pytest.fixture
def standard_market():
    return MarketData(
        spot=100,
        rate=0.05,
        sigma=0.2,
        dividend_yield=0
    )

# eur call: 9.229898019753968
# amr call: 9.229898052272217
# eur put: 6.33297313914773
# amr put: 6.663466131715539
@pytest.fixture
def standard_market_with_dividend():
    return MarketData(
        spot=100,
        rate=0.05,
        sigma=0.2,
        dividend_yield=0.02
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
def standard_model():
    return BlackScholesModel()

@pytest.fixture
def standard_euler_scheme():
    return EulerScheme()