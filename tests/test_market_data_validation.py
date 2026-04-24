import pytest

from src.market_data.market_data import MarketData


def test_market_data_spot_validation():
    with pytest.raises(ValueError):
        market_data = MarketData(0, 0.05, 0.2, 0.02)
    
    with pytest.raises(ValueError):
        market_data = MarketData(-200, 0.05, 0.2, 0.02)

def test_market_data_volatility_validation():
    with pytest.raises(ValueError):
        market_data = MarketData(100, 0.05, 0, 0.02)

    with pytest.raises(ValueError):
        market_data = MarketData(100, 0.05, -0.2, 0.02)

def test_market_data_dividend_yield():
    with pytest.raises(ValueError):
        market_data = MarketData(1000, 0.05, 0.2, -0.1)
