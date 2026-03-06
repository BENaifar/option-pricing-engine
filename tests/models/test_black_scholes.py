import unittest

import numpy as np

from src.instruments.european_option import EuropeanOption
from src.models.black_scholes import BlackScholes
from src.market_data.market_data import MarketData

class TestBlackScholes(unittest.TestCase):

    def test_basic_call(self):
        option = EuropeanOption(120, 1, 'call')
        market = MarketData(100, 0.1, 0.2)
        black_scholes = BlackScholes()
        expected = 4.708
        price = float(black_scholes.price(option, market))

        self.assertAlmostEqual(price, expected, places=3)

    def test_basic_put(self):
        option = EuropeanOption(80, 1, 'put')
        market = MarketData(100, 0.1, 0.2)
        black_scholes = BlackScholes()
        expected = 0.38
        price = float(black_scholes.price(option, market))

        self.assertAlmostEqual(price, expected, places=3)
    
    def test_deep_ITM_call(self):
        option = EuropeanOption(100, 1, 'call')
        market = MarketData(200, 0.05, 0.2)
        black_scholes = BlackScholes()
        expected = 200 - 100 * np.exp(-0.05*1)
        price = float(black_scholes.price(option, market))

        self.assertAlmostEqual(price, expected, delta=0.01)
    
    def test_deep_ITM_put(self):
        option = EuropeanOption(200, 1, 'put')
        market = MarketData(100, 0.05, 0.2)
        black_scholes = BlackScholes()
        expected = 200 * np.exp(-0.05*1) - 100 
        price = float(black_scholes.price(option, market))

        self.assertAlmostEqual(price, expected, delta=0.01)

    def test_deep_OTM_call(self):
        option = EuropeanOption(100, 1, 'call')
        market = MarketData(50, 0.05, 0.2)
        black_scholes = BlackScholes()
        price = float(black_scholes.price(option, market))

        self.assertLessEqual(price, 1)

    def test_deep_OTM_put(self):
        option = EuropeanOption(50, 1,'put')
        market = MarketData(100, 0.05, 0.2)
        black_scholes = BlackScholes()
        price = float(black_scholes.price(option, market))

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
        
        black_scholes_call = BlackScholes()
        black_scholes_put = BlackScholes()

        C = float(black_scholes_call.price(call, market))
        P = float(black_scholes_put.price(put, market))

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
            black = BlackScholes()
            calculated = float(black.price(opt, market))
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

            black_scholes_call = BlackScholes()
            black_scholes_put = BlackScholes()

            C = float(black_scholes_call.price(call, market))
            P = float(black_scholes_put.price(put, market))

            self.assertGreaterEqual(C, 0)
            self.assertLessEqual(C, spot)
            self.assertGreaterEqual(P, 0)
            self.assertLessEqual(P, strike * np.exp(-risk_free_rate*maturity))
    
    def test_delta_finite_difference(self):

        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")
        market = MarketData(spot, risk_free_rate, sigma)
        bs = BlackScholes()

        market_up = MarketData(spot + epsilon, risk_free_rate, sigma)
        market_down = MarketData(spot - epsilon, risk_free_rate, sigma)

        price_up = BlackScholes().price(option, market_up)
        price_down = BlackScholes().price(option, market_down)

        numerical_delta = float((price_up - price_down) / (2 * epsilon))

        self.assertAlmostEqual(float(bs.delta(option, market)), numerical_delta, places=3)

    def test_gamma_finite_difference(self):

        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")
        market = MarketData(spot, risk_free_rate, sigma)
        bs = BlackScholes()

        price = bs.price(option, market)

        market_up = MarketData(spot + epsilon, risk_free_rate, sigma)
        market_down = MarketData(spot - epsilon, risk_free_rate, sigma)

        price_up = BlackScholes().price(option, market_up)
        price_down = BlackScholes().price(option, market_down)

        numerical_gamma = (price_up - 2*price + price_down) / (epsilon**2)

        self.assertAlmostEqual(bs.gamma(option, market), numerical_gamma, places=3)

    def test_vega_finite_difference(self):

        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")
        market = MarketData(spot, risk_free_rate, sigma)
        bs = BlackScholes()

        market_up = MarketData(spot, risk_free_rate, sigma + epsilon)
        market_down = MarketData(spot, risk_free_rate, sigma - epsilon)

        price_up = BlackScholes().price(option, market_up)
        price_down = BlackScholes().price(option, market_down)

        numerical_vega = (price_up - price_down) / (2 * epsilon)

        self.assertAlmostEqual(bs.vega(option, market), numerical_vega, places=3)

    def test_rho_finite_difference(self):

        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")
        market = MarketData(spot, risk_free_rate, sigma)
        bs = BlackScholes()

        market_up = MarketData(spot, risk_free_rate + epsilon, sigma)
        market_down = MarketData(spot, risk_free_rate - epsilon, sigma)

        price_up = BlackScholes().price(option ,market_up)
        price_down = BlackScholes().price(option, market_down)

        numerical_rho = (price_up - price_down) / (2 * epsilon)

        self.assertAlmostEqual(bs.rho(option, market), numerical_rho, places=3)

    def test_theta_finite_difference(self):

        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-5

        option = EuropeanOption(strike, maturity, "call")
        market = MarketData(spot, risk_free_rate, sigma)
        bs = BlackScholes()

        option_forward = EuropeanOption(strike, maturity + epsilon, "call")

        price = bs.price(option, market)
        price_forward = BlackScholes().price(option_forward, market)

        numerical_theta = (price - price_forward) / epsilon

        self.assertAlmostEqual(bs.theta(option, market), numerical_theta, places=2)

    def test_call_delta_bounds(self):
        option = EuropeanOption(100, 1, "call")
        market = MarketData(100, 0.05, 0.2)
        bs = BlackScholes()

        delta = bs.delta(option, market)

        self.assertGreater(delta, 0)
        self.assertLess(delta, 1)

    def test_put_delta_bounds(self):
        option = EuropeanOption(100, 1, "put")
        market = MarketData(100, 0.05, 0.2)
        bs = BlackScholes()

        delta = bs.delta(option, market)

        self.assertLess(delta, 0)
        self.assertGreater(delta, -1)

    def test_gamma_positive(self):
        option = EuropeanOption(100, 1, "call")
        market = MarketData(100, 0.05, 0.2)
        bs = BlackScholes()

        self.assertGreater(bs.gamma(option, market), 0)

    def test_vega_positive(self):
        option = EuropeanOption(100, 1, "call")
        market = MarketData(100, 0.05, 0.2)
        bs = BlackScholes()

        self.assertGreater(bs.vega(option, market), 0)

    def test_rho_signs(self):
        market = MarketData(100, 0.05, 0.2)
        call = EuropeanOption(100, 1, "call")
        put = EuropeanOption(100, 1, "put")

        bs_call = BlackScholes()
        bs_put = BlackScholes()

        self.assertGreater(bs_call.rho(call, market), 0)
        self.assertLess(bs_put.rho(put, market), 0)

    def test_theta_negative(self):
        option = EuropeanOption(100, 1, "call")
        market = MarketData(100, 0.05, 0.2)
        bs = BlackScholes()

        self.assertLess(bs.theta(option, market), 0)

    def test_call_delta_increases_with_spot(self):
        market1 = MarketData(90, 0.05, 0.2)
        market2 = MarketData(110, 0.05, 0.2)

        option = EuropeanOption(100, 1, "call")

        delta1 = BlackScholes().delta(option, market1)
        delta2 = BlackScholes().delta(option, market2)

        self.assertGreater(delta2, delta1)

    def test_gamma_peak_near_atm(self):
        option = EuropeanOption(100, 1, "call")

        deep_itm = MarketData(150, 0.05, 0.2)
        atm = MarketData(100, 0.05, 0.2)
        deep_otm = MarketData(50, 0.05, 0.2)

        gamma_itm = BlackScholes().gamma(option, deep_itm)
        gamma_atm = BlackScholes().gamma(option, atm)
        gamma_otm = BlackScholes().gamma(option, deep_otm)

        self.assertGreater(gamma_atm, gamma_itm)
        self.assertGreater(gamma_atm, gamma_otm)

    def test_vega_increases_with_maturity(self):
        market = MarketData(100, 0.05, 0.2)
        short = EuropeanOption(100, 0.5, "call")
        long = EuropeanOption(100, 2, "call")

        vega_short = BlackScholes().vega(short, market)
        vega_long = BlackScholes().vega(long, market)

        self.assertGreater(vega_long, vega_short)

if __name__ == "__main__":
    unittest.main()
