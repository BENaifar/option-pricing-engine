from src.instruments.european_option import EuropeanOption
from src.market_data.market_data import MarketData
from src.pricers.european_pricer import EuropeanPricer
from src.models.black_scholes import BlackScholes
from src.models.monte_carlo import MonteCarlo

def test_engine():
    option = EuropeanOption(100, 1, "call")
    market_data = MarketData(100, 0.05, 0.2)
    bs = BlackScholes()
    pricer_bs = EuropeanPricer(bs)
    pricer_mc = EuropeanPricer(MonteCarlo())

    return pricer_bs.greeks(option, market_data)

if __name__ == "__main__":
    try:
        print(test_engine())
    except Exception as e:
        print(f"Error: {e}")