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
    
    def test_delta_finite_difference(self):

        S0 = 100
        K = 100
        T = 1
        sigma = 0.2
        r = 0.05
        epsilon = 1e-4

        option = Option(S0, K, T, sigma, r, "call")
        bs = BlackScholes(option)

        option_up = Option(S0 + epsilon, K, T, sigma, r, "call")
        option_down = Option(S0 - epsilon, K, T, sigma, r, "call")

        price_up = BlackScholes(option_up).price()
        price_down = BlackScholes(option_down).price()

        numerical_delta = float((price_up - price_down) / (2 * epsilon))

        self.assertAlmostEqual(float(bs.delta()), numerical_delta, places=3)

    def test_gamma_finite_difference(self):

        S0 = 100
        K = 100
        T = 1
        sigma = 0.2
        r = 0.05
        epsilon = 1e-4

        option = Option(S0, K, T, sigma, r, "call")
        bs = BlackScholes(option)

        price = bs.price()

        option_up = Option(S0 + epsilon, K, T, sigma, r, "call")
        option_down = Option(S0 - epsilon, K, T, sigma, r, "call")

        price_up = BlackScholes(option_up).price()
        price_down = BlackScholes(option_down).price()

        numerical_gamma = (price_up - 2*price + price_down) / (epsilon**2)

        self.assertAlmostEqual(bs.gamma(), numerical_gamma, places=3)

    def test_vega_finite_difference(self):

        S0 = 100
        K = 100
        T = 1
        sigma = 0.2
        r = 0.05
        epsilon = 1e-4

        option = Option(S0, K, T, sigma, r, "call")
        bs = BlackScholes(option)

        option_up = Option(S0, K, T, sigma + epsilon, r, "call")
        option_down = Option(S0, K, T, sigma - epsilon, r, "call")

        price_up = BlackScholes(option_up).price()
        price_down = BlackScholes(option_down).price()

        numerical_vega = (price_up - price_down) / (2 * epsilon)

        self.assertAlmostEqual(bs.vega(), numerical_vega, places=3)

    def test_rho_finite_difference(self):

        S0 = 100
        K = 100
        T = 1
        sigma = 0.2
        r = 0.05
        epsilon = 1e-4

        option = Option(S0, K, T, sigma, r, "call")
        bs = BlackScholes(option)

        option_up = Option(S0, K, T, sigma, r + epsilon, "call")
        option_down = Option(S0, K, T, sigma, r - epsilon, "call")

        price_up = BlackScholes(option_up).price()
        price_down = BlackScholes(option_down).price()

        numerical_rho = (price_up - price_down) / (2 * epsilon)

        self.assertAlmostEqual(bs.rho(), numerical_rho, places=3)

    def test_theta_finite_difference(self):

        S0 = 100
        K = 100
        T = 1
        sigma = 0.2
        r = 0.05
        epsilon = 1e-5

        option = Option(S0, K, T, sigma, r, "call")
        bs = BlackScholes(option)

        option_forward = Option(S0, K, T + epsilon, sigma, r, "call")

        price = bs.price()
        price_forward = BlackScholes(option_forward).price()

        numerical_theta = (price - price_forward) / epsilon

        self.assertAlmostEqual(bs.theta(), numerical_theta, places=2)

    def test_call_delta_bounds(self):
        option = Option(100, 100, 1, 0.2, 0.05, "call")
        bs = BlackScholes(option)

        delta = bs.delta()

        self.assertGreater(delta, 0)
        self.assertLess(delta, 1)

    def test_put_delta_bounds(self):
        option = Option(100, 100, 1, 0.2, 0.05, "put")
        bs = BlackScholes(option)

        delta = bs.delta()

        self.assertLess(delta, 0)
        self.assertGreater(delta, -1)

    def test_gamma_positive(self):
        option = Option(100, 100, 1, 0.2, 0.05, "call")
        bs = BlackScholes(option)

        self.assertGreater(bs.gamma(), 0)

    def test_vega_positive(self):
        option = Option(100, 100, 1, 0.2, 0.05, "call")
        bs = BlackScholes(option)

        self.assertGreater(bs.vega(), 0)

    def test_rho_signs(self):

        call = Option(100, 100, 1, 0.2, 0.05, "call")
        put = Option(100, 100, 1, 0.2, 0.05, "put")

        bs_call = BlackScholes(call)
        bs_put = BlackScholes(put)

        self.assertGreater(bs_call.rho(), 0)
        self.assertLess(bs_put.rho(), 0)

    def test_theta_negative(self):

        option = Option(100, 100, 1, 0.2, 0.05, "call")
        bs = BlackScholes(option)

        self.assertLess(bs.theta(), 0)

    def test_call_delta_increases_with_spot(self):

        option1 = Option(90, 100, 1, 0.2, 0.05, "call")
        option2 = Option(110, 100, 1, 0.2, 0.05, "call")

        delta1 = BlackScholes(option1).delta()
        delta2 = BlackScholes(option2).delta()

        self.assertGreater(delta2, delta1)

    def test_gamma_peak_near_atm(self):

        deep_itm = Option(150, 100, 1, 0.2, 0.05, "call")
        atm = Option(100, 100, 1, 0.2, 0.05, "call")
        deep_otm = Option(50, 100, 1, 0.2, 0.05, "call")

        gamma_itm = BlackScholes(deep_itm).gamma()
        gamma_atm = BlackScholes(atm).gamma()
        gamma_otm = BlackScholes(deep_otm).gamma()

        self.assertGreater(gamma_atm, gamma_itm)
        self.assertGreater(gamma_atm, gamma_otm)

    def test_vega_increases_with_maturity(self):

        short = Option(100, 100, 0.5, 0.2, 0.05, "call")
        long = Option(100, 100, 2, 0.2, 0.05, "call")

        vega_short = BlackScholes(short).vega()
        vega_long = BlackScholes(long).vega()

        self.assertGreater(vega_long, vega_short)

if __name__ == "__main__":
    unittest.main()
