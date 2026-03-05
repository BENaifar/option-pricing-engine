import numpy as np
from scipy.stats import norm

from src.models.option import Option

class BlackScholes:
    def __init__(self, option: Option):
        self.option = option

    def _d1_d2(self):
        d1 = (np.log(self.option.spot / self.option.strike) + (self.option.risk_free_rate + 0.5 * self.option.sigma ** 2) * self.option.maturity) / (self.option.sigma * np.sqrt(self.option.maturity))
        d2 = d1 - self.option.sigma * np.sqrt(self.option.maturity)

        return d1, d2


    def price(self) -> (np.float64):
        d1, d2 = self._d1_d2()

        if (self.option.option_type == "call"):
            price = self.option.spot * norm.cdf(d1) - self.option.strike * np.exp((-self.option.risk_free_rate) * self.option.maturity) * norm.cdf(d2)
            return price
        else:
            price = self.option.strike * np.exp((-self.option.risk_free_rate) * self.option.maturity) * norm.cdf(-d2) - self.option.spot * norm.cdf(-d1)
            return price
        
    def delta(self):
        d1, _ = self._d1_d2()

        if (self.option.option_type == "call"):
            return norm.cdf(d1)
        
        else:
            return norm.cdf(d1) - 1
    
    def gamma(self):
        d1, _ = self._d1_d2()

        return norm.pdf(d1) / (
            self.option.spot * self.option.sigma * np.sqrt(self.option.maturity)
        )
    
    def vega(self):
        d1, _ = self._d1_d2()

        return self.option.spot * norm.pdf(d1) * np.sqrt(self.option.maturity)
    
    def theta(self):
        d1, d2 = self._d1_d2()
        spot = self.option.spot
        strike = self.option.strike
        maturity = self.option.maturity
        sigma = self.option.sigma
        risk_free_rate = self.option.risk_free_rate

        volatility_decay = - ((spot * norm.pdf(d1) * sigma)
                   / (2 * np.sqrt(maturity)))
        
        if (self.option.option_type == 'call'):
            theta = volatility_decay - risk_free_rate * strike * np.exp((-risk_free_rate) * maturity) * norm.cdf(d2)
            return theta

        else:
            theta = volatility_decay + risk_free_rate * strike * np.exp((-risk_free_rate) * maturity) * norm.cdf(-d2)
            return theta
        
    def rho(self):
        _, d2 = self._d1_d2()
        strike = self.option.strike
        maturity = self.option.maturity
        risk_free_rate = self.option.risk_free_rate

        if (self.option.option_type == "call"):
            return strike * maturity * np.exp(-risk_free_rate * maturity) * norm.cdf(d2)
        
        else:
            return -strike * maturity * np.exp(-risk_free_rate * maturity) * norm.cdf(-d2)