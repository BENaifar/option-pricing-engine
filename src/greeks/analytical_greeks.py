from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.instruments.base_option import BaseOption

@dataclass
class AnalyticalGreeks:
    spot: float
    rate: float
    sigma: float

    def __post_init__(self):
        if self.spot <= 0:
            raise ValueError("Spot price must be positive.")
        if self.sigma <= 0:
            raise ValueError("Volatility must be positive.")

    def _d1_d2(self, option: BaseOption):
        d1 = (np.log(self.spot / option.strike) + (self.rate + 0.5 * self.sigma ** 2) * option.maturity) / (self.sigma * np.sqrt(option.maturity))
        d2 = d1 - self.sigma * np.sqrt(option.maturity)

        return d1, d2
    
    def delta(self, option: BaseOption):
        d1, _ = self._d1_d2(option)

        if (option.option_type == "call"):
            return norm.cdf(d1)
        
        else:
            return norm.cdf(d1) - 1
    
    def gamma(self, option: BaseOption):
        d1, _ = self._d1_d2(option)

        return norm.pdf(d1) / (
            self.spot * self.sigma * np.sqrt(option.maturity)
        )
    
    def vega(self, option: BaseOption):
        d1, _ = self._d1_d2(option)

        return self.spot * norm.pdf(d1) * np.sqrt(option.maturity)
    
    def theta(self, option: BaseOption):
        d1, d2 = self._d1_d2(option)
        spot = self.spot
        strike = option.strike
        maturity = option.maturity
        sigma = self.sigma
        rate = self.rate

        volatility_decay = - ((spot * norm.pdf(d1) * sigma)
                   / (2 * np.sqrt(maturity)))
        
        if (option.option_type == 'call'):
            theta = volatility_decay - rate * strike * np.exp((-rate) * maturity) * norm.cdf(d2)
            return theta

        else:
            theta = volatility_decay + rate * strike * np.exp((-rate) * maturity) * norm.cdf(-d2)
            return theta
        
    def rho(self, option: BaseOption):
        _, d2 = self._d1_d2(option)
        strike = option.strike
        maturity = option.maturity
        rate = self.rate

        if (option.option_type == "call"):
            return strike * maturity * np.exp(-rate * maturity) * norm.cdf(d2)
        
        else:
            return -strike * maturity * np.exp(-rate * maturity) * norm.cdf(-d2)