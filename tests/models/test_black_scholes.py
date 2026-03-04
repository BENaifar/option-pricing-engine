import unittest

import numpy as np

from src.models.option import Option
from src.models.black_scholes import BlackScholes

class TestBlackScholes(unittest.TestCase):

    def test_basic_call(self):
        option = Option(100, 120, 1, 0.2, 0.1, 'call')
        black_scholes = BlackScholes(option)
        expected = 4.708
        price = float(black_scholes.price())

        self.assertAlmostEqual(price, expected, places=3)

    def test_basic_put(self):
        option = Option(100, 80, 1, 0.2, 0.1, 'put')
        black_scholes = BlackScholes(option)
        expected = 0.38
        price = float(black_scholes.price())

        self.assertAlmostEqual(price, expected, places=3)
    
    def test_deep_ITM_call(self):
        option = Option(200, 100, 1, 0.2, 0.05, 'call')
        black_scholes = BlackScholes(option)
        expected = 200 - 100 * np.exp(-0.05*1)
        price = float(black_scholes.price())

        self.assertAlmostEqual(price, expected, delta=0.01)
    
    def test_deep_ITM_put(self):
        option = Option(100, 200, 1, 0.2, 0.05, 'put')
        black_scholes = BlackScholes(option)
        expected = 200 * np.exp(-0.05*1) - 100 
        price = float(black_scholes.price())

        self.assertAlmostEqual(price, expected, delta=0.01)

    def test_deep_OTM_call(self):
        option = Option(50, 100, 1, 0.2, 0.05, 'call')
        black_scholes = BlackScholes(option)
        price = float(black_scholes.price())

        self.assertLessEqual(price, 1)

    def test_deep_OTM_put(self):
        option = Option(100, 50, 1, 0.2, 0.05, 'put')
        black_scholes = BlackScholes(option)
        price = float(black_scholes.price())

        self.assertLessEqual(price, 1)

    def test_put_call_parity(self):
        S0 = 100
        K = 150
        T = 2
        sigma = 0.3
        r = 0.05
        
        call = Option(S0, K, T, sigma, r, 'call')
        put = Option(S0, K, T, sigma, r, 'put')
        
        black_scholes_call = BlackScholes(call)
        black_scholes_put = BlackScholes(put)

        C = float(black_scholes_call.price())
        P = float(black_scholes_put.price())

        diff_C_P = C - P
        diff = float(S0 - K * np.exp((-r) * T))

        self.assertAlmostEqual(diff_C_P, diff, places=12)

    def test_volatility_monotone(self):
        """Call price should increase with volatility."""
        S0 = 100
        K = 100
        T = 1
        r = 0.05
        sigmas = np.linspace(0.01, 1.0, 10)
        previous_price = 0
        for sigma in sigmas:
            opt = Option(S0, K, T, sigma, r, 'call')
            black = BlackScholes(opt)
            calculated = float(black.price())
            self.assertGreaterEqual(calculated, previous_price)
            previous_price = calculated

    def test_random_stress(self):
        """Random options within bounds, price within no-arbitrage limits."""
        rng = np.random.default_rng(seed=42)
        for _ in range(20):
            S0 = rng.uniform(10, 200)
            K = rng.uniform(10, 200)
            T = rng.uniform(0.01, 5)
            sigma = rng.uniform(0.05, 1)
            r = rng.uniform(0, 0.2)

            call = Option(S0, K, T, sigma, r, 'call')
            put = Option(S0, K, T, sigma, r, 'put')

            black_scholes_call = BlackScholes(call)
            black_scholes_put = BlackScholes(put)

            C = float(black_scholes_call.price())
            P = float(black_scholes_put.price())

            self.assertGreaterEqual(C, 0)
            self.assertLessEqual(C, S0)
            self.assertGreaterEqual(P, 0)
            self.assertLessEqual(P, K * np.exp(-r*T))
    
if __name__ == "__main__":
    unittest.main()
