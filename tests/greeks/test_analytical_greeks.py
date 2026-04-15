import unittest

import numpy as np

from src.greeks.analytical_greeks import AnalyticalGreeks
from src.instruments.european_option import EuropeanOption
from src.models.gbm_model import GBMModel
from src.pricers.black_scholes import BlackScholesPricer

class TestAnalyticalGreeks(unittest.TestCase):

    def test_delta_finite_difference(self):
        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")

        market_up = GBMModel(spot + epsilon, risk_free_rate, sigma)
        market_down = GBMModel(spot - epsilon, risk_free_rate, sigma)

        price_up = BlackScholesPricer(market_up).price(option)
        price_down = BlackScholesPricer(market_down).price(option)

        numerical_delta = float((price_up - price_down) / (2 * epsilon))

        analytical_delta = AnalyticalGreeks(spot, risk_free_rate, sigma).delta(option)

        self.assertAlmostEqual(float(analytical_delta), numerical_delta, places=3)

    def test_gamma_finite_difference(self):
        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")
        model = GBMModel(spot, risk_free_rate, sigma)
        bs = BlackScholesPricer(model)

        price = bs.price(option)

        market_up = GBMModel(spot + epsilon, risk_free_rate, sigma)
        market_down = GBMModel(spot - epsilon, risk_free_rate, sigma)

        price_up = BlackScholesPricer(market_up).price(option)
        price_down = BlackScholesPricer(market_down).price(option)

        numerical_gamma = (price_up - 2*price + price_down) / (epsilon**2)
        analytical_gamma = AnalyticalGreeks(spot, risk_free_rate, sigma).gamma(option)

        self.assertAlmostEqual(analytical_gamma, numerical_gamma, places=3)

    def test_vega_finite_difference(self):
        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")
        model = GBMModel(spot, risk_free_rate, sigma)
        bs = BlackScholesPricer(model)

        market_up = GBMModel(spot, risk_free_rate, sigma + epsilon)
        market_down = GBMModel(spot, risk_free_rate, sigma - epsilon)

        price_up = BlackScholesPricer(market_up).price(option)
        price_down = BlackScholesPricer(market_down).price(option)

        numerical_vega = (price_up - price_down) / (2 * epsilon)
        analytical_vega = AnalyticalGreeks(spot, risk_free_rate, sigma).vega(option)

        self.assertAlmostEqual(analytical_vega, numerical_vega, places=3)

    def test_rho_finite_difference(self):
        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-4

        option = EuropeanOption(strike, maturity, "call")
        model = GBMModel(spot, risk_free_rate, sigma)
        bs = BlackScholesPricer(model)

        market_up = GBMModel(spot, risk_free_rate + epsilon, sigma)
        market_down = GBMModel(spot, risk_free_rate - epsilon, sigma)

        price_up = BlackScholesPricer(market_up).price(option)
        price_down = BlackScholesPricer(market_down).price(option)

        numerical_rho = (price_up - price_down) / (2 * epsilon)
        analytical_rho = AnalyticalGreeks(spot, risk_free_rate, sigma).rho(option)

        self.assertAlmostEqual(analytical_rho, numerical_rho, places=3)

    def test_theta_finite_difference(self):
        spot = 100
        strike = 100
        maturity = 1
        sigma = 0.2
        risk_free_rate = 0.05
        epsilon = 1e-5

        option = EuropeanOption(strike, maturity, "call")
        option_forward = EuropeanOption(strike, maturity + epsilon, "call")

        model = GBMModel(spot, risk_free_rate, sigma)

        price = BlackScholesPricer(model).price(option)
        price_forward = BlackScholesPricer(model).price(option_forward)

        numerical_theta = (price - price_forward) / epsilon
        analytical_theta = AnalyticalGreeks(spot, risk_free_rate, sigma).theta(option)

        self.assertAlmostEqual(analytical_theta, numerical_theta, places=2)

    def test_call_delta_bounds(self):
        option = EuropeanOption(100, 1, "call")
        delta = AnalyticalGreeks(100, 0.05, 0.2).delta(option)

        self.assertGreater(delta, 0)
        self.assertLess(delta, 1)

    def test_put_delta_bounds(self):
        option = EuropeanOption(100, 1, "put")
        delta = AnalyticalGreeks(100, 0.05, 0.2).delta(option)

        self.assertLess(delta, 0)
        self.assertGreater(delta, -1)

    def test_gamma_positive(self):
        option = EuropeanOption(100, 1, "call")
        gamma = AnalyticalGreeks(100, 0.05, 0.2).gamma(option)

        self.assertGreater(gamma, 0)

    def test_vega_positive(self):
        option = EuropeanOption(100, 1, "call")
        vega = AnalyticalGreeks(100, 0.05, 0.2).vega(option)

        self.assertGreater(vega, 0)

    def test_rho_signs(self):
        call = EuropeanOption(100, 1, "call")
        put = EuropeanOption(100, 1, "put")

        rho_call = AnalyticalGreeks(100, 0.05, 0.2).rho(call)
        rho_put = AnalyticalGreeks(100, 0.05, 0.2).rho(put)

        self.assertGreater(rho_call, 0)
        self.assertLess(rho_put, 0)

    def test_theta_negative(self):
        option = EuropeanOption(100, 1, "call")
        theta = AnalyticalGreeks(100, 0.05, 0.2).theta(option)

        self.assertLess(theta, 0)

    def test_call_delta_increases_with_spot(self):
        option = EuropeanOption(100, 1, "call")

        delta1 = AnalyticalGreeks(90, 0.05, 0.2).delta(option)
        delta2 = AnalyticalGreeks(110, 0.05, 0.2).delta(option)

        self.assertGreater(delta2, delta1)

    def test_gamma_peak_near_atm(self):
        option = EuropeanOption(100, 1, "call")

        gamma_itm = AnalyticalGreeks(150, 0.05, 0.2).gamma(option)
        gamma_atm = AnalyticalGreeks(100, 0.05, 0.2).gamma(option)
        gamma_otm = AnalyticalGreeks(50, 0.05, 0.2).gamma(option)

        self.assertGreater(gamma_atm, gamma_itm)
        self.assertGreater(gamma_atm, gamma_otm)

    def test_vega_increases_with_maturity(self):
        short = EuropeanOption(100, 0.5, "call")
        long = EuropeanOption(100, 2, "call")

        vega_short = AnalyticalGreeks(100, 0.05, 0.2).vega(short)
        vega_long = AnalyticalGreeks(100, 0.05, 0.2).vega(long)

        self.assertGreater(vega_long, vega_short)
