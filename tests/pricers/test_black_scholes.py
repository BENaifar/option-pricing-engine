import unittest

import numpy as np

from src.instruments.european_option import EuropeanOption
from src.pricers.black_scholes import BlackScholesPricer
from src.market_data.market_data import MarketData
from src.models.gbm_model import GBMModel

class TestBlackScholes(unittest.TestCase):

    def test_basic_call(self):
        option = EuropeanOption(120, 1, 'call')
        market = MarketData(100, 0.1, 0.2)
        model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
        black_scholes = BlackScholesPricer(model)
        expected = 4.708
        price = float(black_scholes.price(option))

        self.assertAlmostEqual(price, expected, places=3)

    def test_basic_put(self):
        option = EuropeanOption(80, 1, 'put')
        market = MarketData(100, 0.1, 0.2)
        model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
        black_scholes = BlackScholesPricer(model)
        expected = 0.38
        price = float(black_scholes.price(option))

        self.assertAlmostEqual(price, expected, places=3)
    
    def test_deep_ITM_call(self):
        option = EuropeanOption(100, 1, 'call')
        market = MarketData(200, 0.05, 0.2)
        model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
        black_scholes = BlackScholesPricer(model)
        expected = 200 - 100 * np.exp(-0.05*1)
        price = float(black_scholes.price(option))

        self.assertAlmostEqual(price, expected, delta=0.01)
    
    def test_deep_ITM_put(self):
        option = EuropeanOption(200, 1, 'put')
        market = MarketData(100, 0.05, 0.2)
        model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
        black_scholes = BlackScholesPricer(model)
        expected = 200 * np.exp(-0.05*1) - 100 
        price = float(black_scholes.price(option))

        self.assertAlmostEqual(price, expected, delta=0.01)

    def test_deep_OTM_call(self):
        option = EuropeanOption(100, 1, 'call')
        market = MarketData(50, 0.05, 0.2)
        model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
        black_scholes = BlackScholesPricer(model)
        price = float(black_scholes.price(option))

        self.assertLessEqual(price, 1)

    def test_deep_OTM_put(self):
        option = EuropeanOption(50, 1,'put')
        market = MarketData(100, 0.05, 0.2)
        model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
        black_scholes = BlackScholesPricer(model)
        price = float(black_scholes.price(option))

        self.assertLessEqual(price, 1)

    def test_put_call_parity(self):
        spot = 100
        strike = 150
        maturity = 2
        sigma = 0.3
        risk_free_rate = 0.05
        
        market = MarketData(spot, risk_free_rate, sigma)
        call = EuropeanOption(strike, maturity,'call')
        put = EuropeanOption(strike, maturity, 'put')
        
        model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
        black_scholes = BlackScholesPricer(model)

        C = float(black_scholes.price(call))
        P = float(black_scholes.price(put))

        diff_C_P = C - P
        diff = float(spot - strike * np.exp((-risk_free_rate) * maturity))

        self.assertAlmostEqual(diff_C_P, diff, places=12)

    def test_volatility_monotone(self):
        """Call price should increase with volatility."""
        spot = 100
        strike = 100
        maturity = 1
        risk_free_rate = 0.05
        sigmas = np.linspace(0.01, 1.0, 10)
        previous_price = 0
        opt = EuropeanOption(strike, maturity, 'call')
        for sigma in sigmas:
            market = MarketData(spot, risk_free_rate, sigma)
            model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
            black_scholes = BlackScholesPricer(model)
            calculated = float(black_scholes.price(opt))
            self.assertGreaterEqual(calculated, previous_price)
            previous_price = calculated

    def test_random_stress(self):
        """Random options within bounds, price within no-arbitrage limits."""
        rng = np.random.default_rng(seed=42)
        for _ in range(20):
            spot = rng.uniform(10, 200)
            strike = rng.uniform(10, 200)
            maturity = rng.uniform(0.01, 5)
            sigma = rng.uniform(0.05, 1)
            risk_free_rate = rng.uniform(0, 0.2)

            market = MarketData(spot, risk_free_rate, sigma)

            call = EuropeanOption(strike, maturity, 'call')
            put = EuropeanOption(strike, maturity, 'put')

            model = GBMModel(market.spot, market.risk_free_rate, market.sigma, 1)
            black_scholes = BlackScholesPricer(model)

            C = float(black_scholes.price(call))
            P = float(black_scholes.price(put))

            self.assertGreaterEqual(C, 0)
            self.assertLessEqual(C, spot)
            self.assertGreaterEqual(P, 0)
            self.assertLessEqual(P, strike * np.exp(-risk_free_rate*maturity))
    
if __name__ == "__main__":
    unittest.main()
